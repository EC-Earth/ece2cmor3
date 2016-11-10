#!/usr/bin/env python

import os
import sys
import f90nml
import json
import ece2cmor
import cmor_source
import cmor_target
import cmor_task
import namloader
import jsonloader

# This script reads all variables from the fortran namelists in the resources and
# creates tasks for them. Then these tasks are serialized to the preferred json
# format for later use by ece2cmor. This scripts can be executed if the fortran
# namelist files are more complete than the json files and the latter need syncing.

def convert_parlist(inputfile,outputfile):
    ifsparlist = f90nml.read(inputfile)
    pardictlist = ifsparlist.get("parameter")
    parlist = [p["out_name"] for p in pardictlist]
    targets = []
    for p in parlist:
        t = ece2cmor.get_cmor_target(p)
        if(isinstance(t,cmor_target.cmor_target)):
            targets.append(t)
        else:
            targets.extend(t)
    namloader.load_targets(targets)
    dictlist = map(makedict,ece2cmor.tasks)
    with open(outputfile,'w') as ofile:
        json.dump(dictlist,ofile,indent=True)


def makedict(task):
    result = {}
    result[jsonloader.json_source_key] = task.source.var_id if isinstance(task.source,cmor_source.nemo_source) else str(task.source.get_grib_code())
    result[jsonloader.json_target_key] = task.target.variable
    result[jsonloader.json_table_key] = task.target.table
    if(isinstance(task.source,cmor_source.nemo_source)):
        result[jsonloader.json_grid_key] = task.source.grid()
    if(hasattr(task.source,cmor_source.expression_key)):
        result[cmor_source.expression_key] = getattr(task.source,cmor_source.expression_key)
    if(hasattr(task,cmor_task.conversion_key)):
        result[cmor_task.conversion_key] = getattr(task,cmor_task.conversion_key)
    return result


def main(args):

    ifs_input = os.path.join(os.path.dirname(ece2cmor.__file__),"resources","ifs.par")
    ifs_output = "ifspar.json"
    nemo_input = os.path.join(os.path.dirname(ece2cmor.__file__),"resources","nemo.par")
    nemo_output = "nemopar.json"

    ece2cmor.initialize(os.path.join(os.path.dirname(ece2cmor.__file__),"test","test_data","cmor3_metadata.json"))
    convert_parlist(ifs_input,ifs_output)
    ece2cmor.finalize()
    ece2cmor.initialize(os.path.join(os.path.dirname(ece2cmor.__file__),"test","test_data","cmor3_metadata.json"))
    convert_parlist(nemo_input,nemo_output)
    ece2cmor.finalize()


if __name__ == "__main__":
    main(sys.argv[1:])
