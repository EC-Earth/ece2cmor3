#!/bin/bash
# Thomas Reerink
#
# This scripts requires 1 argument:
#
# ${1} the first argument is the drqlist.json file to convert
#
# Run example:
#  ./convert-varlist.sh varlist-nemo-Omon-msftbarot.json
#
# This script converts a drqlist.json file to a varlist.json file


if [ "$#" -eq 1 ]; then

 file_name=$1

  ../../scripts/drq2varlist.py --drq ${file_name} --varlist ${file_name}-new;
  mv -f ${file_name}-new ${file_name}

else
    echo '  '
    echo '  This scripts requires one argument, e.g.:'
    echo '  ' $0 varlist-nemo-Omon-msftbarot.json
    echo '  '
fi
