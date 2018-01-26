#!/bin/bash
# Thomas Reerink
#
# This scripts needs no arguments
#
# ${1} the first  argument is the MIP name
# ${2} the first  argument is the experiment name or MIP name in the latter case all MIP experiments are taken.
#
# Run example:
#  ./determine-missing-variables.sh CMIP CMIP
#

if [ "$#" -eq 2 ]; then
 mip=$1
 experiment=$2
 tier=1
 priority=1

 # Check whether more than one MIP is specified in the data request
 multiplemips='no'
 if [[ ${mip} == *","* ]];then
  multiplemips='yes'
  echo ' Multiple mip case = ' ${multiplemips}
 fi
 
 # Replace , by dot in label:
 mip_label=$(echo ${mip} | sed 's/,/-/g')      # Note that the checkvars.py script is not able to cope with this replacement if a dot is used instead of the dash in the replacement
#echo ' mip =' ${mip} '    experiment =' ${experiment} '    mip_label =' ${mip_label}
#echo "${mip_label}" | tr '[:upper:]' '[:lower:]'
#exit

#activateanaconda
 if ! type "drq" > /dev/null; then
  echo
  echo ' The CMIP6 data request tool drq is not available because of one of the following reasons:' 
  echo '  1. drq might be not installed'
  echo '  2. drq might be not active, as the anaconda environment is not activated'
  echo ' Stop'
  echo
 else
 #source activate ece2cmor3
  cd ${HOME}/cmorize/ece2cmor3/; python setup.py install; cd -;
  cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/cmip6-data-request/
  drq -m ${mip} -t ${tier} -p ${priority} -e ${experiment} --xls --xlsDir cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/
  if [ "${multiplemips}" == "yes" ]; then
   ./checkvars.py -v --vars cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/*.*TOTAL*.xlsx                                             --output cmvmm_m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  else
   ./checkvars.py -v --vars cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/*TOTAL*.xlsx                                               --output cmvmm_m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  #./checkvars.py -v --vars cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/cmvmm_${mip_label}_${experiment}_${tier}_${priority}.xlsx  --output cmvmm_m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  fi
 #source deactivate
 fi

#compare_directory='bup/bup8'
#diff cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.missing.txt           ${compare_directory}/cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.missing.txt           >  differences-with-${compare_directory}.txt
#diff cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.identifiedmissing.txt ${compare_directory}/cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.identifiedmissing.txt >> differences-with-${compare_directory}.txt
#diff cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.available.txt         ${compare_directory}/cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.available.txt         >> differences-with-${compare_directory}.txt
#diff cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.ignored.txt           ${compare_directory}/cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.ignored.txt           >> differences-with-${compare_directory}.txt

else
    echo '  '
    echo '  Illegal number of arguments, e.g.:'
    echo '  ' $0 CMIP CMIP
    echo '  or:'
    echo '  ' $0 CMIP,AerChemMIP CMIP
    echo '  '
fi

# Request for all EC-EARTH3-AOGCM MIPs of the CMIP experiments (default tier=1 and priority=1):
# ./determine-missing-variables.sh DCPP,LS3MIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB CMIP

# Request for all EC-EARTH3-AOGCM MIPs + DAMIP of the CMIP experiments (default tier=1 and priority=1):
# ./determine-missing-variables.sh DCPP,LS3MIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB,DAMIP CMIP

# Request for all EC-EARTH3 MIPs of the CMIP experiments (default tier=1 and priority=1):
# ./determine-missing-variables.sh CMIP,AerChemMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB CMIP

# Request for all EC-EARTH3 MIPs + DAMIP of the CMIP experiments (default tier=1 and priority=1):
# ./determine-missing-variables.sh CMIP,AerChemMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB,DAMIP CMIP
