#!/usr/bin/env python
"""
Command line interface for retrieving simple variable lists from the data request.
Return a list per specified experiment of CMIP7 compound variables including the mapping to the CMIP6 table - var combination

This script is based on the script: CMIP7_DReq_Software/data_request_api/data_request_api/command_line/export_dreq_lists_json.py
"""

import sys
import json
import os
import argparse
import xml.etree.ElementTree as ET
from collections import OrderedDict

import data_request_api
import data_request_api.content.dreq_content as dc
import data_request_api.query.dreq_query as dq
from importlib.metadata import version

PACKAGE_NAME = "CMIP7_data_request_api"
api_version  = version(PACKAGE_NAME)
print(' The CMIP7 dreq python api version is: v{}'.format(api_version))


# A dictionary which relates the variable priorities to a numerical value:
priority_dict = {
  "Core"  : 4,
  "High"  : 3,
  "Medium": 2,
  "Low"   : 1
}
# The inverse dictionary:
priority_dict_inverse = {
  4 : "Core"  ,
  3 : "High"  ,
  2 : "Medium",
  1 : "Low"
}


def parse_args():
    """
    Parse command-line arguments
    """

    parser = argparse.ArgumentParser(
        description='Create a list with CMIP7 to CMIP6 mapped CMIP7 requested variables by specifying a list of experiments, and write them to a ascii file.'
    )

    # Positional (mandatory) input arguments
    parser.add_argument('dreq_version', choices=dc.get_versions()                              , help="data request version")
   #parser.add_argument('output_file'                                                          , help='file to write JSON output to')

    sep = ','

    def parse_input_list(input_str: str, sep=sep) -> list:
        '''Create list of input args separated by separator "sep" (str)'''
        input_args = input_str.split(sep)
        # Guard against leading, trailing, or repeated instances of the separator
        input_args = [s for s in input_args if s not in ['']]
        return input_args

    # Optional input arguments
    parser.add_argument('-a', '--all_opportunities' , action='store_true'                      , help="respond to all opportunities")
    parser.add_argument('-f', '--opportunities_file', type=str                                 , help="path to JSON file listing opportunities to respond to. If it doesn't exist, a template will be created")
    parser.add_argument('-i', '--opportunity_ids'   , type=parse_input_list                    , help=f'opportunity ids (integers) of opportunities to respond to, example: -i 69{sep}22{sep}37')
    parser.add_argument('-e', '--experiments'       , type=parse_input_list                    , help=f'limit output to the specified experiments (case sensitive), example: -e historical{sep}piControl')
    parser.add_argument('-p', '--priority_cutoff'   , default='low', choices=dq.PRIORITY_LEVELS, help="discard variables that are requested at lower priority than this cutoff priority")
    parser.add_argument('-m', '--variables_metadata', type=str                                 , help='output file containing metadata of requested variables, can be ".json" or ".csv" file')

    return parser.parse_args()


def write_xml_file_line_for_variable(xml_file, element):
    xml_file.write('  <variable  cmip7_compound_name={:55} physical_parameter_name={:28} cmip6_table={:14} region={:12} priority={:10} long_name={:132}>  </variable>\n'.format( \
                   '"' + element.get('cmip7_compound_name'    ) + '"', \
                   '"' + element.get('physical_parameter_name') + '"', \
                   '"' + element.get('cmip6_table'            ) + '"', \
                   '"' + element.get('region'                 ) + '"', \
                   '"' + element.get('priority'               ) + '"', \
                   '"' + element.get('long_name'              ) + '"') \
                  )


def main():
    """
    main routine
    """
    args = parse_args()

    use_dreq_version = args.dreq_version

    if args.experiments:
     experiment_label = ''
     for exp in args.experiments:
      experiment_label = experiment_label + '-' + exp
    else:
     experiment_label = '-all'
    outfile = 'cmip7-request-{}{}.json'.format(use_dreq_version, experiment_label)


    # Download specified version of data request content (if not locally cached)
    dc.retrieve(use_dreq_version)
    # Load content into python dict
    content = dc.load(use_dreq_version)
    # Render data request tables as dreq_table objects
    base = dq.create_dreq_tables_for_request(content, use_dreq_version)

    # Deal with opportunities
    if args.opportunities_file:
        # Select opportunities by their title, as given in a user-specified json file
        opportunities_file = args.opportunities_file
        dreq_opps = base['Opportunity']
        if not os.path.exists(opportunities_file):
            # create opportunities file template
            use_opps = sorted([opp.title for opp in dreq_opps.records.values()], key=str.lower)
            default_opportunity_dict = OrderedDict({
                'Header': OrderedDict({
                    'Description': 'Opportunities template file for use with export_dreq_lists_json. Set supported/unsupported Opportunities to true/false.',
                    'dreq content version': use_dreq_version,
                    'dreq api version': data_request_api.version,
                }),
                'Opportunity': OrderedDict({title: True for title in use_opps})
            })
            with open(opportunities_file, 'w') as fh:
                json.dump(default_opportunity_dict, fh, indent=4)
                print("written opportunities dict to {}. Please edit and re-run".format(opportunities_file))
                sys.exit(0)
        else:
            # load existing opportunities file
            with open(opportunities_file, 'r') as fh:
                opportunity_dict = json.load(fh)

            dreq_version = opportunity_dict['Header']['dreq content version']
            if dreq_version != use_dreq_version:
                raise ValueError('Data request version mismatch!' +
                                 f'\nOpportunities file was generated for data request version {dreq_version}' +
                                 f'\nPlease regenerate the file using version {use_dreq_version}')

            opportunity_dict = opportunity_dict['Opportunity']

            # validate opportunities
            # (mismatches can occur if an opportunities file created with an earlier data request version is loaded)
            valid_opps = [opp.title for opp in dreq_opps.records.values()]
            invalid_opps = [title for title in opportunity_dict if title not in valid_opps]
            if invalid_opps:
                raise ValueError(f'\nInvalid opportunities were found in {opportunities_file}:\n' + '\n'.join(sorted(invalid_opps, key=str.lower)))

            # filter opportunities
            use_opps = [title for title in opportunity_dict if opportunity_dict[title]]

    elif args.opportunity_ids:
        # Select opportunities by their integer IDs, specified from the command line
        dreq_opps = base['Opportunity']
        all_opp_ids = [opp.opportunity_id for opp in dreq_opps.records.values()]
        if len(all_opp_ids) != len(set(all_opp_ids)):
            raise ValueError(f'Opportunity IDs (integers) in data request {use_dreq_version} are not unique!')
        oppid2title = {int(opp.opportunity_id): opp.title for opp in dreq_opps.records.values()}
        use_opps = []
        invalid_opp_ids = set()
        for opp_id in args.opportunity_ids:
            try:
                opp_id = int(opp_id)
            except BaseException:
                ValueError('Opportunity ID should be an integer')
            if opp_id in oppid2title:
                use_opps.append(oppid2title[opp_id])
            else:
                invalid_opp_ids.add(opp_id)
        if len(invalid_opp_ids) > 0:
            raise ValueError(f'The following Opportunity IDs were not found in data request {use_dreq_version}: '
                             + ', '.join([str(opp_id) for opp_id in sorted(invalid_opp_ids)]))

    elif args.all_opportunities:
        # Use all available opportunities in the data request
        use_opps = 'all'

    else:
        print("Please use one of the opportunities arguments")
        sys.exit(1)

    # Get the requested variables for each opportunity and aggregate them into variable lists by experiment
    # (i.e., for every experiment, a list of the variables that should be produced to support all of the specified opportunities)
    expt_vars = dq.get_requested_variables(base, use_dreq_version,
                                           use_opps=use_opps, priority_cutoff=args.priority_cutoff,
                                           verbose=False)

    # filter output by requested experiments
    if args.experiments:
        experiments = list(expt_vars['experiment'].keys())  # names of experiments requested by opportunities in use_opps

        # validate the requested experiment names
        Expts = base['Experiments']
        valid_experiments = [expt.experiment for expt in Expts.records.values()]  # all valid experiment names in data request
        invalid_experiments = [entry for entry in args.experiments if entry not in valid_experiments]
        if invalid_experiments:
            raise ValueError('\nInvalid experiments: ' + ', '.join(sorted(invalid_experiments, key=str.lower)) +
                             '\nValid experiment names: ' + ', '.join(sorted(valid_experiments, key=str.lower)))

        # discard experiments that aren't requested
        for entry in experiments:
            if entry not in args.experiments:
                del expt_vars['experiment'][entry]


    var_list                        = []
    prio_list                       = []
    var_list_for_xml                = []
    message_list_changed_priorities = []

    # Construct output
    if len(expt_vars['experiment']) > 0:

        # Show user what was found
        dq.show_requested_vars_summary(expt_vars, use_dreq_version)

        # Write json file with the variable lists
        content_path = dc._dreq_content_loaded['json_path']
        dq.write_requested_vars_json(outfile, expt_vars, use_dreq_version, args.priority_cutoff, content_path)

        # Get all variable names for all requested experiments
        all_var_names = set()
        for vars_by_priority in expt_vars['experiment'].values():
            for var_names in vars_by_priority.values():
                all_var_names.update(var_names)
        print('\nTotal number of different variables: {}\n'.format(len(all_var_names)))
        var_metadata = dq.get_variables_metadata(base, use_dreq_version, compound_names=all_var_names, verbose=False)

       #print(json.dumps(expt_vars['experiment'],sort_keys=True, indent=4))

        input_dictionary  = expt_vars['experiment']
        sorted_dictionary = dict(sorted(input_dictionary.items()))
        for experiment, priority_groups in OrderedDict(sorted_dictionary).items():
        #print('{} {}'.format(experiment, priority_groups))
         for priority_group, variable_list in priority_groups.items():
         #print('\nCMIP7 priority group: {}\n'.format(priority_group))
          print('\nCMIP7 experiment: {}; CMIP7 priority group: {}'.format(experiment, priority_group))
         #print('{} {}'.format(priority_group, variable_list))
          for compound_var in variable_list:
          #print('{}'.format(compound_var))
          #print('{}\n'.format(var_metadata))
          #print('{}\n'.format(var_metadata[compound_var]))
         ##for attribute, value in sorted(var_metadata[compound_var].items()):
         ## print('{:40} {}'.format(attribute, value))
         ##print('')
        ###print('MIPS per var: {}'.format(DataRequest.find_mips_per_variable(self=self, variable=compound_var)))

           # Write one XML line per variable into a list (this list will be used to write the XML file lateron):
           if compound_var not in var_list:
            var_list.append(compound_var)
            prio_list.append(priority_dict[priority_group])  # same sequence as for var_list
            var_list_for_xml.append('  <variable  cmip7_compound_name={:55} physical_parameter_name={:28} cmip6_table={:14} region={:12} priority={:10} long_name={:132}>  </variable>\n'.format( \
                                    '"' + var_metadata[compound_var]['cmip7_compound_name'    ] + '"', \
                                    '"' + var_metadata[compound_var]['physical_parameter_name'] + '"', \
                                    '"' + var_metadata[compound_var]['cmip6_table'            ] + '"', \
                                    '"' + var_metadata[compound_var]['region'                 ] + '"', \
                                    '"' + priority_group                                        + '"', \
                                    '"' + var_metadata[compound_var]['long_name'              ] + '"') \
                                   )
           else:
            index = var_list.index(compound_var)
            previous_prio_numeric = prio_list[index]
            previous_prio         = priority_dict_inverse[previous_prio_numeric]
            current_prio_numeric  = priority_dict[priority_group]
            current_prio          = priority_group
            if previous_prio != current_prio:
             # Keep the highest encountered prio (e.g. --experiments dcppB-forecast-cmip6,esm-scen7-m):
             if current_prio_numeric > previous_prio_numeric:
              previous_prio_formatted = '{:10}'.format('"' + previous_prio + '"')
              current_prio_formatted  = '{:10}'.format('"' + current_prio  + '"')
              var_list_for_xml[index] = var_list_for_xml[index].replace('priority=' + previous_prio_formatted, 'priority=' + current_prio_formatted)
              message_list_changed_priorities.append(' Priority adjusted from {:10} to {:10} for {}'.format(previous_prio, current_prio, compound_var))
             #message_list_changed_priorities.append(' Priority adjusted from {:10} to {:10} for {:55} resulting in: {}'.format(previous_prio, current_prio, compound_var, var_list_for_xml[index]))
              print(' Warning: Different priorities detected for: {:55} {:10} {:10} adjusted'.format(compound_var, previous_prio,                        current_prio                      ))
             else:
              print(' Warning: Different priorities detected for: {:55} {:10} {}'            .format(compound_var, previous_prio,                        current_prio                      ))
             #print(' Warning: Different priorities detected for: {:55} {:10}={} & {}={}'    .format(compound_var, previous_prio, previous_prio_numeric, current_prio, current_prio_numeric))

    else:
        print(f'\nFor data request version {use_dreq_version}, no requested variables were found')

    # Write directly a neat formatted XML file with all content in attributes for each variable:
    xml_filename_alphabetic_ordered = 'cmip7-request-{}{}-alphabetic-ordered.xml'.format(use_dreq_version, experiment_label)
    with open(xml_filename_alphabetic_ordered, 'w') as xml_file:
     xml_file.write('<cmip7_variables dr_version="{}" api_version="{}">\n'.format(use_dreq_version, api_version))
     for var in sorted(var_list_for_xml):
      xml_file.write(var)
     xml_file.write('</cmip7_variables>\n')

    if len(message_list_changed_priorities) > 0:
     print('\n\nOverview of adjusted priorities:')
     for message in message_list_changed_priorities:
      print(message)


    # Load the xml file:
    tree_main = ET.parse(xml_filename_alphabetic_ordered)
    root_main = tree_main.getroot()

    print()
    xml_filename_realm_ordered = xml_filename_alphabetic_ordered.replace('alphabetic', 'realm')
    with open(xml_filename_realm_ordered, 'w') as xml_file:
     xml_file.write('<cmip7_variables dr_version="{}" api_version="{}">\n'.format(use_dreq_version, api_version))
     for realm in ["atmos.", "atmosChem.", "aerosol.", "land.", "landIce.", "ocean", "ocnBgchem.", "seaIce."]:
      count = 0
      xpath_expression = './/variable[@cmip7_compound_name]'
      for element in root_main.findall(xpath_expression):
       if realm in element.get('cmip7_compound_name'):
        write_xml_file_line_for_variable(xml_file, element)
        count += 1
      print(' {:4} variables with realm {}'.format(count, realm))
     xml_file.write('</cmip7_variables>\n')


    # Load the xml file:
    tree_main = ET.parse(xml_filename_realm_ordered)
    root_main = tree_main.getroot()

    print()
    xml_filename_priority_ordered = xml_filename_alphabetic_ordered.replace('alphabetic', 'priority')
    with open(xml_filename_priority_ordered, 'w') as xml_file:
     xml_file.write('<cmip7_variables dr_version="{}" api_version="{}">\n'.format(use_dreq_version, api_version))
     for priority in ["Core", "High", "Medium", "Low"]:
      count = 0
      xpath_expression = './/variable[@priority="' + priority + '"]'
      for element in root_main.findall(xpath_expression):
       write_xml_file_line_for_variable(xml_file, element)
       count += 1
      print(' {:4} variables with priority {}'.format(count, priority))
     xml_file.write('</cmip7_variables>\n')


    # Load the xml file:
    tree_main = ET.parse(xml_filename_realm_ordered)
    root_main = tree_main.getroot()

    print()
    xml_filename_frequency_ordered = xml_filename_alphabetic_ordered.replace('alphabetic', 'frequency')
    with open(xml_filename_frequency_ordered, 'w') as xml_file:
     xml_file.write('<cmip7_variables dr_version="{}" api_version="{}">\n'.format(use_dreq_version, api_version))
     for frequency in ["fx", "Efx", "AERfx", "Ofx", "IfxAnt", "IfxGre", \
                       "CFsubhr", "Esubhr", "E1hr", "E1hrClimMon", "AERhr", "3hr", "E3hr", "CF3hr", "3hrPt", "E3hrPt", "6hrPlev", "6hrPlevPt", "6hrLev", \
                       "day", "Eday", "EdayZ", "AERday", "CFday", "Oday", "SIday", \
                       "Amon", "Emon", "EmonZ", "CFmon", "AERmon", "AERmonZ", "Lmon", "LImon", "Omon", "SImon", "ImonAnt", "ImonGre", \
                       "Eyr", "Oyr", "IyrAnt", "IyrGre", \
                       "Odec"]:
      count = 0
      xpath_expression = './/variable[@cmip6_table="' + frequency + '"]'
      for element in root_main.findall(xpath_expression):
       write_xml_file_line_for_variable(xml_file, element)
       count += 1
      print(' {:4} variables with cmip6_table {}'.format(count, frequency))
     xml_file.write('</cmip7_variables>\n')


    if args.variables_metadata:
        # Get all variable names for all requested experiments
        all_var_names = set()
        for vars_by_priority in expt_vars['experiment'].values():
            for var_names in vars_by_priority.values():
                all_var_names.update(var_names)

        # Get metadata for variables
        all_var_info = dq.get_variables_metadata(
            base,
            use_dreq_version,
            compound_names=all_var_names,
            verbose=False,
        )

        # Write output file(s)
        filepath = args.variables_metadata
        dq.write_variables_metadata(
            all_var_info,
            use_dreq_version,
            filepath,
            api_version=data_request_api.version,
            content_path=dc._dreq_content_loaded['json_path']
        )


if __name__ == '__main__':
    main()
