#!/bin/bash
# Thomas Reerink
#
# This script applies the required changes to run ece2cmor3 & genecec in the DynVarMIP mode or it resets these adjustments.
# It includes activating the pextra mode.
#
# This scripts requires one argument: activate-DynVarMIP-mode or deactivate-DynVarMIP-mode
#
# For examples how to call this script, run it without arguments.
#

if [ "$#" -eq 1 ]; then

 if [ $1 == 'activate-DynVarMIP-mode' ]; then
  cp -f ../resources/list-of-ignored-cmip6-requested-variables-enable-DynVarMIP.xlsx ../resources/list-of-ignored-cmip6-requested-variables.xlsx
  ./switch-on-off-pextra-mode.sh activate-pextra-mode
  git diff ../resources/list-of-ignored-cmip6-requested-variables.xlsx
  echo '  '
 elif [ $1 == 'deactivate-DynVarMIP-mode' ]; then
  git checkout ../resources/list-of-ignored-cmip6-requested-variables.xlsx
  ./switch-on-off-pextra-mode.sh deactivate-pextra-mode
  git diff ../resources/list-of-ignored-cmip6-requested-variables.xlsx
 else
  echo
  echo "  Error: the value of the first argument is wrong."
  echo
  echo " This scripts requires one argument: There are only two options:"
  echo "  $0 activate-DynVarMIP-mode"
  echo "  $0 deactivate-DynVarMIP-mode"
  echo
 fi

else
  echo
  echo " This scripts requires one argument: There are only two options:"
  echo "  $0 activate-DynVarMIP-mode"
  echo "  $0 deactivate-DynVarMIP-mode"
  echo
fi
