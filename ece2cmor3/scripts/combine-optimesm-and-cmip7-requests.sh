#!/usr/bin/env bash
# Thomas Reerink
#
# This script creates the output-control-files based on the combined rdata requests from OptimESM and CMIP7 (core & high) esm-hist
#
# This script requires one argument: a version label
#

if [ "$#" -eq 1 ]; then

 version=$1

 mip=CMIP
 experiment=esm-hist
 
 cmip7_dir=cmip7
 archive_dir=archive
 optimesm_dir=cmip7/${archive_dir}/optimesm-${version}

 # Produce component varlist request files and move them to an archive:
 ./add-optimesm-variables.sh >& add-optimesm-variables.log    # This adds the 6hrLev zg for the high request below
 cd ${cmip7_dir}
 mkdir -p ${archive_dir}
 ./genecec-cmip7-wrapper.sh core ${experiment} EC-Earth3-ESM-1;  mv cmip7-output-control-files ${archive_dir}/cmip7-output-control-files-EC-Earth3-ESM-1-CMIP7-${experiment}-core-${version}/
 ./genecec-cmip7-wrapper.sh high ${experiment} EC-Earth3-ESM-1;  mv cmip7-output-control-files ${archive_dir}/cmip7-output-control-files-EC-Earth3-ESM-1-CMIP7-${experiment}-high-${version}/

 # This includes the production of the cmip6Plus varlists (which are not used for this case):
 cd ../
 ./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/optimesm-request/optimesm-request-EC-EARTH-ESM-1-varlist.json ${mip} ${experiment} EC-EARTH-ESM-1 ${optimesm_dir}/  &> genecec-for-individual-experiments.log
 mv -f genecec-for-individual-experiments.log ${optimesm_dir}/

 # Combine and merge the OptimESM data request files and the CMIP7 request files:
 ./combine-and-merge-json-request-files.py ${optimesm_dir}/optimesm-request-EC-EARTH-ESM-1-varlist.json cmip7/${archive_dir}/cmip7-output-control-files-EC-Earth3-ESM-1-CMIP7-${experiment}-core-${version}/${experiment}-core-EC-Earth3-ESM-1/component-request-cmip7-${experiment}-core-EC-Earth3-ESM-1.json combined-optimesm-cmip7-core-request-EC-EARTH-ESM-1-varlist.json
 ./combine-and-merge-json-request-files.py ${optimesm_dir}/optimesm-request-EC-EARTH-ESM-1-varlist.json cmip7/${archive_dir}/cmip7-output-control-files-EC-Earth3-ESM-1-CMIP7-${experiment}-high-${version}/${experiment}-high-EC-Earth3-ESM-1/component-request-cmip7-${experiment}-high-EC-Earth3-ESM-1.json combined-optimesm-cmip7-high-request-EC-EARTH-ESM-1-varlist.json

 # Use the combined optimesm and CMIP7 (core or high) request to generate the combined output-control-files:
 ./genecec-for-individual-experiments.sh combined-optimesm-cmip7-core-request-EC-EARTH-ESM-1-varlist.json                                       ${mip} ${experiment} EC-EARTH-ESM-1 cmip7/${archive_dir}/optimesm-core-combined-${version}/ &> genecec-for-individual-experiments-combined-core.log
 ./genecec-for-individual-experiments.sh combined-optimesm-cmip7-high-request-EC-EARTH-ESM-1-varlist.json                                       ${mip} ${experiment} EC-EARTH-ESM-1 cmip7/${archive_dir}/optimesm-high-combined-${version}/ &> genecec-for-individual-experiments-combined-high.log
 mv -f genecec-for-individual-experiments-combined-core.log cmip7/${archive_dir}/optimesm-core-combined-${version}/
 mv -f genecec-for-individual-experiments-combined-high.log cmip7/${archive_dir}/optimesm-high-combined-${version}/

 ./revert-nested-cmor-table-branch.sh

 echo
 echo " Finished, the result can be found here:"
 echo "  cmip7/${archive_dir}/optimesm-core-combined-${version}/"
 echo "  cmip7/${archive_dir}/optimesm-high-combined-${version}/"
 echo

else
 echo
 echo " This scripts requires one argument:"
 echo "  $0 v01"
 echo
fi
