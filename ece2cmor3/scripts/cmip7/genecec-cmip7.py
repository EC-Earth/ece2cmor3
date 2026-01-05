#!/usr/bin/env python
"""
Command line interface for retrieving EC-Earth3 configuration files based on the CMIP7 variable request per CMIP7 experiment.

Call example:
 cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/cmip7
 rm -f -r cmip7; ./genecec-cmip7.py --all_opportunities --experiment piControl,historical --variables_metadata metadata-of-requested-cmip7-variables.json --priority_cutoff high v1.2.2.3 --ececonf EC-Earth3-ESM-1 cmip7-requested-varlist-per-experiment.json &> genecec-cmip7.log
 grep Skip genecec-cmip7.log > summarize.log; echo '' >> summarize.log; grep -e 'Created' genecec-cmip7.log >> summarize.log; echo '' >> summarize.log; grep -e 'json' genecec-cmip7.log | grep -v -e INFO >> summarize.log

This script generates:
 for each CMIP7 requested experiment (or a list of CMIP7 experiments)
 for a given cutoff priority
 for all opportunities (default) or for a selection of oppertunities (or a list of oppertunities IDs)
 for a specified EC-Earth3 configuration (or a list of them)
the CMIP7 request including the mapping of the CMIP7 compound variables to the CMIP6 table - variable
combinations. All EC-Earth3 (CMIP6) identified variables are kept in the remaining request including
the so called EC-Earth3 component preferences depending on the EC-Earth3 configuration.


This script includes the consecutive genecec steps for creating the output-control-files for the EC-Earth3
configurations based on the CMIP7 experiment requests. These steps include:

Create the component request file (varlist) from the flat request file (based on the cmip7 request) by using drq2varlist:
 drq2varlist --drq flat-full-cmip7-request-historical-high.json --ececonf EC-EARTH-ESM-1 --varlist component-request-cmip7-historical-high-EC-EARTH-ESM-1.json

Create the request-overview file for the requested experiment for the selected EC-Earth3 configuration(s):
 checkvars -v --asciionly --drq flat-full-cmip7-request-historical-high.json --output request-overview-cmip7-historical-high-including-EC-EARTH-ESM-1-preferences.txt

Create the NEMO, IFS & LPJG configuration files:
 drq2file_def --basic_file_def_file ../../../../resources/xios-nemo-file_def-files/basic-cmip6-file_def_nemo.xml --vars component-request-cmip7-historical-high-EC-EARTH-ESM-1.json
 drq2ppt --vars component-request-cmip7-historical-high-EC-EARTH-ESM-1.json
 drq2ins --vars component-request-cmip7-historical-high-EC-EARTH-ESM-1.json

Create the TM% volume estimates:
 estimate_tm5_volume --vars component-request-cmip7-historical-high-EC-EARTH-ESM-1.json

Create the CMIP6 metadata template files for all active component of the used EC-Earth3 configuration (which thereafter is tweaked for CMIP7):
 ../../../modify-metadata-template.sh CMIP historical EC-EARTH-ESM-1 ../../../../resources/metadata-templates/metadata-cmip6-CMIP-piControl-template.json


This script is partly based on the script: CMIP7_DReq_Software/data_request_api/data_request_api/command_line/export_dreq_lists_json.py
with an intermediate step via the (local) script: cmip7-request.py
And it is partly pased on the genecec.py & genecec-per-mip-experiment.sh scripts.

"""

import sys
import json
import os
import subprocess
import argparse
from collections import OrderedDict

import data_request_api
import data_request_api.content.dreq_content as dc
import data_request_api.query.dreq_query as dq
from importlib.metadata import version

PACKAGE_NAME = "CMIP7_data_request_api"
print('The CMIP7 dreq python api version is: v{}'.format(version(PACKAGE_NAME)))


def parse_args():
    """
    Parse command-line arguments
    """

    parser = argparse.ArgumentParser(
        description='Retrieving EC-Earth3 configuration files based on the CMIP7 variable request per CMIP7 experiment.'
    )

    # Positional (mandatory) input arguments
    parser.add_argument('dreq_version', choices=dc.get_versions(), help="data request version")
    parser.add_argument('output_file'                            , help='file to write JSON output to')

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
    parser.add_argument('-c', '--ececonfs'          , type=parse_input_list                    , help='limit output to the specified EC-Earth3 configurations (space-delimited list, case sensitive)')

    return parser.parse_args()


def main():
    """
    main routine
    """
    args = parse_args()

    use_dreq_version = args.dreq_version


    # Define a dictionary with the EC-Earth3 configurations: normal configuration names related to the predfined ece2cmor configuration names:
    valid_ece_configurations = {
       "EC-Earth3"         : "EC-EARTH-AOGCM",
       "EC-Earth3-HR"      : "EC-EARTH-HR",
       "EC-Earth3-LR"      : "EC-EARTH-LR",
       "EC-Earth3-CC"      : "EC-EARTH-CC",
       "EC-Earth3-ESM-1"   : "EC-EARTH-ESM-1",
       "EC-Earth3-AerChem" : "EC-EARTH-AerChem",
       "EC-Earth3-Veg"     : "EC-EARTH-Veg",
       "EC-Earth3-Veg-LR"  : "EC-EARTH-Veg-LR"
    }

    # Define a dictionary for the relation between experiment and its parent MIP (don't know yet how to achieve this via cmip7 API interface):
    experiment_mip_relation = {
       "1pctCO2"                           :  "CMIP",
       "1pctCO2-bgc"                       :  "C4MIP",
       "1pctCO2-rad"                       :  "C4MIP",
       "abrupt-0p5CO2"                     :  "CFMIP",
       "abrupt-2xCO2"                      :  "CFMIP",
       "abrupt-4xCO2"                      :  "CMIP",
       "abrupt-127k"                       :  "PMIP",
       "amip"                              :  "CMIP",
       "amip-irr"                          :  "IRRMIP",
       "amip-m4K"                          :  "CFMIP",
       "amip-noirr"                        :  "IRRMIP",
       "amip-p4k"                          :  "CFMIP",
       "amip-p4K-SST-rad"                  :  "CFMIP",
       "amip-p4K-SST-turb"                 :  "CFMIP",
       "amip-piForcing"                    :  "CFMIP",
       "dcppA-assim"                       :  "DCPP",
       "dcppA-hindcast"                    :  "DCPP",
       "dcppB-forecast"                    :  "DCPP",
       "dcppB-forecast-cmip6"              :  "DCPP",
       "esm-flat10"                        :  "C4MIP",
       "esm-flat10-cdr"                    :  "C4MIP",
       "esm-flat10-zec"                    :  "C4MIP",
       "esm-hist"                          :  "CMIP",
       "esm-piControl"                     :  "CMIP",
       "esm-s7h-noFireChange"              :  "FireMIP",
       "esm-scen7-h-Aer"                   :  "AerChemMIP2",
       "esm-scen7-h-AQ"                    :  "AerChemMIP2",
       "esm-scen7-hc"                      :  "ScenarioMIP",
       "esm-scen7-hc-ext"                  :  "ScenarioMIP",
       "esm-scen7-hc-ext-os"               :  "ScenarioMIP",
       "esm-scen7-lc"                      :  "ScenarioMIP",
       "esm-scen7-lc-ext"                  :  "ScenarioMIP",
       "esm-scen7-mc"                      :  "ScenarioMIP",
       "esm-scen7-mc-ext"                  :  "ScenarioMIP",
       "esm-scen7-mlc"                     :  "ScenarioMIP",
       "esm-scen7-mlc-ext"                 :  "ScenarioMIP",
       "esm-scen7-vlho-Aer"                :  "AerChemMIP2",
       "esm-scen7-vlho-AQ"                 :  "AerChemMIP2",
       "esm-scen7-vlhoc"                   :  "ScenarioMIP",
       "esm-scen7-vlhoc-ext"               :  "ScenarioMIP",
       "esm-scen7-vlloc"                   :  "ScenarioMIP",
       "esm-scen7-vlloc-ext"               :  "ScenarioMIP",
       "esm-up2p0"                         :  "TIPMIP",
       "esm-up2p0-gwl1p5"                  :  "TIPMIP",
       "esm-up2p0-gwl2p0"                  :  "TIPMIP",
       "esm-up2p0-gwl2p0-50y-dn2p0"        :  "TIPMIP",
       "esm-up2p0-gwl3p0"                  :  "TIPMIP",
       "esm-up2p0-gwl4p0"                  :  "TIPMIP",
       "esm-up2p0-gwl4p0-50y-dn2p0"        :  "TIPMIP",
       "esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0" :  "TIPMIP",
       "esm-up2p0-gwl5p0"                  :  "TIPMIP",
       "g7-15k-sai"                        :  "GeoMIP",
       "highres-future-xxx"                :  "HighResMIP",
       "highresSST-pxxkpat"                :  "HighResMIP",
       "hist-1950"                         :  "HighResMIP",
       "hist-aer"                          :  "DAMIP",
       "hist-GHG"                          :  "DAMIP",
       "hist-irr"                          :  "IRRMIP",
       "hist-nat"                          :  "DAMIP",
       "hist-noFire"                       :  "FireMIP",
       "hist-noirr"                        :  "IRRMIP",
       "hist-piAer"                        :  "AerChemMIP2",
       "hist-piAQ"                         :  "AerChemMIP2",
       "historical"                        :  "CMIP",
       "land-hist"                         :  "LMIP",
       "piClim-4xCO2"                      :  "CMIP",
       "piClim-aer"                        :  "RFMIP",
       "piClim-anthro"                     :  "CMIP",
       "piClim-CH4"                        :  "AerChemMIP2",
       "piClim-control"                    :  "CMIP",
       "piClim-histaer"                    :  "RFMIP",
       "piClim-histall"                    :  "RFMIP",
       "piClim-N2O"                        :  "AerChemMIP2",
       "piClim-NOX"                        :  "AerChemMIP2",
       "piClim-ODS"                        :  "AerChemMIP2",
       "piClim-SO2"                        :  "AerChemMIP2",
       "piControl"                         :  "CMIP",
       "scen7-hc"                          :  "ScenarioMIP",
       "scen7-hc-ext"                      :  "ScenarioMIP",
       "scen7-hc-ext-os"                   :  "ScenarioMIP",
       "scen7-lc"                          :  "ScenarioMIP",
       "scen7-lc-ext"                      :  "ScenarioMIP",
       "scen7-mc"                          :  "ScenarioMIP",
       "scen7-mc-ext"                      :  "ScenarioMIP",
       "scen7-mlc"                         :  "ScenarioMIP",
       "scen7-mlc-ext"                     :  "ScenarioMIP",
       "scen7-vlhoc"                       :  "ScenarioMIP",
       "scen7-vlhoc-ext"                   :  "ScenarioMIP",
       "scen7-vlloc"                       :  "ScenarioMIP",
       "scen7-vlloc-ext"                   :  "ScenarioMIP"
    }


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


    # Construct output
    if len(expt_vars['experiment']) > 0:

        # Show user what was found
        dq.show_requested_vars_summary(expt_vars, use_dreq_version)

        # Write json file with the variable lists
        content_path = dc._dreq_content_loaded['json_path']
        outfile = args.output_file
        dq.write_requested_vars_json(outfile, expt_vars, use_dreq_version, args.priority_cutoff, content_path)

       #print(json.dumps(expt_vars['experiment'],sort_keys=True, indent=4))

        duplicate_messages = []   # A list collecting the duplicate messages in order to print them afterwards for pretty printing

        for experiment, priority_groups in expt_vars['experiment'].items():
         # Initialize an empty dictionary at the start of each experiment:
         flat_request = {}
        #print('{} {}'.format(experiment, priority_groups))
        #print('\n\nCMIP7 experiment: {}\n'.format(experiment))
         print('')
         for priority_group, variable_list in priority_groups.items():
         #print('\nCMIP7 priority group: {}\n'.format(priority_group))
          print('\nCMIP7 experiment: {}; CMIP7 priority group: {}\n'.format(experiment, priority_group))
         #print('{} {}'.format(priority_group, variable_list))
          print('{:65} {:40} {:13} {}'.format('CMIP7 compound name', 'CMIP7 branded variable name', 'CMIP6 table', 'CMIP6 CMOR variable name'))
          for compound_var in variable_list:
           var_metadata = dq.get_variables_metadata(base, use_dreq_version, compound_names=compound_var, verbose=False)
          #print('{}'.format(compound_var))
          #print('{}\n'.format(var_metadata))
          #print('{}\n'.format(var_metadata[compound_var]))
         ##for attribute, value in sorted(var_metadata[compound_var].items()):
         ## print('{:40} {}'.format(attribute, value))
         ##print('')
           # Here the CMIP7 - CMIP6 mapping is achieved: The CMIP7 compound name is linked to the CMIP6 table - cmor variable name combination:
           cmip6_table    = var_metadata[compound_var]['cmip6_table']               # CMIP6 cmor table    name
           cmip6_variable = var_metadata[compound_var]['physical_parameter_name']   # CMIP6 cmor variable name
           print('{:65} {:40} {:13} {}'.format(compound_var, var_metadata[compound_var]['branded_variable_name'], cmip6_table, cmip6_variable))
          #print('MIPS per var: {}'.format(dr.find_mips_per_variable(compound_var)))
           if cmip6_table in flat_request:
            # If the CMIP6 table is already present in the flat request json list then no action for the CMIP6 table part is needed.
           #print('flat_request: {}'.format(flat_request))
           #print('flat_request[cmip6_table]: {}'.format(flat_request[cmip6_table]))
            if cmip6_variable in flat_request[cmip6_table]:
             duplicate_messages.append(' Skip duplicate cmip6 table - variable combination: {:10} {:13} coming from the cmip7 request: {:18} {}'.format(cmip6_table, cmip6_variable, compound_var, experiment))
            else:
             # Add another variable to an already created CMIP6 table in the float request json list:
             flat_request[cmip6_table].append(cmip6_variable)
           else:
            # If the CMIP6 table is not yet present in the flat request json list then the CMIP6 table has to be added to the flat request json list:
           #print('{}'.format(cmip6_table))
           #print('flat_request: {}'.format(flat_request))
            # Add a first variable as the first element of a list for a new encounterd table:
            flat_request.update({cmip6_table: [cmip6_variable]})

        #print('flat_request: {}'.format(flat_request))


         # The genecec part (continuing with and based on the flat CMIP7 request file):

         # Read the list of specified EC-Earth3 configurations:
         if args.ececonfs:
          ececonfs = args.ececonfs
          if ececonfs == ['all']:
           ececonfs = valid_ece_configurations
          else:
             valid_ececonfs   = [entry for entry in ececonfs if entry     in valid_ece_configurations]
             invalid_ececonfs = [entry for entry in ececonfs if entry not in valid_ece_configurations]
             if invalid_ececonfs:
                 raise ValueError('\n Invalid user specified EC-Earth3 configuration names: ' + ', '.join(sorted(invalid_ececonfs, key=str.lower)) +
                                  '\n Valid   user specified EC-Earth3 configuration names: ' + ', '.join(sorted(valid_ececonfs  , key=str.lower)) +
                                  '\n \n Valid EC-Earth3 configuration names are: ' + ', '.join(valid_ece_configurations.keys()))

         # Selected the EC-Earth3 configuration:
         for ececonf in ececonfs:
          ececonf_in_ece2cmor = valid_ece_configurations[ececonf]
          print('\n Creating the output-control-files for EC-Earth configuration: {}'.format(ececonf))

          flat_request_file_name = 'flat-full-cmip7-request-for-' + experiment + '-' + args.priority_cutoff + '.json'
          dir_name = 'cmip7/' + experiment + '-' + args.priority_cutoff  + '-' + ececonf
          previous_working_dir = os.getcwd()
          subprocess.run(["mkdir", "-p", dir_name])
          os.chdir(dir_name)
          with open(flat_request_file_name, 'w') as outfile:
              json.dump(flat_request, outfile, sort_keys=True, indent=4)
          outfile.close()

          component_request_file_name = 'component-request-cmip7-' + experiment + '-' + args.priority_cutoff + '-' + ececonf + '.json'
          subprocess.run(["drq2varlist", "--drq", flat_request_file_name, "--ececonf", ececonf_in_ece2cmor, "--varlist", component_request_file_name])
          request_overview_filename = 'request-overview-cmip7-' + experiment + '-' + args.priority_cutoff + '-including-' + ececonf + '-preferences.txt'
          subprocess.run(["checkvars", "-v", "--asciionly", "--drq", flat_request_file_name, "--output", request_overview_filename])
         #subprocess.run(["checkvars", "-v",                "--drq", flat_request_file_name, "--output", request_overview_filename])

          subprocess.run(["drq2file_def", "--basic_file_def_file", "../../../../resources/xios-nemo-file_def-files/basic-cmip6-file_def_nemo.xml", "--vars", component_request_file_name])
          command_01 = "sed -i -e 's/uoce_e3u_vsum_e2u_cumul. freq_op=.1ts/uoce_e3u_vsum_e2u_cumul/' file_def_nemo-opa.xml"
          command_02 = "sed -i -e '/deptho/d' file_def_nemo-opa.xml"
          command_03 = "sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' file_def_nemo*"
          os.system(command_01)
          os.system(command_02)
          os.system(command_03)
          subprocess.run(["rm", "-f", "cmip6-file_def_nemo.xml"])

          subprocess.run(["drq2ppt", "--vars", component_request_file_name])
          subprocess.run(["drq2ins", "--vars", component_request_file_name])

          # Estimating the Volume of the TM5 output:
          subprocess.run(["estimate_tm5_volume", "--vars", component_request_file_name])

          command_04 = "cat request-overview-cmip7-*.available.txt volume-estimate-ifs.txt volume-estimate-nemo.txt volume-estimate-tm5.txt volume-estimate-lpj-guess.txt > " + request_overview_filename
          command_05 = "rm -f volume-estimate-*.txt *txt.available.txt"
          command_06 = "if [ -f pptdddddd0100 ]; then rm -f pptdddddd0100 ; fi" # Removing the hourly / sub hourly table variables.
          os.system(command_04)
          os.system(command_05)
          os.system(command_06)

          # Produce the metadata files for this MIP experiment:
          mip_name = experiment_mip_relation[experiment]
          subprocess.run(["../../../modify-metadata-template.sh", mip_name, experiment, ececonf_in_ece2cmor, "../../../../resources/metadata-templates/metadata-cmip6-CMIP-piControl-template.json"])
          # This could be considered to do right a way from here (at the python level).
          # For CMIP7 it would be nice to be able to request the parent_experiment for each experiment (same as for the MIP).
          # It would be pretty to be able to drop the licence from the mtadata template - however to be able to adjust it at a certain level remains fafourable

          # Rename the metadata files such that the cmip6 label becomes cmip7:
          for filename in os.listdir("."):
           if filename.startswith("metadata-cmip6"):
            os.rename(filename, filename.replace("cmip6", "cmip7").replace("EC-EARTH", "EC-Earth3"))

          command_07 = "sed -i -e 's/cmip6-data@ec-earth.org/ec-earth-data-questions@ec-earth.org/'  -e 's/CMIP6/CMIP7/g' -e /cmip6_option/d  metadata-cmip*-template.json"
          os.system(command_07)

          os.chdir(previous_working_dir)

        for message in duplicate_messages:
         print(message)
        print()


    else:
        print(f'\nFor data request version {use_dreq_version}, no requested variables were found')


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




#  1pctCO2                           CMIP                 150       [damip_experiment_group, deck, deck_idealized_co2_experiments, dynvar, pmip, synoptic_systems_and_impacts, temperature_variability_opportunity                                   ]
#  1pctCO2-bgc                       C4MIP                150       [damip_experiment_group, fast-track, temperature_variability_opportunity                                                                                                         ]
#  1pctCO2-rad                       C4MIP                150       [damip_experiment_group, fast-track, temperature_variability_opportunity                                                                                                         ]
#  abrupt-0p5CO2                     CFMIP                300       [fast-track, fast-track_cfmip, pmip                                                                                                                                              ]
#  abrupt-2xCO2                      CFMIP                300       [fast-track, fast-track_cfmip, pmip                                                                                                                                              ]
#  abrupt-4xCO2                      CMIP                 300       [damip_experiment_group, deck, deck_idealized_co2_experiments, dynvar, pmip, synoptic_systems_and_impacts, temperature_variability_opportunity                                   ]
#  abrupt-127k                       PMIP                 100       [fast-track, pmip                                                                                                                                                                ]
#  amip                              CMIP                 42        [cfmip_amip_amip4K, climate_extreme, damip_experiment_group, deck, dynvar, synoptic_systems_and_impacts, temperature_variability_opportunity                                     ]
#  amip-irr                          IRRMIP               122       [all-non-fasttrack, irrmip-nonfasttrack                                                                                                                                          ]
#  amip-m4K                          CFMIP                44        [all-non-fasttrack, cfmip-additional-nonfasttrack                                                                                                                                ]
#  amip-noirr                        IRRMIP               122       [all-non-fasttrack, irrmip-nonfasttrack                                                                                                                                          ]
#  amip-p4k                          CFMIP                36        [cfmip_amip_amip4K, damip_experiment_group, dynvar, fast-track, fast-track_cfmip, synoptic_systems_and_impacts, temperature_variability_opportunity                              ]
#  amip-p4K-SST-rad                  CFMIP                44        [all-non-fasttrack, cfmip-additional-nonfasttrack                                                                                                                                ]
#  amip-p4K-SST-turb                 CFMIP                44        [all-non-fasttrack, cfmip-additional-nonfasttrack                                                                                                                                ]
#  amip-piForcing                    CFMIP                145       [damip_experiment_group, fast-track, fast-track_cfmip                                                                                                                            ]
#  dcppA-assim                       DCPP                 56        [all-non-fasttrack, dcpp-cmip6-exps                                                                                                                                              ]
#  dcppA-hindcast                    DCPP                 5         [all-non-fasttrack, dcpp-cmip6-exps                                                                                                                                              ]
#  dcppB-forecast                    DCPP                 5         [all-non-fasttrack, dcpp-cmip6-exps                                                                                                                                              ]
#  dcppB-forecast-cmip6              DCPP                 10        [damip_experiment_group, dcpp, fast-track, firemip_fast-track_subset, impact_climserv_core_expt, temperature_variability_opportunity                                             ]
#  esm-flat10                        C4MIP                150       [fast-track                                                                                                                                                                      ]
#  esm-flat10-cdr                    C4MIP                200       [fast-track                                                                                                                                                                      ]
#  esm-flat10-zec                    C4MIP                200       [fast-track                                                                                                                                                                      ]
#  esm-hist                          CMIP                 172       [damip_experiment_group, deck, dynvar, firemip_fast-track_subset, historical, impact_climserv_core_expt, pmip, synoptic_systems_and_impacts, temperature_variability_opportunity ]
#  esm-piControl                     CMIP                 400       [damip_experiment_group, deck, dynvar, picontrol, pmip, synoptic_systems_and_impacts, temperature_variability_opportunity                                                        ]
#  esm-s7h-noFireChange              FireMIP              10        [all-non-fasttrack, firemip-nonfasttrack                                                                                                                                         ]
#  esm-scen7-h-Aer                   AerChemMIP2          104       [aerchemmip, fast-track                                                                                                                                                          ]
#  esm-scen7-h-AQ                    AerChemMIP2          104       [aerchemmip, fast-track                                                                                                                                                          ]
#  esm-scen7-hc                      ScenarioMIP          75        [dynvar, fast-track, scenarios                                                                                                                                                   ]
#  esm-scen7-hc-ext                  ScenarioMIP          50        [all-non-fasttrack, dynvar, ismip7-scenario-extensions, scenarios_extensions, scenarios_extensions-low-medium-high                                                               ]
#  esm-scen7-hc-ext-os               ScenarioMIP          50        [all-non-fasttrack, ismip7-scenario-extensions, scenarios_extensions                                                                                                             ]
#  esm-scen7-lc                      ScenarioMIP          75        [dynvar, fast-track, scenarios                                                                                                                                                   ]
#  esm-scen7-lc-ext                  ScenarioMIP          50        [all-non-fasttrack, dynvar, scenarios_extensions, scenarios_extensions-low-medium-high                                                                                           ]
#  esm-scen7-mc                      ScenarioMIP          75        [climate_extreme, dynvar, fast-track, scenarios                                                                                                                                  ]
#  esm-scen7-mc-ext                  ScenarioMIP          50        [all-non-fasttrack, dynvar, ismip7-scenario-extensions, scenarios_extensions, scenarios_extensions-low-medium-high                                                               ]
#  esm-scen7-mlc                     ScenarioMIP          75        [dynvar, fast-track, scenarios                                                                                                                                                   ]
#  esm-scen7-mlc-ext                 ScenarioMIP          50        [all-non-fasttrack, dynvar, ismip7-scenario-extensions, scenarios_extensions                                                                                                     ]
#  esm-scen7-vlho-Aer                AerChemMIP2          104       [aerchemmip, fast-track                                                                                                                                                          ]
#  esm-scen7-vlho-AQ                 AerChemMIP2          104       [aerchemmip, fast-track                                                                                                                                                          ]
#  esm-scen7-vlhoc                   ScenarioMIP          75        [fast-track, scenarios                                                                                                                                                           ]
#  esm-scen7-vlhoc-ext               ScenarioMIP          50        [all-non-fasttrack, scenarios_extensions                                                                                                                                         ]
#  esm-scen7-vlloc                   ScenarioMIP          75        [fast-track, scenarios                                                                                                                                                           ]
#  esm-scen7-vlloc-ext               ScenarioMIP          50        [all-non-fasttrack, ismip7-scenario-extensions, scenarios_extensions                                                                                                             ]
#  esm-up2p0                         TIPMIP               200       [all-non-fasttrack, tipmip-experiments                                                                                                                                           ]
#  esm-up2p0-gwl1p5                  TIPMIP               300       [all-non-fasttrack, tipmip-experiments                                                                                                                                           ]
#  esm-up2p0-gwl2p0                  TIPMIP               300       [all-non-fasttrack, tipmip-experiments                                                                                                                                           ]
#  esm-up2p0-gwl2p0-50y-dn2p0        TIPMIP               100       [all-non-fasttrack, tipmip-experiments                                                                                                                                           ]
#  esm-up2p0-gwl3p0                  TIPMIP               300       [all-non-fasttrack, tipmip-experiments                                                                                                                                           ]
#  esm-up2p0-gwl4p0                  TIPMIP               300       [all-non-fasttrack, tipmip-experiments                                                                                                                                           ]
#  esm-up2p0-gwl4p0-50y-dn2p0        TIPMIP               200       [all-non-fasttrack, tipmip-experiments                                                                                                                                           ]
#  esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0 TIPMIP               300       [all-non-fasttrack, tipmip-experiments                                                                                                                                           ]
#  esm-up2p0-gwl5p0                  TIPMIP               300       [all-non-fasttrack, tipmip-experiments                                                                                                                                           ]
#  g7-15k-sai                        GeoMIP               50        [dynvar, fast-track, impact_climserv_core_expt, synoptic_systems_and_impacts, temperature_variability_opportunity                                                                ]
#  highres-future-xxx                HighResMIP           78        [all-non-fasttrack, highresmip2-ia                                                                                                                                               ]
#  highresSST-pxxkpat                HighResMIP           20        [all-non-fasttrack, highresmip2-ia                                                                                                                                               ]
#  hist-1950                         HighResMIP           73        [all-non-fasttrack, highresmip2-ia                                                                                                                                               ]
#  hist-aer                          DAMIP                186       [climate_extreme, damip_experiment_group, fast-track, firemip_fast-track_subset, impact_climserv_core_expt, synoptic_systems_and_impacts, temperature_variability_opportunity    ]
#  hist-GHG                          DAMIP                186       [climate_extreme, damip_experiment_group, fast-track, firemip_fast-track_subset, impact_climserv_core_expt, synoptic_systems_and_impacts, temperature_variability_opportunity    ]
#  hist-irr                          IRRMIP               122       [all-non-fasttrack, irrmip-nonfasttrack                                                                                                                                          ]
#  hist-nat                          DAMIP                172       [climate_extreme, damip_experiment_group, fast-track, firemip_fast-track_subset, impact_climserv_core_expt, synoptic_systems_and_impacts, temperature_variability_opportunity    ]
#  hist-noFire                       FireMIP              172       [all-non-fasttrack, firemip-nonfasttrack                                                                                                                                         ]
#  hist-noirr                        IRRMIP               122       [all-non-fasttrack, irrmip-nonfasttrack                                                                                                                                          ]
#  hist-piAer                        AerChemMIP2          172       [aerchemmip, damip_experiment_group, fast-track                                                                                                                                  ]
#  hist-piAQ                         AerChemMIP2          172       [aerchemmip, damip_experiment_group, fast-track                                                                                                                                  ]
#  historical                        CMIP                 171       [damip_experiment_group, deck, dynvar, firemip_fast-track_subset, historical, impact_climserv_core_expt, pmip, synoptic_systems_and_impacts, temperature_variability_opportunity ]
#  land-hist                         LMIP                 172       [fast-track, firemip_fast-track_subset, impact_climserv_core_expt, lmip                                                                                                          ]
#  piClim-4xCO2                      CMIP                 30        [deck, firemip_deck_subset                                                                                                                                                       ]
#  piClim-aer                        RFMIP                30        [aerchemmip, fast-track                                                                                                                                                          ]
#  piClim-anthro                     CMIP                 30        [damip_experiment_group, deck, firemip_deck_subset                                                                                                                               ]
#  piClim-CH4                        AerChemMIP2          30        [aerchemmip, fast-track                                                                                                                                                          ]
#  piClim-control                    CMIP                 30        [deck, firemip_deck_subset                                                                                                                                                       ]
#  piClim-histaer                    RFMIP                30        [fast-track                                                                                                                                                                      ]
#  piClim-histall                    RFMIP                30        [fast-track                                                                                                                                                                      ]
#  piClim-N2O                        AerChemMIP2          30        [aerchemmip, fast-track                                                                                                                                                          ]
#  piClim-NOX                        AerChemMIP2          30        [aerchemmip, fast-track                                                                                                                                                          ]
#  piClim-ODS                        AerChemMIP2          30        [aerchemmip, fast-track                                                                                                                                                          ]
#  piClim-SO2                        AerChemMIP2          30        [aerchemmip, fast-track                                                                                                                                                          ]
#  piControl                         CMIP                 400       [damip_experiment_group, deck, dynvar, firemip_deck_subset, picontrol, pmip, synoptic_systems_and_impacts, temperature_variability_opportunity                                   ]
#  scen7-hc                          ScenarioMIP          75        [dynvar, fast-track, scenarios                                                                                                                                                   ]
#  scen7-hc-ext                      ScenarioMIP          50        [all-non-fasttrack, conc-driven-scenario-extensions, dynvar, ismip7-scenario-extensions, scenarios_extensions, scenarios_extensions-low-medium-high                              ]
#  scen7-hc-ext-os                   ScenarioMIP          50        [all-non-fasttrack, conc-driven-scenario-extensions, ismip7-scenario-extensions, scenarios_extensions                                                                            ]
#  scen7-lc                          ScenarioMIP          75        [dynvar, fast-track, scenarios                                                                                                                                                   ]
#  scen7-lc-ext                      ScenarioMIP          50        [all-non-fasttrack, conc-driven-scenario-extensions, dynvar, scenarios_extensions, scenarios_extensions-low-medium-high                                                          ]
#  scen7-mc                          ScenarioMIP          75        [climate_extreme, dynvar, fast-track, scenarios                                                                                                                                  ]
#  scen7-mc-ext                      ScenarioMIP          50        [all-non-fasttrack, conc-driven-scenario-extensions, dynvar, ismip7-scenario-extensions, scenarios_extensions, scenarios_extensions-low-medium-high                              ]
#  scen7-mlc                         ScenarioMIP          75        [dynvar, fast-track, scenarios                                                                                                                                                   ]
#  scen7-mlc-ext                     ScenarioMIP          50        [all-non-fasttrack, conc-driven-scenario-extensions, dynvar, ismip7-scenario-extensions, scenarios_extensions                                                                    ]
#  scen7-vlhoc                       ScenarioMIP          75        [fast-track, scenarios                                                                                                                                                           ]
#  scen7-vlhoc-ext                   ScenarioMIP          50        [all-non-fasttrack, conc-driven-scenario-extensions, scenarios_extensions                                                                                                        ]
#  scen7-vlloc                       ScenarioMIP          75        [fast-track, scenarios                                                                                                                                                           ]
#  scen7-vlloc-ext                   ScenarioMIP          50        [all-non-fasttrack, conc-driven-scenario-extensions, ismip7-scenario-extensions, scenarios_extensions                                                                            ]





#  AERA-MIP          "Adaptive Emission Reduction Approach Modelling Intercomparison Project                      "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      missing
#  AerChemMIP        "Aerosols and Chemistry Model Intercomparison Project                                        "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://wiki.met.no/aerocom/aerchemmip/start
#  AerChemMIP2       "Aerosol Chemistry Model Intercomparison Project phase 2                                     "     [esm-scen7-h-Aer, esm-scen7-h-AQ, esm-scen7-vlho-Aer, esm-scen7-vlho-AQ, hist-piAer, hist-piAQ, piClim-CH4, piClim-N2O, piClim-NOX, piClim-ODS, piClim-SO2                                                                                                                                                                                                                                                       ]      https://wiki.met.no/aerocom/aerchemmip/start https://www.geomar.de/cacti
#  C4MIP             "Coupled Climate Carbon Cycle MIP                                                            "     [1pctCO2-bgc, 1pctCO2-rad, esm-flat10, esm-flat10-cdr, esm-flat10-zec                                                                                                                                                                                                                                                                                                                                            ]      https://c4mip.net/home
#  CDRMIP            "Carbon Dioxide Removal Model Intercomparison Project                                        "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://cdrmip.carbondioxide-removal.eu/
#  CERESMIP          "CERES-era Model Intercomparison Project                                                     "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://data.giss.nasa.gov/CERESMIP    (not yet live)
#  CFMIP             "CloudFeedback Model Intercomparison Project                                                 "     [abrupt-0p5CO2, abrupt-2xCO2, amip-m4K, amip-p4k, amip-p4K-SST-rad, amip-p4K-SST-turb, amip-piForcing                                                                                                                                                                                                                                                                                                            ]      www.cfmip.org
#  CMIP              "Coupled Model Intercomparison Project                                                       "     [1pctCO2, abrupt-4xCO2, amip, esm-hist, esm-piControl, historical, piClim-4xCO2, piClim-anthro, piClim-control, piControl                                                                                                                                                                                                                                                                                        ]      https://www.wcrp-cmip.org/
#  CORDEX            "Coordinated Regional Climate Downscaling Experiment                                         "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://cordex.org
#  DAMIP             "Detection and Attribution Model Intercomparison Project                                     "     [hist-aer, hist-GHG, hist-nat                                                                                                                                                                                                                                                                                                                                                                                    ]      https://wcrp-cmip.org/damip/
#  DCPP              "Decadal Climate Prediction Project                                                          "     [dcppA-assim, dcppA-hindcast, dcppB-forecast, dcppB-forecast-cmip6                                                                                                                                                                                                                                                                                                                                               ]      https://www.wcrp-climate.org/dcp-overview
#  DynVarMIP         "Dynamics and Variability Model Intercomparison Project                                      "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://dynvarmip.github.io/
#  FAFMIP            "Flux-Anomaly-Forced Model Intercomparison Project                                           "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      http://www.fafmip.org
#  FireMIP           "Fire Modeling Intercomparison Project                                                       "     [esm-s7h-noFireChange, hist-noFire                                                                                                                                                                                                                                                                                                                                                                               ]      https://www.senckenberg.de/en/institutes/sbik-f/quantitative-biogeography/qb-projects/firemip/
#  FishMIP           "Fisheries and Marine Ecosystem Model Intercomparison Project                                "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://fishmip.org/
#  GeoMIP            "Geoengineering Model Intercomparison Project                                                "     [g7-15k-sai                                                                                                                                                                                                                                                                                                                                                                                                      ]      http://climate.envsci.rutgers.edu/GeoMIP/
#  GMMIP             "Global Monsoons Model Intercomparison Project                                               "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      http://www.met.rdg.ac.uk/~sws05agt//MonsoonMIP/
#  HighResMIP        "High Resolution Model Intercomparison Project                                               "     [highres-future-xxx, highresSST-pxxkpat, hist-1950                                                                                                                                                                                                                                                                                                                                                               ]      https://www.highresmip.org
#  HT-MIP/VolMIP     "Joint Hunga-Tonga-MIP and VolMIP "DuoForcer" major phreato-Plinian forced-responseexperiment"     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://www.sparc-climate.org/activities/hunga-tonga/
#  IRRMIP            "Irrigation Model Intercomparison Project                                                    "     [amip-irr, amip-noirr, hist-irr, hist-noirr                                                                                                                                                                                                                                                                                                                                                                      ]      https://hydr.vub.be/projects/irrmip
#  ISIMIP            "Inter-Sectoral Impact Model Intercomparison Project                                         "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://www.isimip.org/
#  ISMIP6            "Ice Sheet Model Intercomparison Project                                                     "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://climate-cryosphere.org/about-ismip6/
#  ISMIP7            "Ice Sheet Model Intercomparison Project for CMIP                                            "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://theghub.org/groups/ismip6/wiki
#  LMIP              "LandModel Intercomparison Project                                                           "     [land-hist                                                                                                                                                                                                                                                                                                                                                                                                       ]      https://cmip7.lmip.org
#  LongRunMIP        "LongRunMIP                                                                                  "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://www.longrunmip.org/
#  LS3MIP            "LandSurface, Snow and Soil Moistures Model Intercomparison Project                          "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://wiki.c2sm.ethz.ch/LS3MIP
#  LUMIP             "Land-Use Model Intercomparison Project                                                      "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://www.cesm.ucar.edu/projects/cmip6/lumip
#  MethaneMIP        "MethaneMIP: Investigating the near-term climate benefits of methane mitigation              "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      tba
#  MISOMIP2          "Marine Ice Sheet-Ocean Model Intercomparions Project                                        "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://misomip.github.io/
#  MUMIP             "ModelUncertainty Model Intercomparison Project                                              "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://mumip.web.ox.ac.uk
#  NAHosMIP          "North Atlantic Hosing Model Intercomparison Project                                         "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://www.tipes.dk/na-hosing-mip/
#  OMIP              "OceanModel Intercomparison Project                                                          "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://OceanMIP.github.io
#  PAMIP             "PolarAmplification Model Intercomparison Project                                            "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://www.cesm.ucar.edu/projects/cmip6/pamip
#  PMIP              "Paleoclimate Modelling Intercomparison Project                                              "     [abrupt-127k                                                                                                                                                                                                                                                                                                                                                                                                     ]      https://pmip.lsce.ipsl.fr/
#  PPEMIP            "Perturbed Parameter Ensemble Model Inter-comparaison Project                                "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      To be determined
#  RAMIP             "Regional Aerosol Model Intercomparison Project                                              "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://ramip.uk/
#  RFMIP             "Radiative Forcing Model Intercomparison Project                                             "     [piClim-aer, piClim-histaer, piClim-histall                                                                                                                                                                                                                                                                                                                                                                      ]      https://rfmip.leeds.ac.uk/
#  ScenarioMIP       "Scenario Model Intercomparison Project                                                      "     [esm-scen7-hc, esm-scen7-hc-ext, esm-scen7-hc-ext-os, esm-scen7-lc, esm-scen7-lc-ext, esm-scen7-mc, esm-scen7-mc-ext, esm-scen7-mlc, esm-scen7-mlc-ext, esm-scen7-vlhoc, esm-scen7-vlhoc-ext, esm-scen7-vlloc, esm-scen7-vlloc-ext, scen7-hc, scen7-hc-ext, scen7-hc-ext-os, scen7-lc, scen7-lc-ext, scen7-mc, scen7-mc-ext, scen7-mlc, scen7-mlc-ext, scen7-vlhoc, scen7-vlhoc-ext, scen7-vlloc, scen7-vlloc-ext]      https://wcrp-cmip.org/mips/scenariomip/
#  SIMIP             "SeaIce Model Intercomparison Project                                                        "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://climate-cryosphere.org/simip-about/
#  SOFIAMIP          "Southern Ocean Freshwater Input from Antarctica Model Intercomparison Project               "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://sofiamip.github.io/
#  SP-MIP            "SoilParameter Model Intercomparison Project                                                 "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      N/A
#  TBIMIP            "Tropical Basin Interaction Model Intercomparison Project                                    "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      https://www.clivar.org/research-foci/basin-interaction
#  TIPMIP            "Tipping Point Modelling Intercomparison Project                                             "     [esm-up2p0, esm-up2p0-gwl1p5, esm-up2p0-gwl2p0, esm-up2p0-gwl2p0-50y-dn2p0, esm-up2p0-gwl3p0, esm-up2p0-gwl4p0, esm-up2p0-gwl4p0-50y-dn2p0, esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0, esm-up2p0-gwl5p0                                                                                                                                                                                                                  ]      https://www.tipmip.org
#  VIACSAB           "Vulnerability, Impacts, Adaptation and Climate Services Advisory Board                      "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      http://viacsab.gerics.de
#  VolMIP            "Model Intercomparison Project on the climate response to Volcanic forcing                   "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      www.volmip.org
#  WhatIfMIP         "What If Modeling Intercomparison Project                                                    "     [                                                                                                                                                                                                                                                                                                                                                                                                                ]      In development

#  Other                                            


# Overview required metadata according to climate_ref:
#  https://github.com/Climate-REF/climate-ref/blob/16caf3f8f2e7154a5903dcf589a74510ed6bf820/packages/ref/src/cmip_ref/datasets/cmip6.py#L80

#   dataset_specific_metadata = (
#       "activity_id",
#       "branch_method",
#       "branch_time_in_child",
#       "branch_time_in_parent",
#       "experiment",
#       "experiment_id",
#       "frequency",
#       "grid",
#       "grid_label",
#       "institution_id",
#       "nominal_resolution",
#       "parent_activity_id",
#       "parent_experiment_id",
#       "parent_source_id",
#       "parent_time_units",
#       "parent_variant_label",
#       "product",
#       "realm",
#       "source_id",
#       "source_type",
#       "sub_experiment",
#       "sub_experiment_id",
#       "table_id",
#       "variable_id",
#       "variant_label",
#       "member_id",
#       "standard_name",
#       "long_name",
#       "units",
#       "vertical_levels",
#       "init_year",
#       "version",
#       slug_column,
#   )

