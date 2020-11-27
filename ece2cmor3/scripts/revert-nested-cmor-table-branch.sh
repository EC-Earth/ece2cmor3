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
 git checkout *
 cd -

else
    echo '  '
    echo '  This scripts requires no argument:'
    echo '  ' $0
    echo '  '
fi
