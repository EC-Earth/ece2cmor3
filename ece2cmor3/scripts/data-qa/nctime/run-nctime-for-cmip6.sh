#!/usr/bin/env bash
# Thomas Reerink
#
# This scripts needs one argument: the directory path with the cmorised data
#
# Run this script without arguments for examples how to call this script.
#

if [ "$#" -eq 1 ]; then

 # Test whether the directory with the cmorised data exists:
 if [ ! -d $1 ]; then 
  echo
  echo ' Error: The directory which was specified for the CMIP6 data: ' $1 ' is not found.'
  echo
  exit
 fi

 # Install nctcck which is part of nctime with pip:
 pip install nctime --upgrade

 # Checking with the nctime command nctcck the conitinuity of the produced time records:
 nctcck -i esgini-dir -l log-nctcck $1

else
 echo
 echo ' This scripts requires one argument: The directory with the cmorised data, e.g.:'
 echo ' ' $0 CMIP6
 echo ' ' $0 /lustre2/projects/model_testing/reerink/cmorised-results/cmor-cmip-historical-for-nsc/cmor-cmip-historical/h003/CMIP6
 echo
fi
