#!/usr/bin/env bash

# To activate or deactivate offline mode for the CMIP7 data request software (dreq_content),
# use the command-line utility CMIP7-data-request-api tool with true or false values.

# Managing Offline Mode

# One can see the current CMIP7 data request config setting values (including the offline mode) by:
 CMIP7_data_request_api_config list

# Your local available cached data request versions:
 dr_cache_dir=`CMIP7_data_request_api_config list | grep cache_dir`
 ls -1l ${dr_cache_dir}

# Activate offline mode: Run:
 CMIP7_data_request_api_config offline true
# to block updates and online version checks.

# Deactivate offline mode: Run:
 CMIP7_data_request_api_config offline false
# to restore online connectivity and update checks.

# Reset configurations: Run:
 CMIP7_data_request_api_config reset
# to return all settings back to their default values.

# For other interaction with the CMIP7 data request config file, see:
 CMIP7_data_request_api_config -h

# See source:
#  data_request_api/data_request_api/command_line/config.py
#  https://github.com/CMIP-Data-Request/CMIP7_DReq_Software/blob/main/data_request_api/data_request_api/command_line/config.py
