#!/usr/bin/env bash
# Thomas Reerink
#
# Run this script without arguments for examples how to call this script.
#
# With this script genecec7 can be run and the output is written to a log file.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.
#
# Note that this script calls genecec-cmip7.py

if [ "$#" -eq 3 ]; then

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

  if ! type "export_dreq_lists_json" > /dev/null; then
   echo; tput setaf 1;
   echo ' The CMIP7 data request tool CLI is not available because of one of the following reasons:'
   echo '  1. it might be not installed'
   echo '  2. it might be not active, check whether the ece2cmor3 environment is activated'
   echo ' Stop'
   tput sgr0; echo
   exit
  fi


  priority_cutoff=$1
  experiment_list=$2
  ececonf_list=$3

  if [ "${experiment_list}" == 'all' ]; then
   experiment_option=''
  else
   # Relplace the comma delimeters with spaces:
   experiment_option='--experiment '${experiment_list//,/ }
  fi

  log_dir=./
  log_file=${log_dir}/genecec-cmip7.log
  sum_file=${log_dir}/summarize.log

  drq_version=v1.2.1
  metadata_filename=metadata-of-requested-cmip7-variables.json

  rm -rf cmip7
  ./genecec-cmip7.py --all_opportunities                          \
                     --variables_metadata ${metadata_filename}    \
                     --ececonfs           ${ececonf_list}         \
                     ${experiment_option}                         \
                     --priority_cutoff    ${priority_cutoff}      \
                     ${drq_version}                               \
                     cmip7-requested-varlist-per-experiment.json  \
   &> ${log_file}

  sed -i -e '/Retaining only these compound names/d' ${log_file}
  grep Skip ${log_file} > ${sum_file}
  echo '' >> ${sum_file}; grep -e 'Created' ${log_file}                   >> ${sum_file}
  echo '' >> ${sum_file}; grep -e 'json'    ${log_file} | grep -v -e INFO >> ${sum_file}

else
  echo
  echo " This scripts requires three arguments:"
  echo "  - Argument 1: The cutoff priority [core, high, medium, low]"
  echo "  - Argument 2: A comma seperated list of CMIP7 experiments [all, historical,piControl]"
  echo "  - Argument 3: A comma seperated list of EC-Earth3 configurations [all, EC-Earth3,EC-Earth3-ESM-1]"
  echo " For instance:"
  echo "  $0 high historical,piControl EC-Earth3-ESM-1"
  echo "  $0 core all all"
  echo
fi
