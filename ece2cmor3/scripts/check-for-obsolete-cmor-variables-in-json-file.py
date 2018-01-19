#!/usr/bin/env python

# Call this script by:
#  python check-for-obsolete-cmor-variables-in-json-file.py

import sys
import os
import logging
import argparse
import json
from ece2cmor3 import ece2cmorlib,taskloader,cmor_source,cmor_utils

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Logger construction
log = logging.getLogger(__name__)

def check_obsolete(fname):
    f = open(fname).read()
    data = json.loads(f)
    for d in data:
        tgt = d.get("target",None)
        if(not tgt): continue
        tgtlist = [tgt]
        if(isinstance(tgt,list)):
            tgtlist = tgt
        for tvar in tgtlist:
            if tvar not in [t.variable for t in ece2cmorlib.targets]:
               log.info("Obsolete target found in %s: %s" % (fname,tvar))



# Main program
def main():

    parser = argparse.ArgumentParser(description = "Check for obsolete cmor variables in json file")
    parser.add_argument("--tabdir", metavar = "DIR",    type = str, default = ece2cmorlib.table_dir_default, help = "Cmorization table directory")
    parser.add_argument("--tabid",  metavar = "PREFIX", type = str, default = ece2cmorlib.prefix_default, help = "Cmorization table prefix string")
    parser.add_argument("--output", metavar = "FILE",   type = str, default = None, help = "Output path to write variables to")
    parser.add_argument("-a", "--atm", action = "store_true", default = False, help = "Run exclusively for atmosphere variables")
    parser.add_argument("-o", "--oce", action = "store_true", default = False, help = "Run exclusively for ocean variables")

    args = parser.parse_args()

    # Initialize ece2cmor:
    ece2cmorlib.initialize_without_cmor(ece2cmorlib.conf_path_default,mode = ece2cmorlib.PRESERVE,tabledir = args.tabdir,tableprefix = args.tabid)

    # Fix conflicting flags
    procatmos,prococean = not args.oce,not args.atm
    if(not procatmos and not prococean):
        procatmos,prococean = True,True
    print
    if(prococean):
        fname = "../resources/nemopar.json"
        check_obsolete(fname)
        
    print
    if(procatmos):
        fname = "../resources/ifspar.json"
        check_obsolete(fname)

    # Finishing up
    ece2cmorlib.finalize_without_cmor()

if __name__ == "__main__":
    main()
