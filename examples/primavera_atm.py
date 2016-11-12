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
# januari 1st 1990. It requires an output directory, a configuration json-file \
# and an experiment name/prefix to determine the output data files and configure \
# cmor3 correctly. The processed variables are listed in the "variables" dictionary

logging.basicConfig(level=logging.DEBUG)

startdate = datetime.date(1990,1,1)
interval = relativedelta(months=1)

def main(args):

    parser = optparse.OptionParser()
    parser.add_option("-d","--dir" ,dest = "dir" ,help = "IFS output directory")
    parser.add_option("-c","--conf",dest = "conf",help = "CMOR3 meta data json file path",metavar = "FILE")
    parser.add_option("-e","--exp" ,dest = "exp" ,help = "Experiment name (prefix)")
    (opt,args) = parser.parse_args()
    odir = os.path.abspath(opt.dir)
    if(not os.path.isdir(odir)): raise Exception("Nonexistent output directory given:",odir)

    # Initialize ece2cmor with metadata and experiment prefix:
    ece2cmor.initialize(opt.conf,opt.exp)

    # Set directory and time interval for cmorization step:
    ece2cmor.nemodir = odir
    ece2cmor.startdate = startdate
    ece2cmor.interval = interval

    # Load the variables as task targets:
    jsonloader.load_targets("primavera_atm.json")

    # Execute the cmorization:
    ece2cmor.perform_ifs_tasks()

if __name__ == "__main__":
    main(sys.argv[1:])
