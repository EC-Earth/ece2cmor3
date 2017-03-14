#!/usr/bin/env python

import os
import sys
import logging
import ece2cmor
import jsonloader
import optparse
import datetime
from dateutil.relativedelta import relativedelta

# This example script performs cmorization of one month of ocean data, starting at \
# januari 1st 1990. It requires an output directory, a configuration and a name/prefix \
# to determine the output data files and configure \
# cmor3 correctly. The processed variables are listed in the "variables" dictionary

logging.basicConfig(level=logging.DEBUG)

startdate = datetime.date(1990,1,1)
interval = relativedelta(months=1)
curdir = os.path.dirname(os.path.abspath(__file__))


def main(args):

    parser = optparse.OptionParser()
    parser.add_option("-d","--dir" ,dest = "dir" ,help = "IFS output directory")
    parser.add_option("-e","--exp" ,dest = "exp" ,help = "Experiment name (prefix)")
    parser.add_option("-v","--var" ,dest = "varlist" ,help = "Input variable list (optional)")

    (opt,args) = parser.parse_args()
    odir = os.path.abspath(opt.dir)
    if(not os.path.isdir(odir)): raise Exception("Nonexistent output directory given:",odir)

    # Initialize ece2cmor with metadata and experiment prefix:
    ece2cmor.initialize(os.path.join(curdir,"primavera.json"),opt.exp)

    # Set directory and time interval for cmorization step:
    ece2cmor.ifsdir = odir
    ece2cmor.startdate = startdate
    ece2cmor.interval = interval

    # Load the variables as task targets:
    varlist = opt.varlist if opt.varlist else os.path.join(curdir,"varlist.json")
    jsonloader.load_targets(varlist)

    # Execute the cmorization:
    ece2cmor.perform_nemo_tasks()

if __name__ == "__main__":
    main(sys.argv[1:])
