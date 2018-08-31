#!/usr/bin/env python

import os
import sys
import logging
from ece2cmor import taskloader
from ece2cmor import ece2cmorlib
import optparse
import datetime
from dateutil.relativedelta import relativedelta

# This example script performs cmorization of one month of ocean data, starting at \
# januari 1st 1990. It requires an output directory, a configuration json-file \
# and an experiment name/prefix to determine the output data files and configure \
# cmor3 correctly. The processed variables are listed in the "variables" dictionary

logging.basicConfig(level=logging.DEBUG)

#Eyr        longitude latitude time1                 cSoil                Carbon Mass in Soil Pool 
#Eyr        longitude latitude time1                 cVeg                 Carbon Mass in Vegetation 
#Eyr        longitude latitude time1                 cLitter              Carbon Mass in Litter Pool 
#Eyr        longitude latitude landUse time1         cSoilLut             carbon  in soil pool on land use tiles 
#Eyr        longitude latitude landUse time1         cVegLut              carbon in vegetation on land use tiles 
#Eyr        longitude latitude landUse time1         cLitterLut           carbon  in above and belowground litter pools on land use tiles 

#variables = {"Eyr" : ["cSoil","cSoilLut","cVeg","cLitter"]}
variables = {"Eyr" : ["cSoil"]} #"cSoilLut",
#startdate = datetime.date(1990,1,1)
startdate = datetime.date(1870,1,1)
interval = relativedelta(months=1)
#srcdir = os.path.dirname(os.path.abspath(ece2cmorlib.__file__))
#datadir = os.path.join(srcdir,"test","test_data","nemodata")
mydir = os.path.dirname(os.path.abspath(__file__))
datadir = os.path.join(mydir,"..","test","test_data","lpjgdata")

def main(args):

    parser = optparse.OptionParser()
    parser.add_option("-c","--conf",dest = "conf",help = "CMOR3 meta data json file path",metavar = "FILE",default = ece2cmorlib.conf_path_default)
    parser.add_option("-d","--dir" ,dest = "dir" ,help = "LPJG output directory",default = datadir)
    parser.add_option("-e","--exp" ,dest = "exp" ,help = "Experiment name (prefix)",default = "exp")
    parser.add_option("--ncdir", dest = "ncdir", help = "working directory for netCDF files, relative to datadir or absolute", default = "nc")
    (opt,args) = parser.parse_args()

    # Initialize ece2cmorlib with metadata and experiment prefix:
    ece2cmorlib.initialize(opt.conf)

    # Load the variables as task targets:
    taskloader.load_targets(variables)

    # Execute the cmorization:
    ece2cmorlib.perform_lpjg_tasks(opt.dir,opt.ncdir,opt.exp,startdate,interval, datetime.datetime(1850,1,1,0,0,0))

if __name__ == "__main__":
    main(sys.argv[1:])
