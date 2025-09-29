#!/usr/bin/env python
# Thomas Reerink

# This script takes a request-overview file, as genereted by ECE3 genecec and converts its content into a XML file where per variable all metadata
# is stored in attributes. For the input request overview file, we take one which covers the most ECE3 variables: the test-all pextra CC one for instance.

# Relevance: This lists all CMOR variables which have been identified for CMIP6 for EC-Earth3. It gives the grib codes for th eECE3 IFS variables. It shows
# when a variable can be obtained from more than one model component (which involves the preferences).

# Run this script like:
#  ./convert-request-overview-to-xml.py request-overview-all-including-EC-EARTH-CC-preferences.txt request-overview-all-including-EC-EARTH-CC-preferences.xml

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
    parser = argparse.ArgumentParser(description=' Reading an ECE3 request-overview file and convert its content to an xml file.')
    parser.add_argument('request_file', help='input ascii request-overview file')
    parser.add_argument('xml_file'    , help='output xml file')

    return parser.parse_args()


def main():

   args = parse_args()

   # Echo the exact call of the script in the log messages:
   logging.info('Running:\n\n {:} {:} {:}\n'.format(sys.argv[0], sys.argv[1], sys.argv[2]))

  #request_overview_file_name = os.path.expanduser('~/cmorize/control-output-files/output-control-files-v460/cmip6-pextra/test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-CC-preferences.txt')
  #xml_file_name              = os.path.expanduser('request-overview-ec-earth3-cc-pextra-test-all.xml')
   request_overview_file_name = args.request_file
   xml_file_name              = args.xml_file

   # Split in path pf[0] & file pf[1]:
   pf = os.path.split(request_overview_file_name)
   print('\n Reading the file: {}\n'.format(pf[1]))

   # Create the basic main structure which will be populated with the elements of the various ping files later on:
   root_main     = ET.Element('ecearth_request_overview')
  #el_nemo       = ET.SubElement(root_main, 'ecearth_nemo')
  #el_oifs       = ET.SubElement(root_main, 'ecearth_oifs')
  #el_lpjg       = ET.SubElement(root_main, 'ecearth_lpjg')
  #el_tm5        = ET.SubElement(root_main, 'ecearth_tm5')
  #el_co2box     = ET.SubElement(root_main, 'ecearth_co2box')
  #el_var_nemo   = ET.SubElement(el_nemo  , 'variable')
  #el_var_oifs   = ET.SubElement(el_oifs  , 'variable')
  #el_var_lpjg   = ET.SubElement(el_lpjg  , 'variable')
  #el_var_tm5    = ET.SubElement(el_tm5   , 'variable')
  #el_var_co2box = ET.SubElement(el_co2box, 'variable')

   # The column indices match those written in the taskloader:
   # # In case the input data request is a json file, a reduced number of columns is printed:
   # ofile.write('{:11} {:20} {:45} {:115} {:20} {}{}'.format('table', 'variable', 'dimensions', 'long_name', 'unit', 'comment', '\n'))
   i0 =        0
   i1 = i0 +  12
   i2 = i1 +  21
   i3 = i2 +  45
   i4 = i3 + 115
   i5 = i4 +  20
   # One issue with the length of the long_name of fLitterFire: Carbon Mass Flux from Litter, CWD or any non-Living Pool into Atmosphere
   #  Therefore shortend the word Atmosphere to Atmos

   with open(request_overview_file_name) as request_overview_file:
    header_line = next(request_overview_file)
    for line in request_overview_file:
     # Reading the request-overview file data line by line (i.e. variable by variable):
     if line.strip():                       # skip empty lines
      cmip6_table    = line[i0:i1].strip()
      cmip6_variable = line[i1:i2].strip()
      dimensions     = line[i2:i3].strip()
      long_name      = line[i3:i4].strip()
      unit           = line[i4:i5].strip()
      comment        = line[i5:  ].strip()

      el_var = ET.Element('variable')

      # Add the metadata variable by variable to the XML data tree
      el_var.set('cmip6_table'   , cmip6_table   )
      el_var.set('cmip6_variable', cmip6_variable)
      el_var.set('dimensions'    , dimensions    )
      el_var.set('unit'          , unit          )

      if 'ifs  code name' in comment:
       model_component = 'ifs'
      elif 'tm5  code name' in comment:
       model_component = 'tm5'
      elif 'nemo code name' in comment:
       model_component = 'nemo'
      elif 'lpjg code name' in comment:
       model_component = 'lpjg'
      elif 'co2box code name' in comment:
       model_component = 'co2box'
      else:
       model_component = 'unknown'
       print('WARNING: Unknown model component.')

      # Abstract the grib code or the var name:
      varname_code = comment.split("code name = ", 1)[1].strip()
      varname_code = varname_code.split(" | ", 1)[0]
      varname_code = varname_code.split(", expression", 1)[0]
      el_var.set('varname_code', varname_code)

      el_var.set('model_component', model_component)
      if ' | ' in comment:
       if False: print('{:12} {:21} {:45} {:115} {:20} {}'.format(cmip6_table, cmip6_variable, dimensions, long_name, unit, comment))
       match = re.search(' \| (.+?) ', comment)
       if match:
        other_component = match.group(1).strip()
      else:
       other_component = 'None'
      el_var.set('other_component', other_component)


      el_var.set('long_name'      , long_name      )
      if 'expression' in comment:
       # Obtain the bare expression part:
       if ' | ' in comment:
        match = re.search('expression = (.+?) \| ', comment)
        if match:
         expression = match.group(1).strip()
         if False: print('Case 1: expression = {}'.format(expression))
       else:
        expression = comment.split("expression = ", 1)[1].strip()
        if False: print('Case 2: expression = {}'.format(expression))
       el_var.set('expression', expression)
      else:
       el_var.set('expression', 'None')
      el_var.set('comment'       , comment       )

      ET.indent(root_main, space='  ')
      root_main.append(el_var)

   ET.indent(root_main, space='  ')


   # Create the tree object for the fresh created root for our main structure:
   tree_main = ET.ElementTree(root_main)

   # Writing the combined result to a new xml file:
   tree_main.write(xml_file_name)


   if False:
    # Alphabetically ordering of attributes and tags, explicit tag closing (i.e with tag name), removing non-functional spaces
    xml_canonic_file_name = xml_file_name.replace('.xml', '-canonic.xml')
    with open(xml_canonic_file_name, mode='w', encoding='utf-8') as out_file:
     ET.canonicalize(from_file=xml_file_name, with_comments=True, out=out_file)


   # Load the xml file:
   tree_main = ET.parse(xml_file_name)
   root_main = tree_main.getroot()

   if False:
    for element in root_main.findall('.//variable[@model_component="ifs"]'):
     if '129' not in element.get('varname_code'):
      print(' Test XML file: {} {}'.format(element.tag, element.get('varname_code')))


if __name__ == '__main__':
    main()
