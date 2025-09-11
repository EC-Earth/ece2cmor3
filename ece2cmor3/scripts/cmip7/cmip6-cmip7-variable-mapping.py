#!/usr/bin/env python
'''
Mapping of CMIP6 to CMIP7 CMOR variables and optionally provide metadata.

Mapping of one CMIP6 table-variable combination:
 ./cmip6-cmip7-variable-mapping.py v1.2.2 -t Amon -v tas

Multiple mapping of various variables from various tables:
 ./cmip6-cmip7-variable-mapping.py v1.2.2 -t Omon,Amon -v tas,tos

Mapping of two CMIP7 compound names:
 ./cmip6-cmip7-variable-mapping.py v1.2.2 -c atmos.areacell.ti-u-hxy-u.fx.GLB,ocean.areacell.ti-u-hxy-u.fx.GLB

Mapping of all variables:
 ./cmip6-cmip7-variable-mapping.py v1.2.2 -r > cmip6-cmip7-mapping-v1.2.2.txt

'''

import argparse

import data_request_api.content.dreq_content as dc
import data_request_api.query.dreq_query as dq
import json


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
    parser.add_argument('-o', '--omitheader'      , action='store_true'  , default=False, help='omit the header')
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

    if args.omitheader == False:
     print()
     if args.showextracolumns == False:
      print(' {:14} {:25}     {:65}   {}'                                                                                             .format('cmip6 table', 'cmip6 variable name', 'cmip7 compound name', 'cmip7 branded variable name'))
     else:
      print(' {:14} {:25}     {:65}   {:40} {:25} {:40} {:120} {:160} {:20} {:45} {:15} {:25} {:15} {:15} {:35} {:140} {:15} {:20} {}'.format('cmip6 table', 'cmip6 variable name', 'cmip7 compound name', 'cmip7 branded variable name', 'branding_label' ,'cmip6_compound_name' ,'long_name' ,'standard_name' ,'units' ,'dimensions' ,'frequency' ,'temporal_shape' ,'spatial_shape' ,'region' ,'cell_measures' ,'cell_methods' ,'modeling_realm' ,'out_name' ,'type'))
     print()

    for k, v in all_var_info.items():
     if args.showextracolumns == False:
      print(' {:14} {:25} ==> {:65} | {}'                                                                                             .format(v['cmip6_table'], v['physical_parameter_name'], k, v['branded_variable_name']))
     else:
      print(' {:14} {:25} ==> {:65} | {:40} {:25} {:40} {:120} {:160} {:20} {:45} {:15} {:25} {:15} {:15} {:35} {:140} {:15} {:20} {}'.format(v['cmip6_table'], v['physical_parameter_name'], k, v['branded_variable_name'], v['branding_label'] ,v['cmip6_compound_name'] ,v['long_name'] ,v['standard_name'] ,v['units'] ,v['dimensions'] ,v['frequency'] ,v['temporal_shape'] ,v['spatial_shape'] ,v['region'] ,v['cell_measures'] ,v['cell_methods'] ,v['modeling_realm'] ,v['out_name'] ,v['type']))

     if args.showmetadata:
      for attname, attvalue in sorted(v.items()):
       print('  {:35} {}'.format(attname, attvalue))

    if args.showmetadata:
     # Write the metadata of the selected list of variables to a json file:
     label = ''
     if args.cmor_tables is not None:
      delim = "-"
      label = label + '-' + delim.join(map(str, args.cmor_tables))
     if args.cmor_variables is not None:
      delim = "-"
      label = label + '-' + delim.join(map(str, args.cmor_variables))
     if args.compound_names is not None:
      delim = "-"
      label = label + '-' + delim.join(map(str, args.compound_names))
     if label == '':
      label = '-all'
     var_json_file = 'cmip6-cmip7-variable-mapping-for' + label + '.json'

     with open(var_json_file, 'w') as outfile:
         json.dump(all_var_info, outfile, sort_keys=True, indent=2)
     outfile.close()

if __name__ == '__main__':
    main()
