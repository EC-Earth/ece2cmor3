#!/bin/bash
# Thomas Reerink
#
# This scripts requires four arguments (a fifth argument is OPTIONAL):
#
# ${1} the first   argument is the MIP name. The first argument can represent a list of MIPs, seperated by commas.
# ${2} the second  argument is the experiment name or MIP name in the latter case all MIP experiments are taken.
# ${3} the third   argument is the experiment tier (tier 1 is obligatory, higher tier is non-obligatory). In case tier 2 is specified, tier 1 and 2 experiments are considered.
# ${4} the fourth  argument is the maximum priority of the variables (1 is highest priority, 3 is lowest priority). In case priority 2 is specified, priority 1 and 2 variables are considered.
# ${5} the fifth   argument [OPTIONAL] is an additional checkvars.py argument, e.g.: --nemo for only ocean variables
#
# Run example:
#  ./determine-missing-variables.sh CMIP CMIP 1 1
#


# Set the root directory of ece2cmor3 (default ${HOME}/cmorize/ece2cmor3/ ):
ece2cmor_root_directory=${HOME}/cmorize/ece2cmor3/

# Test whether the ece2cmor_root_directory exists:
if [ ! -d ${ece2cmor_root_directory} ]; then 
 echo
 echo ' The root directory of ece2cmor3: ' ${ece2cmor_root_directory} ' is not found.'
 echo ' Adjust the ece2cmor_root_directory at line 18 of the script: ' $0
 echo ' Stop'
 echo
 exit
fi


if [ "$#" -eq 4 ] || [ "$#" -eq 5 ]; then
 mip=$1
 experiment=$2
 tier=$3
 priority=$4
 if [ "$#" -eq 5 ]; then
  additional_checkvars_argument=$5
 else
  additional_checkvars_argument=''
 fi

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
  exit
 else
 #source activate ece2cmor3
  cd ${ece2cmor_root_directory}; python setup.py install; cd -;
  mkdir -p  ${ece2cmor_root_directory}/ece2cmor3/scripts/cmip6-data-request/; cd ${ece2cmor_root_directory}/ece2cmor3/scripts/cmip6-data-request/;
  if [ ${mip} = 'VolMIP' ]; then
   drq -m ${mip} -t ${tier} -p ${priority}                  --xls --xlsDir cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  else
   drq -m ${mip} -t ${tier} -p ${priority} -e ${experiment} --xls --xlsDir cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  fi
  cd ${ece2cmor_root_directory}/ece2cmor3/scripts/
  # Note that the *TOTAL* selection below has the risk that more than one file is selected (causing a crash) which only could happen if externally files are added in this directory:
  if [ "${multiplemips}" == "yes" ]; then
   ./checkvars.py ${additional_checkvars_argument} -v --drq cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/*.*TOTAL*.xlsx                                             --output cmvmm_m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  else
   ./checkvars.py ${additional_checkvars_argument} -v --drq cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/cmvmm_${mip_label}_TOTAL_${tier}_${priority}.xlsx          --output cmvmm_m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  #./checkvars.py -v --drq cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/cmvmm_${mip_label}_${experiment}_${tier}_${priority}.xlsx  --output cmvmm_m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  fi
 #source deactivate
 fi


 if [ ${mip} == 'CMIP,AerChemMIP,CDRMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,OMIP,PAMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB' ] && [ ${experiment} == 'CMIP' ]; then
  mv cmvmm_m=CMIP.AerChemMIP.CDRMIP.C4MIP.DCPP.HighResMIP.ISMIP6.LS3MIP.LUMIP.OMIP.PAMIP.PMIP.RFMIP.ScenarioMIP.VolMIP.CORDEX.DynVarMIP.SIMIP.VIACSAB-e=CMIP-t=1-p=1.available.json         cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.available.json
  mv cmvmm_m=CMIP.AerChemMIP.CDRMIP.C4MIP.DCPP.HighResMIP.ISMIP6.LS3MIP.LUMIP.OMIP.PAMIP.PMIP.RFMIP.ScenarioMIP.VolMIP.CORDEX.DynVarMIP.SIMIP.VIACSAB-e=CMIP-t=1-p=1.missing.txt            cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.missing.txt
  mv cmvmm_m=CMIP.AerChemMIP.CDRMIP.C4MIP.DCPP.HighResMIP.ISMIP6.LS3MIP.LUMIP.OMIP.PAMIP.PMIP.RFMIP.ScenarioMIP.VolMIP.CORDEX.DynVarMIP.SIMIP.VIACSAB-e=CMIP-t=1-p=1.identifiedmissing.txt  cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.identifiedmissing.txt
  mv cmvmm_m=CMIP.AerChemMIP.CDRMIP.C4MIP.DCPP.HighResMIP.ISMIP6.LS3MIP.LUMIP.OMIP.PAMIP.PMIP.RFMIP.ScenarioMIP.VolMIP.CORDEX.DynVarMIP.SIMIP.VIACSAB-e=CMIP-t=1-p=1.available.txt          cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.available.txt
  mv cmvmm_m=CMIP.AerChemMIP.CDRMIP.C4MIP.DCPP.HighResMIP.ISMIP6.LS3MIP.LUMIP.OMIP.PAMIP.PMIP.RFMIP.ScenarioMIP.VolMIP.CORDEX.DynVarMIP.SIMIP.VIACSAB-e=CMIP-t=1-p=1.ignored.txt            cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.ignored.txt
  mv cmvmm_m=CMIP.AerChemMIP.CDRMIP.C4MIP.DCPP.HighResMIP.ISMIP6.LS3MIP.LUMIP.OMIP.PAMIP.PMIP.RFMIP.ScenarioMIP.VolMIP.CORDEX.DynVarMIP.SIMIP.VIACSAB-e=CMIP-t=1-p=1.missing.xlsx           cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.missing.xlsx
  mv cmvmm_m=CMIP.AerChemMIP.CDRMIP.C4MIP.DCPP.HighResMIP.ISMIP6.LS3MIP.LUMIP.OMIP.PAMIP.PMIP.RFMIP.ScenarioMIP.VolMIP.CORDEX.DynVarMIP.SIMIP.VIACSAB-e=CMIP-t=1-p=1.identifiedmissing.xlsx cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.identifiedmissing.xlsx
  mv cmvmm_m=CMIP.AerChemMIP.CDRMIP.C4MIP.DCPP.HighResMIP.ISMIP6.LS3MIP.LUMIP.OMIP.PAMIP.PMIP.RFMIP.ScenarioMIP.VolMIP.CORDEX.DynVarMIP.SIMIP.VIACSAB-e=CMIP-t=1-p=1.available.xlsx         cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.available.xlsx
  mv cmvmm_m=CMIP.AerChemMIP.CDRMIP.C4MIP.DCPP.HighResMIP.ISMIP6.LS3MIP.LUMIP.OMIP.PAMIP.PMIP.RFMIP.ScenarioMIP.VolMIP.CORDEX.DynVarMIP.SIMIP.VIACSAB-e=CMIP-t=1-p=1.ignored.xlsx           cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.ignored.xlsx
 fi

 # Some benchmark diffing, which can be activated by the developer:
 benchmark_step_1_and_2='benchmark-step-1+2-v39'

 if [ -d benchmark/${benchmark_step_1_and_2} ] && [ ${mip} == 'CMIP,AerChemMIP,CDRMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,OMIP,PAMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB' ] && [ ${experiment} == 'CMIP' ]; then
  echo 'Diff missing.txt file:       ' >  differences-with-${benchmark_step_1_and_2}.txt;  diff -b cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.missing.txt           benchmark/${benchmark_step_1_and_2}/cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.missing.txt           >> differences-with-${benchmark_step_1_and_2}.txt; echo ' ' >> differences-with-${benchmark_step_1_and_2}.txt;
  echo 'Diff identified missing file:' >> differences-with-${benchmark_step_1_and_2}.txt;  diff -b cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.identifiedmissing.txt benchmark/${benchmark_step_1_and_2}/cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.identifiedmissing.txt >> differences-with-${benchmark_step_1_and_2}.txt; echo ' ' >> differences-with-${benchmark_step_1_and_2}.txt;
  echo 'Diff available.txt file:     ' >> differences-with-${benchmark_step_1_and_2}.txt;  diff -b cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.available.txt         benchmark/${benchmark_step_1_and_2}/cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.available.txt         >> differences-with-${benchmark_step_1_and_2}.txt; echo ' ' >> differences-with-${benchmark_step_1_and_2}.txt;
  echo 'Diff ignored.txt file:       ' >> differences-with-${benchmark_step_1_and_2}.txt;  diff -b cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.ignored.txt           benchmark/${benchmark_step_1_and_2}/cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.ignored.txt           >> differences-with-${benchmark_step_1_and_2}.txt; echo ' ' >> differences-with-${benchmark_step_1_and_2}.txt;
 fi

else
    echo '  '
    echo '  This scripts requires four arguments: MIP, MIP experiment, experiment tier, priority of variable, e.g.:'
    echo '  ' $0 CMIP CMIP 1 1
    echo '  The first argument can represent a list of MIPs, seperated by commas, e.g.:'
    echo '  ' $0 CMIP,AerChemMIP,CDRMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,OMIP,PAMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB CMIP 1 1
    echo '  '
fi

# Filling eventually some or all of the omit lists below:
#  cp cmvmm_m=CMIP-e=CMIP-t=1-p=1.missing.xlsx ../resources/lists-of-omitted-variables/list-of-omitted-variables-01.xlsx
#  cp identification/NEMO-identification/to-be-checked-if-PISCES-can-provide--not-in-LPJ-GUESS-version-2.xlsx ../resources/lists-of-omitted-variables/list-of-omitted-variables-02.xlsx
#  cp cmvmm_m=CMIP.AerChemMIP.CDRMIP.C4MIP.DCPP.HighResMIP.ISMIP6.LS3MIP.LUMIP.OMIP.PAMIP.PMIP.RFMIP.ScenarioMIP.VolMIP.CORDEX.DynVarMIP.SIMIP.VIACSAB-e=CMIP-t=1-p=1.missing.xlsx ../resources/lists-of-omitted-variables/list-of-omitted-variables-03.xlsx


# Step 1: Request for CMIP experiments for tier=1 and priority=1:
# ./determine-missing-variables.sh CMIP CMIP 1 1

# Step 1+2: Request for all EC-EARTH3 MIPs of the CMIP experiments for tier=1 and priority=1:
# ./determine-missing-variables.sh CMIP,AerChemMIP,CDRMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,OMIP,PAMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB CMIP 1 1

# Step 3:

# cpf benchmark/benchmark-step-1+2-v39-pextra/cmvmm_m=all-ece-mips-step-1+2-e=CMIP-t=1-p=1.available.xlsx              ../resources/lists-of-omitted-variables/list-of-omitted-variables-01.xlsx
# cpf benchmark/benchmark-step-1+2-v39-pextra/cmvmm_m\=all-ece-mips-step-1+2-e\=CMIP-t\=1-p\=1.identifiedmissing.xlsx  ../resources/lists-of-omitted-variables/list-of-omitted-variables-02.xlsx
# cpf benchmark/benchmark-step-1+2-v39-pextra/cmvmm_m\=all-ece-mips-step-1+2-e\=CMIP-t\=1-p\=1.ignored.xlsx            ../resources/lists-of-omitted-variables/list-of-omitted-variables-03.xlsx
#
# ./determine-missing-variables.sh AerChemMIP  AerChemMIP   1 1
# ./determine-missing-variables.sh CDRMIP      CDRMIP       1 1
# ./determine-missing-variables.sh C4MIP       C4MIP        1 1
# ./determine-missing-variables.sh DCPP        DCPP         1 1
# ./determine-missing-variables.sh HighResMIP  HighResMIP   1 1
# ./determine-missing-variables.sh ISMIP6      ISMIP6       1 1
# ./determine-missing-variables.sh LS3MIP      LS3MIP       1 1
# ./determine-missing-variables.sh LUMIP       LUMIP        1 1
# ./determine-missing-variables.sh OMIP        OMIP         1 1
# ./determine-missing-variables.sh PAMIP       PAMIP        1 1
# ./determine-missing-variables.sh PMIP        PMIP         1 1
# ./determine-missing-variables.sh RFMIP       RFMIP        1 1
# ./determine-missing-variables.sh ScenarioMIP ScenarioMIP  1 1
# ./determine-missing-variables.sh VolMIP      VolMIP       1 1   # The request: drq -m VolMIP -e VolMIP -p 1 -t 1  gives an error (see #573) with: -e VolMIP after drq version 01.00.29
#
# git checkout ../resources/lists-of-omitted-variables/list-of-omitted-variables-*.xlsx

# The Diagnostic MIPs (CORDEX,DynVarMI, SIMIP & VIACSAB) have no self defined experiments

# ll *.missing.xlsx|grep -v 5.5K
