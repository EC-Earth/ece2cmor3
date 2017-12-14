#!/usr/bin/env python

import os
import sys
import logging
import argparse
import cmor_source
import ece2cmorlib
import jsonloader
import dateutil.parser
import dateutil.relativedelta
import datetime

logging.basicConfig(level=logging.DEBUG)

def is3hrtask(task):
   if(not isinstance(task.source,cmor_source.ifs_source)): return False
   if(task.target.variable in ["ua850","va850"]): return True
   return (task.source.spatial_dims == 2)

def is6hrtask(task):
   if(not isinstance(task.source,cmor_source.ifs_source)): return False
   if(task.target.variable in ["ua850","va850"]): return False
   if(getattr(task.target,"frequency",None) == "3hr"): return False
   return (task.source.spatial_dims == 3)

varlistcmip = os.path.join(os.path.dirname(__file__),"resources","data_request","CMIP6","varlist.json")
varlistprim = os.path.join(os.path.dirname(__file__),"resources","data_request","PRIMAVERA","varlist.json")

def main(args):

    varlist_path_default = os.path.join(os.path.dirname(__file__),"resources","varlist.json")

    parser = argparse.ArgumentParser(description = "Post-processing and cmorization of EC-Earth output",
                                     formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("datadir",  metavar = "DIR",        type = str)
    parser.add_argument("date",     metavar = "YYYY-mm-dd", type = str)
    parser.add_argument("--conf",   metavar = "FILE.json",  type = str,     default = ece2cmorlib.conf_path_default,help = "Input metadata file")
    parser.add_argument("--exp",    metavar = "EXPID",      type = str,     default = "ECE3",help = "Experiment prefix")
    parser.add_argument("--vars",   metavar = "FILE.json",  type = str,     default = None,help = "json-file containing cmor variables")
    parser.add_argument("--refd",   metavar = "YYYY-mm-dd", type = str,     default = None,help = "Reference date (for atmosphere data), by default 1950-01-01")
    parser.add_argument("--mode",   metavar = "MODE",       type = str,     default = "preserve",help = "CMOR netcdf mode",choices = ["preserve","replace","append"])
    parser.add_argument("--freq",   metavar = "N",          type = int,     default = 3,help = "IFS output frequency, in hours",choices = [3,6])
    parser.add_argument("--tabid",  metavar = "PREFIX",     type = str,     default = "CMIP6",help = "Cmorization table prefix string",choices = ["CMIP6","PRIMAVERA"])
    parser.add_argument("--tmpdir", metavar = "DIR",        type = str,     default = "/tmp/ece2cmor3", help = "Temporary working directory")
    parser.add_argument("--npp",    metavar = "N",          type = int,     default = 8, help = "Number of post-processing threads")
    parser.add_argument("--tmpsize",metavar = "X",          type = float,   default = float("inf"),help = "Size of tempdir (in GB) that triggers flushing")
    parser.add_argument("--ncdo",   metavar = "N",          type = int,     default = 4,help = "Number of available threads per CDO postprocessing task")
    parser.add_argument("-a", "--atm", action = "store_true", default = False, help = "Run ece2cmor3 exclusively for atmosphere data")
    parser.add_argument("-o", "--oce", action = "store_true", default = False, help = "Run ece2cmor3 exclusively for ocean data")
    parser.add_argument("--nomask"   , action = "store_true", default = False, help = "Disable masking of fields")

    args = parser.parse_args()

    modedict = {"preserve":ece2cmorlib.PRESERVE,"append":ece2cmorlib.APPEND,"replace":ece2cmorlib.REPLACE}
    # Initialize ece2cmor:
    ece2cmorlib.initialize(args.conf,mode = modedict[args.mode],tableprefix = args.tabid)
    ece2cmorlib.enable_masks = not args.nomask

    varlist = args.vars
    if(not varlist):
        varlist = varlistcmip if args.tabid == "CMIP6" else varlistprim

    # Load the variables as task targets:
    jsonloader.load_targets(varlist)

    # Fix conflicting flags
    procatmos,prococean = not args.oce,not args.atm
    if(not procatmos and not prococean):
        procatmos,prococean = True,True

    startdate = dateutil.parser.parse(args.date)
    length = dateutil.relativedelta.relativedelta(months = 1)
    if(procatmos):
        filterfunc = is6hrtask if args.freq == 6 else is3hrtask
        ece2cmorlib.tasks = [t for t in ece2cmorlib.tasks if filterfunc(t)]
        refdate = dateutil.parser.parse(args.refd) if args.refd else datetime.date(1950,1,1)
        # Execute the atmosphere cmorization:
        ece2cmorlib.perform_ifs_tasks(args.datadir,args.exp,startdate,length,refdate = refdate,
                                                                             outputfreq = args.freq,
                                                                             tempdir = args.tmpdir,
                                                                             taskthreads = args.npp,
                                                                             cdothreads = args.ncdo,
                                                                             maxsizegb = args.tmpsize)
    if(prococean):
        ece2cmorlib.perform_nemo_tasks(args.datadir,args.exp,startdate,length)

if __name__ == "__main__":
    main(sys.argv[1:])
