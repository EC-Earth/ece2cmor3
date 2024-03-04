#!/usr/bin/env bash
# Thomas Reerink
#
# This wrapper calls a few scripts that add various non-cmor variables (which thus do not exit in
# the CMIP6 data request) for the OpimESM project.
#
# This script requires no argument.
#

if [ "$#" -eq 0 ]; then

 # The order matters:
 ./revert-nested-cmor-table-branch.sh
 ./add-variables-for-co2box.sh
 ./add-lpjg-cc-diagnostics.sh
 ./add-nemo-variables.sh no-clean-before
 ./add-htessel-vegetation-variables.sh no-clean-before

else
 echo
 echo " This scripts requires one argument:"
 echo "  $0"
 echo
fi
