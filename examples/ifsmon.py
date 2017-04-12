#!/usr/bin/env python

import os
import sys
import logging
import ece2cmor
import jsonloader
import optparse
import datetime
from dateutil.relativedelta import relativedelta

# This example script performs cmorization of one month of IFS data, starting at \
# januari 1st 1990. It requires an output directory, a metadata json-file \
# and an experiment name/prefix to determine the output data files and configure \
# cmor3 correctly. The processed variables are listed in the "variables" dictionary

logging.basicConfig(level=logging.DEBUG)

variables = {"Amon" : ["tas","uas","vas"]}
startdate = datetime.date(1990,1,1)
interval = relativedelta(months=1)
srcdir = os.path.dirname(os.path.abspath(ece2cmor.__file__))
datadir = os.path.join(srcdir,"test","test_data","ifsdata","3hr")

def main(args):

    parser = optparse.OptionParser()
    parser.add_option("-c","--conf",dest = "conf",help = "CMOR3 meta data json file path",metavar = "FILE",default = ece2cmor.conf_path_default)
    parser.add_option("-d","--dir" ,dest = "dir" ,help = "IFS output directory",default = datadir)
    parser.add_option("-e","--exp" ,dest = "exp" ,help = "Experiment name (prefix)",default = "ECE3")
    (opt,args) = parser.parse_args()

    # Initialize ece2cmor with metadata and experiment prefix:
    ece2cmor.initialize(opt.conf)

    # Load the variables as task targets:
    jsonloader.load_targets(variables)

    # Execute the cmorization:
    ece2cmor.perform_ifs_tasks(opt.dir,opt.exp,startdate,interval,outputfreq = 3,tempdir="./tmp",cleanup=False)

if __name__ == "__main__":
    main(sys.argv[1:])
