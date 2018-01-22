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
 mip_label=$(echo ${mip} | sed 's/,/-/')       # Note that the checkvars.py script is not able to cope with this replacement if a dot is used instead of the dash in the replacement
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
  drq -m ${mip} -t ${tier} -p ${priority} -e ${experiment} --xls --xlsDir cmip6-data-request-m=${mip_label}-e=${experiment}
  cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/
  if [ "${multiplemips}" == "yes" ]; then
   ./checkvars.py -v --vars cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}/*.*TOTAL*.xlsx                                             --output cmvmm_m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  else
   ./checkvars.py -v --vars cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}/*TOTAL*.xlsx                                               --output cmvmm_m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  #./checkvars.py -v --vars cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}/cmvmm_${mip_label}_${experiment}_${tier}_${priority}.xlsx  --output cmvmm_m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  fi
 #source deactivate
 fi

 compare_directory='bup8'
 diff cmvmm_m=CMIP-e=CMIP-t=1-p=1.missing.txt           ${compare_directory}/cmvmm_m=CMIP-e=CMIP-t=1-p=1.missing.txt           >  differences-with-${compare_directory}.txt
 diff cmvmm_m=CMIP-e=CMIP-t=1-p=1.identifiedmissing.txt ${compare_directory}/cmvmm_m=CMIP-e=CMIP-t=1-p=1.identifiedmissing.txt >> differences-with-${compare_directory}.txt
 diff cmvmm_m=CMIP-e=CMIP-t=1-p=1.available.txt         ${compare_directory}/cmvmm_m=CMIP-e=CMIP-t=1-p=1.available.txt         >> differences-with-${compare_directory}.txt
 diff cmvmm_m=CMIP-e=CMIP-t=1-p=1.ignored.txt           ${compare_directory}/cmvmm_m=CMIP-e=CMIP-t=1-p=1.ignored.txt           >> differences-with-${compare_directory}.txt

else
    echo '  '
    echo '  Illegal number of arguments, e.g.:'
    echo '  ' $0 CMIP CMIP
    echo '  or:'
    echo '  ' $0 CMIP,AerChemMIP CMIP
    echo '  '
fi

# drq -m DCPP,LS3MIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB -e CMIP  --xls --xlsDir xls-CMIP-all-EC-EARTH3-AOGCM-mips
# ./checkvars.py -v --vars xls-CMIP-all-EC-EARTH3-AOGCM-mips/cmvmm_cm.co.dc.dy.ls.rf.sc.si.vi.vo_CMIP_1_1.xlsx   --output cmvmm_m=cm.co.dc.dy.ls.rf.sc.si.vi.vo-e=CMIP-t=1-p=1

# drq -m DCPP,LS3MIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB,DAMIP -e CMIP  --xls --xlsDir xls-CMIP-all-EC-EARTH3-AOGCM-mips
# ./checkvars.py -v --vars xls-CMIP-all-EC-EARTH3-AOGCM-mips/cmvmm_cm.co.da.dc.dy.ls.rf.sc.si.vi.vo_TOTAL_1_1.xlsx   --output cmvmm_m=cm.co.da.dc.dy.ls.rf.sc.si.vi.vo-e=CMIP-t=1-p=1

# All CMIP6 MIPs where EC-EARTH3 is involved:
# drq -m CMIP,AerChemMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB,DAMIP   -t 1 -p 1 -e CMIP --xls --xlsDir xls-all-ec-earth-participating-mips
# ./checkvars.py -v --vars xls-all-ec-earth-participating-mips/cmvmm_ae.c4.cm.co.da.dc.dy.hi.is.ls.lu.pm.rf.sc.si.vi.vo_TOTAL_1_1.xlsx    --output cmvmm_m=ae.c4.cm.co.da.dc.dy.hi.is.ls.lu.pm.rf.sc.si.vi.vo-e=TOTAL-t=1-p=1

# drq -m CMIP,AerChemMIP -t 1 -p 1 -e CMIP --xls --xlsDir xls-CMIP-AerChemMIP
# ./checkvars.py -v --vars xls-CMIP-AerChemMIP/cmvmm_ae.cm_TOTAL_1_1.xlsx    --output cmvmm_m=ae-cm-TOTAL_1_1-t=1-p=1
