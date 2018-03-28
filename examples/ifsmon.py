#!/usr/bin/env python

import os
import sys
import logging
from ece2cmor import ece2cmorlib #weird had to change to ece2cmor, or it won't work within eclipse
from ece2cmor import taskloader
import optparse
import datetime
from dateutil.relativedelta import relativedelta

# This example script performs cmorization of one month of IFS data, starting at \
# januari 1st 1990. It requires an output directory, a metadata json-file \
# and an experiment name/prefix to determine the output data files and configure \
# cmor3 correctly. The processed variables are listed in the "variables" dictionary

logging.basicConfig(level=logging.DEBUG)

variables = {"Amon" : ["tas","uas","vas"]}
startdate = datetime.date(1870,1,1)
interval = relativedelta(months=1)
#srcdir = os.path.dirname(os.path.abspath(ece2cmorlib.__file__))
#datadir = os.path.join(srcdir,"test","test_data","ifsdata","3hr")
mydir = os.path.dirname(os.path.abspath(__file__))
#datadir = os.path.join(mydir,"..","test","test_data","ifsdata","3hr")
datadir = os.path.join("/Users/anthoni-p/EC-Earth/supermuc/runs/r1902-merge-new-components_impi/LNTS/run_i108_n0_micro_phase2_10years/output/ifs/001")

def main(args):

    parser = optparse.OptionParser()
    parser.add_option("-c","--conf",dest = "conf",help = "CMOR3 meta data json file path",metavar = "FILE",default = ece2cmorlib.conf_path_default)
    parser.add_option("-d","--dir" ,dest = "dir" ,help = "IFS output directory",default = datadir)
    parser.add_option("-e","--exp" ,dest = "exp" ,help = "Experiment name (prefix)",default = "ECE3")
    (opt,args) = parser.parse_args()

    # Initialize ece2cmorlib with metadata and experiment prefix:
    ece2cmorlib.initialize(opt.conf)

    # Load the variables as task targets:
    taskloader.load_targets(variables)

    # Execute the cmorization:
    ece2cmorlib.perform_ifs_tasks(opt.dir,opt.exp,startdate,interval,outputfreq = 3,tempdir="./tmp",cleanup=False)

if __name__ == "__main__":
    main(sys.argv[1:])
