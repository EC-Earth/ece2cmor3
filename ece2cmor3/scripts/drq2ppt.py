#!/usr/bin/env python

import sys
import os
import logging
import argparse
import json
import f90nml
import re
from ece2cmor3 import ece2cmorlib,taskloader,cmor_source,cmor_utils


# Logging configuration
logging.basicConfig(level=logging.DEBUG)


# Logger construction
log = logging.getLogger(__name__)


# Determines the ifs output period for given task (in hours)
def get_output_freq(task):
    if(task.target.frequency == "fx"):
        return 0
    if(task.target.frequency.startswith("subhr")):
        return -1
    regex = re.search("^[0-9]+hr*",task.target.frequency)
    if(regex):
        return int(regex.group(0)[:-2])
    return get_sample_freq(task)


# Determines the ifs output frequency for daily/monthly variables. By default
# 2D variables are requested on 3-hourly basis and 3D variables on 6-hourly basis.
def get_sample_freq(task):
    if(getattr(task.target,"spatial_dims",2) == 3):
        return 6
    else:
        return 3


# Writes a set of input IFS files for the requested tasks
def write_ppt_files(tasks):
    freqgroups = cmor_utils.group(tasks,get_output_freq)
    for freq in freqgroups:
        # TODO: implement writing


# Main program
def main():

    parser = argparse.ArgumentParser(description = "Create IFS ppt files for given data request")
    parser.add_argument("--vars",   metavar = "FILE",   type = str, required = True, help = "File (json|f90 namelist|xlsx) containing cmor variables (Required)")
    parser.add_argument("--tabdir", metavar = "DIR",    type = str, default = ece2cmorlib.table_dir_default, help = "Cmorization table directory")
    parser.add_argument("--tabid",  metavar = "PREFIX", type = str, default = ece2cmorlib.prefix_default, help = "Cmorization table prefix string")

    args = parser.parse_args()

    # Initialize ece2cmor:
    ece2cmorlib.initialize_without_cmor(ece2cmorlib.conf_path_default,mode = ece2cmorlib.PRESERVE,tabledir = args.tabdir,tableprefix = args.tabid)

    # Load the variables as task targets:
    taskloader.load_targets(args.vars,load_atm_tasks = True,load_oce_tasks = False)

    # Write the IFS input files
    write_ppt_files(ece2cmorlib.tasks)

    # Finishing up
    ece2cmorlib.finalize_without_cmor()

if __name__ == "__main__":
    main()
