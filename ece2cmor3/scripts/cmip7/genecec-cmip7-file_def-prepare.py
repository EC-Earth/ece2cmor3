#!/usr/bin/env python3
"""

 Creating the various file_def files for XIOS for ECE4 based on the CMIP7 data request.

 Call example:
  ./genecec-cmip7-file_def-files.py &> genecec-cmip7-file_def-files.log

"""
import sys
import os
import subprocess
import re
import xml.etree.ElementTree as ET
from os.path import expanduser

from list_dict_nemo import nemo_dict
from list_dict_oifs import oifs_dict

error_message   = '\n \033[91m' + 'Error:'   + '\033[0m'        # Red    error   message
warning_message = '\n \033[93m' + 'Warning:' + '\033[0m'        # Yellow warning message


def print_next_step_message(step, comment):
    print('\n')
    print(' ##############################################################################################')
    print(' ###  Part {:<2}:  {:73}   ###'.format(step, comment))
    print(' ##############################################################################################\n')


def print_message_list(message_list):
    for message in message_list:
     print(message)
    print()


if len(sys.argv) == 2:

  if __name__ == "__main__": config = {}                       # python config syntax

  config_filename = sys.argv[1]                                # Reading the config file name from the argument line
  if os.path.isfile(config_filename) == False:                 # Checking if the config file exists
   print(error_message, ' The config file ', config_filename, '  does not exist.\n')
   sys.exit()
  exec(open(config_filename).read(), config)                   # Reading the config file

  # Echo the exact call of the script in the log messages:
  print('Running:\n\n {:} {:}\n'.format(sys.argv[0], sys.argv[1]))

  # The input files:
  dr_filename             = os.path.expanduser(config['dr_filename'            ]) # dr_filename               = 'xml-files/experiment-requests/cmip7-request-v1.2.2.5-esm-hist-priority-ordered.xml'
  identified_filename     = os.path.expanduser(config['identified_filename'    ]) # identified_filename       = 'xml-files/genecec-cmip7/identify-ece4-cmip7/cmip7-request-v1.2.2.5-all-full-identified-freq-mc-prio.xml'
  ece_field_def_filename  = os.path.expanduser(config['ece_field_def_filename' ]) # ece_field_def_filename    = 'xml-files/genecec-cmip7/ec-earth-definition/ec-earth-definition-inherited-neat-formatted.xml'

  # The outnput files:
  ece4_file_def_file      = os.path.expanduser(config['ece4_file_def_file'     ]) # ece4_file_def_file        = 'xml-files/genecec-cmip7/ec-earth-file_def-files/ece4_file_def.xml'
  ece4_file_def_file_nemo = os.path.expanduser(config['ece4_file_def_file_nemo']) # ece4_file_def_file_nemo   = 'xml-files/genecec-cmip7/ec-earth-file_def-files/ece4_nemo_file_def.xml'
  ece4_file_def_file_oifs = os.path.expanduser(config['ece4_file_def_file_oifs']) # ece4_file_def_file_oifs   = 'xml-files/genecec-cmip7/ec-earth-file_def-files/ece4_oifs_file_def.xml'


  print_next_step_message(1, 'Read the experiment CMIP7 data request')

  if os.path.isfile(dr_filename) == False:
   print(' The file {} does not exist.'.format(dr_filename))
   sys.exit(' Stop in: {}'.format(sys.argv[0]))

  # Split in path pf[0] & file pf[1]:
  pf = os.path.split(dr_filename)
  print('\n\n Reading the data request file: {}\n'.format(pf[1]))

  # Load the xml file:
  tree_dr = ET.parse(dr_filename)
  root_dr = tree_dr.getroot()

  selected_attribute = 'cmip7_compound_name'
  xpath_path         = ".//variable"                           # Looping over all      variable    elements in any                                layer
  xpath_expression   = xpath_path

  i = 0
  for element in root_dr.findall(xpath_expression):
   i += 1
  #print('{:4} {} {:25} {}'.format(i, element.tag, element.get(selected_attribute), element.attrib))
   print('{:4} {}'.format(i, element.get(selected_attribute)))


  print_next_step_message(2, 'Read the CMIP7 - ECE4 identified files')

  if os.path.isfile(identified_filename) == False:
   print(' The file {} does not exist.'.format(identified_filename))
   sys.exit(' Stop in: {}'.format(sys.argv[0]))

  # Split in path pf[0] & file pf[1]:
  pf = os.path.split(identified_filename)
  print('\n\n Reading the data request file: {}\n'.format(pf[1]))

  # Load the xml file:
  tree_identified = ET.parse(identified_filename)
  root_identified = tree_identified.getroot()

  selected_attribute = 'cmip7_compound_name'
  xpath_path         = ".//variable"                           # Looping over all variable elements in any layer
  xpath_expression   = xpath_path

  i = 0
  for element in root_identified.findall(xpath_expression):
   i += 1
   print('{:5} {}'.format(i, element.get(selected_attribute)))



  print_next_step_message(3, 'Read the ECE4 inherited neat formatted field_def file')

  if os.path.isfile(ece_field_def_filename) == False:
   print(' The file {} does not exist.'.format(ece_field_def_filename))
   sys.exit(' Stop in: {}'.format(sys.argv[0]))

  # Split in path pf[0] & file pf[1]:
  pf = os.path.split(ece_field_def_filename)
  print('\n\n Reading the data request file: {}\n'.format(pf[1]))

  # Load the xml file:
  tree_ece_field_def = ET.parse(ece_field_def_filename)
  root_ece_field_def = tree_ece_field_def.getroot()

  selected_attribute = 'id'
  xpath_path         = ".//field"
  xpath_expression   = xpath_path

  i = 0
  for element in root_ece_field_def.findall(xpath_expression):
   i += 1
   print('{:5} {}'.format(i, element.get(selected_attribute)))



  print_next_step_message(4, 'Iterate over the experiment DR while iterating for each variable through the identified file')

  message_list_identified_var   = []
  message_list_unidentified_var = []
  message_list_match_fd         = [] # fd refers to field_def (for looking up the grid_def, operation, freq_op, freq_offset))
  message_list_no_match_fd      = []

  i          = 0
  j          = 0
  k_match    = 0
  k_no_match = 0
  # Set first the xpath search for iterating through the DR file:
  selected_attribute_dr = 'cmip7_compound_name'
  xpath_path_dr         = ".//variable"                           # Looping over all variable elements in any layer
  xpath_expression_dr   = xpath_path_dr
  for element_dr in root_dr.findall(xpath_expression_dr):
   # Set first the xpath search for iterating through the identified file:
   selected_attribute_dr_value = element_dr.get(selected_attribute_dr)
   xpath_path_identified = ".//variable"
   xpath_expression_identified = xpath_path_identified + '[@' + selected_attribute_dr + '="' + selected_attribute_dr_value + '"]'
   match = 0 # For bookkeeping the identification matches
   for element_identified in root_identified.findall(xpath_expression_identified):
    match += 1
    j += 1
    message = '{:4}     identified for ECE4: {}'.format(j, element_identified.get(selected_attribute_dr))
    message_list_identified_var.append(message)

    # Determine the code_name:
    if element_identified.get('ifs_shortname') == "NotAnIFSvar":
     code_name = element_identified.get('varname_code')
    elif element_identified.get('ifs_shortname') == "None":           # Usually the 129 case
     code_name = element_identified.get('varname_code')
    else:
     code_name = element_identified.get('ifs_shortname')

    # Set first the xpath search for iterating through the field_def file:
    xpath_path_fd         = ".//field"
    xpath_expression_fd   = xpath_path_fd + '[@' + 'id' + '="' + code_name + '"]'
    match_fd              = 0 # For bookkeeping the identification matches
    for element_fd in root_ece_field_def.findall(xpath_expression_fd):
     k_match += 1
     match_fd += 1

     grid_ref_info    = ''
     operation_info   = ''
     freq_op_info     = ''
     freq_offset_info = ''
     if element_fd.get('grid_ref'   ): grid_ref_info    = ' grid_ref = {}'   .format(element_fd.get('grid_ref'))
     if element_fd.get('operation'  ): operation_info   = ' operation = {}'  .format(element_fd.get('operation'))
     if element_fd.get('freq_op'    ): freq_op_info     = ' freq_op = {}'    .format(element_fd.get('freq_op'))
     if element_fd.get('freq_offset'): freq_offset_info = ' freq_offset = {}'.format(element_fd.get('freq_offset'))
     attribute_info = ' {:23}{}{}{}'.format(grid_ref_info, operation_info, freq_op_info, freq_offset_info)

     message = '{:4} {:40} {:15} {}'.format(k_match, selected_attribute_dr_value, element_fd.get('id'), attribute_info)
     message_list_match_fd.append(message)
    else:  # The for-else:
     if match_fd == 0:
      k_no_match += 1
      message = '{:4} No matching field in the ECE4 field_def file: {}'.format(k_no_match, selected_attribute_dr_value)
      message_list_no_match_fd.append(message)

   else:   # The for-else:
    if match == 0:
     i += 1
     message = '{:4} Not identified for ECE4: {}'.format(i, element_dr.get(selected_attribute_dr))
     message_list_unidentified_var.append(message)

  print_message_list(message_list_identified_var)
  print_message_list(message_list_match_fd)
  print_message_list(message_list_no_match_fd)
  print()
  print_message_list(message_list_unidentified_var)
 #print_message_list(message_list_lpjg_ins_vars)

  print_next_step_message(10, 'FINISHING')
  print(' The script {} has finished\n'.format(sys.argv[0]))

else:
   print()
   print(' This script needs one argument: a config file name. E.g.:')
   print('  ', sys.argv[0], 'config-genecec-cmip7-file_def')
   print()
