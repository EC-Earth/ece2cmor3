#!/usr/bin/env python3
# Thomas Reerink
#
# This script converts a component json file produced by genecec including the preferences
# into a flat json without the component structue (ifs, nemo, lpjg & tm5) such that it can be
# read with: checkvars -v --asciionly --drq flat-json-file.json --output request-overview
#
# Note that when a flat json file is given (instead of a component json file) the produced json
# file will be just equal to the input flat json file.
#
# Run this script without arguments for examples how to call this script.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.

import sys
import os
import os.path                                                  # for checking file existence with: os.path.isfile
import json

error_message   = '\n \033[91m' + 'Error:'   + '\033[0m'        # Red    error   message
warning_message = '\n \033[93m' + 'Warning:' + '\033[0m'        # Yellow warning message

if len(sys.argv) == 2:

   input_json_file = sys.argv[1]                                # Reading the data request file name from the argument line
   if os.path.isfile(input_json_file) == False:                 # Checking if the data request file exists
    print(error_message, ' The data request file ', input_json_file, ' does not exist.\n')
    sys.exit()

   with open(input_json_file) as json_file:
       data_request = json.load(json_file)
   json_file.close()

   data_request_1 = data_request
   ifs_request  = data_request_1["ifs"]
   nemo_request = data_request_1["nemo"]
   lpjg_request = data_request_1["lpjg"]
   tm5_request  = data_request_1["tm5"]


   # Determine whether a same table is present in the nemo dictionary as in the ifs dictionary:
   for x in nemo_request:
    if x in ifs_request:
     for i in range(0, len(nemo_request[x])):
      ifs_request[x].append(nemo_request[x][i])
    else:
     ifs_request.update({x: nemo_request[x]})

   # Determine whether a same table is present in the lpjg dictionary as in the ifs dictionary:
   for x in lpjg_request:
    if x in ifs_request:
     for i in range(0, len(lpjg_request[x])):
      ifs_request[x].append(lpjg_request[x][i])
    else:
     ifs_request.update({x: lpjg_request[x]})

   # Determine whether a same table is present in the tm5 dictionary as in the ifs dictionary:
   for x in tm5_request:
    if x in ifs_request:
     for i in range(0, len(tm5_request[x])):
      ifs_request[x].append(tm5_request[x][i])
    else:
     ifs_request.update({x: tm5_request[x]})

   output_json_file = os.path.basename(input_json_file).replace('.json','-flat.json')
   with open(output_json_file, 'w') as outfile:
       json.dump(ifs_request, outfile, sort_keys=True, indent=4)
   outfile.close()


   print()
   print(' The script:')
   print(' ', sys.argv[0], sys.argv[1])
   print(' produced the file:')
   print('  ', output_json_file)
   print()

else:
   print()
   print('  This scripts requires one argument, a json file, e.g.:')
   print('  ', sys.argv[0], 'control-output-files/output-control-files-v196/cmip6/CMIP/EC-EARTH-AOGCM/cmip6-experiment-CMIP-historical/cmip6-data-request-varlist-CMIP-historical-EC-EARTH-AOGCM.json')
   print('  ', sys.argv[0], '../resources/miscellaneous-data-requests/lamaclima/lamaclima-data-request-varlist-EC-EARTH-Veg.json')
   print('  ', sys.argv[0], 'control-output-files/output-control-files-v196/cmip6/AerChemMIP/cmip6-experiment-AerChemMIP-hist-1950HC/cmip6-data-request-varlist-AerChemMIP-hist-1950HC-EC-EARTH-AerChem.json')
   print()


# Validation:
#
# non_flat_json=control-output-files/output-control-files-v196/cmip6/CMIP/EC-EARTH-AOGCM/cmip6-experiment-CMIP-historical/cmip6-data-request-varlist-CMIP-historical-EC-EARTH-AOGCM.json
# flat_json=cmip6-data-request-varlist-CMIP-historical-EC-EARTH-AOGCM-flat.json
# non_flat_json=../resources/miscellaneous-data-requests/lamaclima/lamaclima-data-request-varlist-EC-EARTH-Veg.json
# flat_json=lamaclima-data-request-varlist-EC-EARTH-Veg-flat.json
# non_flat_json=control-output-files/output-control-files-v196/cmip6/AerChemMIP/cmip6-experiment-AerChemMIP-hist-1950HC/cmip6-data-request-varlist-AerChemMIP-hist-1950HC-EC-EARTH-AerChem.json
# flat_json=cmip6-data-request-varlist-AerChemMIP-hist-1950HC-EC-EARTH-AerChem-flat.json
# 
# more ${flat_json}  | grep -v -e '}' -e '{' -e ']' -e '\[' | sort > sorted-flat.txt
# more ${non_flat_json} | grep -v -e '}' -e '{' -e ']' -e '\[' | sort > sorted-non-flat.txt
# wc sorted-non-flat.txt; wc sorted-flat.txt
# diff -b sorted-non-flat.txt sorted-flat.txt
# 
# rm -f cmip6-data-request-varlist-CMIP-historical-EC-EARTH-AOGCM-flat.json lamaclima-data-request-varlist-EC-EARTH-Veg-flat.json cmip6-data-request-varlist-AerChemMIP-hist-1950HC-EC-EARTH-AerChem-flat.json sorted-flat.txt sorted-non-flat.txt