#!/usr/bin/env python
# Thomas Reerink
#
# Run examples:
#  python genecec.py
#  mkdir -p log-genecec; ./genecec.py >& log-genecec/log-genecec &
#  mkdir -p log-genecec; ./genecec.py >& log-genecec/log-genecec-32-drq-v29 &
#  mkdir -p log-genecec; ./genecec.py 1> log-genecec/log-genecec-stdout 2> log-genecec/log-genecec-stderr &
#  mkdir -p log-genecec; ./genecec.py 1> log-genecec/log-genecec-stdout-22-with-freq_op-drq-v29b1 2> log-genecec/log-genecec-stderr-22-with-freq_op-drq-v29b1 &
#  mkdir -p log-genecec; ./genecec.py 1> log-genecec/log-genecec-stdout-32-drq-v29 2> log-genecec/log-genecec-stderr-32-drq-v29 &
#
# Looping over all MIPs and within each MIP over all its MIP experiments.
# The experiment tier can be selected. For each selected experiment the
# namelists are created by calling the generate-ec-earth-namelists.sh script.
#
# With this script it is possible to generate the EC-Earth3 control output files, i.e.
# the IFS Fortran namelists (the ppt files) and the NEMO xml files for XIOS (the
# file_def files for OPA, LIM and PISCES) for all MIP experiments in which EC-Earth3
# participates.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.
#
# drq -m CMIP,DCPP,LS3MIP,PAMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB -e CMIP -t 1 -p 1 --xls --xlsDir xls-e=CMIP-t=1-p=1-m=all-ece-AOGCM-mips
# drq -m CMIP,DCPP,HighResMIP                                                        -e CMIP -t 1 -p 1 --xls --xlsDir xls-e=CMIP-t=1-p=1-m=all-ece-HR-mips
# drq -m CMIP,PMIP                                                                   -e CMIP -t 1 -p 1 --xls --xlsDir xls-e=CMIP-t=1-p=1-m=all-ece-LR-mips
# drq -m CMIP,CDRMIP,C4MIP,LUMIP,OMIP                                                -e CMIP -t 1 -p 1 --xls --xlsDir xls-e=CMIP-t=1-p=1-m=all-ece-CC-mips
# drq -m CMIP,ISMIP6,PMIP                                                            -e CMIP -t 1 -p 1 --xls --xlsDir xls-e=CMIP-t=1-p=1-m=all-ece-GrisIS-mips
# drq -m CMIP,AerChemMIP                                                             -e CMIP -t 1 -p 1 --xls --xlsDir xls-e=CMIP-t=1-p=1-m=all-ece-AerChem-mips
# drq -m CMIP,CDRMIP,LUMIP,LS3MIP,ScenarioMIP                                        -e CMIP -t 1 -p 1 --xls --xlsDir xls-e=CMIP-t=1-p=1-m=all-ece-Veg-mips
# drq -m CMIP,PMIP,ScenarioMIP                                                       -e CMIP -t 1 -p 1 --xls --xlsDir xls-e=CMIP-t=1-p=1-m=all-ece-Veg-LR-mips

import sys
import os
from dreqPy import dreq
dq = dreq.loadDreq()

# Specify in the list below which tier experiments should be included. For
# instance [1,2] means tier 1 and tier 2 experiments are included:
experiment_tiers_included = [1]
ec_earth_mips  = ['CMIP', 'AerChemMIP', 'CDRMIP', 'C4MIP',                   'DCPP',                              'HighResMIP', 'ISMIP6', 'LS3MIP', 'LUMIP', 'OMIP', 'PAMIP', 'PMIP', 'RFMIP', 'ScenarioMIP', 'VolMIP', 'CORDEX', 'DynVar', 'SIMIP', 'VIACSAB'] # All 19 EC-Earth MIPs
#ec_earth_mips = ['CMIP', 'AerChemMIP', 'CDRMIP', 'C4MIP', 'CFMIP', 'DAMIP', 'DCPP', 'FAFMIP', 'GeoMIP', 'GMMIP', 'HighResMIP', 'ISMIP6', 'LS3MIP', 'LUMIP', 'OMIP', 'PAMIP', 'PMIP', 'RFMIP', 'ScenarioMIP', 'VolMIP', 'CORDEX', 'DynVar', 'SIMIP', 'VIACSAB'] # All 24 CMIP6 MIPs
#ec_earth_mips = ['CMIP', 'DCPP']
#ec_earth_mips = ['CMIP'] # for basic test
experiment_counter = 0


command_0 = 'rm -rf cmip6-output-control-files'
os.system(command_0)

# Loop over MIPs:
for mip in dq.coll['mip'].items:
  # Loop over experiments:
  for u in dq.inx.iref_by_sect[mip.uid].a['experiment']:
    ex = dq.inx.uid[u]
    mip_label = mip.label
    if ex.label == 'esm-hist' or ex.label == 'esm-piControl':
     print 'Skipping this esm experiment ' + ex.label + ' because its CMIP6 data request fails so far.\n'
    else:
     if experiment_counter == 0:
       omit_setup_argument = ''
     else:
       omit_setup_argument = ' omit-setup'
     command   = './generate-ec-earth-namelists.sh ' + mip_label + ' ' + ex.label + ' ' + str(ex.tier[0]) + ' 1 ' + omit_setup_argument
     command_2 = 'rm -rf cmip6-output-control-files/' + mip_label + '/cmip6-experiment-*/file_def-compact'
     command_3 = 'rm -f  cmip6-output-control-files/' + mip_label + '/cmip6-experiment-*/cmip6-file_def_nemo.xml'
     command_4 = "sed -i -e 's/True\" field_ref=\"toce_pot\"/False\" field_ref=\"toce_pot\"/' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
     command_5 = "sed -i -e '/sfdsi_2/d' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
    #command_4 = "sed -i -e 's/True\" field_ref=\"toce_pot\"/False\" field_ref=\"toce_pot\"/' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-m=' + mip_label + '-e=' + ex.label + '-t=' + str(ex.tier[0]) + '-p=1/file_def_nemo-opa.xml'
    #command_5 = "sed -i -e '/sfdsi_2/d' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-m=' + mip_label + '-e=' + ex.label + '-t=' + str(ex.tier[0]) + '-p=1/file_def_nemo-opa.xml'
     command_6 = "sed -i -e 's/uoce_e3u_vsum_e2u_cumul. freq_op=.1ts/uoce_e3u_vsum_e2u_cumul/' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
    #print print '{}'.format(command)
     if mip_label in ec_earth_mips:
       #if ex.tier[0] in experiment_tiers_included and mip_label in ec_earth_mips and ex.label == 'piControl':  # for basic test
        if ex.tier[0] in experiment_tiers_included and mip_label in ec_earth_mips:
           os.system(command)
           os.system(command_2) # Remove the file_def-compact subdirectory with the compact file_def files
           os.system(command_3) # Remove the cmip6-file_def_nemo.xml file
          #os.system(command_4) # Just set the toce fields false again because we still face troubles with them
          #os.system(command_5) # Delete the line with sfdsi_2 from the file_def_nemo-opa.xml files
           os.system(command_6) # Remove the freq_op attribute for the variable msftbarot (uoce_e3u_vsum_e2u_cumul) from the file_def_nemo.xml file
           experiment_counter = experiment_counter + 1
        else:
           print ' Tier {} experiments are not included: Skipping: {}'.format(ex.tier[0], command)
     else:
        print ' EC-Earth3 does not participate in {:11}: Skipping: {}'.format(mip_label, command)


print ' There are {} experiments included. '.format(experiment_counter)

# Add a test case with which all available variables over all EC-Earth MIP experiments are switched on,
# i.e. are enabled in the file_def files:
command_a = "cp -r cmip6-output-control-files/CMIP/cmip6-experiment-CMIP-piControl/ cmip6-output-control-files/test-all-mips/"
command_b = "sed -i 's/enabled=\"False\"/enabled=\"True\"/' cmip6-output-control-files/test-all-mips/file_def_nemo-*"
command_c = "sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' cmip6-output-control-files/test-all-mips/file_def_nemo-*"
os.system(command_a) # Create a new subdirectory for testing all available variables in the file_def files
os.system(command_b) # Switch on all available variables in the file_def files
os.system(command_c) # Switch of the 'transect' variables (the transect grid definition seems to depend on the XIOS 2.5 upgrade)
