#!/usr/bin/env python
# Thomas Reerink
#
# This script converts a cmip6 json file into cmip6Plus json file.
#
# Run this script without arguments for examples how to call this script.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.


import sys
import os
import json
import os.path                                                # for checking file existence with: os.path.isfile
import numpy as np                                            # for the use of e.g. np.multiply

error_message   = ' \033[91m' + 'Error:'   + '\033[0m'        # Red    error   message
warning_message = ' \033[93m' + 'Warning:' + '\033[0m'        # Yellow warning message

# Main program
def main():

    # FUNCTION DEFINITIONS:

    def load_cmip6_cmip6plus_map_table():
       # In case the path contains the ~ character this will be expanded to the home dir:
       file_name_mapping_table = 'cmip6-cmip6plus-mapping-table.txt'
       cmip6_cmip6plus_map_table_file_name = os.path.expanduser(file_name_mapping_table)

       # Checking if the cmip6-cmip6plus-mapping file exist, if not try to create it:
       if os.path.isfile(cmip6_cmip6plus_map_table_file_name) == False:

        # Git checkout of the github wiki table of the mip-cmor-tables if not available
        # for converting the github wiki table to an ascii file with columns:
        #  https://github.com/PCMDI/mip-cmor-tables/wiki/Mapping-between-variables-in-CMIP6-and-CMIP6Plus
        wiki_table_file = 'mip-cmor-tables.wiki/Mapping-between-variables-in-CMIP6-and-CMIP6Plus.md'
        if not os.path.isfile(wiki_table_file):
         command_1 = "git clone git@github.com:PCMDI/mip-cmor-tables.wiki"
         print(' Cloning git repo mip-cmor-tables.wiki:')
         print('  ' + command_1 + '\n')
         os.system(command_1)

        print('\n Creating the {} neat columnwise ascii file by applying:'.format(file_name_mapping_table))
        command_2 = "sed -e '/| CMIP6 table |/,$!d' -e 's/|/ /g' " + wiki_table_file + " | column -t > " + file_name_mapping_table
        print('  ' + command_2 + '\n')
        os.system(command_2)

       if os.path.isfile(cmip6_cmip6plus_map_table_file_name) == False: print(error_message, ' The file ', cmip6_cmip6plus_map_table_file_name, '  does not exist.\n'); sys.exit()

       # Loading the cmip6-cmip6plus-mapping file
       cmip6_cmip6plus_map_table = np.loadtxt(cmip6_cmip6plus_map_table_file_name, skiprows=2, usecols=(0,1,2,3), dtype='str')

       # Clean:
       command_3 = "rm -rf mip-cmor-tables.wiki"
       command_4 = "rm -f " + file_name_mapping_table
       os.system(command_3)
      #os.system(command_4)

       return cmip6_cmip6plus_map_table


    def convert(cmip6_cmip6plus_map_table, cmip6_table, cmip6_variable):
       # Convert table - var combination from cmip6 to cmip6Plus
       verbose=False

       if verbose: print("\n Looking up the CMIP6plus equivalents of the CMIP6 table {} and CMIP6 variable {}\n".format(cmip6_table, cmip6_variable))


       cmip6plus_table    = None
       cmip6plus_variable = None
       for line in cmip6_cmip6plus_map_table:
        if line[0] == cmip6_table and line[1] == cmip6_variable:
         cmip6plus_table    = line[2]
         cmip6plus_variable = line[3]
         if verbose: print(line)
         exit

       if cmip6plus_table == None:
        status='nomatch'
       elif cmip6plus_table == cmip6_table and cmip6plus_variable == cmip6_variable:
        status='equal'
       else:
        status='converted'

       if verbose: print("{} {} {}".format(cmip6plus_table, cmip6plus_variable, status))

       return cmip6plus_table, cmip6plus_variable


    def convert_component_request(component, cmip6_data_request):
        if component in cmip6_data_request:
          # Empty initialization of the converted cmip6Plus request:
          converted_request = {}
          unidentified_request = {}
          # Initialization of the cmip6 component request:
          component_request = cmip6_data_request[component]
          # Loop the cmip6 request of a certain component:
          for cmip6_table in component_request:
             # Loop the cmip6 variables in a certain cmip6 table (for the given component):
             for i in range(0, len(component_request[cmip6_table])):
              cmip6_variable = component_request[cmip6_table][i]
              # cmip6 => cmip6Plus converion for table & variable:
              cmip6plus_table, cmip6plus_variable = convert(cmip6_cmip6plus_map_table, cmip6_table, cmip6_variable)

              if cmip6plus_variable == None:
               # Filter variables without an detected cmip6Plus equivalent:
               print(warning_message, ' Ignoring the cmip6  {:10} {:12} (i={:2}): combination because no cmip6Plus equivalent is found: {} {}'.format(cmip6_table, cmip6_variable, i, cmip6plus_table, cmip6plus_variable))

               # The cmip6 variables for which are no cmip6Plus ones are identified will be logged in a json file as well:
               if cmip6_table in unidentified_request:
                # Add a another cmip6Plus variable to an already created cmip6Plus table:
                unidentified_request[cmip6_table].append(cmip6_variable)
               else:
                # Add a first cmip6Plus variable for a first encounterd cmip6Plus table:
                unidentified_request.update({cmip6_table: [cmip6_variable]})

              else:
               if cmip6plus_table in converted_request:
                if cmip6plus_variable in converted_request[cmip6plus_table]:
                 print(warning_message, ' Skip dublicate {} {} due non bijective cmip6 - cmip6Plus mapping (cmip6 source: {} {})'.format(cmip6plus_table, cmip6plus_variable, cmip6_table, cmip6_variable))
                else:
                 # Add a another cmip6Plus variable to an already created cmip6Plus table:
                 converted_request[cmip6plus_table].append(cmip6plus_variable)
               else:
                # Add a first cmip6Plus variable for a first encounterd cmip6Plus table:
                converted_request.update({cmip6plus_table: [cmip6plus_variable]})

          # Adding the component level:
          converted_request = {
           component : converted_request
          }

          # Adding the component level:
          unidentified_request = {
           component : unidentified_request
          }

        return converted_request, unidentified_request


    # MAIN:

    if len(sys.argv) == 2:

       print('\n Running {:} with:\n  {:} {:}\n'.format(os.path.basename(sys.argv[0]), os.path.basename(sys.argv[0]), sys.argv[1]))

       # Reading and loading the cmip6 data request json file:
       input_json_file = sys.argv[1]                                # Reading the data request file name from the argument line
       if os.path.isfile(input_json_file) == False:                 # Checking if the data request file exists
        print(error_message, ' The data request file ', input_json_file, ' does not exist.\n')
        sys.exit()

       with open(input_json_file) as json_file:
        data_request = json.load(json_file)
       json_file.close()

       # Load (and create if necessary) the cmip6 cmip6plus map table:
       cmip6_cmip6plus_map_table = load_cmip6_cmip6plus_map_table()

       ece2cmor_components = ["ifs", "nemo", "lpjg", "tm5", "co2box"]

       # Check whether the input json file is a component json or a flat json file:
       if any(x in ece2cmor_components for x in data_request):
        print(' The cmip6 varlist input file is a component based file:')

       coposed_converted_request = {}
       coposed_unidentified_request = {}
       for component in ece2cmor_components:
        if component in data_request: print('  {:6} in request'.format(component))
        coposed_converted_request.update(convert_component_request(component, data_request)[0])
        coposed_unidentified_request.update(convert_component_request(component, data_request)[1])
       print()


       # Naming the cmip6Plus varlist by adding a label:
       converted_request_file = os.path.basename(input_json_file).replace('.json','-cmip6Plus.json')
       with open(converted_request_file, 'w') as outfile:
           json.dump(coposed_converted_request, outfile, sort_keys=True, indent=4)
       outfile.close()


       # Naming the cmip6Plus varlist by adding a label:
       unidientified_request_file = os.path.basename(input_json_file).replace('.json','-cmip6Plus-unidentified.json')
       with open(unidientified_request_file, 'w') as outfile:
           json.dump(coposed_unidentified_request, outfile, sort_keys=True, indent=4)
       outfile.close()


       print('\n which produced the file:')
       print('  ', converted_request_file)
       print('  ', unidientified_request_file)
       print()

    else:
       print()
       print('  This scripts requires one argument, a json file, e.g.:')
       print('  ./' + os.path.basename(sys.argv[0]), '../../../control-output-files/output-control-files-v458/cmip6/test-all-ece-mip-variables/cmip6-data-request-varlist-all-EC-EARTH-AOGCM.json')
       print('  ./' + os.path.basename(sys.argv[0]), '../../../control-output-files/output-control-files-v458/cmip6/test-all-ece-mip-variables/cmip6-data-request-varlist-all-EC-EARTH-CC.json')
       print('  ./' + os.path.basename(sys.argv[0]), '../../../control-output-files/output-control-files-v458/cmip6/test-all-ece-mip-variables/cmip6-data-request-varlist-all-EC-EARTH-AerChem.json')
       print('  ./' + os.path.basename(sys.argv[0]), 'optimesm/optimesm-request-EC-EARTH-ESM-1-varlist.json')
       print()

if __name__ == "__main__":
    main()
