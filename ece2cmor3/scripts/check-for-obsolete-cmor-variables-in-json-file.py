#!/usr/bin/env python

# Call this script by:
#  ./check-for-obsolete-cmor-variables-in-json-file.py

import sys
import os
import logging
import argparse
import json
from ece2cmor3 import ece2cmorlib, taskloader, cmor_source, cmor_utils, components

# Logging configuration
logformat = "%(levelname)s:%(name)s: %(message)s"
logdateformat = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.DEBUG, format=logformat, datefmt=logdateformat)

# Logger construction
log = logging.getLogger(__name__)


def check_obsolete(fname):
    f = open(fname).read()
    data = json.loads(f)
    for d in data:
        tgt = d.get("target", None)
        if not tgt: continue
        tgtlist = [tgt]
        if isinstance(tgt, list):
            tgtlist = tgt
        for tvar in tgtlist:
            if tvar not in [t.variable for t in ece2cmorlib.targets]:
                if tvar in ["rsscsaf", "rssaf", "rlscsaf", "rlsaf"]:
                 log.info("Non-cmor target found (see #575) in %s: %s" % (fname, tvar))
                elif tvar in ["icnc", "icncpip", "icncsip", "icncullrichdn", "icncharrison", "icncwilson"]:
                 log.info("Non-cmor target found (see #575 later added) in %s: %s" % (fname, tvar))
                elif tvar in ["tosa", "ta23r", "ta36", "ua23r", "ua36", "va23r", "va36", "hus23r", "hus36", "tsl4sl"]:
                 log.info("Non-cmor target found (see #664) in %s: %s" % (fname, tvar))
              # elif tvar in ["tsl4sl"]:
              #  log.info("Non-cmor target found (see #664 and commit a300ac9) in %s: %s" % (fname, tvar))
                elif tvar in ["cLand1st", "cFluxYr", "cLandYr"]:
                 log.info("Non-cmor target found (see #778 & #782) in %s: %s" % (fname, tvar))
                elif tvar in ["conccnmode01", "conccnmode02", "conccnmode03", "conccnmode04", "conccnmode05", "conccnmode06", "conccnmode07", "mmraerh2omode01", "mmraerh2omode02", "mmraerh2omode03", "mmraerh2omode04", "mmrbcmode02", "mmrbcmode03", "mmrbcmode04", "mmrbcmode05", "mmrdustmode03", "mmrdustmode04", "mmrdustmode06", "mmrdustmode07", "mmroamode02", "mmroamode03", "mmroamode04", "mmroamode05", "mmrso4mode01", "mmrso4mode02", "mmrso4mode03", "mmrso4mode04", "mmrsoamode01", "mmrsoamode02", "mmrsoamode03", "mmrsoamode04", "mmrsoamode05", "mmrssmode03", "mmrssmode04", "ald2", "c2h4", "c2h5oh", "ch3cocho", "ch3o2h", "ch3o2no2", "ch3oh", "h2o2", "h2so4", "hcooh", "hno4", "hono", "ispd", "mcooh", "msa", "n2o5", "nh3", "ole", "orgntr", "par", "rooh", "terp"]:
                 log.info("Non-cmor target found (see #775) in %s: %s" % (fname, tvar))
                elif tvar in ["cvl", "cvh", "tvl", "tvh", "laiLv", "laiHv"]:
                 log.info("Non-cmor target found (see #802) in %s: %s" % (fname, tvar))
                elif tvar in ["sfdsi_2"]:
                 log.info("Non-cmor target found (see #762) in %s: %s" % (fname, tvar))
                elif tvar in ["siflsaltbot"]:
                 log.info("Non-cmor target found (see #811) in %s: %s" % (fname, tvar))
                elif tvar in ["sltnortha"]:
                 log.info("Non-cmor target found (see #311 left out) in %s: %s" % (fname, tvar))
               #elif tvar in ["hcont300"]:
               # log.info("Non-cmor target found (see #814) in %s: %s" % (fname, tvar))
                else:
                 log.info("Obsolete target found            in %s: %s" % (fname, tvar))




# Main program
def main():
    parser = argparse.ArgumentParser(description="Check for obsolete cmor variables in json file")
    parser.add_argument("--tabdir", metavar="DIR", type=str, default=ece2cmorlib.table_dir_default,
                        help="Cmorization table directory")
    parser.add_argument("--tabid", metavar="PREFIX", type=str, default=ece2cmorlib.prefix_default,
                        help="Cmorization table prefix string")
    parser.add_argument("--output", metavar="FILE", type=str, default=None, help="Output path to write variables to")
    cmor_utils.ScriptUtils.add_model_exclusive_options(parser, "checkvars")

    args = parser.parse_args()

    # Initialize ece2cmor:
    ece2cmorlib.initialize_without_cmor(ece2cmorlib.conf_path_default, mode=ece2cmorlib.PRESERVE, tabledir=args.tabdir,
                                        tableprefix=args.tabid)

    active_components = cmor_utils.ScriptUtils.get_active_components(args)

    for model in list(components.models.keys()):
        if model in active_components:
            check_obsolete(components.models[model][components.table_file])

    # Finishing up
    ece2cmorlib.finalize_without_cmor()


if __name__ == "__main__":
    main()
