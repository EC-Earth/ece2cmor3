#!/usr/bin/env python

import sys
import os
import logging
import argparse
from ece2cmor3 import ece2cmorlib
from ece2cmor3 import jsonloader

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Logger construction
log = logging.getLogger(__name__)

# Main program
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate input variable list against CMIP tables")
    parser.add_argument("--vars",dest = "varlist",help = "Input variable list json file",default = "varlist.json")
    parser.add_argument("--tabdir",dest = "tables",help = "CMIP tables directory (default: ../resources/tables)",
                        default = os.path.join(os.path.dirname(__file__),"..","resources","tables"))
    parser.add_argument("--prefix",dest = "prefix",help = "CMIP tables prefix (default: CMIP6)",default = "CMIP6")

    args = parser.parse_args()

    varlist = args.varlist
    if(not os.path.isfile(varlist)):
        log.error("Variable list file %s does not exist" % varlist)
        sys.exit(1)
    if(not  varlist.endswith(".json")):
        log.error("Variable list file %s has incorrect file type" % varlist)
        sys.exit(1)
    varlist = os.path.abspath(varlist)
    log.info("Checking input file %s" % varlist)

    tabdir = args.tables
    if(not os.path.isdir(tabdir)):
        log.error("Table directory %s does not exist" % tabdir)
        sys.exit(1)
    tabdir = os.path.abspath(tabdir)
    prefix = args.prefix
    if(not prefix):
        log.error("No table prefix has been defined")
        sys.exit(1)
    log.info("Checking against table files %s/%s_*.json" % (tabdir,prefix))

    ece2cmorlib.prefix = prefix
    ece2cmorlib.table_dir = tabdir
    ece2cmorlib.initialize()
    jsonloader.load_targets(varlist)
