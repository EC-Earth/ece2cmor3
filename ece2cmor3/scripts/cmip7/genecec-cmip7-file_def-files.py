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


def print_message_list(message_list):
    for message in message_list:
     print(message)
    print()

def write_xml_file_opening(xml_file_filename):
    xml_file = open(xml_file_filename, 'w')
    xml_file.write('<?xml version="1.0"?>\n\n')
    xml_file.write('<file_definition min_digits="4" name="@expname@_@freq@_@startdate@_@enddate@" sync_freq="1d" type="one_file">\n')
    return xml_file

def write_xml_file_group_opening(xml_file, file_group_id):
    xml_file.write('  <file_group id="' + file_group_id + '" default_value="1e20" chunking_blocksize_target="3.0">\n')

def write_xml_file_group_closing(xml_file):
    xml_file.write('  </file_group>\n')
    return

def write_xml_file_closing(xml_file):
    xml_file.write('</file_definition>\n')
    xml_file.close()
    return

def write_xml_file_group(file_def_file, id_file_group, model_dict, verbose):
    write_xml_file_group_opening(file_def_file, id_file_group)
    for ii in model_dict:
     for jj in model_dict[ii]:
      for kk in model_dict[ii][jj]:
       if model_dict[ii][jj][kk] != []:
        # Write the non empty lists:
        if verbose: print(' {:12} {:8} {:8} {}'.format(ii, jj, kk, len(model_dict[ii][jj][kk])))
        write_file_group_body_to_xml_file(file_def_file, ii, jj, kk, model_dict[ii][jj][kk])
    write_xml_file_group_closing(file_def_file)

def map_freq(frequency):
    # Those frequency strings which differ in XIOS from CMIP7 are mapped:
    if   frequency == 'fx':
         frequency =  'once'
    elif frequency == 'day':
         frequency =  '1d'
    elif frequency == 'mon':
         frequency =  '1mo'
    elif frequency == 'yr':
         frequency =  '1yr'
    return frequency

def write_file_group_body_to_xml_file(xml_file, grid, output_freq, region, list_with_xml_lines_of_group):
    # Add a group only if it has some content:
    if len(list_with_xml_lines_of_group) != 0:
    #if region == 's30': region = '30S-90S'
     if region == 's30': region = '30Sto90S'
     group_id  = grid.strip() + '_' + output_freq.strip() + '_' + region.strip()
     xios_freq = map_freq(output_freq.strip())
    #xml_file.write('    <file id="group_{}" name_suffix="_{}" output_freq="{}">\n'.format(group_id, group_id, xios_freq))
     xml_file.write('    <file id="group_{}" name_suffix="_{}" output_freq="{}" grid_ref="grid_{}" region="{}">\n'.format(group_id, group_id, xios_freq, grid, region.replace('to', '-')))
     for xml_line in list_with_xml_lines_of_group:
      xml_file.write('{}\n'.format(xml_line))
     xml_file.write('    </file>\n')
    return

def determine_operation_value(element):
  if   element.get('branding_label')[:5] == 'tavg-':
   operation = 'average'
  elif element.get('branding_label')[:4] == 'tpt-':
   operation = 'instant'
  elif element.get('branding_label')[:5] == 'tmax-':
   operation = 'maximum'
  elif element.get('branding_label')[:5] == 'tmin-':
   operation = 'minimum'
  elif element.get('branding_label')[:3] == 'ti-':
   operation = 'once'
 #elif element.get('branding_label')[:3] == 'tmaxavg-':
 # operation = ''                                            # Achieve: Daily Maximum
 #elif element.get('branding_label')[:3] == 'tminavg-':
 # operation = ''                                            # Achieve: Daily Minimum
 #elif element.get('branding_label')[:3] == 'tclm-':
 # operation = ''                                            # Achieve: temporal_shape="climatology", i.e. a 30 year mean of monly means [Standard climatology (time2 dimensions)]
 #elif element.get('branding_label')[:3] == 'tclmdc-':
 # operation = ''                                            # Achieve: temporal_shape="diurnal-cycle", i.e. a 30 year mean of hourly means [diurnal mean climatology (a daily cycle pattern averaged over a reference climatological period), using the time3 dimension]
  else:
   operation = 'unknown'
  return operation

def generate_xml_line_for_variable(cmip7_element, field_id, verbosity):
    if cmip7_element.get('expression'):
     if cmip7_element.get('expression') != 'None':
      expression = cmip7_element.get('expression').replace('&','&amp;').replace('<','&lt;')
     else:
      expression = ''
    else:
     expression = ''

    # Taking the grid_ref, freq_op, freq_offset and operation from the ECE4 inherited field_def file if available:
    grid_ref    = ''
    operation   = ''
    freq_op     = ''
    freq_offset = ''
    # Set first the xpath search for iterating through the field_def file:
    xpath_expression_fd = './/field[@id="' + field_id + '"]'
    match_fd = 0
    for element_fd in root_ece_field_def.findall(xpath_expression_fd):
     if element_fd.get('grid_ref'   ): grid_ref    = element_fd.get('grid_ref')
     if element_fd.get('freq_op'    ): freq_op     = element_fd.get('freq_op')
     if element_fd.get('freq_offset'): freq_offset = element_fd.get('freq_offset')
     if element_fd.get('operation'  ): operation   = element_fd.get('operation')
     match_fd += 1
     if verbosity >= 2: print(' A  fd match for {:25} with i = {}'.format(field_id, match_fd))
    if match_fd == 0:
     if verbosity >= 1: print(' No fd match for {:25} with i = {}'.format(field_id, match_fd))
     # Initialisation required because this variable is an returned function argument.
     element_fd = None

    operation_based_on_branding = determine_operation_value(cmip7_element)
    if operation != operation_based_on_branding:
     message = ' Warning: The inherited operation differs from the branding one: {:8} -vs- {:8} for {:23} for {}'.format(operation, operation_based_on_branding, field_id, cmip7_element.get('cmip7_compound_name'))
     message_list_of_operation_comparsion.append(message)
     # Give preference to the operation value from the CMIP7 branding:
     operation = operation_based_on_branding

    xml_line = ('      <field  enabled="True" '\
                             ' field_ref={:25}' \
                             ' priority={:10}' \
                             ' grid_ref={:20}' \
                             ' units={:20}' \
                             ' operation={:10}' \
                             ' freq_op={:20}' \
                             ' freq_offset={:20}' \
                             ' name={:55}' \
                             ' long_name={:132}' \
                             ' standard_name={:160}' \
                             ' modeling_realm={:33}' \
                             ' region={:12}' \
                             ' frequency={:12}' \
                             ' dimensions={:45}' \
                             ' branding_label={:25}' \
                             ' cmip6_table={:14}' \
                             ' physical_parameter_name={:28}' \
                             ' ifs_shortname={:13}' \
                             ' varname_code={:25}' \
                ' > {:81}</field>'.format( \
                '"' +                    field_id                  + '"', \
                '"' + cmip7_element.get('priority'               ) + '"', \
                '"' + grid_ref                                     + '"', \
                '"' + cmip7_element.get('units'                  ) + '"', \
                '"' + operation                                    + '"', \
                '"' + freq_op                                      + '"', \
                '"' + freq_offset                                  + '"', \
                '"' + cmip7_element.get('cmip7_compound_name'    ) + '"', \
                '"' + cmip7_element.get('long_name'              ) + '"', \
                '"' + cmip7_element.get('standard_name'          ) + '"', \
                '"' + cmip7_element.get('modeling_realm'         ) + '"', \
                '"' + cmip7_element.get('region'                 ) + '"', \
                '"' + cmip7_element.get('frequency'              ) + '"', \
                '"' + cmip7_element.get('dimensions'             ) + '"', \
                '"' + cmip7_element.get('branding_label'         ) + '"', \
                '"' + cmip7_element.get('cmip6_table'            ) + '"', \
                '"' + cmip7_element.get('physical_parameter_name') + '"', \
                '"' + cmip7_element.get('ifs_shortname'          ) + '"', \
                '"' + cmip7_element.get('varname_code'           ) + '"', \
                ' ' +                    expression                + ' ') \
               )
    return element_fd, xml_line

# Note: there are cases left which are not covered due to deviating dimensional shape and
# a lacking grid_ref definition (see the warning list). In case of a not earlier catched
# region, another warning will be given.
def add_xml_line_to_selected_group(cmip7_element, field_id, list_cluster, message_list):
    model_component = cmip7_element.get('model_component')
    output_freq     = cmip7_element.get('frequency')
    region          = cmip7_element.get('region')
    if region == '30S-90S': region = 's30'
    # Generate the XML file line for one variable, also make the inherited field_def info of
    # this variable available at this level in this function:
    element_fd, xml_line = generate_xml_line_for_variable(cmip7_element, field_id, verbosity_level)
    # Note that this method does not create a new XML tree, but with the group knowledge the
    # XML file is directly written
    if   element_fd == None:
     if   cmip7_element.get('dimensions') == 'longitude latitude time':
      if model_component == 'nemo':
       grid = 'T_2D'
      elif model_component == 'ifs':
       grid = 'reduced_sfc'
     elif cmip7_element.get('dimensions') == 'time':
      grid = 'time'
     else:
      grid = 'other' # To bypass the 'dec' case which is not implemented
      message_list['grid'].append(' Warning: case {:3} not covered in {:4} part with element_fd = None with {:48} {:6} {:12} {}'.format( \
               output_freq                                           , \
               model_component.upper()                               , \
               'dimensions="' + cmip7_element.get('dimensions') + '"', \
               cmip7_element.get('priority')                         , \
               cmip7_element.get('status')                           , \
               cmip7_element.get('cmip7_compound_name')))
    else:
     if element_fd.get('grid_ref'):
      grid = element_fd.get('grid_ref').replace('grid_', '')
     else:
      grid = 'other'
    # To bypass the 'dec' case which is not implemented
    if output_freq in ['fx', '1hr', '3hr', '6hr', 'day', 'mon', 'yr']:
     if region in ['glb', 'nh', 'sh', 's30', 'grl']:
      list_cluster[grid][output_freq][region].append(xml_line)
     else:
      message_list['region'].append(' Warning: unknown region: {:20} {:7} {}'.format(grid, output_freq, region))
    else:
     message_list['freq'].append(' Warning: unknown output_freq: {:20} {:7} {}'.format(grid, output_freq, region))
    return

def write_lpjg_ins_file(lpjg_ins_file_filename, list_of_lpjg_ins_lines):
    lpjg_ins_file_file = open(lpjg_ins_file_filename, 'w')
    for lpjg_ins_line in list_of_lpjg_ins_lines:
     lpjg_ins_file_file.write('{}\n'.format(lpjg_ins_line))
    return


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

  # The outnput files (not used yet):
  ece4_file_def_file      = os.path.expanduser(config['ece4_file_def_file'     ]) # ece4_file_def_file        = 'xml-files/genecec-cmip7/ec-earth-file_def-files/ece4_file_def.xml'
  ece4_file_def_file_nemo = os.path.expanduser(config['ece4_file_def_file_nemo']) # ece4_file_def_file_nemo   = 'xml-files/genecec-cmip7/ec-earth-file_def-files/ece4_nemo_file_def.xml'
  ece4_file_def_file_oifs = os.path.expanduser(config['ece4_file_def_file_oifs']) # ece4_file_def_file_oifs   = 'xml-files/genecec-cmip7/ec-earth-file_def-files/ece4_oifs_file_def.xml'

  # Options:
  verbosity_level         =                    config['verbosity_level'        ]  # verbosity_level           = 0          # Default 0     options: 0-3
  show_warnings           =                    config['show_warnings'          ]  # show_warnings             = True       # Default True  options: True, False


  if os.path.isfile(dr_filename) == False:
   print(' The file {} does not exist.'.format(dr_filename))
   sys.exit(' Stop in: {}'.format(sys.argv[0]))

  # Split in path pf[0] & file pf[1]:
  pf = os.path.split(dr_filename)
  print(' Reading the data request file: {}\n'.format(pf[1]))

  # Load the xml file:
  tree_dr = ET.parse(dr_filename)
  root_dr = tree_dr.getroot()

  if os.path.isfile(identified_filename) == False:
   print(' The file {} does not exist.'.format(identified_filename))
   sys.exit(' Stop in: {}'.format(sys.argv[0]))

  # Split in path pf[0] & file pf[1]:
  pf = os.path.split(identified_filename)
  print(' Reading the data request file: {}\n'.format(pf[1]))

  # Load the xml file:
  tree_identified = ET.parse(identified_filename)
  root_identified = tree_identified.getroot()

  if os.path.isfile(ece_field_def_filename) == False:
   print(' The file {} does not exist.'.format(ece_field_def_filename))
   sys.exit(' Stop in: {}'.format(sys.argv[0]))

  # Split in path pf[0] & file pf[1]:
  pf = os.path.split(ece_field_def_filename)
  print(' Reading the data request file: {}\n'.format(pf[1]))

  # Load the xml file:
  tree_ece_field_def = ET.parse(ece_field_def_filename)
  root_ece_field_def = tree_ece_field_def.getroot()

  # Writing the combined result to a new xml file:
  output_dir_name = 'xml-files/genecec-cmip7/ec-earth-file_def-files/'
  subprocess.run(["mkdir", "-p", output_dir_name])

  ecearth_file_def_filename      = output_dir_name + 'ece4_file_def.xml'
  ecearth_nemo_file_def_filename = output_dir_name + 'ece4_nemo_file_def.xml'
  ecearth_oifs_file_def_filename = output_dir_name + 'ece4_oifs_file_def.xml'

  list_of_lpjg_ins_lines               = []
  message_list_of_operation_comparsion = []
  message_list_lpjg_ins_vars           = []
  warnings_nemo = {'grid': [], 'freq': [], 'region' : []} # dict with three message lists
  warnings_oifs = {'grid': [], 'freq': [], 'region' : []} # dict with three message lists

  i_dr = 0

  # Iterate over the variables in the (experiment) CMIP7 data request (including unidentified variables):
  for element_dr in root_dr.findall('.//variable'):
   i_dr += 1

   # Set the xpath search for iterating through the identified file:
   selected_attribute_dr       = 'cmip7_compound_name'
   selected_attribute_dr_value = element_dr.get(selected_attribute_dr)
   xpath_path_identified       = ".//variable"
   xpath_expression_identified = xpath_path_identified + '[@' + selected_attribute_dr + '="' + selected_attribute_dr_value + '"]'
   match = 0 # For bookkeeping the number of identification matches
   for element_identified in root_identified.findall(xpath_expression_identified):
    match += 1

    model_component = element_identified.get('model_component')
    if model_component == 'nemo':
     # The varname_code is based on the ECE ping file for NEMO via the request or identified files
     add_xml_line_to_selected_group(element_identified                     , \
                                    element_identified.get('varname_code') , \
                                    nemo_dict                              , \
                                    warnings_nemo                            \
                                   )
    elif model_component == 'ifs':
     # Handling the OIFS cases in order to create the OIFS file_def file
     add_xml_line_to_selected_group(element_identified                     , \
                                    element_identified.get('ifs_shortname'), \
                                    oifs_dict                              , \
                                    warnings_oifs                            \
                                   )
    elif model_component == 'lpjg':
     # Handling the LPJG cases in order to create the LPJG configuration .ins file
     # Determine the LPJG frequency naming in the .ins file:
     if   element_dr.get('frequency') == 'mon':
      lpjg_freq = 'monthly'
     elif element_dr.get('frequency') == 'yr':
      lpjg_freq = 'yearly'
     elif element_dr.get('frequency') == 'day':
      lpjg_freq = 'daily'
     else:
      print(' Unknown LPJG frequency: {}'.format(element_dr.get('frequency')))
      sys.exit(' Stop in: {} due to unknown LPJG frequency'.format(sys.argv[0]))
     # Determine the CMIP6 LPJG CMOR name for in the .ins file:
     lpjg_var = element_dr.get('physical_parameter_name')
     # Compose the LPJG .ins line for the considered CMIP7 variable - frequency combination:
     lpjg_ins_file_line = 'file_{}_{} "{}_{}.out"'.format(lpjg_var, lpjg_freq, lpjg_var, lpjg_freq)
     # Append the .ins file line for this CMIP7 variable - frequency combination to the list of .ins lines:
     list_of_lpjg_ins_lines.append(lpjg_ins_file_line)
     # Besides, create a message list for this includive printing the cmip7_compound_name:
     message = ' {:66} {}'.format(lpjg_ins_file_line, element_dr.get('cmip7_compound_name'))
     message_list_lpjg_ins_vars.append(message)
    elif model_component == 'tm5':
     # To be added
     pass
    else:
     print(' Warning: the component {} is not covered.'.format(model_component))


  print()
  # Write the NEMO file_def XML file with all the id's:
  ecearth_nemo_file_def_file = write_xml_file_opening(ecearth_nemo_file_def_filename)
  write_xml_file_group(ecearth_nemo_file_def_file, 'id_file_group_ocean'     , nemo_dict, verbosity_level >= 1)
  write_xml_file_closing(ecearth_nemo_file_def_file)

  print()
  # Write the OIFS file_def XML file with all the id's:
  ecearth_oifs_file_def_file = write_xml_file_opening(ecearth_oifs_file_def_filename)
  write_xml_file_group(ecearth_oifs_file_def_file, 'id_file_group_atmosphere', oifs_dict, verbosity_level >= 1)
  write_xml_file_closing(ecearth_oifs_file_def_file)

  # In case we would prefer to have one XML file_def file for ECE4 (NEMO + OIFS):
  ecearth_file_def_file = write_xml_file_opening(ecearth_file_def_filename)
  write_xml_file_group(ecearth_file_def_file     , 'id_file_group_ocean'     , nemo_dict, False)
  write_xml_file_group(ecearth_file_def_file     , 'id_file_group_atmosphere', oifs_dict, False)
  write_xml_file_closing(ecearth_file_def_file)

  # Writing the LPJG .ins congiguration file for the specified data request:
  write_lpjg_ins_file('lpjg-cmip7-output.ins', list_of_lpjg_ins_lines)


  # Test the XML syntax by reading the just created file_def_nemo file:
  tree_ece_file_def_nemo = ET.parse(ecearth_nemo_file_def_filename)
  root_ece_file_def_nemo = tree_ece_file_def_nemo.getroot()

  # Test the XML syntax by reading the just created file_def_oifs file:
  tree_ece_file_def_oifs = ET.parse(ecearth_oifs_file_def_filename)
  root_ece_file_def_oifs = tree_ece_file_def_oifs.getroot()

  # Test the XML syntax by reading the just created file_def file:
  tree_ece_file_def = ET.parse(ecearth_file_def_filename)
  root_ece_file_def = tree_ece_file_def.getroot()


  # Print the message list for those variable-cases where the operation from inheriting differs
  # from the one deduced from the CMIP7 branding:
 #print_message_list(message_list_of_operation_comparsion)

  print()
  # Print the warning messages for fields which are not in the fd file:
  print_message_list(warnings_nemo['grid'  ])
  print_message_list(warnings_oifs['grid'  ])
  print_message_list(warnings_nemo['freq'  ])
  print_message_list(warnings_oifs['freq'  ])
  print_message_list(warnings_nemo['region'])
  print_message_list(warnings_oifs['region'])

  # Print each .ins-file line with the CMIP7 compound name attached:
 #print_message_list(message_list_lpjg_ins_vars)

  print(' The script {} has finished, the results can be found in the directory:\n  {}\n'.format(sys.argv[0], output_dir_name))

else:
   print()
   print(' This script needs one argument: a config file name. E.g.:')
   print('  ', sys.argv[0], 'config-genecec-cmip7-file_def')
   print()
