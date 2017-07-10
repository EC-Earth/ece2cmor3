#!/usr/bin/env python

import os
import sys
import logging
from ece2cmor3 import ece2cmorlib
from ece2cmor3 import jsonloader
import optparse
import datetime
from dateutil.relativedelta import relativedelta

# This example script performs cmorization of one month of ocean data, starting at \
# januari 1st 1990. It requires an output directory, a configuration json-file \
# and an experiment name/prefix to determine the output data files and configure \
# cmor3 correctly. The processed variables are listed in the "variables" dictionary

logging.basicConfig(level=logging.DEBUG)

variables = {"Omon" : ["sos","tos"]}
startdate = datetime.date(1990,1,1)
interval = relativedelta(months=1)
srcdir = os.path.dirname(os.path.abspath(ece2cmorlib.__file__))
datadir = os.path.join(srcdir,"test","test_data","nemodata")

def main(args):

    parser = optparse.OptionParser()
    parser.add_option("-c","--conf",dest = "conf",help = "CMOR3 meta data json file path",metavar = "FILE",default = ece2cmorlib.conf_path_default)
    parser.add_option("-d","--dir" ,dest = "dir" ,help = "IFS output directory",default = datadir)
    parser.add_option("-e","--exp" ,dest = "exp" ,help = "Experiment name (prefix)",default = "exp")
    (opt,args) = parser.parse_args()

    # Initialize ece2cmorlib with metadata and experiment prefix:
    ece2cmorlib.initialize(opt.conf)

    # Load the variables as task targets:
    jsonloader.load_targets(variables)

    # Execute the cmorization:
    ece2cmorlib.perform_nemo_tasks(opt.dir,opt.exp,startdate,interval)

if __name__ == "__main__":
    main(sys.argv[1:])
