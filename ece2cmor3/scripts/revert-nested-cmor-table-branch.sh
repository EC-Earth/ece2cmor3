#!/bin/bash
# Thomas Reerink
#
# This script simply reverts all local changes on top of the nested CMOR table repository in ece2cmor3
#
# This scripts requires no arguments.
#
# Run example:
#  ./add-non-cmor-variables.sh
#

if [ "$#" -eq 0 ]; then

 cd ../resources/tables
 # Check whether the directory change was succesful, if not exit the script:
 if [ ! $? -eq 0 ]; then
  echo
  echo " Abort $0 because the correct CMIP6 table directory was not found."
  echo
  exit
 fi

 # Remove unversioned table files if present:
 git clean -f
 
 git checkout *
 cd -

else
 echo '  '
 echo '  This scripts requires no argument:'
 echo '  ' $0
 echo '  '
fi
