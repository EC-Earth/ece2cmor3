#!/usr/bin/env python
'''
Matching of all CMIP7 requested variables with the ECE3-CMIP6 identified ones:
 ./cmip7-variable-identification-with-help-of-ECE3-CMIP6.py -r
'''

import argparse
import xml.etree.ElementTree as ET
from importlib.metadata import version

PACKAGE_NAME = "CMIP7_data_request_api"
print(' The CMIP7 dreq python api version is: v{}'.format(version(PACKAGE_NAME)))

def parse_args():
    '''
    Parse command-line arguments
    '''
    # Positional (mandatory) input arguments
    parser = argparse.ArgumentParser(description='Mapping of CMIP6 to CMIP7 CMOR variables and optionally provide metadata.')
    return parser.parse_args()


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


# For the reverse check:
def print_ece3_info(element):
    info_string = '{:26} {:12} {:10} {:55} {}({})'.format(element.get('cmip6_variable'     ), \
                                                          element.get('cmip6_table'        ), \
                                                          element.get('region'             ), \
                                                          element.get('cmip7_compound_name'), \
                                                          element.get('model_component'    ), \
                                                          element.get('other_component'    ))
    info_string = info_string.replace('(None)', '')
    # Apply preferences: When lpjg output available use that one instead of the ifs output. Needs a decesion. Here concerning the variables: snw, snd, snc, mrfso, tsl, mrsol, mrso, mrros, mrro, evspsbl
   #info_string = info_string.replace('ifs(lpjg)', 'lpjg')      # Needs a decesion, see comment above
    info_string = info_string.replace('ifs(tm5)', 'ifs(m7)')
    # Note for no3: tm5(tm5) which looks strange.
    info_string = info_string.replace('tm5(tm5)', 'nemo(tm5)')  # Adhoc fix (ocnBgchem variable)
    return info_string


def main():

    args = parse_args()

    # Lists with messages for combined printing per message cathegory afterwards:
    message_list_of_identified_variables                          = []
    message_list_of_1hr_variables                                 = []
    message_list_of_subhr_variables                               = []
    message_list_of_antarctic_variables                           = []
    message_list_of_greenland_variables                           = []
    message_list_of_nh_variables                                  = []
    message_list_of_sh_variables                                  = []
    message_list_of_other_climatology_variables                   = []
    message_list_of_non_glb_variables                             = []
    message_list_of_no_matched_identification                     = []
    message_list_of_identification_matches_in_reverse_check       = []
    message_list_of_ece3_cmip6_identified_variables_not_in_cmip7  = []
    message_list2_of_ece3_cmip6_identified_variables_not_in_cmip7 = []

    # Lists which contains only variables (so with set & sorted unique ordered variable lists can be generated):
    list_of_identified_variables                                  = []
    list_of_identification_matches_in_reverse_check               = []
    list_of_ece3_cmip6_identified_variables_not_in_cmip7          = []
    list2_of_ece3_cmip6_identified_variables_not_in_cmip7         = []
    list_of_no_matched_identification                             = []


    # Load the xml file:
    cmip7_variables_xml_filename = 'cmip7-request-v1.2.2.3-all-frequency-ordered.xml'
    tree_cmip7_variables = ET.parse(cmip7_variables_xml_filename)
    root_cmip7_variables = tree_cmip7_variables.getroot()

    # Read & load the request-overview ECE3-CMIP6 identification:
    request_overview_xml_filename = 'request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml'
    tree_request_overview = ET.parse(request_overview_xml_filename)
    root_request_overview = tree_request_overview.getroot()


    xpath_expression_for_cmip7_request = './/variable'
    for cmip7_element in root_cmip7_variables.findall(xpath_expression_for_cmip7_request):
     var_info     = print_var_info    (cmip7_element)
     var_info_xml = print_var_info_xml(cmip7_element)

     if 'Ant' in cmip7_element.get('cmip6_table') and 'ata' not in cmip7_element.get('region'):
      print(' WARNING: Antarctic table determined but region not ata for: {}'.format(cmip7_element.get('cmip7_compound_name')))
     if 'Gre' in cmip7_element.get('cmip6_table') and 'grl' not in cmip7_element.get('region'):
      print(' WARNING: Greenland table determined but region not grl for: {}'.format(cmip7_element.get('cmip7_compound_name')))

     # The if & elif statements deselect cathegories of variables from the CMIP7 request (which are ignored for now) and creates for each cathegory a message list.
     # For the remaining variables in the else statement the CMIP7 requested variables are checked for a match with the ECE3-CMIP6 identified variables.
     if   '1hr'   in cmip7_element.get('cmip6_table')         : message_list_of_1hr_variables              .append(' 1HR          variable: {}'.format(var_info))
     elif 'subhr' in cmip7_element.get('cmip6_table')         : message_list_of_subhr_variables            .append(' SUBHR        variable: {}'.format(var_info))
     elif 'Ant'   in cmip7_element.get('cmip6_table')         : message_list_of_antarctic_variables        .append(' Antarctic    variable: {}'.format(var_info))
     elif 'Gre'   in cmip7_element.get('cmip6_table')         : message_list_of_greenland_variables        .append(' Greenland    variable: {}'.format(var_info))
     elif cmip7_element.get('region'        ) == 'nh'         : message_list_of_nh_variables               .append(' NH           variable: {}'.format(var_info))
     elif cmip7_element.get('region'        ) == 'sh'         : message_list_of_sh_variables               .append(' SH           variable: {}'.format(var_info))
     elif cmip7_element.get('region'        ) != 'glb'        : message_list_of_non_glb_variables          .append(' Non glb      variable: {}'.format(var_info))
     elif cmip7_element.get('temporal_shape') == "climatology": message_list_of_other_climatology_variables.append(' Climatology  variable: {}'.format(var_info))
     else:
     #print(' {}'.format(var_info))
      count = 0
      xpath_expression_cmip6_overview = './/variable[@cmip6_variable="' + cmip7_element.get('physical_parameter_name') + '"]'
      for ece3_element in root_request_overview.findall(xpath_expression_cmip6_overview):
       var_info_plus_ece3_info = print_var_info_plus_ece3_info(cmip7_element, ece3_element)

       count += 1
       if cmip7_element.get('physical_parameter_name') == ece3_element.get('cmip6_variable'):
        if ece3_element.get('cmip6_table') == cmip7_element.get('cmip6_table') and ece3_element.get('region') == cmip7_element.get('region'):
        #print(' {:2}    match for: {}'.format(count, var_info_plus_ece3_info))
         list_of_identified_variables.append(cmip7_element.get('physical_parameter_name'))
         message_list_of_identified_variables.append(' Match for: {}'.format(var_info_plus_ece3_info))
        else:
         pass
        #print(' {:2} no match for: {}'.format(count, var_info_plus_ece3_info))
       else:
        print('ERROR 01')
      else:
       # The for-else:
       if count == 0:
        list_of_no_matched_identification.append(cmip7_element.get('physical_parameter_name'))
       #message_list_of_no_matched_identification.append(' No identification for: {:105} long_name={}'.format(var_info, '"' + cmip7_element.get('long_name') + '"'))
        message_list_of_no_matched_identification.append(' {}'.format(var_info_xml))

    sorted_set_list_of_identified_variables      = sorted(set(list_of_identified_variables     ))
    sorted_set_list_of_no_matched_identification = sorted(set(list_of_no_matched_identification))
    print('\n The basic check gives:')
    print('  This CMIP7 data request contains {}        variables which are     identified in the ECE3 - CMIP6 framewordk (in this case pre-deselection of cathogories: 1hr, subhr, Ant, Gre, non-glb & climatology).'.format(len(list_of_identified_variables                )))
    print('  This CMIP7 data request contains {} unique variables which are     identified in the ECE3 - CMIP6 framewordk (in this case pre-deselection of cathogories: 1hr, subhr, Ant, Gre, non-glb & climatology).'.format(len(sorted_set_list_of_identified_variables     )))
    print('  This CMIP7 data request contains {}        variables which are not identified in the ECE3 - CMIP6 framewordk.'.format(len(list_of_no_matched_identification           )))
    print('  This CMIP7 data request contains {} unique variables which are not identified in the ECE3 - CMIP6 framewordk.'.format(len(sorted_set_list_of_no_matched_identification)))


    # The reverse case: investigate which ECE3-CMIP6 identified variables are not part of the CMIP7 request:
    count_matches = 0
    count_cmip6_identified_but_not_in_cmip7 = 0
    xpath_expression_cmip6_overview = './/variable'
    for ece3_element in root_request_overview.findall(xpath_expression_cmip6_overview):
     var_info = print_ece3_info(ece3_element)

     count = 0
     xpath_expression_cmip7_request = './/variable[@physical_parameter_name="' + ece3_element.get('cmip6_variable') + '"]'
     for cmip7_element in root_cmip7_variables.findall(xpath_expression_cmip7_request):
      if cmip7_element.get('physical_parameter_name') == ece3_element.get('cmip6_variable'):
       count += 1
       if ece3_element.get('cmip6_table') == cmip7_element.get('cmip6_table') and ece3_element.get('region') == cmip7_element.get('region'):
        list_of_identification_matches_in_reverse_check.append(cmip7_element.get('physical_parameter_name'))
        message_list_of_identification_matches_in_reverse_check.append(' Reverse check, identification match: {}'.format(var_info))
        count_matches += 1
      else:
       print('ERROR 02')
     else:
      # The for-else:
      if count == 0:
       count_cmip6_identified_but_not_in_cmip7 += 1
       list_of_ece3_cmip6_identified_variables_not_in_cmip7.append(ece3_element.get('cmip6_variable'))
       message_list_of_ece3_cmip6_identified_variables_not_in_cmip7.append(' Reverse check, not in CMIP7 request: {}'.format(var_info))
      else:
       if count_matches == 0:
        print(' Weird (not impossible but not expected (hopefully not the case).')  # Indeed, so far this is never the case.

    sorted_set_list_of_identification_matches_in_reverse_check      = sorted(set(list_of_identification_matches_in_reverse_check     ))
    sorted_set_list_of_ece3_cmip6_identified_variables_not_in_cmip7 = sorted(set(list_of_ece3_cmip6_identified_variables_not_in_cmip7))
    print('\n From the reverse check we have:')
    print('  A number of {} total  variables which do     match (i.e. they are both in the CMIP7 request and identified within the ECE3-CMIP6 framework)'.format(count_matches                                                       ))
    print('  A number of {} unique variables which do     match (i.e. they are both in the CMIP7 request and identified within the ECE3-CMIP6 framework)'.format(len(sorted_set_list_of_identification_matches_in_reverse_check     )))
    print('  A number of {} total  variables which do not match (these are ECE3-CMIP6 identified variables which are not in the CMIP7 request)'          .format(count_cmip6_identified_but_not_in_cmip7                             ))
    print('  A number of {} unique variables which do not match (these are ECE3-CMIP6 identified variables which are not in the CMIP7 request)'          .format(len(sorted_set_list_of_ece3_cmip6_identified_variables_not_in_cmip7)))
    print()

    '''
     See also:
      echo '<cmip6_variables>'                                                                         > list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
      grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
      echo '</cmip6_variables>'                                                                       >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
     Or the same but sorted per model component as described in the bash accompanying script.

     So there are 238 CMIP6 table - variable combinations which are not in the CMIP7 request, from which 101 CMIP6 variables are not at all in the CMIP7 request.
    '''

    # The difference in the method below (list2) is that certain table - variable combinations, also for a variable which is used in another table combination
    # which is requested by CMIP7, do pop up here. With that more variables pop up here, also in the unique list2.
    # Only variables with the attribute cmip7_compound_name="no-cmip7-equivalent-var-*" have region="None", therefore:
    xpath_expression_cmip6_overview = './/variable[@region="None"]'
    for ece3_element in root_request_overview.findall(xpath_expression_cmip6_overview):
     var_info = print_ece3_info(ece3_element)
     list2_of_ece3_cmip6_identified_variables_not_in_cmip7.append(ece3_element.get('cmip6_variable'))
     message_list2_of_ece3_cmip6_identified_variables_not_in_cmip7.append(' Reverse check, not in CMIP7 request: {}'.format(var_info))
    sorted_set_list2_of_ece3_cmip6_identified_variables_not_in_cmip7 = sorted(set(list2_of_ece3_cmip6_identified_variables_not_in_cmip7))
    print(' The method by selecting in the XML the region="None", i.e. the "no-cmip7-equivalent-var-*" cases:')
    print('  A number of {} unique variables which do not match (these are ECE3-CMIP6 identified variables which are not in the CMIP7 request)'          .format(len(sorted_set_list2_of_ece3_cmip6_identified_variables_not_in_cmip7)))


    print()

    print_message_list_reorder(message_list_of_identified_variables)
    print_message_list(message_list_of_1hr_variables               )
    print_message_list(message_list_of_subhr_variables             )
    print_message_list(message_list_of_antarctic_variables         )
    print_message_list(message_list_of_greenland_variables         )
    print_message_list(message_list_of_nh_variables                )
    print_message_list(message_list_of_sh_variables                )
    print_message_list(message_list_of_non_glb_variables           )
    print_message_list(message_list_of_other_climatology_variables )
    print(' No identification for:')
    print_message_list(message_list_of_no_matched_identification   )

   #print_message_list(sorted(list_of_ece3_cmip6_identified_variables_not_in_cmip7))
   #print_message_list(sorted_set_list_of_ece3_cmip6_identified_variables_not_in_cmip7)

   #print_message_list(message_list_of_identification_matches_in_reverse_check     )
   #print_message_list(message_list_of_ece3_cmip6_identified_variables_not_in_cmip7)
    print_message_list_reorder(message_list_of_identification_matches_in_reverse_check     )
    print_message_list_reorder(message_list_of_ece3_cmip6_identified_variables_not_in_cmip7)
   #print_message_list_reorder(message_list2_of_ece3_cmip6_identified_variables_not_in_cmip7)        # With this one instead of the one at line above, the differences can be spotted with a meld
   #print_message_list_reorder(sorted(message_list_of_identification_matches_in_reverse_check     )) # in order to see which variables in this list occur in more than one table
   #print_message_list_reorder(sorted(message_list_of_ece3_cmip6_identified_variables_not_in_cmip7)) # in order to see which variables in this list occur in more than one table



    print('\n Previous approach:\n')

    # Lists with messages for combined printing per message cathegory afterwards:
    message_list_of_multiple_match_messages                      = []
    message_list_of_no_climatology_messages                      = []
    message_list_of_no_identification                            = []
    message_list_of_not_identified_physical_parameters           = []

    # Lists which contains only variables (so with set & sorted unique ordered variable lists can be generated):
    list_of_not_identified_physical_parameters                   = []

    count_dim_changed = 0
    xpath_expression_for_cmip7_request = './/variable'
    for cmip7_element in root_cmip7_variables.findall(xpath_expression_for_cmip7_request):

     # Check whether a variable element with the same physical_parameter_name and cmip6_table is present in the ECE3 CMIP6 identified set:
     count = 0
     xpath_expression_cmip6_overview = './/variable[@cmip6_variable="' + str(cmip7_element.get('physical_parameter_name')) + '"]'
     for ece3_element in root_request_overview.findall(xpath_expression_cmip6_overview):

      if False:
       if ece3_element.get('dimensions') != cmip7_element.get('dimensions'):
        count_dim_changed += 1
        print(' {:4} WARNING dimensions differ for {:46} {:20}: cmip6: {:40} cmip7: {}'.format(count_dim_changed, cmip7_element.get('cmip7_compound_name'), cmip7_element.get('cmip6_compound_name'), ece3_element.get('dimensions'), cmip7_element.get('dimensions')))

      if ece3_element.get('cmip6_table') == cmip7_element.get('cmip6_table') and ece3_element.get('region') == cmip7_element.get('region'):
       if cmip7_element.get('temporal_shape') == "climatology":
        message_list_of_no_climatology_messages.append(' Climatologies not included for: {:45} {}'.format(cmip7_element.get('cmip7_compound_name'), xpath_expression_cmip6_overview))
       else:
        # Deselect the ch4 & co2 ECE3-CMIP6 climatology cases:
        if ece3_element.get('temporal_shape') != "climatology":
         # Deselect Omon hfx & hfy vertically integrated fields:
         if cmip7_element.get('cmip6_compound_name') == cmip7_element.get('cmip6_table') + '.' + cmip7_element.get('physical_parameter_name'):
          count += 1
          if count == 1:
           pass
          #print(' For: {} {} {} {} ECE3-CMIP6 match found in the CMIP7 request {}'.format(cmip7_element.get('cmip6_table'), cmip7_element.get('physical_parameter_name'), cmip7_element.get('region'), count, cmip7_element.get('cmip6_compound_name')))
          else:
           message_list_of_multiple_match_messages.append(' WARNING: for: {} {} {} {} ECE3-CMIP6 matches found in the CMIP7 request'.format(cmip7_element.get('cmip6_table'), cmip7_element.get('physical_parameter_name'), cmip7_element.get('region'), count))
          #message_list_of_multiple_match_messages.append('{} {} {}'.format(cmip7_element.get('cmip6_compound_name'), cmip7_element.get('cmip6_table'), cmip7_element.get('physical_parameter_name')))
      else:
       message_list_of_no_identification.append(' No ECE3-CMIP6 identified equivalent for: {:55} {}'.format(cmip7_element.get('cmip7_compound_name'), cmip7_element.get('cmip6_compound_name')))
       if cmip7_element.get('physical_parameter_name') not in list_of_not_identified_physical_parameters:
        list_of_not_identified_physical_parameters.append(cmip7_element.get('physical_parameter_name'))
        message_list_of_not_identified_physical_parameters.append( \
        ' physical_parameter_name = {:28} long_name = {:132} cmip7_compound_name = {:55}'.format('"' + cmip7_element.get('physical_parameter_name') + '"', \
                                                                                                 '"' + cmip7_element.get('long_name'              ) + '"', \
                                                                                                 '"' + cmip7_element.get('cmip7_compound_name'    ) + '"'))
       elif cmip7_element.get('physical_parameter_name') in list_of_not_identified_physical_parameters:
        try:
         index = list_of_not_identified_physical_parameters.index(cmip7_element.get('physical_parameter_name'))
         message_list_of_not_identified_physical_parameters[index] = '{} {:50}'.format( \
          message_list_of_not_identified_physical_parameters[index], \
         #cmip7_element.get('cmip7_compound_name') \
          cmip7_element.get('cmip6_compound_name')+'-'+cmip7_element.get('region')  \
         )
        except ValueError:
         print('Warning: item {} not found in the list_of_not_identified_physical_parameters list.'.format(cmip7_element.get('physical_parameter_name')))

    print_message_list(message_list_of_no_climatology_messages    )
    print_message_list(message_list_of_multiple_match_messages    )
    print_message_list(message_list_of_no_identification          )
    print(' The list of CMIP7 physical parameters which are not in the ECE3 - CMIP6 identified list:')
    print_message_list(message_list_of_not_identified_physical_parameters)

    print('\n This CMIP7 data request contains {} variables which are not identified in the ECE3 - CMIP6 framewordk.\n'.format(len(message_list_of_not_identified_physical_parameters)))

    number_of_variables = 0
    for element in root_cmip7_variables.findall('.//variable'):
     number_of_variables += 1
    print('\n This CMIP7 data request contains {} different variables.\n'.format(number_of_variables))

    if False:
     for element in root_cmip7_variables.findall('.//variable[@cmip7_compound_name="seaIce.sitempsnic.tavg-u-hxy-si.day.glb"]'):
      print(' test: For the element {} the CMIP7 compound name: {} corresponds with the CMIP6 table - cmor name combination: {} {}'.format(element.tag, element.get('cmip7_compound_name'), element.get('cmip6_table'), element.get('physical_parameter_name')))

if __name__ == '__main__':
    main()
