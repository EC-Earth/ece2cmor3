#!/usr/bin/env bash
# Thomas Reerink
#
# This script switches on/off the CMIP7 data request offline mode. In the offline mode the
# cached CMIP7 data request is used.
#
# This scripts requires one argument: activate-dr-offline-mode or deactivate-dr-offline-mode
#
# For examples how to call this script, run it without arguments.
#

if [ "$#" -eq 1 ]; then

 echo
 # To activate or deactivate offline mode for the CMIP7 data request software (dreq_content),
 # use the command-line utility CMIP7-data-request-api tool with true or false values.
 if [ $1 == 'activate-dr-offline-mode' ]; then
  # Activate offline mode (blocking updates and online version checks):
  CMIP7_data_request_api_config offline true
 elif [ $1 == 'deactivate-dr-offline-mode' ]; then
  # Deactivate offline mode (restoring online connectivity and update checks):
  CMIP7_data_request_api_config offline false
 else
  echo
  echo " Error: the value of the first argument is wrong."
  echo
  echo " This scripts requires one argument: There are only two options:"
  echo "  $0 activate-dr-offline-mode"
  echo "  $0 deactivate-dr-offline-mode"
  echo
 fi

 echo
 # Show the resulting situation:
 echo "The CMIP7 data request offline mode currently is:"
 CMIP7_data_request_api_config list | grep offline
 echo

 echo "Your local available cached CMIP7 data request versions:"
 dr_cache_dir=`CMIP7_data_request_api_config list | grep cache_dir | sed 's/cache_dir: //1'`
 ls -1ld ${dr_cache_dir}/*
 echo


 # One can see the current CMIP7 data request config setting values (including the offline mode) by:
#CMIP7_data_request_api_config list

 # Reset configurations (in order to return all settings back to their default values):
#CMIP7_data_request_api_config reset

 # For other interaction with the CMIP7 data request config file, see:
#CMIP7_data_request_api_config -h

# See source:
#  data_request_api/data_request_api/command_line/config.py
#  https://github.com/CMIP-Data-Request/CMIP7_DReq_Software/blob/main/data_request_api/data_request_api/command_line/config.py

else
  echo
  echo " This scripts requires one argument: There are only two options:"
  echo "  $0 activate-dr-offline-mode"
  echo "  $0 deactivate-dr-offline-mode"
  echo
fi
