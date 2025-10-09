#!/usr/bin/env python
# Thomas Reerink

# This script takes a request-overview file, as genereted by ECE3 genecec and converts its content into a XML file where per variable all metadata
# is stored in attributes. For the input request overview file, we take one which covers the most ECE3 variables: the test-all pextra CC one for instance.

# Relevance: This lists all CMOR variables which have been identified for CMIP6 for EC-Earth3. It gives the grib codes for th eECE3 IFS variables. It shows
# when a variable can be obtained from more than one model component (which involves the preferences).

# Run this script like:
#  ./convert-grib-table-to-xml.py grib-table.xml

import argparse
import xml.etree.ElementTree as ET
import os                                                       # for checking file or directory existence with: os.path.isfile or os.path.isdir
import sys                                                      # for aborting: sys.exit
import numpy as np                                              # for the use of e.g. np.multiply
import logging
import re

error_message   = '\n \033[91m' + 'Error:'   + '\033[0m'        # Red    error   message
warning_message = '\n \033[93m' + 'Warning:' + '\033[0m'        # Yellow warning message

# Logging configuration
#logformat = "%(asctime)s %(levelname)s:%(name)s: %(message)s"
logformat  =             "%(levelname)s:%(name)s: %(message)s"
logdateformat = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.DEBUG, format=logformat, datefmt=logdateformat)

# Logger construction
log = logging.getLogger(__name__)

def print_next_step_message(step, comment):
    print('\n')
    print(' ##############################################################################################')
    print(' ###  Part {:<2}:  {:73}   ###'.format(step, comment))
    print(' ##############################################################################################\n')


def parse_args():
    '''
    Parse command-line arguments
    '''

    # Positional (mandatory) input arguments
    parser = argparse.ArgumentParser(description=' Reading grib table files from the ece2cmor3 resources and converts their content to an xml file.')
    parser.add_argument('xml_file'    , help='output xml file')

    return parser.parse_args()


def main():

   args = parse_args()

   # Echo the exact call of the script in the log messages:
   logging.info('Running:\n\n {:} {:}\n'.format(sys.argv[0], sys.argv[1]))

   grib_table_file_shortname   = os.path.expanduser('~/cmorize/ece2cmor3/ece2cmor3/resources/grib-table/grib1/localConcepts/ecmf/shortName.def')
   grib_table_file_description = os.path.expanduser('~/cmorize/ece2cmor3/ece2cmor3/resources/grib-table/grib1/localConcepts/ecmf/name.def')
   grib_table_file_unit        = os.path.expanduser('~/cmorize/ece2cmor3/ece2cmor3/resources/grib-table/grib1/localConcepts/ecmf/units.def')
   grib_table_file_id          = os.path.expanduser('~/cmorize/ece2cmor3/ece2cmor3/resources/grib-table/grib1/localConcepts/ecmf/paramId.def')
  #grib_table_file_cfname      = os.path.expanduser('~/cmorize/ece2cmor3/ece2cmor3/resources/grib-table/grib1/localConcepts/ecmf/cfName.def')
  #grib_table_file_cfvarname   = os.path.expanduser('~/cmorize/ece2cmor3/ece2cmor3/resources/grib-table/grib1/localConcepts/ecmf/cfVarName.def')

   grib_table_file_collection  = [grib_table_file_shortname  , \
                                  grib_table_file_description, \
                                  grib_table_file_unit       , \
                                  grib_table_file_id           \
                                 ]
  #grib_table_file_collection  = [grib_table_file_shortname]

   xml_filename                = args.xml_file

   # Take all info from the first file, for the following files check whether the same variable is in the same block and add
   # only the additional info from this file.
   first_file  = True
   description = []
   short_name  = []
   grib_table  = []
   grib_param  = []
   name        = []
   units       = []
   paramId     = []

   # Loop over the various field_def files:
   for grib_table_filename in grib_table_file_collection:
    if os.path.isfile(grib_table_filename) == False: print(' The file {} does not exist.'.format(grib_table_filename)); sys.exit(' stop')

    # Split in path pf[0] & file pf[1]:
    pf = os.path.split(grib_table_filename)
    print(' Read and convert the grib table file: {}\n'.format(pf[1]))

    count = 0
    with open(grib_table_filename, 'r') as infile:
        next(infile)                                # Skip the first header line
        lines = []
        for line in infile:
         if line.strip() != '':
          #if count < 10:
            lines.append(line)
            if len(lines) >= 5:
              # Read the variable info per five-line blocks:
              line_0 = lines[0].replace('#', '').strip()
              line_1 = lines[1].replace('\'', '').replace('= {', '').strip()
              line_2 = lines[2].replace('table2Version = ', '').replace(';', '').strip()
              line_3 = lines[3].replace('indicatorOfParameter = ', '').replace(';', '').strip()
             #line_4 : The body closing line is not used
              if first_file:
               description.append(line_0)
               short_name.append(line_1)
               grib_table.append(line_2)
               grib_param.append(line_3)
              else:
               if pf[1] == 'name.def':
                if grib_table[count] == line_2 and grib_param[count] == line_3:
                 name.append(line_1)
                else:
                 print(' WARNING for variable nr {} {}: files do not match'.format(count, short_name[count]))
               if pf[1] == 'units.def':
                if grib_table[count] == line_2 and grib_param[count] == line_3:
                 units.append(line_1)
                else:
                 print(' WARNING for variable nr {} {}: files do not match'.format(count, short_name[count]))
               if pf[1] == 'paramId.def':
                if grib_table[count] == line_2 and grib_param[count] == line_3:
                 paramId.append(line_1)
                else:
                 print(' WARNING for variable nr {} {}: files do not match'.format(count, short_name[count]))

             #print(' Var {:4}: {:100} {:20} {:6} {:6}'.format(count, line_0, line_1, line_2, line_3))
              lines = []
              count += 1
        if len(lines) > 0:
            print(' WARNING: A last unfinished variable block: {}'.format(lines))

    first_file = False


   # Check on sizes:
  #print('\n Size of lists: {} {} {} {} {} {} {}\n'.format(len(description), len(short_name), len(grib_table), len(grib_param), len(name), len(units), len(paramId)))

   # Direct XML writing in neat column format:
   # Write an XML file with all content in attributes for each variable:
   with open(xml_filename, 'w') as xml_file:
    xml_file.write('<grib_table_ifs_ece2cmor3>\n')

    for i in range(len(short_name)):
     #print(' Var {:4}: {:100} {:20} {:6} {:6} {:8} {:24}'   .format(i, name[i], short_name[i], grib_table[i], grib_param[i], paramId[i], units[i]))
      if name[i] != description[i]:
       print(' Var {:4}: {:100} {:20} {:6} {:6} {:8} {:24} {}'.format(i, name[i], short_name[i], grib_table[i], grib_param[i], paramId[i], units[i], description[i]))

      name[i] = name[i].replace('&','&amp;')
      name[i] = name[i].replace('<','&lt;')
      name[i] = name[i].replace('>','&gt;')

      xml_file.write('  <variable  ifs_code_name={:20} grib_table={:6} grib_code={:6} paramID={:8} units={:29} description={:100} >   </variable>\n' \
                     .format('"' +short_name[i]                   + '"', \
                             '"' +grib_table[i]                   + '"', \
                             '"' +grib_param[i]                   + '"', \
                             '"' +paramId   [i]                   + '"', \
                             '"' +units     [i].replace('**', '') + '"', \
                             '"' +name      [i]                   + '"'))

    xml_file.write('</grib_table_ifs_ece2cmor3>\n')


   if False:
    # Alphabetically ordering of attributes and tags, explicit tag closing (i.e with tag name), removing non-functional spaces
    xml_canonic_file_name = xml_filename.replace('.xml', '-canonic.xml')
    with open(xml_canonic_file_name, mode='w', encoding='utf-8') as out_file:
     ET.canonicalize(from_file=xml_filename, with_comments=True, out=out_file)


   # Test: Load the xml file:
   tree_main = ET.parse(xml_filename)
   root_main = tree_main.getroot()

   number_of_variables = 0
   for element in root_main.findall('.//variable'):
    number_of_variables += 1
   print('\n The number of identified CMIP6 variables for EC-Earth3 is: {}.\n'.format(number_of_variables))


if __name__ == '__main__':
    main()
