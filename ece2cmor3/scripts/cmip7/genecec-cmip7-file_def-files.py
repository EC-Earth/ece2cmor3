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


def print_next_step_message(step, comment):
    print('\n')
    print(' ##############################################################################################')
    print(' ###  Part {:<2}:  {:73}   ###'.format(step, comment))
    print(' ##############################################################################################\n')


def print_message_list(message_list):
    for message in message_list:
     print(message)
    print()


def main():

  # The input files:
 #dr_filename            = 'xml-files/experiment-requests/cmip7-request-v1.2.2.5-core.xml'
 #dr_filename            = 'xml-files/experiment-requests/cmip7-request-v1.2.2.5-piControl-priority-ordered.xml'
 #dr_filename            = 'xml-files/experiment-requests/cmip7-request-v1.2.2.5-historical-priority-ordered.xml'
  dr_filename            = 'xml-files/experiment-requests/cmip7-request-v1.2.2.5-esm-hist-priority-ordered.xml'
  identified_filename    = 'xml-files/genecec-cmip7/identify-ece4-cmip7/cmip7-request-v1.2.2.5-all-full-identified-freq-mc-prio.xml'
  ece_field_def_filename = 'xml-files/genecec-cmip7/ec-earth-definition/ec-earth-definition-inherited-neat-formatted.xml'

  # n xml-files/experiment-requests/cmip7-request-v1.2.2.5-core.xml xml-files/genecec-cmip7/identify-ece4-cmip7/cmip7-request-v1.2.2.5-all-full-identified-freq-mc-prio.xml xml-files/genecec-cmip7/ec-earth-definition/ec-earth-definition-inherited-neat-formatted.xml


  ### PART 1 ###
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
 #xpath_path         = "./field_group/field_group/"            # Looping over only the field_group elements in the field_group/field_group/       layer
 #xpath_path         = "./field_group/"                        # Looping over only the field_group elements in the field_group/                   layer
 #xpath_path         = ".//field_group"                        # Looping over all      field_group elements in any                                layer
 #xpath_path         = "./field_group/field_group/field/"      # Looping over only the field       elements in the field_group/field_group/field/ layer
 #xpath_path         = "./field_group/field/"                  # Looping over only the field       elements in the field_group/                   layer
 #xpath_path         = "./field/"                              # Looping over only the field       elements in the field                          layer  id: agrif_spf, ahmf_2d, ahmf_3d
  xpath_path         = ".//variable"                           # Looping over all      variable    elements in any                                layer
 #xpath_expression   = xpath_path + "[@" + selected_attribute + "]"
  xpath_expression   = xpath_path

  i = 0
  for element in root_dr.findall(xpath_expression):
   i += 1
  #print('{:4} {} {:25} {}'.format(i, element.tag, element.get(selected_attribute), element.attrib))
   print('{:4} {}'.format(i, element.get(selected_attribute)))


  ### PART 2 ###
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



  ### PART 3 ###
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



  ### PART 4 ###
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

    #ouput_freq_info  = ''
     grid_ref_info    = ''
     operation_info   = ''
     freq_op_info     = ''
     freq_offset_info = ''
    #if element_fd.get('output_freq'): ouput_freq_info  = ' output_freq = {}'.format(element_fd.get('output_freq'))
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



   # Test the XML syntax by reading the just created file_def_1 file:
  #tree_file_def_1 = ET.parse(file_def_1_filename)
  #root_file_def_1 = tree_file_def_1.getroot()



  print_next_step_message(5, 'Creating a file_def file')


  # Writing the combined result to a new xml file:
  output_dir_name = 'xml-files/genecec-cmip7/ec-earth-file_def-files/'
  subprocess.run(["mkdir", "-p", output_dir_name])

  ecearth_file_def_filename      = output_dir_name + 'ece4_file_def.xml'
  ecearth_nemo_file_def_filename = output_dir_name + 'ece4_nemo_file_def.xml'
  ecearth_oifs_file_def_filename = output_dir_name + 'ece4_oifs_file_def.xml'



  def write_xml_file_opening(xml_file_filename, file_group_id):
      xml_file = open(xml_file_filename, 'w')
      xml_file.write('<?xml version="1.0"?>\n\n')
      xml_file.write('<file_definition min_digits="4" name="@expname@_@freq@_@startdate@_@enddate@" sync_freq="1d" type="one_file">\n')
      xml_file.write('  <file_group id="' + file_group_id + '" default_value="1e20" chunking_blocksize_target="3.0">\n')
      return xml_file

  def write_xml_file_closing(xml_file):
      xml_file.write('   </file_group>\n')
      xml_file.write('</file_definition>\n')
      xml_file.close()
      return

  # The name of this function is not so adequate:
  def write_file_group_to_xml_file(xml_file, group_id, group_grid_ref_value, output_freq, list_with_xml_lines_of_group):
      # Add a group only if it has some content:
      if len(list_with_xml_lines_of_group) != 0:
       suffix = '_' + group_id.strip()
       xml_file.write('    <file id="{}" name_suffix="{}" grid_ref="{}" output_freq="{}">\n'.format(group_id.strip(), suffix, group_grid_ref_value.strip(), output_freq.strip()))
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

  def generate_xml_line_for_variable(cmip7_element, field_id):
      if cmip7_element.get('expression'):
       if cmip7_element.get('expression') != 'None':
        expression = cmip7_element.get('expression')
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
      #print(' TEST A: {}'.format(element_fd.attrib))
      #print(' TEST B: {}'.format(cmip7_element.attrib))
       match_fd += 1
       print(' A  fd match for {:20} with i = {}'.format(field_id, match_fd))
      if match_fd == 0:
       print(' No fd match for {:20} with i = {}'.format(field_id, match_fd))
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
                  ' > {:63}</file>'.format( \
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
                  ' ' +                    expression                + ' ') \
                 )
      return element_fd, xml_line

  def distinguish_in_frequency(output_freq, xml_line, group_fx, group_3hr, group_day, group_mon, group_yr):
       if   output_freq == 'fx':
                                  group_fx .append(xml_line)
       elif output_freq == '3hr':
                                  group_3hr.append(xml_line)
       elif output_freq == 'day':
                                  group_day.append(xml_line)
       elif output_freq == 'mon':
                                  group_mon.append(xml_line)
       elif output_freq == 'yr':
                                  group_yr .append(xml_line)
       else:
        grid_info = re.sub(".*grid_ref", "grid_ref", re.sub("units.*", "", xml_line)).strip()
        print(' Warning: frequency {} not covered for {}'.format(output_freq, grid_info))

  # Remark: Should we distinguish on region as well here? The question is whether we will define
  # other domains (other grid_ref cases) for non global regions like: nh, sh, 30S-90S
  # Note: there are cases left which are not covered (see the two type of warnings in the log files)
  def add_xml_line_to_selected_nemo_group(cmip7_element, field_id, nemo_groups):
      output_freq = cmip7_element.get('frequency')
      # Generate the XML file line for one variable, also make the inherited field_def info of
      # this variable available at this level in this function:
      element_fd, xml_line = generate_xml_line_for_variable(cmip7_element, field_id)
      # Note that this method does not create a new XML tree, but with the group knowledge the
      # XML file is directly written
      if   element_fd == None:
       if   cmip7_element.get('dimensions') == 'longitude latitude time':
        distinguish_in_frequency(output_freq, xml_line, nemo_groups['group_T_2D_fx'      ], \
                                                        nemo_groups['group_T_2D_tavg_3hr'], \
                                                        nemo_groups['group_T_2D_tavg_day'], \
                                                        nemo_groups['group_T_2D_tavg_mon'], \
                                                        nemo_groups['group_T_2D_tavg_yr' ]  )
       elif cmip7_element.get('dimensions') == 'time':
                                                        nemo_groups['group_time'         ].append(xml_line)
       else:
        print(' Warning: case {} not covered in NEMO part with element_fd = None with {:48} {:6} {:12} {}'.format( \
                 output_freq                                           , \
                 'dimensions="' + cmip7_element.get('dimensions') + '"', \
                 cmip7_element.get('priority')                         , \
                 cmip7_element.get('status')                         , \
                 cmip7_element.get('cmip7_compound_name')))
      elif element_fd.get('grid_ref') == 'grid_T_2D':
       distinguish_in_frequency(output_freq, xml_line, nemo_groups['group_T_2D_fx'      ], \
                                                       nemo_groups['group_T_2D_tavg_3hr'], \
                                                       nemo_groups['group_T_2D_tavg_day'], \
                                                       nemo_groups['group_T_2D_tavg_mon'], \
                                                       nemo_groups['group_T_2D_tavg_yr' ]  )
      elif element_fd.get('grid_ref') == 'grid_U_2D':
       distinguish_in_frequency(output_freq, xml_line, nemo_groups['group_U_2D_fx'      ], \
                                                       nemo_groups['group_U_2D_tavg_3hr'], \
                                                       nemo_groups['group_U_2D_tavg_day'], \
                                                       nemo_groups['group_U_2D_tavg_mon'], \
                                                       nemo_groups['group_U_2D_tavg_yr' ]  )
      elif element_fd.get('grid_ref') == 'grid_V_2D':
       distinguish_in_frequency(output_freq, xml_line, nemo_groups['group_V_2D_fx'      ], \
                                                       nemo_groups['group_V_2D_tavg_3hr'], \
                                                       nemo_groups['group_V_2D_tavg_day'], \
                                                       nemo_groups['group_V_2D_tavg_mon'], \
                                                       nemo_groups['group_V_2D_tavg_yr' ]  )
      elif element_fd.get('grid_ref') == 'grid_T_3D':
       distinguish_in_frequency(output_freq, xml_line, nemo_groups['group_T_3D_fx'      ], \
                                                       nemo_groups['group_T_3D_tavg_3hr'], \
                                                       nemo_groups['group_T_3D_tavg_day'], \
                                                       nemo_groups['group_T_3D_tavg_mon'], \
                                                       nemo_groups['group_T_3D_tavg_yr' ]  )
      elif element_fd.get('grid_ref') == 'grid_U_3D':
       distinguish_in_frequency(output_freq, xml_line, nemo_groups['group_U_3D_fx'      ], \
                                                       nemo_groups['group_U_3D_tavg_3hr'], \
                                                       nemo_groups['group_U_3D_tavg_day'], \
                                                       nemo_groups['group_U_3D_tavg_mon'], \
                                                       nemo_groups['group_U_3D_tavg_yr' ]  )
      elif element_fd.get('grid_ref') == 'grid_V_3D':
       distinguish_in_frequency(output_freq, xml_line, nemo_groups['group_V_3D_fx'      ], \
                                                       nemo_groups['group_V_3D_tavg_3hr'], \
                                                       nemo_groups['group_V_3D_tavg_day'], \
                                                       nemo_groups['group_V_3D_tavg_mon'], \
                                                       nemo_groups['group_V_3D_tavg_yr' ]  )
      elif element_fd.get('grid_ref') == 'grid_W_3D':
       distinguish_in_frequency(output_freq, xml_line, nemo_groups['group_W_3D_fx'      ], \
                                                       nemo_groups['group_W_3D_tavg_3hr'], \
                                                       nemo_groups['group_W_3D_tavg_day'], \
                                                       nemo_groups['group_W_3D_tavg_mon'], \
                                                       nemo_groups['group_W_3D_tavg_yr' ]  )
      elif element_fd.get('grid_ref') == 'grid_basin':
                                                       nemo_groups['group_basin'        ].append(xml_line)
      elif element_fd.get('grid_ref') == 'grid_T_vsum':
       distinguish_in_frequency(output_freq, xml_line, nemo_groups['group_T_vsum_fx'    ], \
                                                       nemo_groups['group_T_vsum_3hr'   ], \
                                                       nemo_groups['group_T_vsum_day'   ], \
                                                       nemo_groups['group_T_vsum_mon'   ], \
                                                       nemo_groups['group_T_vsum_yr'    ]  )
      elif element_fd.get('grid_ref') == 'grid_T_iax_20C':
                                                       nemo_groups['group_T_iax_20C'    ].append(xml_line)
      else:
                                                       nemo_groups['group_other'        ].append(xml_line)
      return


# sed -e 's/^.*grid_ref/grid_ref/' -e 's/name=.*$//' -e 's/standard_.*$//' -e 's/operation.*$//' ec-earth-definition-inherited-neat-formatted.xml|sort|uniq|grep grid_ref
#   Encountered grid_ref for OIFS in ECE4 inherited field_def:
#   grid_ref="reduced_sfc"
#   grid_ref="reduced_ml"
#   grid_ref="reduced_plev39"
#   grid_ref="reduced_pv"
#   grid_ref="reduced_th"

  # Note that the OIFS field_def files contain a group with grid_ref="reduced_plev39 while the CMIP7 request asks
  # mainly for grid_ref="reduced_plev19. Figure out if the 39 set overlaps the 19 set.

  # Remark: Should we distinguish on region as well here? The question is whether we will define
  # other domains (other grid_ref cases) for non global regions like: nh, sh, 30S-90S
  # Note: there are cases left which are not covered (see the two type of warnings in the log files)
  def add_xml_line_to_selected_oifs_group(cmip7_element, field_id, oifs_groups):
      output_freq = cmip7_element.get('frequency')
      # Generate the XML file line for one variable, also make the inherited field_def info of
      # this variable available at this level in this function:
      element_fd, xml_line = generate_xml_line_for_variable(cmip7_element, field_id)
      # Note that this method does not create a new XML tree, but with the group knowledge the
      # XML file is directly written
      if   element_fd == None:
       if   cmip7_element.get('dimensions') == 'longitude latitude time':
        distinguish_in_frequency(output_freq, xml_line, oifs_groups['reduced_sfc_fx'    ], \
                                                        oifs_groups['reduced_sfc_3hr'   ], \
                                                        oifs_groups['reduced_sfc_day'   ], \
                                                        oifs_groups['reduced_sfc_mon'   ], \
                                                        oifs_groups['reduced_sfc_yr'    ]  )
       elif cmip7_element.get('dimensions') == 'longitude latitude plev19 time':
        distinguish_in_frequency(output_freq, xml_line, oifs_groups['reduced_plev19_fx' ], \
                                                        oifs_groups['reduced_plev19_3hr'], \
                                                        oifs_groups['reduced_plev19_day'], \
                                                        oifs_groups['reduced_plev19_mon'], \
                                                        oifs_groups['reduced_plev19_yr' ]  )
       elif cmip7_element.get('dimensions') == 'longitude latitude plev39 time':
        distinguish_in_frequency(output_freq, xml_line, oifs_groups['reduced_plev39_fx' ], \
                                                        oifs_groups['reduced_plev39_3hr'], \
                                                        oifs_groups['reduced_plev39_day'], \
                                                        oifs_groups['reduced_plev39_mon'], \
                                                        oifs_groups['reduced_plev39_yr' ]  )
       elif cmip7_element.get('dimensions') == 'time':
                                                        oifs_groups['group_time'        ].append(xml_line)
       else:
        print(' Warning: case {} not covered in oifs part with element_fd = None with {:48} {:6} {:12} {}'.format( \
                 output_freq                                           , \
                 'dimensions="' + cmip7_element.get('dimensions') + '"', \
                 cmip7_element.get('priority')                         , \
                 cmip7_element.get('status')                         , \
                 cmip7_element.get('cmip7_compound_name')))
      elif element_fd.get('grid_ref') == 'reduced_sfc':
       distinguish_in_frequency(output_freq, xml_line, oifs_groups['reduced_sfc_fx'    ], \
                                                       oifs_groups['reduced_sfc_3hr'   ], \
                                                       oifs_groups['reduced_sfc_day'   ], \
                                                       oifs_groups['reduced_sfc_mon'   ], \
                                                       oifs_groups['reduced_sfc_yr'    ]  )
      elif element_fd.get('grid_ref') == 'reduced_plev19':
       distinguish_in_frequency(output_freq, xml_line, oifs_groups['reduced_plev19_fx' ], \
                                                       oifs_groups['reduced_plev19_3hr'], \
                                                       oifs_groups['reduced_plev19_day'], \
                                                       oifs_groups['reduced_plev19_mon'], \
                                                       oifs_groups['reduced_plev19_yr' ]  )
      elif element_fd.get('grid_ref') == 'reduced_plev39':
       distinguish_in_frequency(output_freq, xml_line, oifs_groups['reduced_plev39_fx' ], \
                                                       oifs_groups['reduced_plev39_3hr'], \
                                                       oifs_groups['reduced_plev39_day'], \
                                                       oifs_groups['reduced_plev39_mon'], \
                                                       oifs_groups['reduced_plev39_yr' ]  )
      elif element_fd.get('grid_ref') == 'reduced_ml':
       distinguish_in_frequency(output_freq, xml_line, oifs_groups['reduced_ml_fx'     ], \
                                                       oifs_groups['reduced_ml_3hr'    ], \
                                                       oifs_groups['reduced_ml_day'    ], \
                                                       oifs_groups['reduced_ml_mon'    ], \
                                                       oifs_groups['reduced_ml_yr'     ]  )
     #elif element_fd.get('grid_ref') == 'grid_U_2D':
     #elif element_fd.get('grid_ref') == 'grid_V_2D':
     #elif element_fd.get('grid_ref') == 'grid_T_3D':
     #elif element_fd.get('grid_ref') == 'grid_U_3D':
     #elif element_fd.get('grid_ref') == 'grid_V_3D':
     #elif element_fd.get('grid_ref') == 'grid_W_3D':
     #elif element_fd.get('grid_ref') == 'grid_basin':
     #                                                 oifs_groups['group_basin'        ].append(xml_line)
     #elif element_fd.get('grid_ref') == 'grid_T_vsum':
     #elif element_fd.get('grid_ref') == 'grid_T_iax_20C':
     #                                                 oifs_groups['group_T_iax_20C'    ].append(xml_line)
      else:
                                                       oifs_groups['group_other'    ].append(xml_line)
      return






# def add_xml_line_to_selected_oifs_group(cmip7_element, field_id, oifs_groups):
#     element_fd, xml_line = generate_xml_line_for_variable(cmip7_element, field_id)
#     # Note that this method does not create a new XML tree, but with the group knowledge the
#     # XML file is directly written
#     if   cmip7_element.get('dimensions') == 'longitude latitude time'           :
#      if   cmip7_element.get('frequency') == 'day':
#                                                    oifs_groups['group_lon_lat_time_tavg_day'].append(xml_line)
#      elif cmip7_element.get('frequency') == 'mon':
#                                                    oifs_groups['group_lon_lat_time_tavg_mon'].append(xml_line)
#      elif cmip7_element.get('frequency') == 'yr':
#                                                    oifs_groups['group_lon_lat_time_tavg_yr' ].append(xml_line)
#      else:
#       print(' Warning: frequency not covered for group_lon_lat_time_tavg for {}'.format(field_id))
#     elif cmip7_element.get('dimensions') == 'longitude latitude plev19 time'    :
#                                                                                  oifs_groups['group_lon_lat_plev19_time'   ].append(xml_line)
#     elif cmip7_element.get('dimensions') == 'longitude latitude alevel time'    :
#                                                                                  oifs_groups['group_lon_lat_alevel_time'   ].append(xml_line)
#     elif cmip7_element.get('dimensions') == 'longitude latitude plev3 time1'    :
#                                                                                  oifs_groups['group_lon_lat_plev3_time1'   ].append(xml_line)
#     elif cmip7_element.get('dimensions') == 'longitude latitude time height2m'  :
#                                                                                  oifs_groups['group_lon_lat_time_height2m' ].append(xml_line)
#     elif cmip7_element.get('dimensions') == 'longitude latitude time height10m' :
#                                                                                  oifs_groups['group_lon_lat_time_height10m'].append(xml_line)
#     elif cmip7_element.get('dimensions') == 'longitude latitude'                :
#                                                                                  oifs_groups['group_lon_lat'               ].append(xml_line)
#     else                                                                        :
#                                                                                  oifs_groups['group_other'                 ].append(xml_line)
#     return

  def write_lpjg_ins_file(lpjg_ins_file_filename, list_of_lpjg_ins_lines):
      lpjg_ins_file_file = open(lpjg_ins_file_filename, 'w')
      for lpjg_ins_line in list_of_lpjg_ins_lines:
       lpjg_ins_file_file.write('{}\n'.format(lpjg_ins_line))
      return


  class region:
    glb = []    # Global
    nh  = []    # Northern hemisphere
    sh  = []    # Southern hemisphere
    s30 = []    # 30S-90S

  class frequency:
    freq_fx  = region()
    freq_1hr = region()
    freq_3hr = region()
    freq_6hr = region()
    freq_day = region()
    freq_mon = region()
    freq_yr  = region()

  class nemo_group:
    # NEMO grid_ref or dimensional shape cases
    T_2D    = frequency()
    U_2D    = frequency()
    V_2D    = frequency()
    T_3D    = frequency()
    U_3D    = frequency()
    V_3D    = frequency()
    W_3D    = frequency()
    T_vsum  = frequency()
    time    = frequency()
    basin   = frequency()
    other   = frequency()

  class oifs_group:
    # OIFS grid_ref or dimensional shape cases
    reduced_sfc    = frequency()
    reduced_plev19 = frequency()
    reduced_plev39 = frequency()
    reduced_ml     = frequency()

 #nemo_group.T_2D.freq_mon.glb.append(7)
 #print('\n{}'.format(nemo_group.T_2D.freq_mon.glb))

  # Create a dictionary for the NEMO file groups (each group covers a grid_ref, output_freq combination
  # [later maybe extended with region]):
  nemo_groups = {
    'group_T_2D_fx'      : [],
    'group_T_2D_tavg_3hr': [],
    'group_T_2D_tavg_day': [],
    'group_T_2D_tavg_mon': [],
    'group_T_2D_tavg_yr' : [],
    'group_U_2D_fx'      : [],
    'group_U_2D_tavg_3hr': [],
    'group_U_2D_tavg_day': [],
    'group_U_2D_tavg_mon': [],
    'group_U_2D_tavg_yr' : [],
    'group_V_2D_fx'      : [],
    'group_V_2D_tavg_3hr': [],
    'group_V_2D_tavg_day': [],
    'group_V_2D_tavg_mon': [],
    'group_V_2D_tavg_yr' : [],
    'group_T_3D_fx'      : [],
    'group_T_3D_tavg_3hr': [],
    'group_T_3D_tavg_day': [],
    'group_T_3D_tavg_mon': [],
    'group_T_3D_tavg_yr' : [],
    'group_U_3D_fx'      : [],
    'group_U_3D_tavg_3hr': [],
    'group_U_3D_tavg_day': [],
    'group_U_3D_tavg_mon': [],
    'group_U_3D_tavg_yr' : [],
    'group_V_3D_fx'      : [],
    'group_V_3D_tavg_3hr': [],
    'group_V_3D_tavg_day': [],
    'group_V_3D_tavg_mon': [],
    'group_V_3D_tavg_yr' : [],
    'group_W_3D_fx'      : [],
    'group_W_3D_tavg_3hr': [],
    'group_W_3D_tavg_day': [],
    'group_W_3D_tavg_mon': [],
    'group_W_3D_tavg_yr' : [],
    'group_time'         : [],
    'group_basin'        : [],
    'group_T_vsum_fx'    : [],
    'group_T_vsum_3hr'   : [],
    'group_T_vsum_day'   : [],
    'group_T_vsum_mon'   : [],
    'group_T_vsum_yr'    : [],
    'group_T_iax_20C'    : [],
    'group_other'        : []
  }

  # Create a dictionary for the OIFS file groups (each group covers a grid_ref, output_freq combination
  # [later maybe extended with region]):
  # The XXX frequency needs to be set and extended in case several frequencies per grid_ref case are encountered
  oifs_groups = {
    'reduced_sfc_fx'      : [],
    'reduced_sfc_3hr'     : [],
    'reduced_sfc_day'     : [],
    'reduced_sfc_mon'     : [],
    'reduced_sfc_yr'      : [],
    'reduced_plev19_fx'   : [],
    'reduced_plev19_3hr'  : [],
    'reduced_plev19_day'  : [],
    'reduced_plev19_mon'  : [],
    'reduced_plev19_yr'   : [],
    'reduced_plev39_fx'   : [],
    'reduced_plev39_3hr'  : [],
    'reduced_plev39_day'  : [],
    'reduced_plev39_mon'  : [],
    'reduced_plev39_yr'   : [],
    'reduced_ml_fx'       : [],
    'reduced_ml_3hr'      : [],
    'reduced_ml_day'      : [],
    'reduced_ml_mon'      : [],
    'reduced_ml_yr'       : [],
   #'group_lon_lat_plev19_time_XXX'   : [],
   #'group_lon_lat_alevel_time_XXX'   : [],
   #'group_lon_lat_plev3_time1_XXX'   : [],
   #'group_lon_lat_time_height2m_XXX' : [],
   #'group_lon_lat_time_height10m_XXX': [],
    'group_lon_lat'                   : [],
    'group_other'                     : []
  }

  list_of_lpjg_ins_lines               = []

  message_list_of_operation_comparsion = []
  message_list_lpjg_ins_vars           = []

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

    if element_identified.get('model_component') == 'nemo':
     # The varname_code is based on the ECE ping file for NEMO via the request or identified files
     add_xml_line_to_selected_nemo_group(element_identified, element_identified.get('varname_code'), nemo_groups)
    elif element_identified.get('model_component') == 'ifs':
     # Handling the OIFS cases in order to create the OIFS file_def file
    #add_xml_line_to_selected_oifs_group(element_identified, element_identified.get('varname_code'), oifs_groups)
     add_xml_line_to_selected_oifs_group(element_identified, element_identified.get('ifs_shortname'), oifs_groups)
    elif element_identified.get('model_component') == 'lpjg':
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

  #print(' TEST {:4} {}'.format(i_dr, selected_attribute_dr_value))


  # In case we would prefer to have one XML file_def file for ECE4 (NEMO + OIFS):
  ecearth_file_def_file = write_xml_file_opening(ecearth_file_def_filename     , 'id_file_group_ocean')
  # Yet empty.
  write_xml_file_closing(ecearth_file_def_file)


  # Write the NEMO file_def XML file with all the id's:
  ecearth_nemo_file_def_file = write_xml_file_opening(ecearth_nemo_file_def_filename, 'id_file_group_ocean')
  #                            xml_file                  , group_id              , grid_ref        , freq  , dict['group_list'] = list_with_xml_lines_of_group
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_time'          , 'grid_1point'   , 'mon' , nemo_groups['group_time'         ])

  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_basin'         , 'grid_basin'    , 'once', nemo_groups['group_basin'        ])

  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_2D_fx'       , 'grid_T_2D'     , 'once', nemo_groups['group_T_2D_fx'      ])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_2D_tavg_3hr' , 'grid_T_2D'     , '3hr' , nemo_groups['group_T_2D_tavg_3hr'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_2D_tavg_day' , 'grid_T_2D'     , '1d'  , nemo_groups['group_T_2D_tavg_day'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_2D_tavg_mon' , 'grid_T_2D'     , '1mo' , nemo_groups['group_T_2D_tavg_mon'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_2D_tavg_yr'  , 'grid_T_2D'     , '1yr' , nemo_groups['group_T_2D_tavg_yr' ])

  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_U_2D_fx'       , 'grid_U_2D'     , 'once', nemo_groups['group_U_2D_fx'      ])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_U_2D_tavg_3hr' , 'grid_U_2D'     , '3hr' , nemo_groups['group_U_2D_tavg_3hr'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_U_2D_tavg_day' , 'grid_U_2D'     , '1d'  , nemo_groups['group_U_2D_tavg_day'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_U_2D_tavg_mon' , 'grid_U_2D'     , '1mo' , nemo_groups['group_U_2D_tavg_mon'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_U_2D_tavg_yr'  , 'grid_U_2D'     , '1yr' , nemo_groups['group_U_2D_tavg_yr' ])

  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_V_2D_fx'       , 'grid_V_2D'     , 'once', nemo_groups['group_V_2D_fx'      ])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_V_2D_tavg_3hr' , 'grid_V_2D'     , '3hr' , nemo_groups['group_V_2D_tavg_3hr'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_V_2D_tavg_day' , 'grid_V_2D'     , '1d'  , nemo_groups['group_V_2D_tavg_day'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_V_2D_tavg_mon' , 'grid_V_2D'     , '1mo' , nemo_groups['group_V_2D_tavg_mon'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_V_2D_tavg_yr'  , 'grid_V_2D'     , '1yr' , nemo_groups['group_V_2D_tavg_yr' ])

  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_3D_fx'       , 'grid_T_3D'     , 'once', nemo_groups['group_T_3D_fx'      ])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_3D_tavg_3hr' , 'grid_T_3D'     , '3hr' , nemo_groups['group_T_3D_tavg_3hr'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_3D_tavg_day' , 'grid_T_3D'     , '1d'  , nemo_groups['group_T_3D_tavg_day'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_3D_tavg_mon' , 'grid_T_3D'     , '1mo' , nemo_groups['group_T_3D_tavg_mon'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_3D_tavg_yr'  , 'grid_T_3D'     , '1yr' , nemo_groups['group_T_3D_tavg_yr' ])

  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_U_3D_fx'       , 'grid_U_3D'     , 'once', nemo_groups['group_U_3D_fx'      ])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_U_3D_tavg_3hr' , 'grid_U_3D'     , '3hr' , nemo_groups['group_U_3D_tavg_3hr'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_U_3D_tavg_day' , 'grid_U_3D'     , '1d'  , nemo_groups['group_U_3D_tavg_day'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_U_3D_tavg_mon' , 'grid_U_3D'     , '1mo' , nemo_groups['group_U_3D_tavg_mon'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_U_3D_tavg_yr'  , 'grid_U_3D'     , '1yr' , nemo_groups['group_U_3D_tavg_yr' ])

  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_V_3D_fx'       , 'grid_V_3D'     , 'once', nemo_groups['group_V_3D_fx'      ])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_V_3D_tavg_3hr' , 'grid_V_3D'     , '3hr' , nemo_groups['group_V_3D_tavg_3hr'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_V_3D_tavg_day' , 'grid_V_3D'     , '1d'  , nemo_groups['group_V_3D_tavg_day'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_V_3D_tavg_mon' , 'grid_V_3D'     , '1mo' , nemo_groups['group_V_3D_tavg_mon'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_V_3D_tavg_yr'  , 'grid_V_3D'     , '1yr' , nemo_groups['group_V_3D_tavg_yr' ])

  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_W_3D_fx'       , 'grid_W_3D'     , 'once', nemo_groups['group_W_3D_fx'      ])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_W_3D_tavg_3hr' , 'grid_W_3D'     , '3hr' , nemo_groups['group_W_3D_tavg_3hr'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_W_3D_tavg_day' , 'grid_W_3D'     , '1d'  , nemo_groups['group_W_3D_tavg_day'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_W_3D_tavg_mon' , 'grid_W_3D'     , '1mo' , nemo_groups['group_W_3D_tavg_mon'])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_W_3D_tavg_yr'  , 'grid_W_3D'     , '1yr' , nemo_groups['group_W_3D_tavg_yr' ])

  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_vsum_fx'     , 'grid_T_vsum'   , 'once', nemo_groups['group_T_vsum_fx'    ])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_vsum_3hr'    , 'grid_T_vsum'   , '3hr' , nemo_groups['group_T_vsum_3hr'   ])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_vsum_day'    , 'grid_T_vsum'   , '1d'  , nemo_groups['group_T_vsum_day'   ])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_vsum_mon'    , 'grid_T_vsum'   , '1mo' , nemo_groups['group_T_vsum_mon'   ])
  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_vsum_yr'     , 'grid_T_vsum'   , '1yr' , nemo_groups['group_T_vsum_yr'    ])

  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'group_T_iax_20C'     , 'grid_T_iax_20C', 'mon' , nemo_groups['group_T_iax_20C'    ])

  write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'nemo_cmip7_other'    , '??'            , '??'  , nemo_groups['group_other'        ])
  write_xml_file_closing(ecearth_nemo_file_def_file)


  # Write the OIFS file_def XML file with all the id's:
  ecearth_oifs_file_def_file = write_xml_file_opening(ecearth_oifs_file_def_filename, 'id_file_group_ocean')
  #                            xml_file                  , group_id            , grid_ref     , list_with_xml_lines_of_group)
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_sfc_fx'    , 'reduced_sfc'   , 'once', oifs_groups['reduced_sfc_fx'    ])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_sfc_3hr'   , 'reduced_sfc'   , '3hr' , oifs_groups['reduced_sfc_3hr'   ])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_sfc_day'   , 'reduced_sfc'   , '1d'  , oifs_groups['reduced_sfc_day'   ])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_sfc_mon'   , 'reduced_sfc'   , '1mo' , oifs_groups['reduced_sfc_mon'   ])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_sfc_yr'    , 'reduced_sfc'   , '1yr' , oifs_groups['reduced_sfc_yr'    ])

  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_plev19_fx' , 'reduced_plev19', 'once', oifs_groups['reduced_plev19_fx' ])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_plev19_3hr', 'reduced_plev19', '3hr' , oifs_groups['reduced_plev19_3hr'])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_plev19_day', 'reduced_plev19', '1d'  , oifs_groups['reduced_plev19_day'])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_plev19_mon', 'reduced_plev19', '1mo' , oifs_groups['reduced_plev19_mon'])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_plev19_yr' , 'reduced_plev19', '1yr' , oifs_groups['reduced_plev19_yr' ])

  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_plev39_fx' , 'reduced_plev39', 'once', oifs_groups['reduced_plev39_fx' ])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_plev39_3hr', 'reduced_plev39', '3hr' , oifs_groups['reduced_plev39_3hr'])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_plev39_day', 'reduced_plev39', '1d'  , oifs_groups['reduced_plev39_day'])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_plev39_mon', 'reduced_plev39', '1mo' , oifs_groups['reduced_plev39_mon'])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_plev39_yr' , 'reduced_plev39', '1yr' , oifs_groups['reduced_plev39_yr' ])

  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_ml_fx'     , 'reduced_ml'    , 'once', oifs_groups['reduced_ml_fx'     ])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_ml_3hr'    , 'reduced_ml'    , '3hr' , oifs_groups['reduced_ml_3hr'    ])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_ml_day'    , 'reduced_ml'    , '1d'  , oifs_groups['reduced_ml_day'    ])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_ml_mon'    , 'reduced_ml'    , '1mo' , oifs_groups['reduced_ml_mon'    ])
  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'reduced_ml_yr'     , 'reduced_ml'    , '1yr' , oifs_groups['reduced_ml_yr'     ])

  write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'oifs_cmip7_other'  , '??'            , '??'  , oifs_groups['group_other'       ])
  write_xml_file_closing(ecearth_oifs_file_def_file)

 #write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'oifs_cmip7_lon_lat'                  , 'grid_T_2D'     , 'once', oifs_groups['group_lon_lat'               ])
 #write_file_group_to_xml_file(ecearth_nemo_file_def_file, 'oifs_cmip7_lon_lat_time_tavg_day'    , 'grid_T_2D'     , '1d'  , oifs_groups['group_lon_lat_time_tavg_day' ])
 #write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'oifs_cmip7_lon_lat_plev19_time_tavg' , 'reduced_plev19', '1d'  , oifs_groups['group_lon_lat_plev19_time'   ])
 #write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'oifs_cmip7_lon_lat_alevel_time_tavg' , 'reduced_ml'    , '1d'  , oifs_groups['group_lon_lat_alevel_time'   ])
 #write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'oifs_cmip7_lon_lat_plev3_time1'      , 'reduced_plev3' , '1d'  , oifs_groups['group_lon_lat_plev3_time1'   ])
 #write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'oifs_cmip7_lon_lat_time_height2m'    , 'reduced_sfc'   , '1d'  , oifs_groups['group_lon_lat_time_height2m' ])
 #write_file_group_to_xml_file(ecearth_oifs_file_def_file, 'oifs_cmip7_lon_lat_time_height10m'   , 'reduced_sfc'   , '1d'  , oifs_groups['group_lon_lat_time_height10m'])


  # Writing the LPJG .ins congiguration file for the specified data request:
  write_lpjg_ins_file('lpjg-cmip7-output.ins', list_of_lpjg_ins_lines)


  print()

  # Print the message list for those variable-cases where the operation from inheriting differs
  # from the one deduced from the CMIP7 branding:
  print_message_list(message_list_of_operation_comparsion)

  # Print each .ins-file line with the CMIP7 compound name attached:
  print_message_list(message_list_lpjg_ins_vars)

  print_next_step_message(10, 'FINISHING')
  print(' The script {} has finished, the results can be found in the directory:\n  {}\n'.format(sys.argv[0], output_dir_name))

if __name__ == '__main__':
    main()
