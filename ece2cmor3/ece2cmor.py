#!/usr/bin/env python

import argparse
import datetime
import dateutil.parser
import dateutil.relativedelta
import logging
import os
import sys

from ece2cmor3 import ece2cmorlib, taskloader, components

logging.basicConfig(level=logging.DEBUG)


def main(args=None):
    if args is None:
        pass

    parser = argparse.ArgumentParser(description="Post-processing and cmorization of EC-Earth output",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("datadir", metavar="DIR", type=str)
    parser.add_argument("--vars", metavar="FILE", type=str, default=None,
                        help="File (json|f90 namelist|xlsx) containing cmor variables")
    parser.add_argument("--conf", metavar="FILE.json", type=str, default=ece2cmorlib.conf_path_default,
                        help="Input metadata file")
    parser.add_argument("--exp", metavar="EXPID", type=str, default="ECE3", help="Experiment prefix")
    parser.add_argument("--refd", metavar="YYYY-mm-dd", type=str, default="1850-01-01",
                        help="Reference date for output time axes")
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
    parser.add_argument("--npp", metavar="N", type=int, default=8, help="Number of parallel tasks")
    parser.add_argument("--ncdo", metavar="N", type=int, default=4,
                        help="Number of available threads per CDO postprocessing task")
    parser.add_argument("--nomask", action="store_true", default=False, help="Disable masking of fields")
    parser.add_argument("--nofilter", action="store_true", default=False, help="Disable automatic filtering of grib "
                                                                               "files")
    model_attributes, model_tabfile_attributes = {}, {}
    for c in components.models:
        flag1, flag2 = components.get_script_options(c)
        if flag2 is None:
            parser.add_argument("--" + flag1, action="store_true", default=False,
                                help="Run ece2cmor3 exclusively for %s data" % c)
        else:
            parser.add_argument("--" + flag1, '-' + flag2, action="store_true", default=False,
                                help="Run ece2cmor3 exclusively for %s data" % c)
        model_attributes[c] = flag1
        tabfile = components.models[c].get(components.table_file, "")
        if tabfile:
            option = os.path.basename(tabfile)
            model_tabfile_attributes[c] = option
            parser.add_argument("--" + option, metavar="FILE.json", type=str, default=tabfile,
                                help="%s variable table (optional)" % c)

    args = parser.parse_args()

    if not os.path.isdir(args.datadir):
        print ' ERROR for the datadir argument: The datadir directory is not found: ', args.datadir, ' no such directory.'
        sys.exit(' Exiting ece2cmor.')

    if not os.path.isfile(args.vars):
        print ' ERROR for the --vars argument: The data request file is not found: ', args.vars, ' no such file.'
        sys.exit(' Exiting ece2cmor.')

    if not os.path.isfile(args.conf):
        print ' ERROR for the --conf argument: The metadata file is not found: ', args.conf, ' no such file.'
        sys.exit(' Exiting ece2cmor.')

    modedict = {"preserve": ece2cmorlib.PRESERVE, "append": ece2cmorlib.APPEND, "replace": ece2cmorlib.REPLACE}

    # Initialize ece2cmor:
    ece2cmorlib.initialize(args.conf, mode=modedict[args.mode], tabledir=args.tabdir, tableprefix=args.tabid)
    ece2cmorlib.enable_masks = not args.nomask
    ece2cmorlib.auto_filter = not args.nofilter

    # Fix exclusive run flags: if none are used, we cmorize for all components
    model_active_flags = dict.fromkeys(components.models, False)
    for model in model_attributes:
        model_active_flags[model] = getattr(args, model_attributes[model], False)
    if not any(model_active_flags.values()):
        model_active_flags = dict.fromkeys(model_active_flags, True)

    # Load the variables as task targets:
    for model in model_tabfile_attributes:
        tabfile_attribute = model_tabfile_attributes[model]
        attribute_value = getattr(args, tabfile_attribute, None)
        if attribute_value is not None:
            components.models[model][components.table_file] = attribute_value

    taskloader.load_targets(args.vars, model_active_flags)

    refdate = datetime.datetime.combine(dateutil.parser.parse(args.refd), datetime.datetime.min.time())

    if model_active_flags["ifs"]:
        # Execute the atmosphere cmorization:
        ece2cmorlib.perform_ifs_tasks(args.datadir, args.exp,
                                      refdate=refdate,
                                      outputfreq=args.freq,
                                      tempdir=args.tmpdir,
                                      taskthreads=args.npp,
                                      cdothreads=args.ncdo)
    if model_active_flags["nemo"]:
        ece2cmorlib.perform_nemo_tasks(args.datadir, args.exp, refdate)

    if model_active_flags["lpjg"]:
        ece2cmorlib.perform_lpjg_tasks(args.datadir, args.tmpdir, args.exp, refdate)
    if model_active_flags["tm5"]:
        refdate = dateutil.parser.parse(args.refd) if args.refd else None
        
        ece2cmorlib.perform_tm5_tasks(args.datadir, args.tmpdir, args.exp, startdate, length, refdate)

#   if procNEWCOMPONENT:
#       ece2cmorlib.perform_NEWCOMPONENT_tasks(args.datadir, args.exp, refdate)

    ece2cmorlib.finalize()


if __name__ == "__main__":
    main()
