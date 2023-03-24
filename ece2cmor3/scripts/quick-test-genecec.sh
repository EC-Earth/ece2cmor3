#!/usr/bin/env bash
# Thomas Reerink
#
# Run this script without arguments for examples how to call this script.
#
# With this script a quick genecec test can be run and the output is written to a log file.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.
#
# Note that this script calls genecec.py


if [ "$#" -eq 1 ]; then

  if ! type "ece2cmor" > /dev/null; then
   echo; tput setaf 1;
   echo ' The CMIP6 data request tool ece2cmor is not available because of one of the following reasons:'
   echo '  1. ece2cmor might be not installed'
   echo '  2. ece2cmor might be not active, check whether the ece2cmor3 environment is activated'
   echo ' Stop'
   tput sgr0; echo
   exit
  fi

  if ! type "drq" > /dev/null; then
   echo; tput setaf 1;
   echo ' The CMIP6 data request tool drq is not available because of one of the following reasons:'
   echo '  1. drq might be not installed'
   echo '  2. drq might be not active, check whether the ece2cmor3 environment is activated'
   echo ' Stop'
   tput sgr0; echo
   exit
  fi

  test_version=$1

  mip_list=CMIP,DCPP,LS3MIP,PAMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB
  mip=CMIP
  exp=historical

  test_dir=../../../control-output-files/quicktest
  log_dir=${test_dir}/log-files/; mkdir -p ${log_dir}
  log_file=${log_dir}/log-${mip}-${exp}-${test_version}.txt
  ./genecec-per-mip-experiment.sh ${test_dir}/${mip}-${exp}-${test_version} ${mip_list} ${exp} 1 1 >& ${log_file}

  echo " Compare the results like:"
  echo "  diff -r ${test_dir}/${mip}-${exp}-v01 ${test_dir}/${mip}-${exp}-${test_version}"
  echo "  meld    ${log_file/${test_version}/v01} ${log_file}"

else
  echo
  echo " This scripts has to be run with the correct environment and requires one argument, e.g.:"
  echo "  $0 v01"
  echo
fi
