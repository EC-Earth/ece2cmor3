#!/usr/bin/env python

import os
import sys
import logging
import argparse
import ece2cmorlib
import jsonloader
import dateutil.parser
import dateutil.relativedelta

logging.basicConfig(level=logging.DEBUG)

def main(args):

    varlist_path_default = os.path.join(os.path.dirname(__file__),"resources","varlist.json")

    parser = argparse.ArgumentParser(description = "Post-processing and cmorization of EC-Earth output",
                                     formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("datadir",  metavar = "DIR",        type = str)
    parser.add_argument("date",     metavar = "YYYY-mm-dd", type = str)
    parser.add_argument("--vars",   metavar = "FILE.json",  type = str,     default = varlist_path_default,help = "json-file containing cmor variables")
    parser.add_argument("--conf",   metavar = "FILE.json",  type = str,     default = ece2cmorlib.conf_path_default,help = "Input metadata file")
    parser.add_argument("--exp",    metavar = "EXPID",      type = str,     default = "ECE3",help = "Experiment prefix")
    parser.add_argument("--mode",   metavar = "MODE",       type = str,     default = "preserve",help = "CMOR netcdf mode",choices = ["preserve","replace","append"])
    parser.add_argument("--freq",   metavar = "N",          type = int,     default = 3,help = "IFS output frequency, in hours")
    parser.add_argument("--tabdir", metavar = "DIR",        type = str,     default = ece2cmorlib.table_dir_default,help = "Cmorization table directory")
    parser.add_argument("--tabid",  metavar = "PREFIX",     type = str,     default = ece2cmorlib.prefix_default,help = "Cmorization table prefix string")
    parser.add_argument("--tmpdir", metavar = "DIR",        type = str,     default = "/tmp/ece2cmor3", help = "Temporary working directory")
    parser.add_argument("--npp",    metavar = "N",          type = int,     default = 8, help = "Number of post-processing threads")
    parser.add_argument("--tmpsize",metavar = "X",          type = float,   default = float("inf"),help = "Size of tempdir (in GB) that triggers flushing")
    parser.add_argument("--ncdo",   metavar = "N",          type = int,     default = 4,help = "Number of available threads per CDO postprocessing task")
    parser.add_argument("-a", "--atm", action = "store_true", default = False, help = "Run ece2cmor3 exclusively for atmosphere data")
    parser.add_argument("-o", "--oce", action = "store_true", default = False, help = "Run ece2cmor3 exclusively for ocean data")
    parser.add_argument("--pssh", action = "store_true", default = False, help = "Search surface pressure in spectral files")

    args = parser.parse_args()

    modedict = {"preserve":ece2cmorlib.PRESERVE,"append":ece2cmorlib.APPEND,"replace":ece2cmorlib.REPLACE}

    # Initialize ece2cmor:
    ece2cmorlib.initialize(args.conf,mode = modedict[args.mode],tabledir = args.tabdir,tableprefix = args.tabid)

    # Load the variables as task targets:
    jsonloader.load_targets(args.vars)

    # Fix conflicting flags
    procatmos,prococean = not args.oce,not args.atm
    if(not procatmos and not prococean):
        procatmos,prococean = True,True

    startdate = dateutil.parser.parse(args.date)
    length = dateutil.relativedelta.relativedelta(months = 1)
    if(procatmos):
        # Create temporary working directory:
        if(not os.path.isdir(args.tmpdir)): os.makedirs(args.tmpdir)
        # Execute the atmosphere cmorization:
        ece2cmorlib.perform_ifs_tasks(args.datadir,args.exp,startdate,length,outputfreq = args.freq,
                                                                             tempdir = args.tmpdir,
                                                                             taskthreads = args.npp,
                                                                             cdothreads = args.ncdo,
                                                                             maxsizegb = args.tmpsize,
                                                                             spectralps = args.pssh)
    if(prococean):
        ece2cmorlib.perform_nemo_tasks(args.datadir,args.exp,startdate,length)

if __name__ == "__main__":
    main(sys.argv[1:])
