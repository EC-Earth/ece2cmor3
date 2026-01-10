#!/usr/bin/env python
'''
Mapping of CMIP6 to CMIP7 CMOR variables and optionally provide metadata.

Mapping of one CMIP6 table-variable combination:
 ./cmip6-cmip7-variable-mapping.py v1.2.2.3 -t Amon -v tas

Multiple mapping of various variables from various tables:
 ./cmip6-cmip7-variable-mapping.py v1.2.2.3 -t Omon,Amon -v tas,tos

Mapping of two CMIP7 compound names:
 ./cmip6-cmip7-variable-mapping.py v1.2.2.3 -c atmos.areacell.ti-u-hxy-u.fx.glb,ocean.areacell.ti-u-hxy-u.fx.glb

Mapping of all variables:
 ./cmip6-cmip7-variable-mapping.py v1.2.2.3 -r


This script produces a neat formatted XML file with the metadata in attrbutes. All CMIP7 variables can be inlcuded or a selection based on argument options.
'''

import argparse

import data_request_api.content.dreq_content as dc
import data_request_api.query.dreq_query as dq
import json
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
    parser.add_argument('dreq_version', choices=dc.get_versions(), help='data request version')

    sep = ','

    def parse_input_list(input_str: str, sep=sep) -> list:
        '''Create list of input args separated by separator "sep" (str)'''
        input_args = input_str.split(sep)
        # Guard against leading, trailing, or repeated instances of the separator
        input_args = [s for s in input_args if s not in ['']]
        return input_args

    # Optional input arguments
    parser.add_argument('-c', '--compound_names'  , type=parse_input_list               , help='include only variables with the specified Compound Names (examples: Amon.tas Omon.sos)')
    parser.add_argument('-t', '--cmor_tables'     , type=parse_input_list               , help='include only the specified CMOR tables (aka MIP tables, examples: Amon Omon)')
    parser.add_argument('-v', '--cmor_variables'  , type=parse_input_list               , help='include only the specified CMOR variables (out_name, examples: tas siconc)')
    parser.add_argument('-r', '--showextracolumns', action='store_true'  , default=False, help='show extra metadata in extra columns')

    return parser.parse_args()


def main():

    args = parse_args()

    # Load data request content
    use_dreq_version = args.dreq_version
    content = dc.load(use_dreq_version)

    # Get metadata for variables
    all_var_info = dq.get_variables_metadata(
                    content,
                    use_dreq_version,
                    compound_names=args.compound_names,
                    cmor_tables=args.cmor_tables,
                    cmor_variables=args.cmor_variables,
                    verbose=False
                   )

    label = ''
    delim = "-"
    if args.cmor_tables    is not None: label = label + '-' + delim.join(map(str, args.cmor_tables   ))
    if args.cmor_variables is not None: label = label + '-' + delim.join(map(str, args.cmor_variables))
    if args.compound_names is not None: label = label + '-' + delim.join(map(str, args.compound_names))
    if label               == ''      : label = '-all'

    multiple_match_messages    = []   # A list collecting the multiple match messages for pretty printing afterwards
    no_climatology_messages    = []   # A list collecting the messages which mention that climatology requests are not included for pretty printing afterwards
    no_identification_messages = []   # A list collecting the messages which mention when a vraible is not identified within the ECE3 - CMIP6 framework for pretty printing afterwards
    not_identified_physical_parameter_list_messages = []
    not_identified_physical_parameters = []


    # Load the xml file:
    cmip7_variables_xml_filename = 'cmip7-variables-and-metadata-all.xml'
    tree_cmip7_variables = ET.parse(cmip7_variables_xml_filename)
    root_cmip7_variables = tree_cmip7_variables.getroot()

    # Read & load the request-overview ECE3-CMIP6 identification:
    request_overview_xml_filename = 'request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml'
    tree_request_overview = ET.parse(request_overview_xml_filename)
    root_request_overview = tree_request_overview.getroot()

    count_dim_changed = 0
    for k, v in all_var_info.items():

     # Check whether a variable element with the same physical_parameter_name and cmip6_table is present in the ECE3 CMIP6 identified set:
     count = 0
     xpath_expression = './/variable[@cmip6_variable="' + v['physical_parameter_name'] + '"]'
     for ece3_element in root_request_overview.findall(xpath_expression):
      if False:
       if ece3_element.get('dimensions') != v['dimensions']:
        count_dim_changed += 1
        print(' {:4} WARNING dimensions differ for {:46} {:20}: cmip6: {:40} cmip7: {}'.format(count_dim_changed, k, v['cmip6_compound_name'], ece3_element.get('dimensions'), v['dimensions']))
      if ece3_element.get('cmip6_table') == v['cmip6_table'] and ece3_element.get('region') == v['region']:
       if v['temporal_shape'] == "climatology":
        no_climatology_messages.append(' Climatologies not included for: {:45} {}'.format(k, xpath_expression))
       else:
        # Deselect the ch4 & co2 ECE3-CMIP6 climatology cases:
        if ece3_element.get('temporal_shape') != "climatology":
         # Deselect Omon hfx & hfy vertically integrated fields:
         if v['cmip6_compound_name'] == v['cmip6_table'] + '.' + v['physical_parameter_name']:
          count += 1
          if count == 1:
           pass
          #print(' For: {} {} {} {} ECE3-CMIP6 match found in the CMIP7 request {}'.format(v['cmip6_table'], v['physical_parameter_name'], v['region'], count, v['cmip6_compound_name']))
          else:

           multiple_match_messages.append(' WARNING: for: {} {} {} {} ECE3-CMIP6 matches found in the CMIP7 request'.format(v['cmip6_table'], v['physical_parameter_name'], v['region'], count))
          #multiple_match_messages.append('{} {} {}'.format(v['cmip6_compound_name'], v['cmip6_table'], v['physical_parameter_name']))
      else:
       no_identification_messages.append(' No ECE3-CMIP6 identified equivalent for: {:55} {}'.format(k, v['cmip6_compound_name']))
       if v['physical_parameter_name'] not in not_identified_physical_parameters:
        not_identified_physical_parameters.append(v['physical_parameter_name'])
        not_identified_physical_parameter_list_messages.append(' physical_parameter_name = "{:28}" long_name = "{}"'.format(v['physical_parameter_name'], v['long_name']))

    print()
    for message in no_climatology_messages:
     print(message)
    print()
    for message in multiple_match_messages:
     print(message)
    print()
    for message in no_identification_messages:
     print(message)
    print()
    for message in not_identified_physical_parameter_list_messages:
     print(message)
    print()

    print('\n The CMIP7 data request contains {} variables for the selection: {} which are not identified in the ECE3 - CMIP6 framewordk.\n'.format(len(not_identified_physical_parameter_list_messages), label[1:]))

    number_of_variables = 0
    for element in root_cmip7_variables.findall('.//variable'):
     number_of_variables += 1
    print('\n The CMIP7 data request contains {} different variables for the selection: {}.\n'.format(number_of_variables, label[1:]))

    if False:
     for element in root_cmip7_variables.findall('.//variable[@cmip7_compound_name="seaIce.sitempsnic.tavg-u-hxy-si.day.glb"]'):
      print(' test: For the element {} the CMIP7 compound name: {} corresponds with the CMIP6 table - cmor name combination: {} {}'.format(element.tag, element.get('cmip7_compound_name'), element.get('cmip6_table'), element.get('physical_parameter_name')))

if __name__ == '__main__':
    main()
