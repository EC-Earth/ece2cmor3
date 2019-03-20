#!/usr/bin/env python

# Call this script e.g. by:
#  ./drq2varlist.py --drq cmip6-data-request/cmip6-data-request-m=CMIP-e=CMIP-t=1-p=1/cmvme_CMIP_piControl_1_1.xlsx --ececonf EC-EARTH-AOGCM
#  ./drq2varlist.py --drq ../resources/test-data-request/varlist-nemo-all.json                                      --ececonf EC-EARTH-AOGCM
import os
import sys

import argparse
import logging
import json

from ece2cmor3 import ece2cmorlib, components, taskloader, cmor_utils

# Logging configuration
logformat = "%(asctime)s %(levelname)s:%(name)s: %(message)s"
logdateformat = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.DEBUG, format=logformat, datefmt=logdateformat)
log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Create component-specified varlist json for given data request")
    parser.add_argument("--drq", metavar="FILE", type=str, required=True,
                        help="File (xlsx|json) containing requested cmor variables (Required)")
    parser.add_argument("--varlist", "-o", metavar="FILE.json", type=str, default="varlist.json",
                        help="Output filepath")
    parser.add_argument("--ececonf", metavar='|'.join(components.ece_configs.keys()), type=str,
                        help="EC-Earth configuration (only used with --drq option)")
    parser.add_argument("--tabdir", metavar="DIR", type=str, default=ece2cmorlib.table_dir_default,
                        help="Cmorization table directory")
    parser.add_argument("--tabid", metavar="PREFIX", type=str, default=ece2cmorlib.prefix_default,
                        help="Cmorization table prefix string")

    args = parser.parse_args()

    print ""
    print "Running drq2varlist.py with:"
    print "./drq2varlist.py " + cmor_utils.ScriptUtils.get_drq_vars_options(args)
    print ""

    if not os.path.isfile(args.drq):
        log.fatal("Your data request file %s cannot be found." % args.drq)
        sys.exit(' Exiting drq2varlist.')

    # Initialize ece2cmor:
    ece2cmorlib.initialize_without_cmor(tabledir=args.tabdir, tableprefix=args.tabid)

    try:
        matches, omitted = taskloader.load_drq(args.drq, config=args.ececonf, check_prefs=True)
    except taskloader.SwapDrqAndVarListException as e:
        log.error(e.message)
        opt1, opt2 = "vars" if e.reverse else "drq", "drq" if e.reverse else "vars"
        log.error("It seems you are using the --%s option where you should use the --%s option for this file"
                  % (opt1, opt2))
        sys.exit(' Exiting drq2varlist.')

    result = {}
    for model, targetlist in matches.items():
        result[model] = {}
        for target in targetlist:
            table = target.table
            if table in result[model]:
                result[model][table].append(target.variable)
            else:
                result[model][table] = [target.variable]
    with open(args.varlist, 'w') as ofile:
        json.dump(result, ofile, indent=4, separators=(',', ': '), sort_keys=True)


if __name__ == "__main__":
    main()
