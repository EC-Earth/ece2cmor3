#!/usr/bin/env bash
# Thomas Reerink
#
# This script creates the output-control-files based on the combined data requests from OptimESM and CMIP7 (core or high) esm-hist for EC-Earth3-ESM-1.
#
# This script requires two arguments: 1. The CMIP7 priority level 2. A version label
#

if [ "$#" -eq 2 ]; then

 priority=$1
 version=$2

 if [ $1 == 'core' ] || [ $1 == 'high' ] || [ $1 == 'medium' ] || [ $1 == 'low' ]; then
  mip=CMIP
  experiment=esm-hist
  ECE3_name=EC-Earth3-ESM-1
  ECE_model=EC-EARTH-ESM-1
  cmip7_dir=cmip7
  archive_dir=archive
  optimesm_dir=cmip7/${archive_dir}/optimesm-${version}
  ece3_cmip7_dir=${archive_dir}/cmip7-${priority}-${experiment}-${ECE3_name}-${version}/

  optimesm_request=../resources/miscellaneous-data-requests/optimesm-request/optimesm-request-${ECE_model}-varlist.json
  combined_request=combined-optimesm-cmip7-${priority}-request-${ECE_model}-varlist.json

  # Produce component varlist request files and move them to an archive:
  ./add-optimesm-variables.sh >& add-optimesm-variables.log    # This adds the 6hrLev zg for the high request below
  cd ${cmip7_dir}
  mkdir -p ${archive_dir}
  ./genecec-cmip7-wrapper.sh ${priority} ${experiment} ${ECE3_name}
  mv -f cmip7-output-control-files/log-files cmip7-output-control-files/${experiment}-${priority}-${ECE3_name}/
  mv -f cmip7-output-control-files/${experiment}-${priority}-${ECE3_name}/ ${ece3_cmip7_dir}/

  # This includes the production of the cmip6Plus varlists (which are not used for this case):
  cd ../
  ./genecec-for-individual-experiments.sh ${optimesm_request} ${mip} ${experiment} ${ECE_model} ${optimesm_dir}/  &> genecec-for-individual-experiments.log
  mv -f genecec-for-individual-experiments.log ${optimesm_dir}/

  # Combine and merge the OptimESM data request files and the CMIP7 request files:
  ./combine-and-merge-json-request-files.py ${optimesm_dir}/${optimesm_request##*/} cmip7/${ece3_cmip7_dir}/component-request-cmip7-${experiment}-${priority}-${ECE3_name}.json ${combined_request}

  # Use the combined optimesm and CMIP7 request to generate the combined output-control-files:
  ./genecec-for-individual-experiments.sh ${combined_request} ${mip} ${experiment} ${ECE_model} cmip7/${archive_dir}/optimesm-${priority}-combined-${version}/ &> genecec-for-individual-experiments-combined-${priority}.log
  mv -f genecec-for-individual-experiments-combined-${priority}.log cmip7/${archive_dir}/optimesm-${priority}-combined-${version}/

  ./add-Oday-zos-for-OptimESM-to-xml.sh cmip7/${archive_dir}/optimesm-${priority}-combined-${version}/file_def_nemo-opa.xml

  ./revert-nested-cmor-table-branch.sh

  # Clean:
  rm -f ${combined_request} add-optimesm-variables.log

  echo
  echo " Finished, the result can be found here:"
  echo "  cmip7/${archive_dir}/optimesm-${priority}-combined-${version}/"
  echo

 else
  echo
  echo " Error: the value of the first argument is wrong."
  echo
  echo " This scripts requires two argument: There are only four options for the first argument:"
  echo "  $0 core   ${version}"
  echo "  $0 high   ${version}"
  echo "  $0 medium ${version}"
  echo "  $0 low    ${version}"
  echo
 fi

else
 echo
 echo " This scripts requires two arguments:"
 echo "  1. The CMIP7 priority level [core, high, medium, low]"
 echo "  2. A version label"
 echo
 echo " For instance:"
 echo "  $0 core v01"
 echo "  $0 high v01"
 echo
fi
