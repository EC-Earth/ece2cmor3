#!/usr/bin/env python

# Call this script e.g. by:
#  ./drq2varlist.py --drq cmip6-data-request/cmip6-data-request-m=CMIP-e=CMIP-t=1-p=1/cmvme_CMIP_piControl_1_1.xlsxv --ececonf EC-EARTH-AOGCM
#  ./drq2varlist.py --drq ../resources/test-data-request/varlist-nemo-all.json                                       --ececonf EC-EARTH-AOGCM

import argparse
import logging
import json

from ece2cmor3 import ece2cmorlib, components, taskloader

# Logging configuration
logformat = "%(asctime)s %(levelname)s:%(name)s: %(message)s"
logdateformat = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.DEBUG, format=logformat, datefmt=logdateformat)
log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Create component-specified varlist json for given data request")
    parser.add_argument("--drq", metavar="FILE", type=str, required=True,
                        help="File (xlsx|json) containing requested cmor variables (Required)")
    parser.add_argument("--ececonf", metavar='|'.join(components.ece_configs.keys()), type=str,
                        help="EC-Earth configuration (only used with --drq option)")
    parser.add_argument("--tabdir", metavar="DIR", type=str, default=ece2cmorlib.table_dir_default,
                        help="Cmorization table directory")
    parser.add_argument("--tabid", metavar="PREFIX", type=str, default=ece2cmorlib.prefix_default,
                        help="Cmorization table prefix string")

    args = parser.parse_args()

    # Initialize ece2cmor:
    ece2cmorlib.initialize_without_cmor(tabledir=args.tabdir, tableprefix=args.tabid)

    result = taskloader.load_drq(args.drq, config=args.ececonf, check_prefs=True)
    with open("varlist.json", 'w') as ofile:
        json.dump(result, ofile, indent=4, separators=(',', ': '), sort_keys=True)


if __name__ == "__main__":
    main()
