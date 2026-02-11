#!/usr/bin/env python
# Thomas Reerink
#
# This script converts a component json file produced by genecec including the preferences
# into a flat json without the component structue (ifs, nemo, lpjg, tm5 & co2box) such that it can be
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
import json

error_message   = '\n \033[91m' + 'Error:'   + '\033[0m'        # Red    error   message
warning_message = '\n \033[93m' + 'Warning:' + '\033[0m'        # Yellow warning message



def merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination



# Main program
def main():

    if len(sys.argv) == 3:

       input_json_file_1 = sys.argv[1]                                                           # Reading the 1st data request file name from the argument line
       input_json_file_2 = sys.argv[2]                                                           # Reading the 2nd data request file name from the argument line
       if os.path.isfile(input_json_file_1) == False:                                            # Checking if the data request file exists
        print(error_message, ' The data request file ', input_json_file_1, ' does not exist.\n')
        sys.exit()
       if os.path.isfile(input_json_file_2) == False:                                            # Checking if the data request file exists
        print(error_message, ' The data request file ', input_json_file_2, ' does not exist.\n')
        sys.exit()

       with open(input_json_file_1) as json_file:
           data_request_1 = json.load(json_file)
       json_file.close()
       with open(input_json_file_2) as json_file:
           data_request_2 = json.load(json_file)
       json_file.close()

       output_flat_json_file = os.path.basename(input_json_file_1).replace('.json','-merged-with-' + os.path.basename(input_json_file_2))

       print('\n Running {:} with:\n  {:} {:} {:}\n'.format(os.path.basename(sys.argv[0]), os.path.basename(sys.argv[0]), sys.argv[1], sys.argv[2]))

       merge(data_request_1, data_request_2)

       data_request_merged = data_request_2

       with open(output_flat_json_file, 'w') as outfile:
           json.dump(data_request_merged, outfile, sort_keys=True, indent=4)
       outfile.close()

       command = 'sed -i "s/\s*$//g"' + ' ' + output_flat_json_file
       os.system(command)

       print(' which produced the merged file:')
       print('  ', output_flat_json_file)
       print()

    else:
       file_1 = 'bup/optimesm/optimesm-v02/optimesm-request-EC-EARTH-ESM-1-varlist.json'
       file_2 = 'cmip7/bup/output-control-files-ECE3-ESM-1-CMIP7-esm-hist-high/cmip7/esm-hist-high-EC-Earth3-ESM-1/component-request-cmip7-esm-hist-high-EC-Earth3-ESM-1.json'
       
       print()
       print('  This scripts requires two arguments, two json data request files, e.g.:')
       print('  ./{} {} {}'.format(os.path.basename(sys.argv[0]), file_1, file_2))
       print()

if __name__ == "__main__":
    main()
