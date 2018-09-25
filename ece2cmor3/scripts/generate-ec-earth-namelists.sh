#!/bin/bash
# Thomas Reerink
#
# This scripts needs no arguments
#
# ${1} the first   argument is the MIP name
# ${2} the second  argument is the experiment name or MIP name in the latter case all MIP experiments are taken.
# ${3} the third   argument is the experiment tier (tier 1 is obligatory, higher tier is non-obligatory). In case tier 2 is specified, tier 1 and 2 experiments are considered.
# ${4} the fourth  argument is the maximum priority of the variables (1 is highest priority, 3 is lowest priority). In case priority 2 is specified, priority 1 and 2 variables are considered.
# ${5} the fifth   OPTIONAL argument will omit the install of the ece2cmor setup if equal to "omit-setup". To improve the performance when calling this script multiple times from another script.
#
#
# Run example:
#  ./generate-ec-earth-namelists.sh CMIP amip 1 1
#


# Set the root directory of ece2cmor3 (default ${HOME}/cmorize/ece2cmor3/ ):
ece2cmor_root_directory=${HOME}/cmorize/ece2cmor3/

# Test whether the ece2cmor_root_directory exists:
if [ ! -d ${ece2cmor_root_directory} ]; then 
 echo
 echo ' The root directory of ece2cmor3: ' ${ece2cmor_root_directory} ' is not found.'
 echo ' Adjust the ece2cmor_root_directory at line 19 of the script: ' $0
 echo ' Stop'
 exit
 echo
fi

if [ "$#" -eq 4 ] || [ "$#" -eq 5 ]; then
 mip=$1
 experiment=$2
 tier=$3
 priority=$4

 install_setup="include-setup"
 if [ "$#" -eq 5 ]; then
  if [ "$5" = "omit-setup" ]; then
   install_setup="omit-setup"
  fi
 fi
 
 # Replace , by dot in label:
 mip_label=$(echo ${mip} | sed 's/,/./g')

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
  if [ "${install_setup}" = "include-setup" ]; then
   cd ${ece2cmor_root_directory}; python setup.py install; cd -;
  else
   echo "Omit python setup.py install"
  fi
  echo
  echo 'Executing the following job:'
  echo ' '$0 "$@"
  echo
  echo 'First, the CMIP6 data request is applied by:'
  echo ' ' drq -m ${mip} -t ${tier} -p ${priority} -e ${experiment} --xls --xlsDir cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  echo

  mkdir -p  ${ece2cmor_root_directory}/ece2cmor3/scripts/cmip6-data-request/; cd ${ece2cmor_root_directory}/ece2cmor3/scripts/cmip6-data-request/;
  drq -m ${mip} -t ${tier} -p ${priority} -e ${experiment} --xls --xlsDir cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}
  cd ${ece2cmor_root_directory}/ece2cmor3/scripts/
  # Note that the *TOTAL* selection below has the risk that more than one file is selected (causing a crash) which only could happen if externally files are added in this directory:
  ./drq2ppt.py --vars cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/cmvmm_${mip_label}_TOTAL_${tier}_${priority}.xlsx
 #./drq2ppt.py --vars cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/cmvmm_${mip_label}_${experiment}_${tier}_${priority}.xlsx
 #source deactivate
 fi
 mkdir -p ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/file_def-compact
 mv -f ppt0000000000 pptdddddd0*00 ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/

 # Creating the file_def files for XIOS NEMO input:.
 ./drq2file_def-nemo.py --vars cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/cmvme_${mip_label}_${experiment}_${tier}_${priority}.xlsx
 mv -f ./xios-nemo-file_def-files/cmip6-file_def_nemo.xml          ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/
 mv -f ./xios-nemo-file_def-files/file_def_nemo-opa.xml            ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/
 mv -f ./xios-nemo-file_def-files/file_def_nemo-lim3.xml           ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/
 mv -f ./xios-nemo-file_def-files/file_def_nemo-pisces.xml         ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/
 mv -f ./xios-nemo-file_def-files/file_def_nemo-opa-compact.xml    ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/file_def-compact/file_def_nemo-opa.xml
 mv -f ./xios-nemo-file_def-files/file_def_nemo-lim3-compact.xml   ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/file_def-compact/file_def_nemo-lim3.xml
 mv -f ./xios-nemo-file_def-files/file_def_nemo-pisces-compact.xml ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/file_def-compact/file_def_nemo-pisces.xml

 echo
 echo 'The produced data request excel file:'
 ls -1 cmip6-data-request/cmip6-data-request-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/cmvmm_${mip_label}_TOTAL_${tier}_${priority}.xlsx

 echo
 echo 'The generated ppt files are:'
 ls -1 ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/ppt0000000000
 ls -1 ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/pptdddddd0300
 ls -1 ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/pptdddddd0600

 echo
 echo 'The generated file_def files are:'
 ls -1 ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/cmip6-file_def_nemo.xml
 ls -1 ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/file_def_nemo-opa.xml
 ls -1 ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/file_def_nemo-lim3.xml
 ls -1 ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/file_def_nemo-pisces.xml
 ls -1 ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/file_def-compact/file_def_nemo-opa.xml
 ls -1 ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/file_def-compact/file_def_nemo-lim3.xml
 ls -1 ec-earth-cmip6-nemo-namelists/${mip_label}/cmip6-experiment-m=${mip_label}-e=${experiment}-t=${tier}-p=${priority}/file_def-compact/file_def_nemo-pisces.xml
 echo

else
    echo '  '
    echo '  This scripts requires four arguments: MIP, MIP experiment, experiment tier, priority of variable, e.g.:'
    echo '  ' $0 CMIP piControl 1 1
    echo '  or with the fifth optional arument the "python setup.py install" is omitted:'
    echo '  ' $0 CMIP piControl 1 1 omit-setup
    echo '  '
fi

# ./generate-ec-earth-namelists.sh CMIP         1pctCO2      1 1
# ./generate-ec-earth-namelists.sh CMIP         abrupt-4xCO2 1 1
# ./generate-ec-earth-namelists.sh CMIP         amip         1 1
# ./generate-ec-earth-namelists.sh CMIP         historical   1 1
# ./generate-ec-earth-namelists.sh CMIP         piControl    1 1

# ./generate-ec-earth-namelists.sh AerChemMIP   piControl 1 1
# ./generate-ec-earth-namelists.sh C4MIP        piControl 1 1
# ./generate-ec-earth-namelists.sh DCPP         piControl 1 1
# ./generate-ec-earth-namelists.sh HighResMIP   piControl 1 1
# ./generate-ec-earth-namelists.sh ISMIP6       piControl 1 1
# ./generate-ec-earth-namelists.sh LS3MIP       piControl 1 1
# ./generate-ec-earth-namelists.sh LUMIP        piControl 1 1
# ./generate-ec-earth-namelists.sh PMIP         piControl 1 1
# ./generate-ec-earth-namelists.sh RFMIP        piControl 1 1
# ./generate-ec-earth-namelists.sh ScenarioMIP  piControl 1 1
# ./generate-ec-earth-namelists.sh VolMIP       piControl 1 1
# ./generate-ec-earth-namelists.sh CORDEX       piControl 1 1
# ./generate-ec-earth-namelists.sh DynVar       piControl 1 1
# ./generate-ec-earth-namelists.sh SIMIP        piControl 1 1
# ./generate-ec-earth-namelists.sh VIACSAB      piControl 1 1
# ./generate-ec-earth-namelists.sh DAMIP        piControl 1 1

