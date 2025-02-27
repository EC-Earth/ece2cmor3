#!/usr/bin/env python
# Thomas Reerink
#
# Run examples:
#  ./genecec.py config-genecec
#  ./run-genecec.sh default 001
#
# Looping over all MIPs and within each MIP over all its MIP experiments.
# The experiment tier can be selected. For each selected experiment the
# namelists are created by calling the genecec-per-mip-experiment.sh script.
#
# With this script it is possible to generate the EC-Earth3 control output files, i.e.
# the IFS Fortran namelists (the ppt files), the NEMO xml files for XIOS (the
# file_def files for OPA, LIM and PISCES) and the instruction files for LPJ_GUESS (the
# *.ins files) for all MIP experiments in which EC-Earth3 participates.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.


import sys
import os
import subprocess
from os.path import expanduser                                  # Enable to go to the home dir: ~
from dreqPy import dreq
dq = dreq.loadDreq()

#error_message   = '\n \033[91m' + 'Error:'   + '\033[0m'       # Red    error   message
#warning_message = '\n \033[93m' + 'Warning:' + '\033[0m'       # Yellow warning message
error_message   = '\n Error:'                                   #        error   message
warning_message = '\n Warning:'                                 #        warning message

if len(sys.argv) == 2:

   if __name__ == "__main__": config = {}                       # python config syntax

   config_filename = sys.argv[1]                                # Reading the config file name from the argument line
   if os.path.isfile(config_filename) == False:                 # Checking if the config file exists
    print(error_message, ' The config file ', config_filename, '  does not exist.\n')
    sys.exit()
   exec(open(config_filename).read(), config)                   # Reading the config file

   print()
   print(' The used ece2cmor3 environment: {:}'.format(subprocess.check_output('which ece2cmor'    , shell=True).decode('utf-8').strip("\n")))
   print(' The used drq       version:     {:}'.format(subprocess.check_output('drq -v'            , shell=True)[0:42].decode('utf-8').strip("\n")))
   print(' The used python    version:     {:}'.format(os.sys.version[0:68]))
   print(' The used python    version:     {:}'.format(os.sys.version_info))
   print(' The used dreqPy    version:     {:}'.format(dreq.version))
   print(' The used ece2cmor3 version:     ', end='', flush=True)
   subprocess.check_output('ece2cmor --version', shell=True).decode('utf-8').strip("\n")
  #print(' The used ece2cmor3 version:     {:}'.format(subprocess.check_output('ece2cmor --version', shell=True).decode('utf-8').strip("\n"))) # output printed line before?
   print()

   output_dir_name         = os.path.expanduser(config['output_dir_name'        ])  # output_dir_name                = 'output-control-files/'
   activate_pextra_mode    =                    config['activate_pextra_mode'   ]   # activate_pextra_mode           = False
   add_request_overview    =                    config['add_request_overview'   ]   # add_request_overview           = True
   ece2cmor_root_directory = os.path.expanduser(config['ece2cmor_root_directory'])  # ece2cmor_root_directory        = '~/cmorize/ece2cmor3/'

   # Run ece2cmor's install & check whether an existing ece2cmor root directory is specified in the config file:
   previous_working_dir = os.getcwd()
   if os.path.isdir(ece2cmor_root_directory) == False:
    print(error_message, ' The ece2cmor root directory ', ece2cmor_root_directory, ' does not exist.\n')
    sys.exit()
   if os.path.isfile(ece2cmor_root_directory + '/environment.yml') == False:
    print(error_message, ' The ece2cmor root directory ', ece2cmor_root_directory, ' is not an ece2cmor root directory.\n')
    sys.exit()
   os.chdir(ece2cmor_root_directory)
   os.system('pip install -e .')
   os.chdir(previous_working_dir)

   if output_dir_name[-1] != '/':
    output_dir_name = output_dir_name + '/'

   if activate_pextra_mode:
    cmip6_base_dir_name = output_dir_name + 'cmip6-pextra/'
    os.system('./switch-on-off-pextra-mode.sh activate-pextra-mode')
   else:
    cmip6_base_dir_name = output_dir_name + 'cmip6/'


   # Specify in the list below which tier experiments should be included. For
   # instance [1,2] means tier 1 and tier 2 experiments are included:
   experiment_tiers_included = [1]
   ec_earth_mips  = ['CMIP', 'AerChemMIP', 'CDRMIP', 'C4MIP',                   'DCPP',                              'HighResMIP', 'LS3MIP', 'LUMIP', 'OMIP', 'PAMIP', 'PMIP', 'RFMIP', 'ScenarioMIP', 'VolMIP', 'CORDEX', 'DynVarMIP', 'SIMIP', 'VIACSAB'] # All 19 EC-Earth MIPs


   # The list of MIPs for each of the eight EC-Earth3 model configurations which run CMIP in an iterable dictionary. This lists are needed in order
   # to request the joint CMIP6 data requests for each of the EC-Earth3 model configurations:
   cmip_ece_configurations = {
    'EC-EARTH-AOGCM'   : 'CMIP,DCPP,LS3MIP,PAMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB',
    'EC-EARTH-HR'      : 'CMIP,DCPP,HighResMIP',
    'EC-EARTH-LR'      : 'CMIP,PMIP',
    'EC-EARTH-CC'      : 'C4MIP,CDRMIP,CMIP,LUMIP,OMIP,ScenarioMIP',
    'EC-EARTH-ESM-1'   : 'C4MIP,CDRMIP,CMIP,LUMIP,OMIP,ScenarioMIP',
    'EC-EARTH-AerChem' : 'AerChemMIP,CMIP,RFMIP',
    'EC-EARTH-Veg'     : 'CDRMIP,CMIP,LUMIP,LS3MIP,ScenarioMIP',
    'EC-EARTH-Veg-LR'  : 'CMIP,PMIP,ScenarioMIP'
   }

   # The list of MIPs for each of the four EC-Earth3 model configurations which run ScenarioMIP in an iterable dictionary. This lists are needed in order
   # to request the joint CMIP6 data requests for each of the EC-Earth3 model configurations:
   scenario_ece_configurations = {
    'EC-EARTH-AOGCM'   : 'CMIP,DCPP,LS3MIP,ScenarioMIP,CORDEX,DynVarMIP,VIACSAB',
    'EC-EARTH-CC'      : 'C4MIP,CDRMIP,CMIP,LUMIP,OMIP,ScenarioMIP',
    'EC-EARTH-ESM-1'   : 'C4MIP,CDRMIP,CMIP,LUMIP,OMIP,ScenarioMIP',
    'EC-EARTH-AerChem' : 'AerChemMIP,CMIP,RFMIP,ScenarioMIP',
    'EC-EARTH-Veg'     : 'CMIP,LUMIP,LS3MIP,ScenarioMIP',
    'EC-EARTH-Veg-LR'  : 'CMIP,PMIP,ScenarioMIP'
   }

   #ec_earth_mips = ['CMIP', 'AerChemMIP', 'CDRMIP', 'C4MIP', 'CFMIP', 'DAMIP', 'DCPP', 'FAFMIP', 'GeoMIP', 'GMMIP', 'HighResMIP', 'LS3MIP', 'LUMIP', 'OMIP', 'PAMIP', 'PMIP', 'RFMIP', 'ScenarioMIP', 'VolMIP', 'CORDEX', 'DynVarMIP', 'SIMIP', 'VIACSAB'] # All 24 CMIP6 MIPs
   #ec_earth_mips = ['CMIP']        # for a faster test
   #ec_earth_mips = ['ScenarioMIP'] # for a faster test
   #ec_earth_mips = ['AerChemMIP']  # for a faster test

   # Some test cases:
   #cmip_ece_configurations = {'EC-EARTH-AOGCM':'CMIP,DCPP,LS3MIP,PAMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB'}
   ##cmip_ece_configurations = {'dummy':'dummy'}

   # Some test cases:
   ##scenario_ece_configurations = {'EC-EARTH-AOGCM':'CMIP,DCPP,LS3MIP,ScenarioMIP,CORDEX,DynVarMIP,VIACSAB'}
   ##scenario_ece_configurations = {'dummy':'dummy'}


   # Define a dictionary which lists/maps for each MIP which EC-Earth3 model configurations are used to run the MIP:
   ece_conf_mip_map = {
   #'CMIP'        : ['EC-EARTH-AOGCM','EC-EARTH-HR','EC-EARTH-LR','EC-EARTH-CC','EC-EARTH-ESM-1','EC-EARTH-AerChem','EC-EARTH-Veg','EC-EARTH-Veg-LR'],
    'DCPP'        : ['EC-EARTH-AOGCM','EC-EARTH-HR'],
    'LS3MIP'      : ['EC-EARTH-AOGCM','EC-EARTH-Veg'],
    'PAMIP'       : ['EC-EARTH-AOGCM'],
    'RFMIP'       : ['EC-EARTH-AOGCM','EC-EARTH-AerChem'],
    'ScenarioMIP' : ['EC-EARTH-AOGCM','EC-EARTH-CC','EC-EARTH-ESM-1','EC-EARTH-Veg','EC-EARTH-Veg-LR'],
    'VolMIP'      : ['EC-EARTH-AOGCM'],
    'CORDEX'      : ['EC-EARTH-AOGCM'],
    'DynVarMIP'   : ['EC-EARTH-AOGCM'],
    'SIMIP'       : ['EC-EARTH-AOGCM'],
    'VIACSAB'     : ['EC-EARTH-AOGCM'],
    'HighResMIP'  : ['EC-EARTH-HR'],
    'PMIP'        : ['EC-EARTH-LR','EC-EARTH-Veg-LR'],
    'C4MIP'       : ['EC-EARTH-CC','EC-EARTH-ESM-1'],
    'CDRMIP'      : ['EC-EARTH-CC','EC-EARTH-ESM-1','EC-EARTH-Veg'],
    'LUMIP'       : ['EC-EARTH-CC','EC-EARTH-ESM-1','EC-EARTH-Veg'],
    'OMIP'        : ['EC-EARTH-CC','EC-EARTH-ESM-1'],
    'AerChemMIP'  : ['EC-EARTH-AerChem']
   }


   # Or instead of an (alphabetic) sorted dictionary an ordered dictionary could be used.
   ##for model_configuration in sorted(cmip_ece_configurations.keys()):
   ## print(' {:20}   {}'.format(model_configuration, cmip_ece_configurations[model_configuration]))
   ##for model_configuration in sorted(scenario_ece_configurations.keys()):
   ## print(' {:20}   {}'.format(model_configuration, scenario_ece_configurations[model_configuration]))
   ##sys.exit()

   experiment_counter = 0

   command_show_version = 'git describe --tags | sed "s/^/ Using ece2cmor git revision: /"; echo;'
   os.system(command_show_version)

   command_00 = 'rm -rf ' + cmip6_base_dir_name + ' cmip6-data-request-ece'
   os.system(command_00)

   # Loop over MIPs:
   for mip in dq.coll['mip'].items:
     mip_name  = mip.label
     print('\n Starting to work on: ', mip_name, '\n')

     if mip_name == 'CMIP' or mip_name == 'ScenarioMIP':
      if mip_name == 'CMIP':
       ece_configurations = cmip_ece_configurations
      elif mip_name == 'ScenarioMIP':
       ece_configurations = scenario_ece_configurations
      else:
       print('\n Aborting genecec: programmer error: no case for: ', mip_name, ' in joined MIP treatment.\n')
       sys.exit()

      for model_configuration in sorted(ece_configurations.keys()):
        mip_list         = ece_configurations[model_configuration]
        mip_label        = mip_list.replace(",", ".")      # Convert the comma separated list into a dot separated list because this is what comes out from genecec-per-mip-experiment.sh
        multiplemips     = "." in mip_label
        select_substring = mip_label[0:2].lower()

       #print(' mip = '             , mip             )
       #print(' mip_name = '        , mip_name        )
       #print(' mip_list = '        , mip_list        )
       #print(' mip_label = '       , mip_label       )
       #print(' multiplemips = '    , multiplemips    )
       #print(' select_substring = ', select_substring)
       #sys.exit()

        # Loop over experiments:
        for u in dq.inx.iref_by_sect[mip.uid].a['experiment']:
          ex = dq.inx.uid[u]

          subdirname_experiment = cmip6_base_dir_name + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label
          filename_file_def_nemo_opa = subdirname_experiment + '/file_def_nemo-opa.xml'
          ece_configuration_dir = cmip6_base_dir_name + mip_name + '/' + model_configuration + '/cmip6-experiment-' + mip_name + '-' + ex.label

         #command_x1 = "sed -i -e 's/True\" field_ref=\"toce_pot\"/False\" field_ref=\"toce_pot\"/' " + filename_file_def_nemo_opa
         #command_x2 = "sed -i -e '/sfdsi_2/d' " + filename_file_def_nemo_opa
          command_01 = './genecec-per-mip-experiment.sh ' + cmip6_base_dir_name + ' ' + mip_list + ' ' + ex.label + ' ' + str(ex.tier[0]) + ' 1 '
          command_02 = "sed -i -e 's/uoce_e3u_vsum_e2u_cumul. freq_op=.1ts/uoce_e3u_vsum_e2u_cumul/' " + filename_file_def_nemo_opa
          command_03 = "sed -i -e '/deptho/d' " + filename_file_def_nemo_opa
          command_c  = "sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' " + subdirname_experiment + '/file_def_nemo*'
          command_04 = 'mkdir -p ' + ece_configuration_dir + '; mv ' + subdirname_experiment + '/*' + ' ' + ece_configuration_dir + '; rm -rf ' + cmip6_base_dir_name + mip_label
          command_05 = 'drq2varlist --drq cmip6-data-request/cmip6-data-request-' + mip_label + '-' + ex.label + '-t' + str(ex.tier[0]) + '-p' + '1' + '/cmvme_' + select_substring + '*_' + ex.label + '_' + str(ex.tier[0]) + '_1.xlsx --ececonf ' + model_configuration + ' --varlist ' + ece_configuration_dir + '/cmip6-data-request-varlist-' + mip_name + '-' + ex.label + '-' + model_configuration + '.json'
          command_06 = './modify-metadata-template.sh ' + mip_name + ' ' + ex.label + ' ' + model_configuration + '; mv -f metadata-cmip6-' + mip_name + '-' + ex.label + '-' + model_configuration + '-*-template.json ' + ece_configuration_dir
          command_07 = 'convert_component_to_flat_json ' + ece_configuration_dir + '/cmip6-data-request-varlist-' + mip_name + '-' + ex.label + '-' + model_configuration + '.json'
          command_08 = 'checkvars --asciionly -v --drq ' + 'cmip6-data-request-varlist-' + mip_name + '-' + ex.label + '-' + model_configuration + '-flat.json' +  ' --output ' + ece_configuration_dir + '/request-overview'
          command_09 = 'rm -f ' + 'cmip6-data-request-varlist*-flat.json'
          command_10 = 'cat ' + ece_configuration_dir + '/request-overview.available.txt ' + ece_configuration_dir + '/volume-estimate.txt > ' + ece_configuration_dir + '/request-overview-' + mip_name + '-' + ex.label + '-including-' + model_configuration + '-preferences.txt'
          command_11 = 'rm -f ' + ece_configuration_dir + '/volume-estimate.txt'
          command_12 = 'rm -f ' + ece_configuration_dir + '/request-overview.available.txt'

         #print('{}'.format(command_01))
          if mip_name in ec_earth_mips:
            #if ex.tier[0] in experiment_tiers_included and ex.label == 'piControl':   # for a faster test
            #if ex.tier[0] in experiment_tiers_included and ex.label == 'historical':  # for a faster test
            #if ex.tier[0] in experiment_tiers_included and ex.label == 'ssp585':      # for a faster test
             if ex.tier[0] in experiment_tiers_included:
               #os.system(command_x1)   # Just set the toce fields false again because we still face troubles with them
               #os.system(command_x2)   # Delete the line with sfdsi_2 from the file_def_nemo-opa.xml files
                os.system(command_01)
                os.system(command_02)   # Remove the freq_op attribute for the variable msftbarot (uoce_e3u_vsum_e2u_cumul) from the file_def_nemo.xml file #327 & e.g. #518-165 on the ec-earth portal
                os.system(command_03)   # Remove deptho from the file_def_nemo-opa.xml #249
                os.system(command_c )   # Switching the 'transect' variables off (the transect grid definition seems to depend on the XIOS 2.5 upgrade)
                os.system(command_04)   # Rename directory names for joint MIPs
                os.system(command_05)   # Produce the ec-earth component json data request variant, the so called varlist.json
                os.system(command_06)   # Produce the metadata files for this MIP experiment.
                if add_request_overview:
                 os.system(command_07)  # Convert the json data request file which contains the EC-Earth components to a flat json data request file for checkvars
                 os.system(command_08)  # Execute checkvars --asciionly for the flat json data request file which includes the preferences
                 os.system(command_09)  # Remove the flat json file
                 os.system(command_10)  # Concatenate volume estimates to the request overview file
                os.system(command_11)   # Remove volume estimate file
                os.system(command_12)   # Remove the intermediate request-overview.available.txt file
                experiment_counter = experiment_counter + 1
             else:
                print(' Tier {} experiments are not included: Skipping: {}'.format(ex.tier[0], command_01))
          else:
             print(' EC-Earth3 does not participate in {:11}: Skipping: {}'.format(mip_name, command_01))

     else:
       #print('\n Model configuration is: ', model_configuration, 'for', mip_name, ex.label, '\n')
        print('\n Reporting that ', mip_name, ' concerns a usual single MIP case')
        mip_list  = mip_name
        mip_label = mip_name
        if mip_name in ec_earth_mips:
         model_configuration = ece_conf_mip_map[mip_name]
        else:
         model_configuration = ['no-match']

        # Loop over experiments:
        for u in dq.inx.iref_by_sect[mip.uid].a['experiment']:
          ex = dq.inx.uid[u]

          subdirname_experiment = cmip6_base_dir_name + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label
          filename_file_def_nemo_opa = subdirname_experiment + '/file_def_nemo-opa.xml'

         #command_x1 = "sed -i -e 's/True\" field_ref=\"toce_pot\"/False\" field_ref=\"toce_pot\"/' " + filename_file_def_nemo_opa
         #command_x2 = "sed -i -e '/sfdsi_2/d' " + filename_file_def_nemo_opa
          command_01 = './genecec-per-mip-experiment.sh ' + cmip6_base_dir_name + ' ' + mip_list + ' ' + ex.label + ' ' + str(ex.tier[0]) + ' 1 '
          command_02 = "sed -i -e 's/uoce_e3u_vsum_e2u_cumul. freq_op=.1ts/uoce_e3u_vsum_e2u_cumul/' " + filename_file_def_nemo_opa
          command_03 = "sed -i -e '/deptho/d' " + filename_file_def_nemo_opa
          command_c  = "sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' " + cmip6_base_dir_name + mip_name + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/file_def_nemo*'
         #print('{}'.format(command_01))
          if mip_name in ec_earth_mips:
            #if ex.tier[0] in experiment_tiers_included:
             # Add also the LS3MIP tier 2 experiments: amip-lfmip-pdLC & amip-lfmip-rmLC
             # Add also the AerChemMIP tier 2 & 3 experiments (see #631):
             #  hist-piAer            tier-2  historical forcing, but with pre-industrial aerosol emissions
             #  histSST-piAer         tier-2  historical SSTs and historical forcing, but with pre-industrial aerosol emissions
             #  piClim-2xdust         tier-2  pre-industrial climatological SSTs and forcing, but with doubled emissions of dust
             #  piClim-2xss           tier-2  pre-industrial climatological SSTs and forcing, but with doubled emissions of sea salt
             #  piClim-BC             tier-2  pre-industrial climatological SSTs and forcing, but with 2014 black carbon emissions
             #  ssp370-lowNTCFCH4     tier-3  SSP3-7.0, with low NTCF emissions and methane concentrations
             #  ssp370pdSST           tier-2  SSP3-7.0, with SSTs prescribed as present day
             #  ssp370SST-lowAer      tier-2  SSP3-7.0, prescribed SSTs, with low aerosol emissions
             #  ssp370SST-lowBC       tier-2  SSP3-7.0, prescribed SSTs, with low black carbon emissions
             #  ssp370SST-lowNTCFCH4  tier-3  SSP3-7.0, prescribed SSTs, with low NTCF emissions and methane concentrations
             # Add also the LUMIP tier 2 experiments (see #680):
             #  land-cClim            tier-2  historical land-only constant climate
             #  land-cCO2             tier-2  historical land-only constant CO2
             #  land-noShiftCultivate tier-2  historical land-only with shifting cultivation turned off
             # Add also RFMIP tier 2 experiments (see #694):
             #  piClim-histaer        tier-2  transient effective radiative forcing by aerosols
             #  piClim-histall        tier-2  transient effective radiative forcing
             if ex.tier[0] in experiment_tiers_included or (ex.tier[0] == 2 and ex.label == 'amip-lfmip-pdLC')      or \
                                                           (ex.tier[0] == 2 and ex.label == 'amip-lfmip-rmLC')      or \
                                                           (ex.tier[0] == 2 and ex.label == 'hist-piAer')           or \
                                                           (ex.tier[0] == 2 and ex.label == 'histSST-piAer')        or \
                                                           (ex.tier[0] == 2 and ex.label == 'piClim-2xdust')        or \
                                                           (ex.tier[0] == 2 and ex.label == 'piClim-2xss')          or \
                                                           (ex.tier[0] == 2 and ex.label == 'piClim-BC')            or \
                                                           (ex.tier[0] == 3 and ex.label == 'ssp370-lowNTCFCH4')    or \
                                                           (ex.tier[0] == 2 and ex.label == 'ssp370pdSST')          or \
                                                           (ex.tier[0] == 2 and ex.label == 'ssp370SST-lowAer')     or \
                                                           (ex.tier[0] == 2 and ex.label == 'ssp370SST-lowBC')      or \
                                                           (ex.tier[0] == 3 and ex.label == 'ssp370SST-lowNTCFCH4') or \
                                                           (ex.tier[0] == 2 and ex.label == 'land-cClim')           or \
                                                           (ex.tier[0] == 2 and ex.label == 'land-cCO2')            or \
                                                           (ex.tier[0] == 2 and ex.label == 'land-noShiftCultivate')or \
                                                           (ex.tier[0] == 2 and ex.label == 'piClim-histaer')       or \
                                                           (ex.tier[0] == 2 and ex.label == 'piClim-histall'):
               #os.system(command_x1)    # Just set the toce fields false again because we still face troubles with them
               #os.system(command_x2)    # Delete the line with sfdsi_2 from the file_def_nemo-opa.xml files
                os.system(command_01)
                os.system(command_02)    # Remove the freq_op attribute for the variable msftbarot (uoce_e3u_vsum_e2u_cumul) from the file_def_nemo.xml file #327 & e.g. #518-165 on the ec-earth portal
                os.system(command_03)    # Remove deptho from the file_def_nemo-opa.xml #249
                os.system(command_c )    # Switching the 'transect' variables off (the transect grid definition seems to depend on the XIOS 2.5 upgrade)

                # Looping over the various EC-Earth3 model configurations in order to generate for each of them the json cmip6 data request file:
                for conf in model_configuration:
                 command_05 = 'drq2varlist --drq cmip6-data-request/cmip6-data-request-' + mip_label + '-' + ex.label + '-t' + str(ex.tier[0]) + '-p' + '1' + '/cmvme_' + mip_name + '_' + ex.label + '_' + str(ex.tier[0]) + '_1.xlsx --ececonf ' + conf + ' --varlist ' + cmip6_base_dir_name + mip_name + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/cmip6-data-request-varlist-' + mip_name + '-' + ex.label + '-' + conf + '.json'
                 command_06 = './modify-metadata-template.sh ' + mip_name + ' ' + ex.label + ' ' + conf + '; mv -f metadata-cmip6-' + mip_name + '-' + ex.label + '-' + conf + '-*-template.json ' + cmip6_base_dir_name + mip_name + '/cmip6-experiment-' + mip_name + '-' + ex.label
                 command_07 = 'convert_component_to_flat_json ' + cmip6_base_dir_name + mip_name + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/cmip6-data-request-varlist-' + mip_name + '-' + ex.label + '-' + conf + '.json'
                 command_08 = 'checkvars --asciionly -v --drq ' + 'cmip6-data-request-varlist-' + mip_name + '-' + ex.label + '-' + conf + '-flat.json' +  ' --output ' + subdirname_experiment + '/request-overview'
                 command_09 = 'rm -f ' + 'cmip6-data-request-varlist*-flat.json'
                 command_10 = 'cat ' + subdirname_experiment + '/request-overview.available.txt ' + subdirname_experiment + '/volume-estimate.txt > ' + subdirname_experiment + '/request-overview-' + mip_name + '-' + ex.label + '-including-' + conf + '-preferences.txt'
                 command_11 = 'rm -f ' + subdirname_experiment + '/volume-estimate.txt'
                 command_12 = 'rm -f ' + subdirname_experiment + '/request-overview.available.txt'
                 os.system(command_05)   # Produce the ec-earth component json data request variant, the so called varlist.json
                 os.system(command_06)   # Produce the metadata files for this MIP experiment.
                 if add_request_overview:
                  os.system(command_07)  # Convert the json data request file which contains the EC-Earth components to a flat json data request file for checkvars
                  os.system(command_08)  # Execute checkvars --asciionly for the flat json data request file which includes the preferences
                  os.system(command_09)  # Remove the flat json file
                  os.system(command_10)  # Concatenate volume estimates to the request overview file
                 os.system(command_11)   # Remove volume estimate file
                 os.system(command_12)   # Remove the intermediate request-overview.available.txt file

                experiment_counter = experiment_counter + 1
             else:
                print(' Tier {} experiments are not included: Skipping: {}'.format(ex.tier[0], command_01))
          else:
             print(' EC-Earth3 does not participate in {:11}: Skipping: {}'.format(mip_name, command_01))

   print(' There are {} experiments included. '.format(experiment_counter))


   # Add a test case with which all available variables over all EC-Earth MIP experiments are switched on,
   # i.e. are enabled in the file_def files:
   if os.path.isdir(cmip6_base_dir_name + "CMIP/EC-EARTH-AOGCM/cmip6-experiment-CMIP-piControl/"):
    command_a = "cp -r " + cmip6_base_dir_name + "CMIP/EC-EARTH-AOGCM/cmip6-experiment-CMIP-piControl/ " + cmip6_base_dir_name + "test-all-ece-mip-variables/"
   else:
    command_a = "cp -r " + cmip6_base_dir_name + "CMIP/cmip6-experiment-CMIP-piControl/ " + cmip6_base_dir_name + "test-all-ece-mip-variables/"
   command_b  = "sed -i 's/enabled=\"False\"/enabled=\"True\"/' " + cmip6_base_dir_name + "test-all-ece-mip-variables/file_def_nemo-*"
   command_c  = "sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' " + cmip6_base_dir_name + "test-all-ece-mip-variables/file_def_nemo-*"
   command_d  = "echo 'This directory is intended for the maintainers only. In order to be able to test all NEMO OPA & LIM output by running one experiment, all those fields are enabled in the OPA & LIM file_def files in this directory. And in order to be able to test all IFS output by running one experiment, all available IFS fields are enabled in the ppt files.' > " + cmip6_base_dir_name + "test-all-ece-mip-variables/README"
   command_e  = "rm -f " + cmip6_base_dir_name + "test-all-ece-mip-variables/ppt* " + cmip6_base_dir_name + "test-all-ece-mip-variables/cmip6-data-request-varlist-CMIP-piControl-EC-EARTH-AOGCM.json " + cmip6_base_dir_name + "test-all-ece-mip-variables/volume-estimate-CMIP-piControl-EC-EARTH-AOGCM.txt " + cmip6_base_dir_name + "test-all-ece-mip-variables/request-overview*.txt"
   command_f  = "drq2ppt --allvars"
   command_g  = "mv -f ppt0000000000 pptdddddd* " + cmip6_base_dir_name + "test-all-ece-mip-variables/; rm -f volume-estimate-ifs.txt"
   command_h  = "drq2varlist --allvars --ececonf EC-EARTH-AOGCM   --varlist " + cmip6_base_dir_name + "test-all-ece-mip-variables/cmip6-data-request-varlist-all-EC-EARTH-AOGCM.json"
   command_i  = "drq2varlist --allvars --ececonf EC-EARTH-CC      --varlist " + cmip6_base_dir_name + "test-all-ece-mip-variables/cmip6-data-request-varlist-all-EC-EARTH-CC.json"
   command_s  = "drq2varlist --allvars --ececonf EC-EARTH-ESM-1   --varlist " + cmip6_base_dir_name + "test-all-ece-mip-variables/cmip6-data-request-varlist-all-EC-EARTH-ESM-1.json"
   command_j  = "drq2varlist --allvars --ececonf EC-EARTH-AerChem --varlist " + cmip6_base_dir_name + "test-all-ece-mip-variables/cmip6-data-request-varlist-all-EC-EARTH-AerChem.json"
   command_k  = "rm -f " + cmip6_base_dir_name + "test-all-ece-mip-variables/lpjg_cmip6_output.ins; ln -s ../../../lpjg_cmip6_output.ins lpjg_cmip6_output.ins; mv -f lpjg_cmip6_output.ins " + cmip6_base_dir_name + "test-all-ece-mip-variables/"


   command_l1 = 'convert_component_to_flat_json ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/cmip6-data-request-varlist-all-EC-EARTH-AOGCM.json'
   command_m1 = 'convert_component_to_flat_json ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/cmip6-data-request-varlist-all-EC-EARTH-CC.json'
   command_t1 = 'convert_component_to_flat_json ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/cmip6-data-request-varlist-all-EC-EARTH-ESM-1.json'
   command_n1 = 'convert_component_to_flat_json ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/cmip6-data-request-varlist-all-EC-EARTH-AerChem.json'
   command_l2 = 'checkvars --asciionly -v --drq ' + 'cmip6-data-request-varlist-all-EC-EARTH-AOGCM-flat.json'   + ' --output ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-AOGCM-preferences'
   command_m2 = 'checkvars --asciionly -v --drq ' + 'cmip6-data-request-varlist-all-EC-EARTH-CC-flat.json'      + ' --output ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-CC-preferences'
   command_t2 = 'checkvars --asciionly -v --drq ' + 'cmip6-data-request-varlist-all-EC-EARTH-ESM-1-flat.json'   + ' --output ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-ESM-1-preferences'
   command_n2 = 'checkvars --asciionly -v --drq ' + 'cmip6-data-request-varlist-all-EC-EARTH-AerChem-flat.json' + ' --output ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-AerChem-preferences'
   command_o  = 'rm -f ' + 'cmip6-data-request-varlist-all-EC-EARTH-*-flat.json'
   command_p  = ' mv -f ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-AOGCM-preferences.available.txt   ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-AOGCM-preferences.txt'
   command_q  = ' mv -f ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-CC-preferences.available.txt      ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-CC-preferences.txt'
   command_u  = ' mv -f ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-ESM-1-preferences.available.txt   ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-ESM-1-preferences.txt'
   command_r  = ' mv -f ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-AerChem-preferences.available.txt ' + cmip6_base_dir_name + 'test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-AerChem-preferences.txt'

   os.system(command_a) # Create a new subdirectory for testing all available variables in the file_def files
   os.system(command_b) # Switch on all available variables in the file_def files
   os.system(command_c) # Switching the 'transect' variables off (the transect grid definition seems to depend on the XIOS 2.5 upgrade)
   os.system(command_d) # Add a README to the test-all-ece-mip-variables directory
   os.system(command_e) # Remove the piControl ppt, json data request and volume estimate files from the test-all-ece-mip-variables directory
   os.system(command_f) # Create the ppt files which include all IFS available variables
   os.system(command_g) # Move the ppt files which include all IFS available variables to the test-all-ece-mip-variables directory and remove the volume estimate file.
   os.system(command_h) # Create the json data request file which includes all available variables for EC-Earth3-AOGCM
   os.system(command_i) # Create the json data request file which includes all available variables for EC-Earth3-CC
   os.system(command_s) # Create the json data request file which includes all available variables for EC-Earth3-ESM-1
   os.system(command_j) # Create the json data request file which includes all available variables for EC-Earth3-AerChem
   os.system(command_k) # Remove the piControl LPJG instruction file, and add a link to the instruction file which includes all available LPJG variables.
   os.system(command_l1) # Convert the json data request file which contains the EC-Earth3-AOGCM   components to a flat json data request file for checkvars
   os.system(command_m1) # Convert the json data request file which contains the EC-Earth3-CC      components to a flat json data request file for checkvars
   os.system(command_t1) # Convert the json data request file which contains the EC-Earth3-ESM-1   components to a flat json data request file for checkvars
   os.system(command_n1) # Convert the json data request file which contains the EC-Earth3-AerChem components to a flat json data request file for checkvars
   os.system(command_l2) # Execute checkvars --asciionly for the flat json data request file which includes the EC-Earth3-AOGCM   preferences
   os.system(command_m2) # Execute checkvars --asciionly for the flat json data request file which includes the EC-Earth3-CC      preferences
   os.system(command_t2) # Execute checkvars --asciionly for the flat json data request file which includes the EC-Earth3-ESM-1   preferences
   os.system(command_n2) # Execute checkvars --asciionly for the flat json data request file which includes the EC-Earth3-AerChem preferences
   os.system(command_o ) # Remove the flat json files
   os.system(command_p ) # Rename (omit the avilable label) the request-overview EC-Earth3-AOGCM   file
   os.system(command_q ) # Rename (omit the avilable label) the request-overview EC-Earth3-CC      file
   os.system(command_u ) # Rename (omit the avilable label) the request-overview EC-Earth3-ESM-1   file
   os.system(command_r ) # Rename (omit the avilable label) the request-overview EC-Earth3-AerChem file

   command_fix_s245_s370 = "./apply-the-s126-s585-request-for-s245-370.sh " + cmip6_base_dir_name
   os.system(command_fix_s245_s370) # See issue 517: ScenarioMIP requests for s245 & s370 are taken equal to the ones of s585 & s126.


   include_covidmip = True
  #include_covidmip = False # for a faster test
   if include_covidmip:
    # Create and add the CovidMIP control output files:
    command_covidmip_rm           = "rm -rf CovidMIP"
    command_covidmip_baseline     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-baseline     EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-ssp245-baseline    "
    command_covidmip_covid        = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-covid        EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-ssp245-covid       "
    command_covidmip_cov_strgreen = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-cov-strgreen EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-ssp245-cov-strgreen"
    command_covidmip_cov_modgreen = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-cov-modgreen EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-ssp245-cov-modgreen"
    command_covidmip_cov_fossil   = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-cov-fossil   EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-ssp245-cov-fossil  "
    command_covidmip_cov_aer      = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-cov-aer      EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-ssp245-cov-aer     "
    command_covidmip_mv           = "mv -f CovidMIP " + cmip6_base_dir_name

    os.system(command_covidmip_rm          )
    os.system(command_covidmip_baseline    )
    os.system(command_covidmip_covid       )
    os.system(command_covidmip_cov_strgreen)
    os.system(command_covidmip_cov_modgreen)
    os.system(command_covidmip_cov_fossil  )
    os.system(command_covidmip_cov_aer     )
    os.system(command_covidmip_mv          )


   if not activate_pextra_mode:
    include_compact_request = True
   #include_compact_request = False # for a faster test
    if include_compact_request:
     # Create and add the compact request control output files:
     command_compact_request_rm    = "rm -rf compact-request"
     command_compact_request       = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/compact-request/cmvme_CMIP_ssp245_1_1-additional.xlsx             CMIP        piControl           EC-EARTH-AOGCM compact-request"
     command_compact_request_mv    = "mv -f compact-request " + output_dir_name

     os.system(command_compact_request_rm   )
     os.system(command_compact_request      )
     os.system(command_compact_request_mv   )

    include_rcm_dynamic_plev_forcing = True
   #include_rcm_dynamic_plev_forcing = False # for a faster test
    if include_rcm_dynamic_plev_forcing:
     # Create and add the rcm dynamic plev forcing control output files:
     command_rcm_plev_rm           = "rm -rf rcm-dynamic-plev-forcing"
     command_rcm_plev23_histor     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx  CMIP        historical          EC-EARTH-AOGCM rcm-dynamic-plev23-forcing/EC-EARTH-AOGCM/cmip6-experiment-CMIP-historical   "
     command_rcm_plev23_ssp119     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx  ScenarioMIP ssp119              EC-EARTH-AOGCM rcm-dynamic-plev23-forcing/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp119"
     command_rcm_plev23_ssp126     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx  ScenarioMIP ssp126              EC-EARTH-AOGCM rcm-dynamic-plev23-forcing/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp126"
     command_rcm_plev23_ssp245     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx  ScenarioMIP ssp245              EC-EARTH-AOGCM rcm-dynamic-plev23-forcing/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp245"
     command_rcm_plev23_ssp370     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx  ScenarioMIP ssp370              EC-EARTH-AOGCM rcm-dynamic-plev23-forcing/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp370"
     command_rcm_plev23_ssp585     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx  ScenarioMIP ssp585              EC-EARTH-AOGCM rcm-dynamic-plev23-forcing/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp585"
     command_rcm_plev36_histor     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx   CMIP        historical          EC-EARTH-AOGCM rcm-dynamic-plev36-forcing/EC-EARTH-AOGCM/cmip6-experiment-CMIP-historical   "
     command_rcm_plev36_ssp119     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx   ScenarioMIP ssp119              EC-EARTH-AOGCM rcm-dynamic-plev36-forcing/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp119"
     command_rcm_plev36_ssp126     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx   ScenarioMIP ssp126              EC-EARTH-AOGCM rcm-dynamic-plev36-forcing/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp126"
     command_rcm_plev36_ssp245     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx   ScenarioMIP ssp245              EC-EARTH-AOGCM rcm-dynamic-plev36-forcing/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp245"
     command_rcm_plev36_ssp370     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx   ScenarioMIP ssp370              EC-EARTH-AOGCM rcm-dynamic-plev36-forcing/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp370"
     command_rcm_plev36_ssp585     = "./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx   ScenarioMIP ssp585              EC-EARTH-AOGCM rcm-dynamic-plev36-forcing/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp585"
     command_rcm_plev_mv           = "mv -f rcm-dynamic-plev23-forcing rcm-dynamic-plev36-forcing " + output_dir_name

     os.system(command_rcm_plev_rm          )
     os.system(command_rcm_plev23_histor    )
    #os.system(command_rcm_plev23_ssp119    )
     os.system(command_rcm_plev23_ssp126    )
     os.system(command_rcm_plev23_ssp245    )
    #os.system(command_rcm_plev23_ssp370    )
     os.system(command_rcm_plev23_ssp585    )
     os.system(command_rcm_plev36_histor    )
    #os.system(command_rcm_plev36_ssp119    )
     os.system(command_rcm_plev36_ssp126    )
     os.system(command_rcm_plev36_ssp245    )
    #os.system(command_rcm_plev36_ssp370    )
     os.system(command_rcm_plev36_ssp585    )
     os.system(command_rcm_plev_mv          )

   if activate_pextra_mode:
    os.system('./switch-on-off-pextra-mode.sh deactivate-pextra-mode')

else:
   print()
   print(' This script needs one argument: a config file name. E.g.:')
   print('  ', sys.argv[0], 'config-genecec')
   print()
