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


def print_core_var_info(element):
    info_string = '{:26} {:12} {:10} {}'          .format(element.get('physical_parameter_name'), \
                                                        element.get('cmip6_table'            ), \
                                                        element.get('region'                 ), \
                                                        element.get('cmip7_compound_name'    ))
    return info_string


def print_core_var_plus_ece3_info(element, element_ece3):
    info_string = '{:26} {:12} {:10} {:55} {}({})'.format(element.get('physical_parameter_name'), \
                                                        element.get('cmip6_table'            ), \
                                                        element.get('region'                 ), \
                                                        element.get('cmip7_compound_name'    ), \
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
    info_string = '{:26} {:12} {:10} {:55} {}({})'.format(element.get('cmip6_variable'   ), \
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

    multiple_match_messages                         = []   # A list collecting the multiple match messages for pretty printing afterwards
    no_climatology_messages                         = []   # A list collecting the messages which mention that climatology requests are not included for pretty printing afterwards
    no_identification_messages                      = []   # A list collecting the messages which mention when a vraible is not identified within the ECE3 - CMIP6 framework for pretty printing afterwards
    not_identified_physical_parameter_list_messages = []
    not_identified_physical_parameters              = []

    list_of_identified_variables                    = []   # A list collecting the
    list_of_1hr_variables                           = []   # A list collecting the
    list_of_subhr_variables                         = []   # A list collecting the
    list_of_antarctic_variables                     = []   # A list collecting the
    list_of_greenland_variables                     = []   # A list collecting the
    list_of_other_climatology_variables             = []   # A list collecting the
    list_of_nh_variables                            = []   # A list collecting the
    list_of_sh_variables                            = []   # A list collecting the
    list_of_non_glb_variables                       = []   # A list collecting the
    list_of_no_matched_identification               = []   # A list collecting the

    list_of_identification_matches_in_reverse_check      = []   # A list collecting the
    list_of_ece3_cmip6_identified_variables_not_in_cmip7 = []   # A list collecting the

    no_matched_identification = []

    # Load the xml file:
    cmip7_variables_xml_filename = 'cmip7-variables-and-metadata-all.xml'
    tree_cmip7_variables = ET.parse(cmip7_variables_xml_filename)
    root_cmip7_variables = tree_cmip7_variables.getroot()

    # Read & load the request-overview ECE3-CMIP6 identification:
    request_overview_xml_filename = 'request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml'
    tree_request_overview = ET.parse(request_overview_xml_filename)
    root_request_overview = tree_request_overview.getroot()


    xpath_expression_for_cmip7_request = './/variable'
    for cmip7_element in root_cmip7_variables.findall(xpath_expression_for_cmip7_request):
     core_var_info = print_core_var_info(cmip7_element)

     if   '1hr'   in cmip7_element.get('cmip6_table'):
      list_of_1hr_variables.append(' 1HR          variable: {}'.format(core_var_info))
     elif 'subhr' in cmip7_element.get('cmip6_table'):
      list_of_subhr_variables.append(' SUBHR        variable: {}'.format(core_var_info))
     elif 'Ant' in cmip7_element.get('cmip6_table'):
      if 'ata' not in cmip7_element.get('region'):
       print(' WARNING: Antarctic table determined but region not ata for: {}'.format(cmip7_element.get('cmip7_compound_name')))
      list_of_antarctic_variables.append(' Antarctic    variable: {}'.format(core_var_info))
     elif 'Gre' in cmip7_element.get('cmip6_table'):
      if 'grl' not in cmip7_element.get('region'):
       print(' WARNING: Greenland table determined but region not grl for: {}'.format(cmip7_element.get('cmip7_compound_name')))
      list_of_greenland_variables.append(' Greenland    variable: {}'.format(core_var_info))
     elif cmip7_element.get('region') == 'nh':
      list_of_nh_variables.append(' NH           variable: {}'.format(core_var_info))
     elif cmip7_element.get('region') == 'sh':
      list_of_sh_variables.append(' SH           variable: {}'.format(core_var_info))
     elif cmip7_element.get('region') != 'glb':
      list_of_non_glb_variables.append(' Non glb      variable: {}'.format(core_var_info))
     elif cmip7_element.get('temporal_shape') == "climatology":
      list_of_other_climatology_variables.append(' Climatology  variable: {}'.format(core_var_info))
     else:
     #print(' {}'.format(core_var_info))
      count = 0
      xpath_expression_cmip6_overview = './/variable[@cmip6_variable="' + cmip7_element.get('physical_parameter_name') + '"]'
      for ece3_element in root_request_overview.findall(xpath_expression_cmip6_overview):
       core_var_plus_ece3_info = print_core_var_plus_ece3_info(cmip7_element, ece3_element)

       count += 1
       if cmip7_element.get('physical_parameter_name') == ece3_element.get('cmip6_variable'):
        if ece3_element.get('cmip6_table') == cmip7_element.get('cmip6_table') and ece3_element.get('region') == cmip7_element.get('region'):
        #print(' {:2}    match for: {}'.format(count, core_var_plus_ece3_info))
         list_of_identified_variables.append(' {:2}    match for: {}'.format(count, core_var_plus_ece3_info))
        else:
         pass
        #print(' {:2} no match for: {}'.format(count, core_var_plus_ece3_info))
       else:
        print('ERROR 01')
      else:
       # The for-else:
       if count == 0:
        no_matched_identification.append(cmip7_element.get('physical_parameter_name'))
        list_of_no_matched_identification.append(' No identification for: {}'.format(core_var_info))

    sorted_set_no_matched_identification = sorted(set(no_matched_identification))
    print('\n This CMIP7 data request contains {}        variables which are not identified in the ECE3 - CMIP6 framewordk.'.format(len(no_matched_identification)))
    print('\n This CMIP7 data request contains {} unique variables which are not identified in the ECE3 - CMIP6 framewordk.'.format(len(sorted_set_no_matched_identification)))
    print()


    # The reverse case: investigate which ECE3-CMIP6 identified variables are not part of the CMIP7 request:
    count_matches = 0
    count_cmip6_identified_but_not_in_cmip7 = 0
    xpath_expression_cmip6_overview = './/variable'
    for ece3_element in root_request_overview.findall(xpath_expression_cmip6_overview):
     core_var_info = print_ece3_info(ece3_element)

     count = 0
     xpath_expression_cmip7_request = './/variable[@physical_parameter_name="' + ece3_element.get('cmip6_variable') + '"]'
     for cmip7_element in root_cmip7_variables.findall(xpath_expression_cmip7_request):
      if cmip7_element.get('physical_parameter_name') == ece3_element.get('cmip6_variable'):
       count += 1
       if ece3_element.get('cmip6_table') == cmip7_element.get('cmip6_table') and ece3_element.get('region') == cmip7_element.get('region'):
        list_of_identification_matches_in_reverse_check.append(' Reverse check, identification match: {}'.format(core_var_info))
        count_matches += 1
     else:
      # The for-else:
      if count == 0:
       count_cmip6_identified_but_not_in_cmip7 += 1
       list_of_ece3_cmip6_identified_variables_not_in_cmip7.append(' Reverse check, not in CMIP7: {}'.format(core_var_info))
      else:
       if count_matches == 0:
        print(' Weird (not impossible but not expected (hopefully not the case).')  # Indeed, so far this is never the case.
    print('\n Number of matches is {}. Number of unmatched is {}'.format(count_matches, count_cmip6_identified_but_not_in_cmip7))

    '''
     See also:
      echo '<cmip6_variables>'                                                                         > list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
      grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
      echo '</cmip6_variables>'                                                                       >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml

     Or the same but sorted per model component:
      echo '<cmip6_variables>'                                                                                                               > list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
      grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="ifs"'     >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
      grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="nemo"'    >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
      grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="lpjg"'    >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
      grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="tm5"'     >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
      grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="co2box"'  >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
      echo '</cmip6_variables>'                                                                                                             >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
      sed -i -e 's/region="None"     temporal_shape="None"                     //' -e 's/                     dimensions=/dimensions=/'        list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
      sed -i -e 's/cmip7_long_name="None"                                                                                                                              //' list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml

     So there are 238 CMIP6 table - variable combinations which are not in the CMIP7 request, from which 110 CMIP6 variables are not at all in the CMIP7 request.
    '''

    # Previous approach:

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
        no_climatology_messages.append(' Climatologies not included for: {:45} {}'.format(cmip7_element.get('cmip7_compound_name'), xpath_expression_cmip6_overview))
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
           multiple_match_messages.append(' WARNING: for: {} {} {} {} ECE3-CMIP6 matches found in the CMIP7 request'.format(cmip7_element.get('cmip6_table'), cmip7_element.get('physical_parameter_name'), cmip7_element.get('region'), count))
          #multiple_match_messages.append('{} {} {}'.format(cmip7_element.get('cmip6_compound_name'), cmip7_element.get('cmip6_table'), cmip7_element.get('physical_parameter_name')))
      else:
       no_identification_messages.append(' No ECE3-CMIP6 identified equivalent for: {:55} {}'.format(cmip7_element.get('cmip7_compound_name'), cmip7_element.get('cmip6_compound_name')))
       if cmip7_element.get('physical_parameter_name') not in not_identified_physical_parameters:
        not_identified_physical_parameters.append(cmip7_element.get('physical_parameter_name'))
        not_identified_physical_parameter_list_messages.append( \
        ' physical_parameter_name = {:28} long_name = {:132} cmip7_compound_name = {:55}'.format('"' + cmip7_element.get('physical_parameter_name') + '"', \
                                                                                                 '"' + cmip7_element.get('long_name'              ) + '"', \
                                                                                                 '"' + cmip7_element.get('cmip7_compound_name'    ) + '"'))
       elif cmip7_element.get('physical_parameter_name') in not_identified_physical_parameters:
        try:
         index = not_identified_physical_parameters.index(cmip7_element.get('physical_parameter_name'))
         not_identified_physical_parameter_list_messages[index] = '{} {:50}'.format( \
          not_identified_physical_parameter_list_messages[index], \
         #cmip7_element.get('cmip7_compound_name') \
          cmip7_element.get('cmip6_compound_name')+'-'+cmip7_element.get('region')  \
         )
        except ValueError:
         print('Warning: item {} not found in the not_identified_physical_parameters list.'.format(cmip7_element.get('physical_parameter_name')))


    print()
    print_message_list(list_of_identification_matches_in_reverse_check)
    print_message_list(list_of_ece3_cmip6_identified_variables_not_in_cmip7)

    print_message_list(list_of_identified_variables       )
    print_message_list(list_of_1hr_variables              )
    print_message_list(list_of_subhr_variables            )
    print_message_list(list_of_antarctic_variables        )
    print_message_list(list_of_greenland_variables        )
    print_message_list(list_of_nh_variables               )
    print_message_list(list_of_sh_variables               )
    print_message_list(list_of_non_glb_variables          )
    print_message_list(list_of_other_climatology_variables)
    print_message_list(list_of_no_matched_identification  )

    print_message_list(no_climatology_messages)
    print_message_list(multiple_match_messages)
    print_message_list(no_identification_messages)
    print(' The list of CMIP7 physical parameters which are not in the ECE3 - CMIP6 identified list:')
    print_message_list(not_identified_physical_parameter_list_messages)

    print('\n This CMIP7 data request contains {} variables which are not identified in the ECE3 - CMIP6 framewordk.\n'.format(len(not_identified_physical_parameter_list_messages)))

    number_of_variables = 0
    for element in root_cmip7_variables.findall('.//variable'):
     number_of_variables += 1
    print('\n This CMIP7 data request contains {} different variables.\n'.format(number_of_variables))

    if False:
     for element in root_cmip7_variables.findall('.//variable[@cmip7_compound_name="seaIce.sitempsnic.tavg-u-hxy-si.day.glb"]'):
      print(' test: For the element {} the CMIP7 compound name: {} corresponds with the CMIP6 table - cmor name combination: {} {}'.format(element.tag, element.get('cmip7_compound_name'), element.get('cmip6_table'), element.get('physical_parameter_name')))

if __name__ == '__main__':
    main()
