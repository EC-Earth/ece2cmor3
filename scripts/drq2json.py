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

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    paths = reduce(lambda lst,elem:lst + glob.glob(elem),sys.argv[1:],[])
    files = list(set([os.path.abspath(p) for p in paths]))
    result = {}
    for f in files:
        if(not os.path.exists(f)):
            log.error("Skipping non-existing file %s" % f)
            continue
        if(not f.endswith(".csv")):
            log.error("Skipping non-csv file %s" % f)
            continue
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
