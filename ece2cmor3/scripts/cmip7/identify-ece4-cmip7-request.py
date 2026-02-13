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
     xml_file.write('<cmip7_variables dr_version="{}" api_version="{}" applied_order_sequence="{}">\n'.format(dr_version, api_version, applied_order))


def write_xml_file_root_element_closing(xml_file):
    xml_file.write('</cmip7_variables>\n')


def reorder_xml_file(xml_loading_filename, selected_attribute, list_of_attribute_values, add_all_attributes, xml_out=None, label=None):
    extension                = '.xml'
    replacing_extension      = '-' + selected_attribute + '-ordered' + extension
    if xml_out == None:
     xml_created_filename    = xml_loading_filename.replace(extension, replacing_extension)
    else:
     xml_created_filename    = xml_out
    if label == None:
     order_label             = selected_attribute
    else:
     order_label             = label
    tree = ET.parse(xml_loading_filename)
    root = tree.getroot()
    print('\n For {}:'.format(xml_created_filename))
    with open(xml_created_filename, 'w') as xml_file:
     write_xml_file_root_element_opening(xml_file, root.attrib['dr_version'], \
                                                   root.attrib['api_version'], \
                                                   root.attrib['applied_order_sequence'] + ', ' + order_label)
     for attribute_value in list_of_attribute_values:
      count = 0
      xpath_expression = './/variable[@' + selected_attribute + '="' + attribute_value + '"]'
      for element in root.findall(xpath_expression):
       write_xml_file_line_for_variable(xml_file, element)
       count += 1
      print(' {:4} variables with {:20} {}'.format(count, selected_attribute, attribute_value))
     write_xml_file_root_element_closing(xml_file)


def reorder_xml_file_2(xml_loading_filename, selected_attribute, list_of_attribute_values, add_all_attributes, xml_out=None, label=None):
    extension                = '.xml'
    replacing_extension      = '-' + selected_attribute + '-ordered' + extension
    if xml_out == None:
     xml_created_filename    = xml_loading_filename.replace(extension, replacing_extension)
    else:
     xml_created_filename    = xml_out
    if label == None:
     order_label             = selected_attribute
    else:
     order_label             = label
    tree = ET.parse(xml_loading_filename)
    root = tree.getroot()
    print('\n For {}:'.format(xml_created_filename))
    with open(xml_created_filename, 'w') as xml_file:
     write_xml_file_root_element_opening(xml_file, root.attrib['dr_version'], \
                                                   root.attrib['api_version'], \
                                                   root.attrib['applied_order_sequence'] + ', ' + order_label)
     for attribute_value in list_of_attribute_values:
      count = 0
      xpath_expression = './/variable[@' + selected_attribute + ']'
      for element in root.findall(xpath_expression):
       if attribute_value in element.get(selected_attribute):
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
                                ' comment_author={:20}' \
                                ' comment={:75}' \
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
                    '"' + element.get('comment_author'         )                                          + '"', \
                    '"' + element.get('comment'                )                                          + '"', \
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

    # Predefine the three possible status values:
    identified     = 'identified'
    identified_var = 'var_identified'
    unidentified   = 'unidentified'

    # Lists with messages for combined printing per message cathegory afterwards:
    message_list_of_identified_variables                          = []
    message_list_of_no_matched_identification                     = []

    # Lists which contains only variables (so with set & sorted unique ordered variable lists can be generated):
    list_of_identified_variables                                  = []
    list_of_no_matched_identification                             = []

    # The CMIP7 request file:
    xml_filename_alphabetic_ordered  = 'cmip7-request-v1.2.2.3-all-alphabetic-ordered.xml'

    # Read & load the request-overview ECE3-CMIP6 identification:
    request_overview_xml_filename = 'request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml'
    tree_request_overview = ET.parse(request_overview_xml_filename)
    root_request_overview = tree_request_overview.getroot()

    # Load the alphabetic ordered XML file and create a (primary) realm ordered (starting with atmos) XML file:
    tree_alphabetic = ET.parse(xml_filename_alphabetic_ordered)
    root_alphabetic = tree_alphabetic.getroot()
    dr_version      = root_alphabetic.attrib['dr_version']

    include_additional_xml_output = False

    xml_filename_realm_ordered                = 'cmip7-request-{}-all-full-realm.xml'.format(dr_version)
    xml_filename_priority_ordered             = xml_filename_realm_ordered.replace ('realm', 'priority'    )
    xml_filename_frequency_ordered            = xml_filename_realm_ordered.replace ('realm', 'frequency'   )
    xml_filename_status_ordered               = xml_filename_realm_ordered.replace ('realm', 'status'      )
    xml_filename_cmip6_table_ordered          = xml_filename_realm_ordered.replace ('realm', 'cmip6-table' )
    xml_filename_identified                   = xml_filename_realm_ordered.replace ("realm", identified    )
    xml_filename_identified_var               = xml_filename_realm_ordered.replace ("realm", identified_var)
    xml_filename_unidentified                 = xml_filename_realm_ordered.replace ("realm", unidentified  )

    xml_filename_identified_freq              = xml_filename_identified.replace    (identified    , identified     + "-freq"        )
    xml_filename_identified_freq_mc           = xml_filename_identified.replace    (identified    , identified     + "-freq-mc"     )
    xml_filename_identified_freq_mc_prio      = xml_filename_identified.replace    (identified    , identified     + "-freq-mc-prio")
    xml_filename_identified_var_freq          = xml_filename_identified_var.replace(identified_var, identified_var + "-freq"        )
    xml_filename_identified_var_freq_mc       = xml_filename_identified_var.replace(identified_var, identified_var + "-freq-mc"     )
    xml_filename_identified_var_freq_mc_prio  = xml_filename_identified_var.replace(identified_var, identified_var + "-freq-mc-prio")
    xml_filename_unidentified_freq            = xml_filename_unidentified.replace  (unidentified  , unidentified   + "-freq"           )
    xml_filename_unidentified_freq_realm      = xml_filename_unidentified.replace  (unidentified  , unidentified   + "-freq-realm"     )
    xml_filename_unidentified_freq_realm_prio = xml_filename_unidentified.replace  (unidentified  , unidentified   + "-freq-realm-prio")

    if include_additional_xml_output:
     xml_filename_identified_mc               = xml_filename_identified.replace    (identified    , identified     + "-mc"     )
     xml_filename_identified_mc_prio          = xml_filename_identified.replace    (identified    , identified     + "-mc-prio")
     xml_filename_identified_prio             = xml_filename_identified.replace    (identified    , identified     + "-prio"   )
     xml_filename_identified_var_mc           = xml_filename_identified_var.replace(identified_var, identified_var + "-mc"     )
     xml_filename_identified_var_mc_prio      = xml_filename_identified_var.replace(identified_var, identified_var + "-mc-prio")
     xml_filename_identified_var_prio         = xml_filename_identified_var.replace(identified_var, identified_var + "-prio"   )
     xml_filename_unidentified_realm          = xml_filename_unidentified.replace  (unidentified  , unidentified   + "-realm"     )
     xml_filename_unidentified_realm_prio     = xml_filename_unidentified.replace  (unidentified  , unidentified   + "-realm-prio")
     xml_filename_unidentified_prio           = xml_filename_unidentified.replace  (unidentified  , unidentified   + "-prio"      )

    print()
    with open(xml_filename_realm_ordered, 'w') as xml_file:
     write_xml_file_root_element_opening(xml_file, root_alphabetic.attrib['dr_version'], \
                                                   root_alphabetic.attrib['api_version'], \
                                                   root_alphabetic.attrib['applied_order_sequence'] + ', realm')
     for realm in ["atmos.", "atmosChem.", "aerosol.", "land.", "landIce.", "ocean.", "ocnBgchem.", "seaIce."]:
      count = 0
      xpath_expression = './/variable[@cmip7_compound_name]'
      for element in root_alphabetic.findall(xpath_expression):
       if realm in element.get('cmip7_compound_name'):

       #var_info     = print_var_info    (element)
        var_info_xml = print_var_info_xml(element)

        count_in_req_overview = 0
        xpath_expression_cmip6_overview = './/variable[@cmip6_variable="' + element.get('physical_parameter_name') + '"]'
        for ece3_element in root_request_overview.findall(xpath_expression_cmip6_overview):
         count_in_req_overview += 1
         var_info_plus_ece3_info = print_var_info_plus_ece3_info(element, ece3_element)
         element.set('model_component', ece3_element.get('model_component'))
         element.set('other_component', ece3_element.get('other_component'))
         element.set('ifs_shortname'  , ece3_element.get('ifs_shortname'  ))
         element.set('varname_code'   , ece3_element.get('varname_code'   ))
         if len(ece3_element.get('expression')) < 84:
          element.set('expression'    , ece3_element.get('expression'     ))
         else:
          element.set('expression'    , 'See the ' + request_overview_xml_filename + ' file.')

         if element.get('physical_parameter_name') == ece3_element.get('cmip6_variable'):
          if ece3_element.get('cmip6_table') == element.get('cmip6_table'):
           element.set('status', identified)
           message_list_of_identified_variables.append(' Match for: {}'.format(var_info_plus_ece3_info))
           list_of_identified_variables.append(element.get('physical_parameter_name'))
          #print(' {:2}    match for: {}'.format(count_in_req_overview, var_info_plus_ece3_info))
           # In case the full identification has been achieved break out the loop in order to prevent that afterwards the status will be overwritten by identified_var
           break
          else:
           element.set('status', identified_var)
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
        element.set('comment_author' , '                 ')
        element.set('comment'        , '                                                                        ')

        write_xml_file_line_for_variable(xml_file, element)
        count += 1
      print(' {:4} variables with realm {}'.format(count, realm))
     write_xml_file_root_element_closing(xml_file)


    value_list_with_priorities       = ["Core", "High", "Medium", "Low"]
    value_list_with_cmip6_tables     = ["fx", "Efx", "AERfx", "Ofx", "IfxAnt", "IfxGre", \
                                        "3hr", "E3hr", "CF3hr", "3hrPt", "E3hrPt", "6hrPlev", "6hrPlevPt", "6hrLev", \
                                        "day", "Eday", "EdayZ", "AERday", "CFday", "Oday", "SIday", \
                                        "Amon", "Emon", "EmonZ", "CFmon", "AERmon", "AERmonZ", "Lmon", "LImon", "Omon", "SImon", "ImonAnt", "ImonGre", \
                                        "Eyr", "Oyr", "IyrAnt", "IyrGre", \
                                        "CFsubhr", "Esubhr", "E1hr", "E1hrClimMon", "AERhr", \
                                        "Odec"]
    value_list_with_realms           = ["atmos.", "atmosChem.", "aerosol.", "land.", "landIce.", "ocean.", "ocnBgchem.", "seaIce."]
    value_list_with_model_components = ["ifs", "tm5", "nemo", "lpjg", "co2box"]
    value_list_with_status           = [identified, identified_var, unidentified]
    value_list_with_frequencies      = [".fx.", ".3hr.", ".6hr.", ".day.", ".mon.", ".yr.", ".subhr.", ".1hr.", ".dec."]


    # Load the realm ordered XML file and create the cmip6-table ordered XML file:
    reorder_xml_file(xml_filename_realm_ordered , 'cmip6_table'            , value_list_with_cmip6_tables    , add_all_attributes, xml_filename_cmip6_table_ordered)

    # Load the realm ordered XML file and create the priority ordered XML file:
    reorder_xml_file(xml_filename_realm_ordered , 'priority'               , value_list_with_priorities      , add_all_attributes, xml_filename_priority_ordered)

    # Load the priority ordered XML file and create the frequency ordered XML file:
    reorder_xml_file_2(xml_filename_priority_ordered, 'cmip7_compound_name' , value_list_with_frequencies    , add_all_attributes, xml_filename_frequency_ordered, label='frequency')

    # Load the frequency ordered XML file and create the status ordered XML file:
    reorder_xml_file(xml_filename_frequency_ordered , 'status'              , value_list_with_status         , add_all_attributes, xml_filename_status_ordered)

    # Load the realm ordered XML file and write three different XML files per identification status:
    for status in value_list_with_status:
     reorder_xml_file(xml_filename_realm_ordered, 'status'                 , [status]                        , add_all_attributes, xml_filename_realm_ordered.replace("realm", status), status)


    # 1. Load the identified                           ordered XML file and create the identified frequency                          ordered XML file.
    # 2. Load the identified frequency                 ordered XML file and create the identified frequency model_component          ordered XML file.
    # 3. Load the identified frequency model_component ordered XML file and create the identified frequency model_component priority ordered XML file.
    reorder_xml_file_2(xml_filename_identified        , 'cmip7_compound_name', value_list_with_frequencies     , add_all_attributes, xml_filename_identified_freq        , label='frequency')
    reorder_xml_file  (xml_filename_identified_freq   , 'model_component'    , value_list_with_model_components, add_all_attributes, xml_filename_identified_freq_mc     )
    reorder_xml_file  (xml_filename_identified_freq_mc, 'priority'           , value_list_with_priorities      , add_all_attributes, xml_filename_identified_freq_mc_prio)

    # 1. Load the identified_var                           ordered XML file and create the identified_var frequency                          ordered XML file.
    # 2. Load the identified_var frequency                 ordered XML file and create the identified_var frequency model_component          ordered XML file.
    # 3. Load the identified_var frequency model_component ordered XML file and create the identified_var frequency model_component priority ordered XML file.
    reorder_xml_file_2(xml_filename_identified_var        , 'cmip7_compound_name', value_list_with_frequencies     , add_all_attributes, xml_filename_identified_var_freq        , label='frequency')
    reorder_xml_file  (xml_filename_identified_var_freq   , 'model_component'    , value_list_with_model_components, add_all_attributes, xml_filename_identified_var_freq_mc     )
    reorder_xml_file  (xml_filename_identified_var_freq_mc, 'priority'           , value_list_with_priorities      , add_all_attributes, xml_filename_identified_var_freq_mc_prio)

    # 1. Load the unidentified                 ordered XML file and create the unidentified frequency                ordered XML file.
    # 2. Load the unidentified frequency       ordered XML file and create the unidentified frequency realm          ordered XML file.
    # 3. Load the unidentified frequency realm ordered XML file and create the unidentified frequency realm priority ordered XML file.
    reorder_xml_file_2(xml_filename_unidentified           , 'cmip7_compound_name', value_list_with_frequencies, add_all_attributes, xml_filename_unidentified_freq           , label='frequency')
    reorder_xml_file_2(xml_filename_unidentified_freq      , 'cmip7_compound_name', value_list_with_realms     , add_all_attributes, xml_filename_unidentified_freq_realm     , label='realm')
    reorder_xml_file  (xml_filename_unidentified_freq_realm, 'priority'           , value_list_with_priorities , add_all_attributes, xml_filename_unidentified_freq_realm_prio)


    if include_additional_xml_output:
     # 1. Load the identified                 ordered XML file and create the identified model_component          ordered XML file.
     # 2. Load the identified model_component ordered XML file and create the identified model_component priority ordered XML file.
     reorder_xml_file(xml_filename_identified        , 'model_component'    , value_list_with_model_components, add_all_attributes, xml_filename_identified_mc)
     reorder_xml_file(xml_filename_identified_mc     , 'priority'           , value_list_with_priorities      , add_all_attributes, xml_filename_identified_mc_prio)

     # 1. Load the identified ordered XML file and create the priority ordered XML file:
     reorder_xml_file(xml_filename_identified        , 'priority'           , value_list_with_priorities      , add_all_attributes, xml_filename_identified_prio)


     # 1. Load the identified_var                 ordered XML file and create the identified_var model_component          ordered XML file.
     # 2. Load the identified_var model_component ordered XML file and create the identified_var model_component priority ordered XML file.
     reorder_xml_file(xml_filename_identified_var    , 'model_component'    , value_list_with_model_components, add_all_attributes, xml_filename_identified_var_mc)
     reorder_xml_file(xml_filename_identified_var_mc , 'priority'           , value_list_with_priorities      , add_all_attributes, xml_filename_identified_var_mc_prio)

     # 1. Load the identified_var ordered XML file and create the priority ordered XML file.
     reorder_xml_file(xml_filename_identified_var    , 'priority'           , value_list_with_priorities      , add_all_attributes, xml_filename_identified_var_prio)


     # 1. Load the unidentified       ordered XML file and create the unidentified realm          ordered XML file.
     # 2. Load the unidentified realm ordered XML file and create the unidentified realm priority ordered XML file.
     reorder_xml_file_2(xml_filename_unidentified      , 'cmip7_compound_name', value_list_with_realms        , add_all_attributes, xml_filename_unidentified_realm, label='realm')
     reorder_xml_file  (xml_filename_unidentified_realm, 'priority'           , value_list_with_priorities    , add_all_attributes, xml_filename_unidentified_realm_prio)

     # 1. Load the unidentified ordered XML file and create the priority ordered XML file:
     reorder_xml_file(xml_filename_unidentified      , 'priority'           , value_list_with_priorities      , add_all_attributes, xml_filename_unidentified_prio)



    # For the "identified" and the "var identified ones":
    #  Check the CMIP7 units (used here) with the CMIP6 units: To be implemented


    # Loop over the ECE3 - CMIP6 identified variables which are not requested by CMIP7 (i.e. these variable - frequency combinations are not requested by CMIP7):
    xpath_expression_cmip6_overview = './/variable[@cmip7_compound_name]'
    count = 0
    for ece3_element in root_request_overview.findall(xpath_expression_cmip6_overview):
     if 'no-cmip7-equivalent-var-' in ece3_element.get('cmip7_compound_name'):
      count += 1
      # An XML file for this has been easily compose with a grep, see: xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7*.xml
     #print(' No CMIP7 match for: {}'.format(ece3_element.get('cmip7_compound_name')))
    print('\n There are {:3} variables which are identified within the ECE3 - CMIP6 framework but which are not requested by CMIP7.'.format(count))
    print()

    print_message_list_reorder(message_list_of_identified_variables)


if __name__ == '__main__':
    main()
