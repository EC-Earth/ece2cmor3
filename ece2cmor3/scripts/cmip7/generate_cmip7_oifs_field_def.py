#!/usr/bin/env python3
"""

 Scanning the XML structure of a set of XIOS field_def files:

 Call example:
  ./generate_cmip7_oifs_field_def.py v1.2.2.4 -v > generate_cmip7_oifs_field_def.log

"""
import sys
import subprocess
import argparse
import xml.etree.ElementTree as ET
import data_request_api.content.dreq_content as dc

def parse_args():
    """
    Parse command-line arguments
    """
    parser = argparse.ArgumentParser(
        description='Generate an OIFS field_def file including the CMIP7 variables.'
    )
    # Positional (mandatory) input arguments
    parser.add_argument('dreq_version', choices=dc.get_versions()           , help="data request version")
    # Optional input arguments
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Verbose messaging')
    return parser.parse_args()

def print_next_step_message(step, comment):
    print('\n')
    print(' ##############################################################################################')
    print(' ###  Part {:<2}:  {:73}   ###'.format(step, comment))
    print(' ##############################################################################################\n')


def main():

  args = parse_args()

  dr_version = args.dreq_version
  verbose    = args.verbose

  print_next_step_message(1, 'Generate an OIFS field_def file including CMIP7 variables')

  # Load the ecearth_field_def_inherited_nf_file:
  ecearth_field_def_inherited_nf_filename = 'xml-files/genecec-cmip7/ec-earth-definition/ec-earth-definition-inherited-neat-formatted.xml'
  tree_ecearth_field_def_inherited_nf = ET.parse(ecearth_field_def_inherited_nf_filename)
  root_ecearth_field_def_inherited_nf = tree_ecearth_field_def_inherited_nf.getroot()

  # Load the CMIP7 request with the identified info from CMIP7 - ECE3:
  xml_filename_priority_ordered = 'xml-files/genecec-cmip7/identify-ece4-cmip7/cmip7-request-{}-all-full-priority.xml'.format(dr_version)
  tree_cmip7_request = ET.parse(xml_filename_priority_ordered)
  root_cmip7_request = tree_cmip7_request.getroot()


  def print_message_list(message_list):
      for message in message_list:
       print(message)
      print()
      return

  def add_message(message_head, message_list, element):
      message_list.append(' {} {:10} {:20} {:10} {:55} {}'
                          .format(message_head                      , \
                                  element.get('priority'           ), \
                                  element.get('status'             ), \
                                  element.get('model_component'    ), \
                                  element.get('cmip7_compound_name'), \
                                  element.get('comment'            )  \
                                 ))
      return

  def write_xml_file_opening(xml_file_filename):
      xml_file = open(xml_file_filename, 'w')
      xml_file.write('<?xml version="1.0"?>\n\n')
      xml_file.write('<field_definition>\n')
      xml_file.write('  <field_group id="all_atm_cmip7" default_value="1e20" chunking_blocksize_target="3.0">\n')
      return xml_file

  def write_xml_file_closing(xml_file):
      xml_file.write('   </field_group>\n')
      xml_file.write('</field_definition>\n')
      xml_file.close()
      return

  def write_field_group_to_xml_file(xml_file, group_id, group_grid_ref_value, list_with_xml_lines_of_group):
      xml_file.write('    <field_group id="{}" grid_ref="{}">\n'.format(group_id.strip(), group_grid_ref_value.strip()))
      for xml_line in list_with_xml_lines_of_group:
       xml_file.write('{}\n'.format(xml_line))
      xml_file.write('    </field_group>\n')
      return

  def generate_xml_line_for_variable(cmip7_element, field_id, operation='average'):
      xml_line = ('      <field  id={:12}' \
                               ' priority={:10}' \
                               ' units={:20}' \
                               ' dimensions={:45}' \
                               ' operation={:10}' \
                               ' branding_label={:25}' \
                               ' cmip7_compound_name={:55}' \
                               ' long_name={:132}' \
                               ' standard_name={:160}' \
                               ' modeling_realm={:33}' \
                               ' region={:12}' \
                               ' cmip6_table={:14}' \
                               ' physical_parameter_name={:28}' \
                  ' >   </field>'.format( \
                  '"' +                    field_id                  + '"', \
                  '"' + cmip7_element.get('priority'               ) + '"', \
                  '"' + cmip7_element.get('units'                  ) + '"', \
                  '"' + cmip7_element.get('dimensions'             ) + '"', \
                  '"' +                    operation                 + '"', \
                  '"' + cmip7_element.get('branding_label'         ) + '"', \
                  '"' + cmip7_element.get('cmip7_compound_name'    ) + '"', \
                  '"' + cmip7_element.get('long_name'              ) + '"', \
                  '"' + cmip7_element.get('standard_name'          ) + '"', \
                  '"' + cmip7_element.get('modeling_realm'         ) + '"', \
                  '"' + cmip7_element.get('region'                 ) + '"', \
                  '"' + cmip7_element.get('cmip6_table'            ) + '"', \
                  '"' + cmip7_element.get('physical_parameter_name') + '"') \
                 )
      return xml_line

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
   # operation = ''
   #elif element.get('branding_label')[:3] == 'tminavg-':
   # operation = ''
   #elif element.get('branding_label')[:3] == 'tclm-':
   # operation = ''
   #elif element.get('branding_label')[:3] == 'tclmdc-':
   # operation = ''
    else:
     operation = 'unknown'
    return operation

  def add_xml_line_to_selected_group(cmip7_element               , \
                                     field_id                    , \
                                     group_lon_lat_time_tavg     , \
                                     group_lon_lat_plev19_time   , \
                                     group_lon_lat_alevel_time   , \
                                     group_lon_lat_plev3_time1   , \
                                     group_lon_lat_time_height2m , \
                                     group_lon_lat_time_height10m, \
                                     group_lon_lat               , \
                                     group_other                   \
                                    ):
      xml_line = generate_xml_line_for_variable(cmip7_element, field_id, determine_operation_value(cmip7_element))
      if   cmip7_element.get('dimensions') == 'longitude latitude time'           :
                                                                                   group_lon_lat_time_tavg     .append(xml_line)
      elif cmip7_element.get('dimensions') == 'longitude latitude plev19 time'    :
                                                                                   group_lon_lat_plev19_time   .append(xml_line)
      elif cmip7_element.get('dimensions') == 'longitude latitude alevel time'    :
                                                                                   group_lon_lat_alevel_time   .append(xml_line)
      elif cmip7_element.get('dimensions') == 'longitude latitude plev3 time1'    :
                                                                                   group_lon_lat_plev3_time1   .append(xml_line)
      elif cmip7_element.get('dimensions') == 'longitude latitude time height2m'  :
                                                                                   group_lon_lat_time_height2m .append(xml_line)
      elif cmip7_element.get('dimensions') == 'longitude latitude time height10m' :
                                                                                   group_lon_lat_time_height10m.append(xml_line)
      elif cmip7_element.get('dimensions') == 'longitude latitude'                :
                                                                                   group_lon_lat               .append(xml_line)
      else                                                                        :
                                                                                   group_other                 .append(xml_line)
      return


  # Not in use:
  cmip7_dimension_cases = [ 'longitude latitude time'           , \
                            'longitude latitude plev19 time'    , \
                            'longitude latitude alevel time'    , \
                            'longitude latitude plev3 time1'    , \
                            'longitude latitude time height2m'  , \
                            'longitude latitude time height10m' , \
                            'longitude latitude'                , \
                          ]

  group_lon_lat_time_tavg      = []
  group_lon_lat_plev19_time    = []
  group_lon_lat_alevel_time    = []
  group_lon_lat_plev3_time1    = []
  group_lon_lat_time_height2m  = []
  group_lon_lat_time_height10m = []
  group_lon_lat                = []
  group_other                  = []

  add_existing_oifs_field_def_variables = False

  m7_nr = 0
  oifs_output_dir_name = 'xml-files/genecec-cmip7/oifs-field_def/'
  subprocess.run(["mkdir", "-p", oifs_output_dir_name])
  oifs_cmip7_field_def_file_name = oifs_output_dir_name + 'field_def_oifs_cmip7.xml.j2'
  oifs_cmip7_xml_file = write_xml_file_opening(oifs_cmip7_field_def_file_name)

  # Iterate over all the CMIP7 variables:
  xpath_expression_cmip7_request = './/variable'
  for cmip7_element in root_cmip7_request.findall(xpath_expression_cmip7_request):
   # Iterate over all the fields in the field_def file, but only select the match when the field id in the field_def
   # equals the ifs_shortname in the CMIP7 request file:
   xpath_expression_field_def = './/field[@id="'+cmip7_element.get('ifs_shortname')+'"]'
   for field_def_element in root_ecearth_field_def_inherited_nf.findall(xpath_expression_field_def):
    # This part concerns the oifs variables which are already in the existing oifs field_def file in the ECE4 repo:
    if add_existing_oifs_field_def_variables:
     add_xml_line_to_selected_group(cmip7_element               , \
                                    field_def_element.get('id') , \
                                    group_lon_lat_time_tavg     , \
                                    group_lon_lat_plev19_time   , \
                                    group_lon_lat_alevel_time   , \
                                    group_lon_lat_plev3_time1   , \
                                    group_lon_lat_time_height2m , \
                                    group_lon_lat_time_height10m, \
                                    group_lon_lat               , \
                                    group_other                   \
                                   )
   else: # for-else
    if   cmip7_element.get('model_component') == 'ifs':
     # This part concerns the oifs variables which are not in the existing oifs field_def file in the ECE4 repo:
     if True:
#     if cmip7_element.get('ifs_shortname') == 'None':
#      print(' {:55} {}'.format(cmip7_element.get('cmip7_compound_name'), cmip7_element.get('ifs_shortname')))
      add_xml_line_to_selected_group(cmip7_element               , \
                                     cmip7_element.get('ifs_shortname'), \
                                     group_lon_lat_time_tavg     , \
                                     group_lon_lat_plev19_time   , \
                                     group_lon_lat_alevel_time   , \
                                     group_lon_lat_plev3_time1   , \
                                     group_lon_lat_time_height2m , \
                                     group_lon_lat_time_height10m, \
                                     group_lon_lat               , \
                                     group_other                   \
                                    )
     else:
      pass
    elif cmip7_element.get('model_component') == 'tm5':
     # This part concerns the TM7 oifs variables which are not in the existing oifs field_def file in the ECE4 repo:
     if True:
      m7_nr += 1
      add_xml_line_to_selected_group(cmip7_element               , \
                                     'M7_no_{:03d}'.format(m7_nr), \
                                     group_lon_lat_time_tavg     , \
                                     group_lon_lat_plev19_time   , \
                                     group_lon_lat_alevel_time   , \
                                     group_lon_lat_plev3_time1   , \
                                     group_lon_lat_time_height2m , \
                                     group_lon_lat_time_height10m, \
                                     group_lon_lat               , \
                                     group_other                   \
                                    )
     else:
      pass
    elif cmip7_element.get('model_component') == 'lpjg':            # add other better check
     pass
    elif cmip7_element.get('model_component') == 'nemo':            # add other better check
     pass
    else:
     if cmip7_element.get('modeling_realm') == 'atmos':
      pass
     if cmip7_element.get('modeling_realm') == 'atmosChem':
      pass
     if cmip7_element.get('modeling_realm') == 'aerosol':
      pass
     else:
      pass

  write_field_group_to_xml_file(oifs_cmip7_xml_file, 'oifs_cmip7_lon_lat'                  , 'reduced_sfc'   , group_lon_lat               )
  write_field_group_to_xml_file(oifs_cmip7_xml_file, 'oifs_cmip7_lon_lat_time_tavg'        , 'reduced_sfc'   , group_lon_lat_time_tavg     )
  write_field_group_to_xml_file(oifs_cmip7_xml_file, 'oifs_cmip7_lon_lat_plev19_time_tavg' , 'reduced_plev19', group_lon_lat_plev19_time   )
  write_field_group_to_xml_file(oifs_cmip7_xml_file, 'oifs_cmip7_lon_lat_alevel_time_tavg' , 'reduced_ml'    , group_lon_lat_alevel_time   )
  write_field_group_to_xml_file(oifs_cmip7_xml_file, 'oifs_cmip7_lon_lat_plev3_time1'      , 'reduced_plev3' , group_lon_lat_plev3_time1   )
  write_field_group_to_xml_file(oifs_cmip7_xml_file, 'oifs_cmip7_lon_lat_time_height2m'    , 'reduced_sfc'   , group_lon_lat_time_height2m )
  write_field_group_to_xml_file(oifs_cmip7_xml_file, 'oifs_cmip7_lon_lat_time_height10m'   , 'reduced_sfc'   , group_lon_lat_time_height10m)
  # grid_ref probably incorrect for several of this mixed group:
  write_field_group_to_xml_file(oifs_cmip7_xml_file, 'oifs_cmip7_other'                    , 'reduced_sfc'   , group_other                 )

  write_xml_file_closing(oifs_cmip7_xml_file)



  # Lists with messages for combined printing per message cathegory afterwards:
  message_list_of_ifs_shortname_matches   = []
  message_list_of_no_match_ifs            = []
  message_list_of_no_match_tm5            = []
  message_list_of_no_match_lpjg           = []
  message_list_of_no_match_nemo           = []
  message_list_of_no_match_else_atmos     = []
  message_list_of_no_match_else_atmosChem = []
  message_list_of_no_match_else_aerosol   = []
  message_list_of_no_match_else           = []

  # Iterate over all the CMIP7 variables:
  xpath_expression_cmip7_request = './/variable'
  for cmip7_element in root_cmip7_request.findall(xpath_expression_cmip7_request):
   # Iterate over all the fields in the field_def file, but only select the match when the field id in the field_def
   # equals the ifs_shortname in the CMIP7 request file:
   xpath_expression_field_def = './/field[@id="'+cmip7_element.get('ifs_shortname')+'"]'
   for field_def_element in root_ecearth_field_def_inherited_nf.findall(xpath_expression_field_def):
    # This part concerns the oifs variables which are already in the existing oifs field_def file in the ECE4 repo:
    # Composing the message list just for the output messaging:
    message_head = 'An ifs_shortname match with ' + '{:6}'.format(cmip7_element.get('ifs_shortname'      )) + ' for:'
    add_message(message_head, message_list_of_ifs_shortname_matches, cmip7_element)
   else: # for-else
    message_head = 'No match for:'
    if   cmip7_element.get('model_component') == 'ifs':
     # This part concerns the oifs variables which are not in the existing oifs field_def file in the ECE4 repo:
     add_message(message_head, message_list_of_no_match_ifs , cmip7_element)
    elif cmip7_element.get('model_component') == 'tm5':
     # This part concerns the TM7 oifs variables which are not in the existing oifs field_def file in the ECE4 repo:
     add_message(message_head, message_list_of_no_match_tm5 , cmip7_element)
    elif cmip7_element.get('model_component') == 'lpjg':            # add other better check
     message_head = 'LPJG variable:'
     add_message(message_head, message_list_of_no_match_lpjg, cmip7_element)
    elif cmip7_element.get('model_component') == 'nemo':            # add other better check
     message_head = 'NEMO variable:'
     add_message(message_head, message_list_of_no_match_nemo, cmip7_element)
    else:
     if cmip7_element.get('modeling_realm') == 'atmos':
       add_message(message_head,  message_list_of_no_match_else_atmos    , cmip7_element)
     if cmip7_element.get('modeling_realm') == 'atmosChem':
       add_message(message_head,  message_list_of_no_match_else_atmosChem, cmip7_element)
     if cmip7_element.get('modeling_realm') == 'aerosol':
       add_message(message_head,  message_list_of_no_match_else_aerosol, cmip7_element)
     else:
       add_message(message_head, message_list_of_no_match_else, cmip7_element)

  if verbose:
   print_message_list(message_list_of_ifs_shortname_matches  )
   print_message_list(message_list_of_no_match_ifs           )
   print_message_list(message_list_of_no_match_tm5           )
   print_message_list(message_list_of_no_match_else_atmos    )
   print_message_list(message_list_of_no_match_else_atmosChem)
   print_message_list(message_list_of_no_match_else_aerosol  )
   print_message_list(message_list_of_no_match_lpjg          )
   print_message_list(message_list_of_no_match_nemo          )
   print_message_list(message_list_of_no_match_else          )

  print(' Number of ifs_shortname matches in the ECE field_def file: {}\n'.format(len(message_list_of_ifs_shortname_matches)))

  print(' No ifs_shortname match in the ECE field_def file for:\n  case       number\n   {:10} {}\n   {:10} {}\n   {:10} {}\n   {:10} {}\n   {:10} {}\n   {:10} {}\n   {:10} {}\n   {:10} {}'
         .format('IFS'      , len(message_list_of_no_match_ifs           ), \
                 'TM5'      , len(message_list_of_no_match_tm5           ), \
                 'atmos'    , len(message_list_of_no_match_else_atmos    ), \
                 'atmosChem', len(message_list_of_no_match_else_atmosChem), \
                 'aerosol'  , len(message_list_of_no_match_else_aerosol  ), \
                 'LPJG'     , len(message_list_of_no_match_lpjg          ), \
                 'NMEO'     , len(message_list_of_no_match_nemo          ), \
                 'else'     , len(message_list_of_no_match_else)           ))


# inherit before: unit, freq_offset, grid_ref;  add: id, text


# From the basic flat ece4 file_def file, giving an idea which attributes were explicitly taken to the file_def file
#   <file id="file8" name_suffix="_opa_grid_T_2D" output_freq="3h">

#    <field id="id_3h_tos"                                      # id_<cmip6 var name>_<cmip6 table name>
#           name="tos"                                          # <cmip6 var name>
#           table="3hr"                                         # <cmip6 table name>
#           field_ref="sst_pot"
#           grid_ref="grid_T_2D"
#           unit="degC"
#           enabled="False"
#           operation="instant"
#           freq_op="3h"   >                                                                        </field>

#   </file>

  print_next_step_message(2, 'FINISHING')
  print(' The script\n  {:}\n has finished, the generated file is:\n  {}\n'.format(' '.join(sys.argv), oifs_cmip7_field_def_file_name))

if __name__ == '__main__':
    main()
