#!/usr/bin/env python

import os
import sys
import logging
import f90nml
import json
import argparse
import cmor_utils
import cmor_source
import cmor_target
import cmor_task
import ece2cmor
import namloader
import jsonloader

# This script reads all variables from the fortran namelists in the resources and
# creates tasks for them. Then these tasks are serialized to the preferred json
# format for later use by ece2cmor. This scripts can be executed if the fortran
# namelist files are more complete than the json files and the latter need syncing.

logging.basicConfig(level=logging.WARNING)

# Converts the input fortran parameter namelist file to json
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
    taskgroups = cmor_utils.group(ece2cmor.tasks,lambda t:t.target.variable)
    dictlist = map(makedict,[v[0] for (k,v) in taskgroups.iteritems()])
    with open(outputfile,'w') as ofile:
        json.dump(dictlist,ofile,indent = 4,separators = (',', ': '))

# Creates a ece2cmor-compliant dictionary for the given task
def makedict(task):
    result = {}
    result[jsonloader.json_source_key] = task.source.var_id if isinstance(task.source,cmor_source.nemo_source) else str(task.source.get_grib_code())
    result[jsonloader.json_target_key] = task.target.variable
    if(isinstance(task.source,cmor_source.nemo_source)):
        result[jsonloader.json_grid_key] = task.source.grid()
    if(hasattr(task.source,cmor_source.expression_key)):
        result[cmor_source.expression_key] = getattr(task.source,cmor_source.expression_key)
    if(hasattr(task,cmor_task.conversion_key)):
        result[cmor_task.conversion_key] = getattr(task,cmor_task.conversion_key)
    return result


# Converts the input fortran variable namelist file to json
def convert_varlist(inputfile):
    namloader.load_targets(inputfile)
    nemotasks = cmor_utils.group([t for t in ece2cmor.tasks if isinstance(t.source,cmor_source.nemo_source)],lambda t:t.target.table)
    nemodict = dict([k,[t.target.variable for t in v]] for k,v in nemotasks.iteritems())
    nemofile = os.path.basename(inputfile) + "_oce.json"
    with open(nemofile,'w') as ofile:
        json.dump(nemodict,ofile,indent = 4,separators = (',', ': '))
    ifstasks = cmor_utils.group([t for t in ece2cmor.tasks if isinstance(t.source,cmor_source.ifs_source)],lambda t:t.target.table)
    ifsdict = dict([k,[t.target.variable for t in v]] for k,v in ifstasks.iteritems())
    ifsfile = os.path.basename(inputfile) + "_atm.json"
    with open(ifsfile,'w') as ofile:
        json.dump(ifsdict,ofile,indent = 4,separators = (',', ': '))
    logging.info("File %s written" % ifsfile)


# Main program
# TODO: clean up tmp directory
def main(args):

    ifs_default_input = os.path.join(os.path.dirname(ece2cmor.__file__),"resources","ifs.par")
    ifs_default_output = "ifspar.json"
    nemo_default_input = os.path.join(os.path.dirname(ece2cmor.__file__),"resources","nemo.par")
    nemo_default_output = "nemopar.json"

    parser = argparse.ArgumentParser(description="Input fortran namelist for ece2cmor to convert to json (optional)")
    parser.add_argument("--file",dest = "file",help = "input fortran namelist file (optional)",default = None)

    args = parser.parse_args()

    ifile = args.file
    if(not ifile):
        ece2cmor.initialize(os.path.join(os.path.dirname(ece2cmor.__file__),"test","test_data","cmor3_metadata.json"))
        convert_parlist(ifs_default_input,ifs_default_output)
        ece2cmor.finalize()
        ece2cmor.initialize(os.path.join(os.path.dirname(ece2cmor.__file__),"test","test_data","cmor3_metadata.json"))
        convert_parlist(nemo_default_input,nemo_default_output)
        ece2cmor.finalize()
    elif(os.path.exists(ifile)):
        ece2cmor.initialize(os.path.join(os.path.dirname(ece2cmor.__file__),"test","test_data","cmor3_metadata.json"))
        if(os.path.basename(ifile) in ["ifs.par","nemo.par"]):
            convert_parlist(os.path.abspath(ifile),os.path.basename(ifile).replace(".","") + ".json")
        else:
            convert_varlist(os.path.abspath(ifile))
        ece2cmor.finalize()
    else:
        logging.error("Could not find file % s" % ifile)


if __name__ == "__main__":
    main(sys.argv[1:])
