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
    parser.add_argument('-m', '--showmetadata'    , action='store_true'  , default=False, help='show in addition the metadata of each listed variable')
    parser.add_argument('-a', '--writeascii'      , action='store_true'  , default=False, help='write an ascii file as well')
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

    if args.writeascii == True:
     # Write an ascii file with all content in attributes for each variable:
     cmip7_variables_ascii_filename = 'cmip7-variables-and-metadata' + label + '.txt'
     with open(cmip7_variables_ascii_filename, 'w') as varasciifile:
      if args.showextracolumns == False:
       varasciifile.write(' {:14} {:25}     {:65}   {}\n'                                                                                             .format('cmip6 table', 'cmip6 variable name', 'cmip7 compound name', 'cmip7 branded variable name'))
      else:
       varasciifile.write(' {:14} {:25}     {:65}   {:40} {:25} {:40} {:130} {:160} {:20} {:45} {:15} {:25} {:15} {:15} {:35} {:140} {:33} {:25} {}\n'.format('cmip6 table', 'cmip6 variable name', 'cmip7 compound name', 'cmip7 branded variable name', 'branding_label' ,'cmip6_compound_name' ,'long_name' ,'standard_name' ,'units' ,'dimensions' ,'frequency' ,'temporal_shape' ,'spatial_shape' ,'region' ,'cell_measures' ,'cell_methods' ,'modeling_realm' ,'out_name' ,'type'))
      varasciifile.write('\n')

      for k, v in all_var_info.items():
       if args.showextracolumns == False:
        varasciifile.write(' {:14} {:25} ==> {:65} | {}\n'                                                                                             .format(v['cmip6_table'], v['physical_parameter_name'], k, v['branded_variable_name']))
       else:
        varasciifile.write(' {:14} {:25} ==> {:65} | {:40} {:25} {:40} {:130} {:160} {:20} {:45} {:15} {:25} {:15} {:15} {:35} {:140} {:33} {:25} {}\n'.format(v['cmip6_table'], v['physical_parameter_name'], k, v['branded_variable_name'], v['branding_label'] ,v['cmip6_compound_name'] ,v['long_name'] ,v['standard_name'] ,v['units'] ,v['dimensions'] ,v['frequency'] ,v['temporal_shape'] ,v['spatial_shape'] ,v['region'] ,v['cell_measures'] ,v['cell_methods'] ,v['modeling_realm'] ,v['out_name'] ,v['type']))

    if args.showmetadata:
     # Write the metadata of the selected list of variables to a json file:
     var_json_file = 'cmip6-cmip7-variable-mapping-for' + label + '.json'
     with open(var_json_file, 'w') as outfile:
      json.dump(all_var_info, outfile, sort_keys=True, indent=2)

    # Write an XML file with all content in attributes for each variable:
    cmip7_variables_xml_filename = 'cmip7-variables-and-metadata' + label + '.xml'
    with open(cmip7_variables_xml_filename, 'w') as varxmlfile:
     varxmlfile.write('<cmip7_variables>\n')

     count_dim_changed = 0
     for k, v in all_var_info.items():
      varxmlfile.write('  <variable  cmip7_compound_name={:55} branded_variable_name={:44} branding_label={:25} cmip6_table={:14} physical_parameter_name={:28} cmip6_compound_name={:40} long_name={:132} standard_name={:160} units={:20} dimensions={:45} frequency={:15} temporal_shape={:25} spatial_shape={:15} region={:15} cell_measures={:35} cell_methods={:140} modeling_realm={:33} out_name={:28} type={:10} >   </variable>\n' \
                         .format('"'+k                            + '"', \
                                 '"'+v['branded_variable_name'  ] + '"', \
                                 '"'+v['branding_label'         ] + '"', \
                                 '"'+v['cmip6_table'            ] + '"', \
                                 '"'+v['physical_parameter_name'] + '"', \
                                 '"'+v['cmip6_compound_name'    ] + '"', \
                                 '"'+v['long_name'              ] + '"', \
                                 '"'+v['standard_name'          ] + '"', \
                                 '"'+v['units'                  ] + '"', \
                                 '"'+v['dimensions'             ] + '"', \
                                 '"'+v['frequency'              ] + '"', \
                                 '"'+v['temporal_shape'         ] + '"', \
                                 '"'+v['spatial_shape'          ] + '"', \
                                 '"'+v['region'                 ] + '"', \
                                 '"'+v['cell_measures'          ] + '"', \
                                 '"'+v['cell_methods'           ] + '"', \
                                 '"'+v['modeling_realm'         ] + '"', \
                                 '"'+v['out_name'               ] + '"', \
                                 '"'+v['type'                   ] + '"'))

     varxmlfile.write('</cmip7_variables>\n')

    # Test: Load the xml file:
    tree_cmip7_variables = ET.parse(cmip7_variables_xml_filename)
    root_cmip7_variables = tree_cmip7_variables.getroot()

    number_of_variables = 0
    for element in root_cmip7_variables.findall('.//variable'):
     number_of_variables += 1
    print('\n The CMIP7 data request contains {} different variables for the selection: {}.\n'.format(number_of_variables, label[1:]))

    if False:
     for element in root_cmip7_variables.findall('.//variable[@cmip7_compound_name="seaIce.sitempsnic.tavg-u-hxy-si.day.glb"]'):
      print(' test: For the element {} the CMIP7 compound name: {} corresponds with the CMIP6 table - cmor name combination: {} {}'.format(element.tag, element.get('cmip7_compound_name'), element.get('cmip6_table'), element.get('physical_parameter_name')))

if __name__ == '__main__':
    main()
