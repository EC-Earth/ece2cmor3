#!/usr/bin/env python

import sys
import os
import glob
import logging
import json
import csv
import argparse

# Output file:
ofile = "varlist.json"

# Supported EC-Earth column names:
ecewords = ["ec-earth","ecearth"]

# Output name key:
onamekey = "out_name"

# Supported affirmative keywords:
truewords = ["true","x","yes","y","1"]

# Logger construction
log = logging.getLogger(__name__)

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Retrieve all csv files from input string
def get_drq(drqarg):
    if(not drqarg):
        logging.warning("No data request csv file list given: returning empty variable list")
        return []
    expr = drqarg
    if(os.path.isdir(drqarg)):
        expr = os.path.join(drqarg,"*.csv")
    paths = reduce(lambda lst,elem:lst + glob.glob(elem),expr,[])
    files = list(set([os.path.abspath(p) for p in paths]))
    result = []
    for f in files:
        if(not os.path.exists(f)):
            log.error("Skipping non-existing file %s" % f)
        elif(not f.endswith(".csv")):
            log.error("Skipping non-csv file %s" % f)
        else:
            result.append(f)
    return result

# Write varlist json from EC-Earth fields in drq csv files
def write_varlist(csvfiles):
    result = {}
    for f in csvfiles:
        try:
            csvf = open(f)
            table = os.path.basename(f)[:-4]
            reader = csv.DictReader(csvf)
            if(not onamekey in reader.fieldnames):
                log.error("Field name %s was not found in csv file %s: skipping file" % (onamekey,f))
                continue
            ecearthfields = [f for f in reader.fieldnames if f.lower() in ecewords]
            ecefield = None
            if(len(ecearthfields) == 0):
                log.warning("No valid ec-earth column could be found in %s: we will append all variables to the list" % f)
            if(len(ecearthfields) > 1):
                log.warning("Multiple ec-earth columns found in file %s: will proceed with the first one" % f)
            if(len(ecearthfields) != 0): ecefield = ecearthfields[0]
            for row in reader:
                var = row[onamekey]
                include = True if ecefield == None else (row[ecefield] in truewords)
                if(include):
                    if(table in result):
                        result[table].append(var)
                    else:
                        result[table] = [var]
        except ValueError as err:
            log.error("Error encountered parsing csv file %s: %s" % (f,err))
    with open(ofile,'w') as output:
        json.dump(result,output,indent = 4,separators = (',', ': '))
        log.info("File %s written" % ofile)

# Main program
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Produce variable list from input data request and CMIP tables")
    parser.add_argument("--drq",dest = "drq",help = "Input data request csv file list",default = None)
    args = parser.parse_args()
    csvfiles = get_drq(args.drq)
    write_varlist(csvfiles)
