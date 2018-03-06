#!/bin/bash
# Thomas Reerink
#
# This scripts needs no arguments
#
# ${1} the first   argument is the MIP name
# ${2} the second  argument is the experiment name or MIP name in the latter case all MIP experiments are taken.
# ${3} the third   argument is the experiment tier (tier 1 is obligatory, higher tier is non-obligatory)
# ${4} the fourth  argument is the maximum priority of the variables (1 is highest priority, 3 is lowest priority)
#
# Run example:
#  ./determine-missing-variables.sh CMIP CMIP 1 1
#

if [ "$#" -eq 4 ]; then
 mip=$1
 experiment=$2
 tier=$3
 priority=$4

 # Check whether more than one MIP is specified in the data request
 multiplemips='no'
 if [[ ${mip} == *","* ]];then
  multiplemips='yes'
  echo ' Multiple mip case = ' ${multiplemips}
 fi
 
 # Replace , by dot in label:
 mip_label=$(echo ${mip} | sed 's/,/./g')
#echo ' mip =' ${mip} '    experiment =' ${experiment} '    mip_label =' ${mip_label}
#echo "${mip_label}" | tr '[:upper:]' '[:lower:]'

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
  mkdir -p  ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/cmip6-data-request/; cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/cmip6-data-request/;
  drq -m ${mip} -t ${tier} -p ${priority} -e ${experiment} --xls --xlsDir cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/
  # Note that the *TOTAL* selection below has the risk that more than one file is selected (causing a crash) which only could happen if externally files are added in this directory:
  if [ "${multiplemips}" == "yes" ]; then
   ./checkvars.py -v --vars cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/*.*TOTAL*.xlsx                                             --output cmvmm_m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  else
   ./checkvars.py -v --vars cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/cmvmm_${mip_label}_TOTAL_${tier}_${priority}.xlsx          --output cmvmm_m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  #./checkvars.py -v --vars cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/cmvmm_${mip_label}_${experiment}_${tier}_${priority}.xlsx  --output cmvmm_m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  fi
 #source deactivate
 fi

 diff_with_benchmark=false
 benchmark='benchmark-03'
 if ${diff_with_benchmark} ; then
  echo 'Diff missing.txt file:       ' >  differences-with-${benchmark}.txt;  diff cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.missing.txt           benchmark/${benchmark}/cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.missing.txt           >> differences-with-${benchmark}.txt; echo ' ' >> differences-with-${benchmark}.txt;
  echo 'Diff identified missing file:' >> differences-with-${benchmark}.txt;  diff cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.identifiedmissing.txt benchmark/${benchmark}/cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.identifiedmissing.txt >> differences-with-${benchmark}.txt; echo ' ' >> differences-with-${benchmark}.txt;
  echo 'Diff available.txt file:     ' >> differences-with-${benchmark}.txt;  diff cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.available.txt         benchmark/${benchmark}/cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.available.txt         >> differences-with-${benchmark}.txt; echo ' ' >> differences-with-${benchmark}.txt;
  echo 'Diff ignored.txt file:       ' >> differences-with-${benchmark}.txt;  diff cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.ignored.txt           benchmark/${benchmark}/cmvmm_m=CMIP-e=CMIP-t=${tier}-p=${priority}.ignored.txt           >> differences-with-${benchmark}.txt; echo ' ' >> differences-with-${benchmark}.txt;
 fi

else
    echo '  '
    echo '  Illegal number of arguments, e.g.:'
    echo '  ' $0 CMIP CMIP 1 1
    echo '  or:'
    echo '  ' $0 CMIP,AerChemMIP CMIP 1 1
    echo '  '
fi

# Filling eventually some or all of the omit lists below:
#  cp cmvmm_m=CMIP-e=CMIP-t=1-p=1.missing.xlsx ../resources/lists-of-omitted-variables/list-of-omitted-variables-01.xlsx
#  cp identification/NEMO-identification/to-be-checked-if-PISCES-can-provide--not-in-LPJ-GUESS-version-2.xlsx ../resources/lists-of-omitted-variables/list-of-omitted-variables-02.xlsx
#  cp cmvmm_m=CMIP.AerChemMIP.C4MIP.DCPP.HighResMIP.ISMIP6.LS3MIP.LUMIP.PMIP.RFMIP.ScenarioMIP.VolMIP.CORDEX.DynVar.SIMIP.VIACSAB.DAMIP-e=CMIP-t=1-p=1.missing.xlsx ../resources/lists-of-omitted-variables/list-of-omitted-variables-03.xlsx

# Request for all EC-EARTH3-AOGCM MIPs (+ DAMIP) of the CMIP experiments for tier=1 and priority=1:
# ./determine-missing-variables.sh DCPP,LS3MIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB CMIP 1 1
# ./determine-missing-variables.sh DCPP,LS3MIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB,DAMIP CMIP 1 1

# Request for all EC-EARTH3 MIPs (+ DAMIP) of the CMIP experiments for tier=1 and priority=1:
# ./determine-missing-variables.sh CMIP,AerChemMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB       CMIP 1 1
# ./determine-missing-variables.sh CMIP,AerChemMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB,DAMIP CMIP 1 1

# ./determine-missing-variables.sh AerChemMIP  AerChemMIP   1 1
# ./determine-missing-variables.sh C4MIP       C4MIP        1 1
# ./determine-missing-variables.sh DCPP        DCPP         1 1
# ./determine-missing-variables.sh HighResMIP  HighResMIP   1 1
# ./determine-missing-variables.sh ISMIP6      ISMIP6       1 1
# ./determine-missing-variables.sh LS3MIP      LS3MIP       1 1
# ./determine-missing-variables.sh LUMIP       LUMIP        1 1
# ./determine-missing-variables.sh PMIP        PMIP         1 1
# ./determine-missing-variables.sh RFMIP       RFMIP        1 1
# ./determine-missing-variables.sh ScenarioMIP ScenarioMIP  1 1
# ./determine-missing-variables.sh VolMIP      VolMIP       1 1
# ./determine-missing-variables.sh CORDEX      CORDEX       1 1
# ./determine-missing-variables.sh DynVar      DynVar       1 1
# ./determine-missing-variables.sh SIMIP       SIMIP        1 1
# ./determine-missing-variables.sh VIACSAB     VIACSAB      1 1
# ./determine-missing-variables.sh DAMIP       DAMIP        1 1

# ll *.missing.xlsx|grep -v 5.4K
