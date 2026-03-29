#!/usr/bin/env python
# Thomas Reerink
#
# This script combines and merges two json files which can have nested items. This script is aimed to combine
# two data request varlist json files in order to create a joined request from two separate requests.
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


def merge(source, destination, alphabetic_merge=True, verbose=True):
    for key, value in source.items():
        if isinstance(value, dict):
            if verbose:
                for dict_item in destination[key]:
                    if dict_item not in value:
                        print(' Adding table   : {}'.format(dict_item))
            # Get node or create one
            node = destination.setdefault(key, {})
            merge(value, node, alphabetic_merge, verbose)
        else:
            try:
             if isinstance(value, list):
                 for list_item in destination[key]:
                     if list_item not in value:
                         if verbose:
                             print(' Adding variable: {}'.format(list_item))
                         if alphabetic_merge:
                             # Insert a list item from the second json file (which is not in the first json file) at its alphabetic order. Ohter accidentally not alphabetic ordered items are also affected by this ordering.
                             value.append(list_item)
                             value.sort()
                         else:
                             # Insert a list item from the second json file (which is not in the first json file) at the start of the list: This allows a most clean comparison
                             value.insert(0, list_item)
            except:
             pass
            destination[key] = value
    return destination


# Main program
def main():

    if len(sys.argv) == 3 or len(sys.argv) == 4:

       input_json_file_1 = sys.argv[1]                             # The name of the 1st data request file from read the argument line
       input_json_file_2 = sys.argv[2]                             # The name of the 2nd data request file read from the argument line

       if len(sys.argv) == 4:
        output_json_file = sys.argv[3]                             # The name of the combined-merged output file if specified
       else:
        output_json_file = os.path.basename(input_json_file_1).replace('.json','-merged-with-' + os.path.basename(input_json_file_2))

       # Checking whether the data request files exists:
       if os.path.isfile(input_json_file_1) == False:
        print('{} The data request file {} does not exist.\n'.format(error_message, input_json_file_1))
        sys.exit()
       if os.path.isfile(input_json_file_2) == False:
        print('{} The data request file {} does not exist.\n'.format(error_message, input_json_file_2))
        sys.exit()

       with open(input_json_file_1) as json_file:
           data_request_1 = json.load(json_file)
       json_file.close()
       with open(input_json_file_2) as json_file:
           data_request_2 = json.load(json_file)
       json_file.close()


       print('\n Running {:} with:\n  {:} {:} {:}\n'.format(os.path.basename(sys.argv[0]), os.path.basename(sys.argv[0]), sys.argv[1], sys.argv[2]))

       # Recursive merge of netsed dictionaries including the merge of the elements of lists which are part of any dictionary item:
       merge(data_request_1, data_request_2, alphabetic_merge=False, verbose=True)

       data_request_merged = data_request_2

       with open(output_json_file, 'w') as outfile:
           json.dump(data_request_merged, outfile, sort_keys=True, indent=4)
           outfile.write('\n')
       outfile.close()

       command = r'sed -i "s/\s*$//g"' + ' ' + output_json_file
       os.system(command)

       print('\n which produced the merged file:')
       print('  ', output_json_file)
       print()

    else:
       file_1      = 'cmip7/archive/optimesm-v02/optimesm-request-EC-EARTH-ESM-1-varlist.json'

       file_2_core = 'cmip7/archive/cmip7-output-control-files-EC-Earth3-ESM-1-CMIP7-esm-hist-core-v02/esm-hist-core-EC-Earth3-ESM-1/component-request-cmip7-esm-hist-core-EC-Earth3-ESM-1.json'
       file_2_high = 'cmip7/archive/cmip7-output-control-files-EC-Earth3-ESM-1-CMIP7-esm-hist-high-v02/esm-hist-high-EC-Earth3-ESM-1/component-request-cmip7-esm-hist-high-EC-Earth3-ESM-1.json'

       file_3_core = 'combined-optimesm-cmip7-core-request-EC-EARTH-ESM-1-varlist.json'
       file_3_high = 'combined-optimesm-cmip7-high-request-EC-EARTH-ESM-1-varlist.json'
       print()
       print('  This scripts requires two or three arguments, two json data request files, e.g.:')
       print('  ./{} {} {} {}'.format(os.path.basename(sys.argv[0]), file_1, file_2_core, file_3_core))
       print('  ./{} {} {} {}'.format(os.path.basename(sys.argv[0]), file_1, file_2_high, file_3_high))
       print()

if __name__ == "__main__":
    main()
