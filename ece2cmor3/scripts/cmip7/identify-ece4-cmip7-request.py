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


def write_xml_file_line_for_variable(xml_file, element, add_all_attributes):
    if add_all_attributes:
     xml_file.write('  <variable  cmip7_compound_name={:55}' \
                                ' priority={:10}' \
                                ' frequency={:15}' \
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
                    '"' + element.get('cmip7_compound_name'    ) + '"', \
                    '"' + element.get('priority'               ) + '"', \
                    '"' + element.get('frequency'              ) + '"', \
                    '"' + element.get('region'                 ) + '"', \
                    '"' + element.get('cmip6_table'            ) + '"', \
                    '"' + element.get('physical_parameter_name') + '"', \
                    '"' + element.get('units'                  ) + '"', \
                    '"' + element.get('dimensions'             ) + '"', \
                    '"' + element.get('long_name'              ) + '"', \
                    '"' + element.get('standard_name'          ) + '"', \
                    '"' + element.get('modeling_realm'         ) + '"', \
                    '"' + element.get('branded_variable_name'  ) + '"', \
                    '"' + element.get('branding_label'         ) + '"', \
                    '"' + element.get('cmip6_compound_name'    ) + '"', \
                    '"' + element.get('temporal_shape'         ) + '"', \
                    '"' + element.get('spatial_shape'          ) + '"', \
                    '"' + element.get('cell_measures'          ) + '"', \
                    '"' + element.get('cell_methods'           ) + '"', \
                    '"' + element.get('out_name'               ) + '"', \
                    '"' + element.get('type'                   ) + '"') \
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


def main():

    args = parse_args()

    add_all_attributes = args.addallattributes



    # Read & load the request-overview ECE3-CMIP6 identification:
    request_overview_xml_filename = 'request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml'
    tree_request_overview = ET.parse(request_overview_xml_filename)
    root_request_overview = tree_request_overview.getroot()


    use_dreq_version = 'v1.2.2.3' # Actually this should be read from the xml file attribute in the root element cmip7_variables
    api_version      = 'v1.4'     # Actually this should be read from the xml file attribute in the root element cmip7_variables
    xml_filename_alphabetic_ordered = 'cmip7-request-{}-all-alphabetic-ordered.xml'.format(use_dreq_version)

    # Load the alphabetic ordered XML file and create a (primary) realm ordered (starting with atmos) XML file:
    print()
    tree_alphabetic = ET.parse(xml_filename_alphabetic_ordered)
    root_alphabetic = tree_alphabetic.getroot()
    applied_order = 'alphabetic (on cmip7_compound_name), realm'
    xml_filename_realm_ordered = 'cmip7-request-{}-all-realm-ordered-identification.xml'.format(use_dreq_version)
    with open(xml_filename_realm_ordered, 'w') as xml_file:
     xml_file.write('<cmip7_variables dr_version="{}" api_version="{}" applied_order_sequence="{}">\n'.format(use_dreq_version, api_version, applied_order))
     for realm in ["atmos.", "atmosChem.", "aerosol.", "land.", "landIce.", "ocean.", "ocnBgchem.", "seaIce."]:
      count = 0
      xpath_expression = './/variable[@cmip7_compound_name]'
      for element in root_alphabetic.findall(xpath_expression):
       if realm in element.get('cmip7_compound_name'):
        write_xml_file_line_for_variable(xml_file, element, add_all_attributes)
        count += 1
      print(' {:4} variables with realm {}'.format(count, realm))
     xml_file.write('</cmip7_variables>\n')


    # Load the realm ordered XML file and create the priority ordered XML file:
    print()
    tree_realm = ET.parse(xml_filename_realm_ordered)
    root_realm = tree_realm.getroot()
    applied_order = 'alphabetic (on cmip7_compound_name), realm, priority'
    xml_filename_priority_ordered = xml_filename_realm_ordered.replace('realm', 'priority')
    with open(xml_filename_priority_ordered, 'w') as xml_file:
     xml_file.write('<cmip7_variables dr_version="{}" api_version="{}" applied_order_sequence="{}">\n'.format(use_dreq_version, api_version, applied_order))
     for priority in ["Core", "High", "Medium", "Low"]:
      count = 0
      xpath_expression = './/variable[@priority="' + priority + '"]'
      for element in root_realm.findall(xpath_expression):
       write_xml_file_line_for_variable(xml_file, element, add_all_attributes)
       count += 1
     #print(' {:4} variables with priority {}'.format(count, priority))
     xml_file.write('</cmip7_variables>\n')


    # Load the priority ordered XML file and create the frequency ordered XML file:
    print()
    tree_priority = ET.parse(xml_filename_priority_ordered)
    root_priority = tree_priority.getroot()
    applied_order = 'alphabetic (on cmip7_compound_name), realm, priority, CMIP7 frequency'
    xml_filename_frequency_ordered = xml_filename_realm_ordered.replace('realm', 'frequency')
    with open(xml_filename_frequency_ordered, 'w') as xml_file:
     xml_file.write('<cmip7_variables dr_version="{}" api_version="{}" applied_order_sequence="{}">\n'.format(use_dreq_version, api_version, applied_order))
     for frequency in [".fx.", ".3hr.", ".6hr.", ".day.", ".mon.", ".yr.", ".subhr.", ".1hr.", ".dec."]:
      count = 0
      xpath_expression = './/variable[@cmip7_compound_name]'
      for element in root_priority.findall(xpath_expression):
       if frequency in element.get('cmip7_compound_name'):
        write_xml_file_line_for_variable(xml_file, element, add_all_attributes)
        count += 1
     #print(' {:4} variables with frequency {}'.format(count, frequency))
     xml_file.write('</cmip7_variables>\n')


    # Load the realm ordered XML file and create the cmip6-table ordered XML file:
   #tree_realm = ET.parse(xml_filename_realm_ordered)  # loaded before
   #root_realm = tree_realm.getroot()                  # loaded before
    print()
    applied_order = 'alphabetic (on cmip7_compound_name), realm, cmip6_table'
    xml_filename_cmip6_table_ordered = xml_filename_realm_ordered.replace('realm', 'cmip6-table')
    with open(xml_filename_cmip6_table_ordered, 'w') as xml_file:
     xml_file.write('<cmip7_variables dr_version="{}" api_version="{}" applied_order_sequence="{}">\n'.format(use_dreq_version, api_version, applied_order))
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
       write_xml_file_line_for_variable(xml_file, element, add_all_attributes)
       count += 1
     #print(' {:4} variables with cmip6_table {}'.format(count, cmip6_table))
     xml_file.write('</cmip7_variables>\n')




if __name__ == '__main__':
    main()
