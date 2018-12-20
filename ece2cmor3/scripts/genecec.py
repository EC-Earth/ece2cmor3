#!/usr/bin/env python
# Thomas Reerink
#
# Run examples:
#  python genecec.py
#  mkdir -p log-genecec; ./genecec.py >& log-genecec/log-genecec-50 &
#  mkdir -p log-genecec; ./genecec.py 1> log-genecec/log-genecec-stdout-50 2> log-genecec/log-genecec-stderr-50 &
#
# Looping over all MIPs and within each MIP over all its MIP experiments.
# The experiment tier can be selected. For each selected experiment the
# namelists are created by calling the genecec-per-mip-experiment.sh script.
#
# With this script it is possible to generate the EC-Earth3 control output files, i.e.
# the IFS Fortran namelists (the ppt files) and the NEMO xml files for XIOS (the
# file_def files for OPA, LIM and PISCES) for all MIP experiments in which EC-Earth3
# participates.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.

import sys
import os
from dreqPy import dreq
dq = dreq.loadDreq()

# Specify in the list below which tier experiments should be included. For
# instance [1,2] means tier 1 and tier 2 experiments are included:
experiment_tiers_included = [1]
ec_earth_mips  = ['CMIP', 'AerChemMIP', 'CDRMIP', 'C4MIP',                   'DCPP',                              'HighResMIP', 'ISMIP6', 'LS3MIP', 'LUMIP', 'OMIP', 'PAMIP', 'PMIP', 'RFMIP', 'ScenarioMIP', 'VolMIP', 'CORDEX', 'DynVar', 'SIMIP', 'VIACSAB'] # All 19 EC-Earth MIPs
#ec_earth_mips = ['CMIP', 'AerChemMIP', 'CDRMIP', 'C4MIP', 'CFMIP', 'DAMIP', 'DCPP', 'FAFMIP', 'GeoMIP', 'GMMIP', 'HighResMIP', 'ISMIP6', 'LS3MIP', 'LUMIP', 'OMIP', 'PAMIP', 'PMIP', 'RFMIP', 'ScenarioMIP', 'VolMIP', 'CORDEX', 'DynVar', 'SIMIP', 'VIACSAB'] # All 24 CMIP6 MIPs
#ec_earth_mips = ['CMIP'] # for a faster test
experiment_counter = 0


# The list of MIPs for each of the eight EC-Earth3 model configurations in an iterable dictionary. This lists are needed to request the joint CMIP6 data requests
# for each of the EC-Earth3 model configurations:
dictionary = {
 'EC-EARTH-AOGCM'   : 'CMIP,DCPP,LS3MIP,PAMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB',
 'EC-EARTH-HR'      : 'CMIP,DCPP,HighResMIP',
 'EC-EARTH-LR'      : 'CMIP,PMIP',
 'EC-EARTH-CC'      : 'CDRMIP,CMIP,C4MIP,LUMIP,OMIP',
 'EC-EARTH-GrisIS'  : 'CMIP,ISMIP6,PMIP',
 'EC-EARTH-AerChem' : 'AerChemMIP,CMIP',
 'EC-EARTH-Veg'     : 'CDRMIP,CMIP,LUMIP,LS3MIP,ScenarioMIP',
 'EC-EARTH-Veg-LR'  : 'CMIP,PMIP,ScenarioMIP'
}

# Some test cases:
##dictionary = {'EC-EARTH-AOGCM':'CMIP,DCPP,LS3MIP,PAMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB'}
##dictionary = {'dummy':'dummy'}


# Or instead of an (alphabetic) sorted dictionary an ordered dictionary could be used.
for model_configuration in sorted(dictionary.keys()):
 print ' {:20}   {}'.format(model_configuration, dictionary[model_configuration])


command_0 = 'rm -rf cmip6-output-control-files'
os.system(command_0)

# Loop over MIPs:
for mip in dq.coll['mip'].items:
  mip_name  = mip.label
  print '\n Starting to work on: ', mip_name, '\n'

  if mip_name == 'CMIP':
   for model_configuration in sorted(dictionary.keys()):
   ##mip_list  = 'CMIP'
     mip_list = dictionary[model_configuration]
     mip_label = mip_list.replace(",", ".") # Convert the comma separated list into a dot separated list because this is what comes out from genecec-per-mip-experiment.sh

     # Loop over experiments:
     for u in dq.inx.iref_by_sect[mip.uid].a['experiment']:
       if experiment_counter == 0:
         omit_setup_argument = ''
       else:
         omit_setup_argument = ' omit-setup'
       ex = dq.inx.uid[u]

       command   = './genecec-per-mip-experiment.sh ' + mip_list + ' ' + ex.label + ' ' + str(ex.tier[0]) + ' 1 ' + omit_setup_argument
       command_2 = 'rm -rf cmip6-output-control-files/' + mip_label + '/cmip6-experiment-*/file_def-compact'
       command_3 = 'rm -f  cmip6-output-control-files/' + mip_label + '/cmip6-experiment-*/cmip6-file_def_nemo.xml'
       command_4 = "sed -i -e 's/True\" field_ref=\"toce_pot\"/False\" field_ref=\"toce_pot\"/' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
       command_5 = "sed -i -e '/sfdsi_2/d' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
       command_6 = "sed -i -e 's/uoce_e3u_vsum_e2u_cumul. freq_op=.1ts/uoce_e3u_vsum_e2u_cumul/' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
       command_7 = 'mkdir -p cmip6-output-control-files/' + mip_name + '/' + model_configuration + '/cmip6-experiment-' + mip_name + '-' + ex.label + '; mv cmip6-output-control-files/' + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/*' + ' cmip6-output-control-files/' + mip_name + '/' + model_configuration + '/cmip6-experiment-' + mip_name + '-' + ex.label + '; rm -rf ' + ' cmip6-output-control-files/' + mip_label
       command_8 = '      mv cmip6-output-control-files/' + mip_name + '/' + model_configuration + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/volume-estimate-* cmip6-output-control-files/' + mip_name + '/' + model_configuration + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/volume-estimate-'  + mip_name + '-' + ex.label + '-' + model_configuration + '.txt'
       command_c = "sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' cmip6-output-control-files/" + mip_name + '/' + model_configuration + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/file_def_nemo*'
      #print print '{}'.format(command)
       if mip_name in ec_earth_mips:
         #if ex.tier[0] in experiment_tiers_included and ex.label == 'piControl':  # for a fast test
          if ex.tier[0] in experiment_tiers_included:
            if ex.label == 'esm-hist' or ex.label == 'esm-piControl':
             print 'Skipping this esm experiment ' + ex.label + ' because its CMIP6 data request fails so far.\n'
            else:
             os.system(command)
             os.system(command_2)  # Remove the file_def-compact subdirectory with the compact file_def files
             os.system(command_3)  # Remove the cmip6-file_def_nemo.xml file
            #os.system(command_4)  # Just set the toce fields false again because we still face troubles with them
            #os.system(command_5)  # Delete the line with sfdsi_2 from the file_def_nemo-opa.xml files
             os.system(command_6)  # Remove the freq_op attribute for the variable msftbarot (uoce_e3u_vsum_e2u_cumul) from the file_def_nemo.xml file
             if mip_name == 'CMIP' and ',' in mip_list:
              os.system(command_7) # Rename directry names for joint MIPs
              os.system(command_8) # Rename volume-estimate file for joint MIPs
             os.system(command_c)  # Switching the 'transect' variables off (the transect grid definition seems to depend on the XIOS 2.5 upgrade)
             experiment_counter = experiment_counter + 1
          else:
             print ' Tier {} experiments are not included: Skipping: {}'.format(ex.tier[0], command)
       else:
          print ' EC-Earth3 does not participate in {:11}: Skipping: {}'.format(mip_name, command)

  else:
     print '\n Reporting that ', mip_name, ' concerns a usual single MIP case'
     mip_list  = mip_name
     mip_label = mip_name

     # Loop over experiments:
     for u in dq.inx.iref_by_sect[mip.uid].a['experiment']:
       if experiment_counter == 0:
         omit_setup_argument = ''
       else:
         omit_setup_argument = ' omit-setup'
       ex = dq.inx.uid[u]

       command   = './genecec-per-mip-experiment.sh ' + mip_list + ' ' + ex.label + ' ' + str(ex.tier[0]) + ' 1 ' + omit_setup_argument
       command_2 = 'rm -rf cmip6-output-control-files/' + mip_label + '/cmip6-experiment-*/file_def-compact'
       command_3 = 'rm -f  cmip6-output-control-files/' + mip_label + '/cmip6-experiment-*/cmip6-file_def_nemo.xml'
       command_4 = "sed -i -e 's/True\" field_ref=\"toce_pot\"/False\" field_ref=\"toce_pot\"/' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
       command_5 = "sed -i -e '/sfdsi_2/d' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
       command_6 = "sed -i -e 's/uoce_e3u_vsum_e2u_cumul. freq_op=.1ts/uoce_e3u_vsum_e2u_cumul/' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
       command_c = "sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' cmip6-output-control-files/" + mip_name + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/file_def_nemo*'
      #print print '{}'.format(command)
       if mip_name in ec_earth_mips:
         #if ex.tier[0] in experiment_tiers_included and ex.label == 'piControl':   # for a faster test
         #if ex.tier[0] in experiment_tiers_included and ex.label == 'historical':  # for a faster test
          if ex.tier[0] in experiment_tiers_included:
            if ex.label == 'esm-hist' or ex.label == 'esm-piControl':
             print 'Skipping this esm experiment ' + ex.label + ' because its CMIP6 data request fails so far.\n'
            else:
             os.system(command)
             os.system(command_2)  # Remove the file_def-compact subdirectory with the compact file_def files
             os.system(command_3)  # Remove the cmip6-file_def_nemo.xml file
            #os.system(command_4)  # Just set the toce fields false again because we still face troubles with them
            #os.system(command_5)  # Delete the line with sfdsi_2 from the file_def_nemo-opa.xml files
             os.system(command_6)  # Remove the freq_op attribute for the variable msftbarot (uoce_e3u_vsum_e2u_cumul) from the file_def_nemo.xml file
             os.system(command_c)  # Switching the 'transect' variables off (the transect grid definition seems to depend on the XIOS 2.5 upgrade)
             experiment_counter = experiment_counter + 1
          else:
             print ' Tier {} experiments are not included: Skipping: {}'.format(ex.tier[0], command)
       else:
          print ' EC-Earth3 does not participate in {:11}: Skipping: {}'.format(mip_name, command)

print ' There are {} experiments included. '.format(experiment_counter)


# Add a test case with which all available variables over all EC-Earth MIP experiments are switched on,
# i.e. are enabled in the file_def files:
if os.path.isdir("cmip6-output-control-files/CMIP/EC-EARTH-AOGCM/cmip6-experiment-CMIP-piControl/"):
 command_a = "cp -r cmip6-output-control-files/CMIP/EC-EARTH-AOGCM/cmip6-experiment-CMIP-piControl/ cmip6-output-control-files/test-all-mips/"
else:
 command_a = "cp -r cmip6-output-control-files/CMIP/cmip6-experiment-CMIP-piControl/ cmip6-output-control-files/test-all-mips/"
command_b  = "sed -i 's/enabled=\"False\"/enabled=\"True\"/' cmip6-output-control-files/test-all-mips/file_def_nemo-*"
command_c  = "sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' cmip6-output-control-files/test-all-mips/file_def_nemo-*"
os.system(command_a) # Create a new subdirectory for testing all available variables in the file_def files
os.system(command_b) # Switch on all available variables in the file_def files
os.system(command_c) # Switching the 'transect' variables off (the transect grid definition seems to depend on the XIOS 2.5 upgrade)
