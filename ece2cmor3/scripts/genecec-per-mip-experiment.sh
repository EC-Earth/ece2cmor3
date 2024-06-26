#!/usr/bin/env bash
# Thomas Reerink
#
# This scripts requires five arguments:
#  first  argument is the base directory name which will be created if not existing. The results will be placed in a subdirectory of this base directory.
#  second argument is the MIP name
#  third  argument is the experiment name or MIP name in the latter case all MIP experiments are taken.
#  fourth argument is the experiment tier (tier 1 is obligatory, higher tier is non-obligatory). In case tier 2 is specified, tier 1 and 2 experiments are considered.
#  fifth  argument is the maximum priority of the variables (1 is highest priority, 3 is lowest priority). In case priority 2 is specified, priority 1 and 2 variables are considered.
#
# Run this script without arguments for examples how to call this script.
#
# With this script it is possible to generate the EC-Earth3 control output files, i.e.
# the IFS Fortran namelists (the ppt files), the NEMO xml files for XIOS (the
# file_def files for OPA, LIM and PISCES) and the LPJ-GUESS instruction (.ins) file
# for one MIP experiment. In addition it produces the volume estimates for IFS, NEMO,
# LPJ-GUESS and TM5.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.
#
# Note that this script is called in a loop over the MIP experiments by the script:
#  genecec.py


if [ "$#" -eq 5 ]; then

  if ! type "ece2cmor" > /dev/null; then
   echo
   echo ' The CMIP6 data request tool ece2cmor is not available because of one of the following reasons:'
   echo '  1. ece2cmor might be not installed'
   echo '  2. ece2cmor might be not active, check whether the ece2cmor3 environment is activated'
   echo ' Stop'
   echo
   exit
  fi

  if ! type "drq" > /dev/null; then
   echo
   echo ' The CMIP6 data request tool drq is not available because of one of the following reasons:'
   echo '  1. drq might be not installed'
   echo '  2. drq might be not active, check whether the ece2cmor3 environment is activated'
   echo ' Stop'
   echo
   exit
  fi

  base_dir_name=$1
  mip=$2
  experiment=$3
  tier=$4
  priority=$5

  # Check whether more than one MIP is specified in the data request
  multiplemips='no'
  if [[ ${mip} = *","* ]];then
   multiplemips='yes'
   echo " Multiple mip case = ${multiplemips}"
  fi

  # Replace the comma(s) by dot(s) in label:
  mip_label=$(echo ${mip} | sed 's/,/./g')

  if [ "${multiplemips}" = "yes" ]; then
   # The first two lower case characters of the multiple mip string are saved for selecting the experiment data request file:
   select_substring=$(echo "${mip_label:0:2}" | tr '[:upper:]' '[:lower:]')
  else
   if [ "${mip}" = "AerChemMIP" ]; then
    # For AerChemMIP the joined data request including the Core MIP request is prefered instead of only the specific AerChemMIP experiment specific request:
    # The first two lower case characters of the multiple mip string are saved for selecting the experiment data request file:
    select_substring=$(echo "${mip_label:0:2}" | tr '[:upper:]' '[:lower:]')
   else
    select_substring=${mip}
   fi
  fi

  path_of_created_output_control_files=${base_dir_name}/${mip_label}/cmip6-experiment-${mip_label}-${experiment}

  echo
  echo "Executing the following job:"
  echo " $0 $@"

  if [ ${experiment} = 'esm-hist' ] || [ ${experiment} = 'esm-piControl' ]; then
   esm_label=' --esm'
  else
   esm_label=''
  fi

  xls_dir=cmip6-data-request/cmip6-data-request-${mip_label}-${experiment}-t${tier}-p${priority}
  mkdir -p ${xls_dir};

  echo
  echo "The CMIP6 data request is obtained from:"
  echo " drq -m ${mip} -e ${experiment} -t ${tier} -p ${priority} ${esm_label} --xls --xlsDir ${xls_dir}"
  echo

  drq -m ${mip} -e ${experiment} -t ${tier} -p ${priority} ${esm_label} --xls --xlsDir ${xls_dir}

  # Because in the VolMIP dcppC-forecast-addPinatubo experiment the cmvme_${mip_label}_${experiment}_1_1.xlsx file is not produced, a link
  # with this name is created to a file cmvme_cm.vo_${experiment}_1_1.xlsx which should be most similar:
  if [ ${mip_label} = 'VolMIP' ] && [ ${experiment} = 'dcppC-forecast-addPinatubo' ]; then
   cd ${xls_dir}
   if [ -L cmvme_${mip_label}_${experiment}_1_1.xlsx ]; then
    rm -f cmvme_${mip_label}_${experiment}_1_1.xlsx
   fi
   # However, first check whether the file is correctly present, in that case no action:
   if [ ! -f cmvme_${mip_label}_${experiment}_1_1.xlsx ]; then
    ln -s cmvme_cm.vo_${experiment}_1_1.xlsx cmvme_${mip_label}_${experiment}_1_1.xlsx
    echo
    echo "Create for ${mip_label} a soft link:"
    ls -l cmvme_${mip_label}_${experiment}_1_1.xlsx
   fi
  cd -
  fi

  # Note that the *TOTAL* selection below has the risk that more than one file is selected (causing a crash) which only could happen if externally files are added in this directory:

  cmip6_data_request_file=${xls_dir}/cmvme_${select_substring}*${experiment}_${tier}_${priority}.xlsx

  # Check whether there will be selected a unique matching data request file in the created data request directory:
  number_of_matching_files=$(ls -1 ${cmip6_data_request_file}|wc -l)
  if [ ${number_of_matching_files} != 1 ]; then
   echo "Number of matching files: ${number_of_matching_files}"
   ls ${cmip6_data_request_file}
   exit
  fi

  mkdir -p ${path_of_created_output_control_files}
  if [ ${mip_label} != 'OMIP' ] && [ ${experiment} != 'rad-irf' ]; then
   # Create the ppt files for IFS input and estimate the Volume of the IFS output:
   drq2ppt --drq ${cmip6_data_request_file}

   if [ -f pptdddddd0100 ]; then rm -f pptdddddd0100 ; fi                 # Removing the hourly / sub hourly table variables.
   mv -f ppt0000000000 pptdddddd* ${path_of_created_output_control_files}
  else
   echo
   echo 'Due to an empty IFS requests, see:'
   if [ ${mip_label}  = 'OMIP'    ]; then echo ' https://github.com/EC-Earth/ece2cmor3/issues/660'; fi
   if [ ${experiment} = 'rad-irf' ]; then echo ' https://github.com/EC-Earth/ece2cmor3/issues/661'; fi
   echo "the script $0 will skip:"
   echo "drq2ppt --drq ${cmip6_data_request_file}"
   echo
  fi

  # Creating the file_def files for XIOS NEMO input and estimate the Volume of the NEMO output:
  drq2file_def --drq ${cmip6_data_request_file}
  rm -f cmip6-file_def_nemo.xml
  mv -f file_def_nemo-opa.xml    ${path_of_created_output_control_files}
  mv -f file_def_nemo-lim3.xml   ${path_of_created_output_control_files}
  mv -f file_def_nemo-pisces.xml ${path_of_created_output_control_files}

  # Creating the instruction files for LPJ-GUESS and estimating the Volume of the LPJ-GUESS output:
  drq2ins --drq ${cmip6_data_request_file}
  mv -f ./lpjg_cmip6_output.ins ${path_of_created_output_control_files}

  # Estimating the Volume of the TM5 output:
  estimate_tm5_volume --drq ${cmip6_data_request_file}

  cat volume-estimate-ifs.txt volume-estimate-nemo.txt volume-estimate-tm5.txt volume-estimate-lpj-guess.txt > ${path_of_created_output_control_files}/volume-estimate.txt
  rm -f volume-estimate-ifs.txt volume-estimate-nemo.txt volume-estimate-tm5.txt volume-estimate-lpj-guess.txt
  echo

  # Generating the available, ignored, identified missing and missing files for this MIP experiment:
  xls_ece_dir=cmip6-data-request-ece/cmip6-data-request-ece-${mip_label}-${experiment}-t${tier}-p${priority}
  mkdir -p ${xls_ece_dir};
  checkvars -v --drq ${cmip6_data_request_file} --output ${xls_ece_dir}/cmvmm_${mip_label}-${experiment}-t${tier}-p${priority}

  echo
  echo 'The produced data request excel file:'
  ls -1 ${cmip6_data_request_file}

  echo
  echo 'The generated ppt files are:'
  ls -1 ${path_of_created_output_control_files}/ppt0000000000
  ls -1 ${path_of_created_output_control_files}/pptdddddd0300
  ls -1 ${path_of_created_output_control_files}/pptdddddd0600

  echo
  echo 'The generated file_def files are:'
  ls -1 ${path_of_created_output_control_files}/file_def_nemo-opa.xml
  ls -1 ${path_of_created_output_control_files}/file_def_nemo-lim3.xml
  ls -1 ${path_of_created_output_control_files}/file_def_nemo-pisces.xml
  echo

else
  echo
  echo " This scripts requires five arguments: base output directory, MIP (or comma separated lsit of MIPs), MIP experiment, experiment tier, priority level of variables included, e.g.:"
  echo "  $0 cmip6-output-control-files CMIP                                                                           piControl 1 1"
  echo "  $0 cmip6-output-control-files CMIP,DCPP,LS3MIP,PAMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB piControl 1 1"
  echo
fi

# ./genecec-per-mip-experiment.sh cmip6-output-control-files CMIP         1pctCO2      1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files CMIP         abrupt-4xCO2 1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files CMIP         amip         1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files CMIP         historical   1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files CMIP         piControl    1 1

# ./genecec-per-mip-experiment.sh cmip6-output-control-files AerChemMIP   piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files CDRMIP       piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files C4MIP        piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files DCPP         piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files HighResMIP   piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files ISMIP6       piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files LS3MIP       piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files LUMIP        piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files OMIP         piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files PAMIP        piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files PMIP         piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files RFMIP        piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files ScenarioMIP  piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files VolMIP       piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files CORDEX       piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files DynVarMIP    piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files SIMIP        piControl    1 1
# ./genecec-per-mip-experiment.sh cmip6-output-control-files VIACSAB      piControl    1 1
