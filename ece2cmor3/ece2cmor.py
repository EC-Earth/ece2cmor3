#!/usr/bin/env python

import argparse
import logging
import os

import dateutil.parser
import dateutil.relativedelta

from ece2cmor3 import ece2cmorlib, taskloader

logging.basicConfig(level=logging.DEBUG)


def main(args=None):
    if args is None:
        pass

    varlist_path_default = os.path.join(os.path.dirname(__file__), "resources", "varlist.json")

    parser = argparse.ArgumentParser(description="Post-processing and cmorization of EC-Earth output",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("datadir", metavar="DIR", type=str)
    parser.add_argument("date", metavar="YYYY-mm-dd", type=str)
    parser.add_argument("--vars", metavar="FILE", type=str, default=varlist_path_default,
                        help="File (json|f90 namelist|xlsx) containing cmor variables")
    parser.add_argument("--conf", metavar="FILE.json", type=str, default=ece2cmorlib.conf_path_default,
                        help="Input metadata file")
    parser.add_argument("--exp", metavar="EXPID", type=str, default="ECE3", help="Experiment prefix")
    parser.add_argument("--refd", metavar="YYYY-mm-dd", type=str, default=None,
                        help="Reference date (for atmosphere data), by default the start date")
    parser.add_argument("--mode", metavar="MODE", type=str, default="preserve", help="CMOR netcdf mode",
                        choices=["preserve", "replace", "append"])
    parser.add_argument("--freq", metavar="N", type=int, default=3,
                        help="IFS output frequency, in hours (not required if autofilter is used)")
    parser.add_argument("--tabdir", metavar="DIR", type=str, default=ece2cmorlib.table_dir_default,
                        help="Cmorization table directory")
    parser.add_argument("--tabid", metavar="PREFIX", type=str, default=ece2cmorlib.prefix_default,
                        help="Cmorization table prefix string")
    parser.add_argument("--tmpdir", metavar="DIR", type=str, default="/tmp/ece2cmor",
                        help="Temporary working directory")
    parser.add_argument("--npp", metavar="N", type=int, default=8, help="Number of post-processing threads")
    parser.add_argument("--tmpsize", metavar="X", type=float, default=float("inf"),
                        help="Size of tempdir (in GB) that triggers flushing")
    parser.add_argument("--ncdo", metavar="N", type=int, default=4,
                        help="Number of available threads per CDO postprocessing task")
    parser.add_argument("-a", "--atm", action="store_true", default=False,
                        help="Run ece2cmor3 exclusively for atmosphere data")
    parser.add_argument("-o", "--oce", action="store_true", default=False,
                        help="Run ece2cmor3 exclusively for ocean data")
    parser.add_argument("-v", "--veg", action="store_true", default=False,
                      help="Run ece2cmor3 exclusively for LPJ-Guess data")
#   parser.add_argument("-NEWCOMPONENT", "--NEWCOMPONENT", action="store_true", default=False,
#                      help="Run ece2cmor3 exclusively for ocean data")
    parser.add_argument("--nomask", action="store_true", default=False, help="Disable masking of fields")
    parser.add_argument("--filter", action="store_true", default=False, help="Automatic filtering of grib files")
    parser.add_argument("--ifspar", metavar="FILE.json", type=str,
                        default=taskloader.models["ifs"][taskloader.parfile_key],
                        help="IFS parameter file (optional)")
    parser.add_argument("--nemopar", metavar="FILE.json", type=str,
                        default=taskloader.models["nemo"][taskloader.parfile_key],
                        help="Nemo parameter file (optional")
    parser.add_argument("--lpjgpar", metavar="FILE.json", type=str,
                        default=taskloader.models["lpjg"][taskloader.parfile_key],
                        help="LPJ-Guess parameter file (optional")

    args = parser.parse_args()

    modedict = {"preserve": ece2cmorlib.PRESERVE, "append": ece2cmorlib.APPEND, "replace": ece2cmorlib.REPLACE}

    # Initialize ece2cmor:
    ece2cmorlib.initialize(args.conf, mode=modedict[args.mode], tabledir=args.tabdir, tableprefix=args.tabid)
    ece2cmorlib.enable_masks = not args.nomask
    ece2cmorlib.auto_filter = args.filter

    # Fix conflicting flags
    # The following fix is hopefully clear and more easily adapted than the original as more component data is added
    if sum([args.oce, args.atm, args.veg]) != 1:
        procatmos, prococean, proclpjg = True, True, True
    else:
        procatmos = args.atm
        prococean = args.oce
        proclpjg = args.veg
#    procatmos, prococean = not args.oce, not args.atm
#    if not procatmos and not prococean:
#        procatmos, prococean = True, True

    # Load the variables as task targets:
    taskloader.load_parameter_tables(ifs=args.ifspar, nemo=args.nemopar, lpjg=args.lpjgpar)
    taskloader.load_targets(args.vars, load_atm_tasks=procatmos, load_oce_tasks=prococean, load_lpjg_tasks=proclpjg)

    startdate = dateutil.parser.parse(args.date)
    length = dateutil.relativedelta.relativedelta(months=1)
    if procatmos:
        refdate = dateutil.parser.parse(args.refd) if args.refd else None
        # Execute the atmosphere cmorization:
        ece2cmorlib.perform_ifs_tasks(args.datadir, args.exp, startdate, length, refdate=refdate,
                                      outputfreq=args.freq,
                                      tempdir=args.tmpdir,
                                      taskthreads=args.npp,
                                      cdothreads=args.ncdo,
                                      maxsizegb=args.tmpsize)
    if prococean:
        ece2cmorlib.perform_nemo_tasks(args.datadir, args.exp, startdate, length)
    if proclpjg:
        ece2cmorlib.perform_lpjg_tasks(args.datadir, args.exp, startdate, length)
#   if procNEWCOMPONENT:
#       ece2cmorlib.perform_NEWCOMPONENT_tasks(args.datadir, args.exp, startdate, length)
   
    ece2cmorlib.finalize()


if __name__ == "__main__":
    main()
