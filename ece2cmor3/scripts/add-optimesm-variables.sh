#!/usr/bin/env bash
# Thomas Reerink
#
# This wrapper calls a few scripts that add various non-cmor variables (which thus do not exist in
# the CMIP6 data request) for the OpimESM project.
#
# This script requires no argument.
#

if [ "$#" -eq 0 ]; then

 # The order matters:
 ./revert-nested-cmor-table-branch.sh
 ./add-variables-for-co2box.sh
 ./add-lpjg-cc-diagnostics.sh
 ./add-nemo-variables.sh               no-clean-before
 ./add-htessel-vegetation-variables.sh no-clean-before
 ./add-6hrLev-zg-for-OptimESM.sh       no-clean-before  # Addition for OptimESM CMIP7-FT
 ./add-Oday-zos-for-OptimESM.sh        no-clean-before  # Addition for OptimESM CMIP7-FT (see #863)

 # Addition for OptimESM CMIP7-FT for 3hrPt uas & 3hrPt vas (see #863):
 rsync -a ../resources/tables/CMIP6_3hr.json ../resources/tables/CMIP6_3hrPt.json

else
 echo
 echo " This scripts requires one argument:"
 echo "  $0"
 echo
fi
