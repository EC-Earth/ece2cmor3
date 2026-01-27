#!/usr/bin/env python
"""
Command line interface for retrieving simple variable lists from the data request.
Return a list per specified experiment of CMIP7 compound variables including the mapping to the CMIP6 table - var combination

This script is based on the script: CMIP7_DReq_Software/data_request_api/data_request_api/command_line/export_dreq_lists_json.py
"""

import sys
import os
import argparse
import xml.etree.ElementTree as ET


use_dreq_version = 'v1.2.2.3' # Actually this should be read from the xml file attribute in the root element cmip7_variables


def parse_args():
    """
    Parse command-line arguments
    """
    parser = argparse.ArgumentParser(
        description='Identify the CMIP7 ECE4 requested variables with help of the ECE3 - CMIP6 identification.'
    )

    # Optional input arguments
    parser.add_argument('-a', '--addallattributes'  , action='store_true' , default=False      , help='Add all the attributes with which all the metadata is included')
    return parser.parse_args()


def write_xml_file_root_element_opening(xml_file, dr_version, api_version, applied_order):
     xml_file.write('<cmip7_variables dr_version="{}" api_version="{}" applied_order_sequence="{}">\n'.format(use_dreq_version, api_version, applied_order))


def write_xml_file_root_element_closing(xml_file):
    xml_file.write('</cmip7_variables>\n')


def reorder_xml_file(xml_loading_filename, selected_attribute, list_of_attribute_values, add_all_attributes, xml_out=None):
    extension                = '.xml'
    replacing_extension      = '-' + selected_attribute + '-ordered' + extension
    if xml_out == None:
     xml_created_filename    = xml_loading_filename.replace(extension, replacing_extension)
    else:
     xml_created_filename    = xml_out
    tree = ET.parse(xml_loading_filename)
    root = tree.getroot()
    print('\n For {}:'.format(xml_created_filename))
    with open(xml_created_filename, 'w') as xml_file:
     sequence_label = root.attrib['applied_order_sequence'] + ', ' + selected_attribute
     write_xml_file_root_element_opening(xml_file, root.attrib['dr_version'], root.attrib['api_version'], sequence_label)
     for attribute_value in list_of_attribute_values:
      count = 0
      xpath_expression = './/variable[@' + selected_attribute + '="' + attribute_value + '"]'
      for element in root.findall(xpath_expression):
       write_xml_file_line_for_variable(xml_file, element)
       count += 1
      print(' {:4} variables with {:20} {}'.format(count, selected_attribute, attribute_value))
     write_xml_file_root_element_closing(xml_file)


def write_xml_file_line_for_variable(xml_file, element):
    add_all_attributes = True
    if add_all_attributes:
     xml_file.write('  <variable  cmip7_compound_name={:55}' \
                                ' priority={:10}' \
                                ' status={:20}' \
                                ' model_component={:10}' \
                                ' other_component={:8}' \
                                ' ifs_shortname={:13}' \
                                ' varname_code={:20}' \
                                ' expression={:83}' \
                                ' frequency={:7}' \
                                ' region={:12}' \
                                ' cmip6_table={:14}' \
                                ' physical_parameter_name={:28}' \
                                ' units={:20}' \
                                ' dimensions={:45}' \
                                ' long_name={:132}' \
                                ' standard_name={:160}' \
                                ' modeling_realm={:33}' \
                                ' branded_variable_name={:44}' \
                                ' branding_label={:25}' \
                                ' cmip6_compound_name={:40}' \
                                ' temporal_shape={:25}' \
                                ' spatial_shape={:15}' \
                                ' cell_measures={:35}' \
                                ' cell_methods={:140}' \
                                ' out_name={:28}' \
                                ' type={:10}' \
                    ' >   </variable>\n'.format( \
                    '"' + element.get('cmip7_compound_name'    )                                          + '"', \
                    '"' + element.get('priority'               )                                          + '"', \
                    '"' + element.get('status'                 )                                          + '"', \
                    '"' + element.get('model_component'        )                                          + '"', \
                    '"' + element.get('other_component'        )                                          + '"', \
                    '"' + element.get('ifs_shortname'          )                                          + '"', \
                    '"' + element.get('varname_code'           )                                          + '"', \
                    '"' + element.get('expression'             ).replace('&','&amp;').replace('<','&lt;') + '"', \
                    '"' + element.get('frequency'              )                                          + '"', \
                    '"' + element.get('region'                 )                                          + '"', \
                    '"' + element.get('cmip6_table'            )                                          + '"', \
                    '"' + element.get('physical_parameter_name')                                          + '"', \
                    '"' + element.get('units'                  )                                          + '"', \
                    '"' + element.get('dimensions'             )                                          + '"', \
                    '"' + element.get('long_name'              )                                          + '"', \
                    '"' + element.get('standard_name'          )                                          + '"', \
                    '"' + element.get('modeling_realm'         )                                          + '"', \
                    '"' + element.get('branded_variable_name'  )                                          + '"', \
                    '"' + element.get('branding_label'         )                                          + '"', \
                    '"' + element.get('cmip6_compound_name'    )                                          + '"', \
                    '"' + element.get('temporal_shape'         )                                          + '"', \
                    '"' + element.get('spatial_shape'          )                                          + '"', \
                    '"' + element.get('cell_measures'          )                                          + '"', \
                    '"' + element.get('cell_methods'           )                                          + '"', \
                    '"' + element.get('out_name'               )                                          + '"', \
                    '"' + element.get('type'                   )                                          + '"') \
                   )
    else:
     xml_file.write('  <variable  cmip7_compound_name={:55}' \
                                ' priority={:10}' \
                                ' region={:12}' \
                                ' cmip6_table={:14}' \
                                ' physical_parameter_name={:28}' \
                                ' long_name={:132}>' \
                    '  </variable>\n'.format( \
                    '"' + element.get('cmip7_compound_name'    ) + '"', \
                    '"' + element.get('priority'               ) + '"', \
                    '"' + element.get('region'                 ) + '"', \
                    '"' + element.get('cmip6_table'            ) + '"', \
                    '"' + element.get('physical_parameter_name') + '"', \
                    '"' + element.get('long_name'              ) + '"') \
                   )
    return


def print_var_info_plus_ece3_info(element, element_ece3):
    info_string = '{:55} {:10} {:15} {:10} {:14} {:28} {}({})'.format(element.get('cmip7_compound_name'    ), \
                                                                      element.get('priority'               ), \
                                                                      element.get('frequency'              ), \
                                                                      element.get('region'                 ), \
                                                                      element.get('cmip6_table'            ), \
                                                                      element.get('physical_parameter_name'), \
                                                                      element_ece3.get('model_component'   ), \
                                                                      element_ece3.get('other_component'   ))
    info_string = info_string.replace('(None)', '')
    # Apply preferences: When lpjg output available use that one instead of the ifs output. Needs a decesion. Here concerning the variables: snw, snd, snc, mrfso, tsl, mrsol, mrso, mrros, mrro, evspsbl
   #info_string = info_string.replace('ifs(lpjg)', 'lpjg')      # Needs a decesion, see comment above
    info_string = info_string.replace('ifs(tm5)', 'ifs(m7)')
    # Note for no3: tm5(tm5) which looks strange.
    info_string = info_string.replace('tm5(tm5)', 'nemo(tm5)')  # Adhoc fix (ocnBgchem variable)
    return info_string


def print_message_list(message_list):
 for message in message_list:
  print(message)
 print()


def print_message_list_reorder(message_list):
 # Order the message list on model_component (and preference info).
 # Note another approach could be to write the XML attribute info per variable (each variable one line), so based on that one can select in a more standard way.
 message_list_ifs_m7   = []
 message_list_ifs_lpjg = []
 message_list_ifs      = []
 message_list_nemo     = []
 message_list_lpjg     = []
 message_list_other    = []
 for message in message_list:
  if   'ifs(m7)'   in message.split()[-1]: message_list_ifs_m7  .append(message)
  elif 'ifs(lpjg)' in message.split()[-1]: message_list_ifs_lpjg.append(message)
  elif 'ifs'       in message.split()[-1]: message_list_ifs     .append(message)
  elif 'nemo'      in message.split()[-1]: message_list_nemo    .append(message)
  elif 'lpjg'      in message.split()[-1]: message_list_lpjg    .append(message)
  else                                   : message_list_other   .append(message)
 print_message_list(message_list_ifs_m7  )
 print_message_list(message_list_ifs_lpjg)
 print_message_list(message_list_ifs     )
 print_message_list(message_list_nemo    )
 print_message_list(message_list_lpjg    )
 print_message_list(message_list_other   )
 print()


def print_var_info(element):
    info_string = '{:55} {:10} {:15} {:10} {:14} {}'.format(element.get('cmip7_compound_name'    ), \
                                                            element.get('priority'               ), \
                                                            element.get('frequency'              ), \
                                                            element.get('region'                 ), \
                                                            element.get('cmip6_table'            ), \
                                                            element.get('physical_parameter_name'))
    return info_string


def print_var_info_xml(element):
    info_string = '<variable  cmip7_compound_name={:55} priority={:10} frequency={:15} region={:12} cmip6_table={:14} physical_parameter_name={:28} long_name={:122}>   </variable>'.format( \
     '"' + element.get('cmip7_compound_name'    ) + '"', \
     '"' + element.get('priority'               ) + '"', \
     '"' + element.get('frequency'              ) + '"', \
     '"' + element.get('region'                 ) + '"', \
     '"' + element.get('cmip6_table'            ) + '"', \
     '"' + element.get('physical_parameter_name') + '"', \
     '"' + element.get('long_name'              ) + '"')
    return info_string


def main():

    args = parse_args()

    add_all_attributes = args.addallattributes

    # Lists with messages for combined printing per message cathegory afterwards:
    message_list_of_identified_variables                          = []
    message_list_of_no_matched_identification                     = []

    # Lists which contains only variables (so with set & sorted unique ordered variable lists can be generated):
    list_of_identified_variables                                  = []
    list_of_no_matched_identification                             = []


    # Read & load the request-overview ECE3-CMIP6 identification:
    request_overview_xml_filename = 'request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml'
    tree_request_overview = ET.parse(request_overview_xml_filename)
    root_request_overview = tree_request_overview.getroot()

    # Predefine the three possible status values:
    identified     = 'identified'
    identified_var = 'var_identified'
    unidentified   = 'unidentified'

    xml_filename_alphabetic_ordered  = 'cmip7-request-{}-all-alphabetic-ordered.xml'.format(use_dreq_version)
    xml_filename_realm_ordered       = 'cmip7-request-{}-all-realm-ordered-identification.xml'.format(use_dreq_version)
    xml_filename_priority_ordered    = xml_filename_realm_ordered.replace('realm', 'priority')
    xml_filename_frequency_ordered   = xml_filename_realm_ordered.replace('realm', 'frequency')
    xml_filename_status_ordered      = xml_filename_realm_ordered.replace('realm', 'status')
    xml_filename_cmip6_table_ordered = xml_filename_realm_ordered.replace('realm', 'cmip6-table')
    xml_filename_identified          = xml_filename_realm_ordered.replace("realm-ordered-identification", identified    )
    xml_filename_identified_var      = xml_filename_realm_ordered.replace("realm-ordered-identification", identified_var)
    xml_filename_unidentified        = xml_filename_realm_ordered.replace("realm-ordered-identification", unidentified  )

    xml_filename_identified_mc       = xml_filename_identified.replace(identified, identified + "-mc"     )
    xml_filename_identified_mc_prio  = xml_filename_identified.replace(identified, identified + "-mc-prio")
    xml_filename_identified_prio     = xml_filename_identified.replace(identified, identified + "-prio"   )


    # Load the alphabetic ordered XML file and create a (primary) realm ordered (starting with atmos) XML file:
    print()
    tree_alphabetic = ET.parse(xml_filename_alphabetic_ordered)
    root_alphabetic = tree_alphabetic.getroot()
    with open(xml_filename_realm_ordered, 'w') as xml_file:
     write_xml_file_root_element_opening(xml_file, root_alphabetic.attrib['dr_version'], \
                                                   root_alphabetic.attrib['api_version'], \
                                                   root_alphabetic.attrib['applied_order_sequence'] + ', realm')
     for realm in ["atmos.", "atmosChem.", "aerosol.", "land.", "landIce.", "ocean.", "ocnBgchem.", "seaIce."]:
      count = 0
      xpath_expression = './/variable[@cmip7_compound_name]'
      for element in root_alphabetic.findall(xpath_expression):
       if realm in element.get('cmip7_compound_name'):

        var_info     = print_var_info    (element)
        var_info_xml = print_var_info_xml(element)

        count_in_req_overview = 0
        count_var_match_but_not_full_match = 0
        xpath_expression_cmip6_overview = './/variable[@cmip6_variable="' + element.get('physical_parameter_name') + '"]'
        for ece3_element in root_request_overview.findall(xpath_expression_cmip6_overview):
         var_info_plus_ece3_info = print_var_info_plus_ece3_info(element, ece3_element)

         count_in_req_overview += 1
         if element.get('physical_parameter_name') == ece3_element.get('cmip6_variable'):
          if ece3_element.get('cmip6_table') == element.get('cmip6_table') and ece3_element.get('region') == element.get('region'):
          #print(' {:2}    match for: {}'.format(count_in_req_overview, var_info_plus_ece3_info))
           list_of_identified_variables.append(element.get('physical_parameter_name'))
           message_list_of_identified_variables.append(' Match for: {}'.format(var_info_plus_ece3_info))
           element.set('status', identified)
           element.set('model_component', ece3_element.get('model_component'))
           element.set('other_component', ece3_element.get('other_component'))
           element.set('ifs_shortname'  , ece3_element.get('ifs_shortname'  ))
           element.set('varname_code'   , ece3_element.get('varname_code'   ))
           if len(ece3_element.get('expression')) > 83:
            element.set('expression'     , 'See the ' + request_overview_xml_filename + ' file.')
           else:
            element.set('expression'     , ece3_element.get('expression'))
          else:
           pass
           count_var_match_but_not_full_match += 1
          #print(' {:2} no match for: {}'.format(count_in_req_overview, var_info_plus_ece3_info))
         else:
          print('ERROR 01')
        else:
         # The for-else:
         if count_in_req_overview == 0:
          list_of_no_matched_identification.append(element.get('physical_parameter_name'))
          message_list_of_no_matched_identification.append(' {}'.format(var_info_xml))
          element.set('status', unidentified)
          element.set('model_component', '??')
          element.set('other_component', '??')
          element.set('ifs_shortname'  , '??')
          element.set('varname_code'   , '??')
          element.set('expression'     , '??')
         if count_var_match_but_not_full_match != 0:
          if element.get('status') != identified:
           element.set('status', identified_var)
           element.set('model_component', ece3_element.get('model_component'))
           element.set('other_component', ece3_element.get('other_component'))
           element.set('ifs_shortname'  , ece3_element.get('ifs_shortname'  ))
           element.set('varname_code'   , ece3_element.get('varname_code'   ))
           if len(ece3_element.get('expression')) > 83:
            element.set('expression'     , 'See the ' + request_overview_xml_filename + ' file.')
           else:
            element.set('expression'     , ece3_element.get('expression').replace('&','&amp;').replace('<','&lt;'))
          #print(' Non full match: {}'.format(print_var_info(element)))


        write_xml_file_line_for_variable(xml_file, element)
        count += 1
      print(' {:4} variables with realm {}'.format(count, realm))
     write_xml_file_root_element_closing(xml_file)


    # Load the realm ordered XML file and create the priority ordered XML file:
    reorder_xml_file(xml_filename_realm_ordered, 'priority', ["Core", "High", "Medium", "Low"], add_all_attributes, xml_filename_priority_ordered)


    # The realm ordered XML file has been loaded before, write three different XML files per identification status:
    print()
    tree_realm = ET.parse(xml_filename_realm_ordered)
    root_realm = tree_realm.getroot()
    for status in [identified, identified_var, unidentified]:
     with open(xml_filename_realm_ordered.replace("realm-ordered-identification", status), 'w') as xml_file:
      write_xml_file_root_element_opening(xml_file, root_realm.attrib['dr_version'], \
                                                    root_realm.attrib['api_version'], \
                                                    root_realm.attrib['applied_order_sequence'] + ', ' + status)
      count = 0
      xpath_expression = './/variable[@status="' + status + '"]'
      for element in root_realm.findall(xpath_expression):
       write_xml_file_line_for_variable(xml_file, element)
       count += 1
      print(' The file for {:14} contains {:4} variables.'.format(status, count))
      write_xml_file_root_element_closing(xml_file)


    # Load the identified realm ordered XML file and create the identified model_component ordered XML file:
    reorder_xml_file(xml_filename_identified, 'model_component', ["ifs", "tm5", "nemo", "lpjg", "co2box"], add_all_attributes, xml_filename_identified_mc)

    # Load the identified model_component ordered XML file and create the identified priority ordered XML file:
    reorder_xml_file(xml_filename_identified_mc, 'priority'    , ["Core", "High", "Medium", "Low"]       , add_all_attributes, xml_filename_identified_mc_prio)

    # Load the realm ordered XML file and create the priority ordered XML file:
    reorder_xml_file(xml_filename_identified, 'priority'       , ["Core", "High", "Medium", "Low"]       , add_all_attributes, xml_filename_identified_prio)


    # Thereafter order on:
    #  model_coponent (or realm for the unidentified case)
    #  priority
    #  frequency

    # print(xml_filename_identified)
    # print(xml_filename_identified_var)
    # print(xml_filename_unidentified)

    # For the "identified" and the "var identified ones":
    #  Check the CMIP7 units (used here) with the CMIP6 units: To be implemented




    # Load the priority ordered XML file and create the frequency ordered XML file:
    print()
    tree_priority = ET.parse(xml_filename_priority_ordered)
    root_priority = tree_priority.getroot()
    with open(xml_filename_frequency_ordered, 'w') as xml_file:
     write_xml_file_root_element_opening(xml_file, root_priority.attrib['dr_version'], \
                                                   root_priority.attrib['api_version'], \
                                                   root_priority.attrib['applied_order_sequence'] + ', frequency')
     for frequency in [".fx.", ".3hr.", ".6hr.", ".day.", ".mon.", ".yr.", ".subhr.", ".1hr.", ".dec."]:
      count = 0
      xpath_expression = './/variable[@cmip7_compound_name]'
      for element in root_priority.findall(xpath_expression):
       if frequency in element.get('cmip7_compound_name'):
        write_xml_file_line_for_variable(xml_file, element)
        count += 1
     #print(' {:4} variables with frequency {}'.format(count, frequency))
     write_xml_file_root_element_closing(xml_file)


    # Load the frequency ordered XML file and create the status ordered XML file:
    reorder_xml_file(xml_filename_frequency_ordered, 'status' , [identified, identified_var, unidentified], add_all_attributes, xml_filename_status_ordered)


    # The realm ordered XML file has been loaded before, create the cmip6-table ordered XML file:
    print()
    with open(xml_filename_cmip6_table_ordered, 'w') as xml_file:
     write_xml_file_root_element_opening(xml_file, root_realm.attrib['dr_version'], \
                                                   root_realm.attrib['api_version'], \
                                                   root_realm.attrib['applied_order_sequence'] + ', cmip6_table')
     for cmip6_table in ["fx", "Efx", "AERfx", "Ofx", "IfxAnt", "IfxGre", \
                       "3hr", "E3hr", "CF3hr", "3hrPt", "E3hrPt", "6hrPlev", "6hrPlevPt", "6hrLev", \
                       "day", "Eday", "EdayZ", "AERday", "CFday", "Oday", "SIday", \
                       "Amon", "Emon", "EmonZ", "CFmon", "AERmon", "AERmonZ", "Lmon", "LImon", "Omon", "SImon", "ImonAnt", "ImonGre", \
                       "Eyr", "Oyr", "IyrAnt", "IyrGre", \
                       "CFsubhr", "Esubhr", "E1hr", "E1hrClimMon", "AERhr", \
                       "Odec"]:
      count = 0
      xpath_expression = './/variable[@cmip6_table="' + cmip6_table + '"]'
      for element in root_realm.findall(xpath_expression):
       write_xml_file_line_for_variable(xml_file, element)
       count += 1
     #print(' {:4} variables with cmip6_table {}'.format(count, cmip6_table))
     write_xml_file_root_element_closing(xml_file)


     #cmip7_compound_name="no-cmip7-equivalent-var-.*"
     xpath_expression_cmip6_overview = './/variable[@cmip7_compound_name]'
     count = 0
     for ece3_element in root_request_overview.findall(xpath_expression_cmip6_overview):
      if 'no-cmip7-equivalent-var-' in ece3_element.get('cmip7_compound_name'):
       count += 1
       # An XML file for this has been easily compose with a grep, see: xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7*.xml
      #print(' No CMIP7 match for: {}'.format(ece3_element.get('cmip7_compound_name')))
     print(' There are {:3} variables which are identified within the ECE3 - CMIP6 framework but which are not requested by CMIP7.'.format(count))
     print()

    print_message_list_reorder(message_list_of_identified_variables)


if __name__ == '__main__':
    main()
