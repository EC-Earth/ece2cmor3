#!/bin/bash
# Thomas Reerink
#
# This script omits eight pressure levels from the plev19 coordinate in order to reduce PMIP
# output for unoffical use, i.e. the variables which use this adjusted plev19 coordinate won't
# be longer cmor-compliant and will fail the ESGF node checks.
#
# This scripts requires no arguments.
#
# Run example:
#  ./omit-few-plev19-layers-for-unoffical-PMIP-use.sh
#

if [ "$#" -eq 0 ]; then

 omit_few_plev19_layers_for_unoffical_PMIP_use=True


 if [ omit_few_plev19_layers_for_unoffical_PMIP_use ]; then
  # Add two sets of dynamic RCM forcing variables on dedicated pressure levels #664.

  cd ../resources/cmip6-cmor-tables
  git checkout Tables/CMIP6_coordinate.json
  cd -

 ## Reduce the number of plev19 levels in the CMOR tables:
 #sed -i -e '/plev19/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;d'               ../resources/tables/CMIP6_coordinate.json
 #sed -i -e '/plev19/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;d'         ../resources/tables/CMIP6_coordinate.json
 #sed -i -e '/plev19/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;d'       ../resources/tables/CMIP6_coordinate.json
 #sed -i -e '/plev19/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;d'     ../resources/tables/CMIP6_coordinate.json
 #sed -i -e '/plev19/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;d'   ../resources/tables/CMIP6_coordinate.json
 #sed -i -e '/plev19/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;d'   ../resources/tables/CMIP6_coordinate.json
 #sed -i -e '/plev19/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;d' ../resources/tables/CMIP6_coordinate.json
 #sed -i -e '/plev19/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;d' ../resources/tables/CMIP6_coordinate.json


  # Replace the reduced plev19 coordinate in the CMOR tables:
  sed -i -e '/plev19/,+42d' ../resources/tables/CMIP6_coordinate.json
  sed -i  '/"plev23": {/i \
        "plev19": {\
            "standard_name": "air_pressure", \
            "units": "Pa", \
            "axis": "Z", \
            "long_name": "pressure", \
            "climatology": "", \
            "formula": "", \
            "must_have_bounds": "no", \
            "out_name": "plev", \
            "positive": "down", \
            "requested": [\
                "100000.", \
                "92500.", \
                "85000.", \
                "70000.", \
                "50000.", \
                "40000.", \
                "30000.", \
                "20000.", \
                "10000.", \
                "5000.", \
                "1000."\
            ], \
            "requested_bounds": "", \
            "stored_direction": "decreasing", \
            "tolerance": "", \
            "type": "double", \
            "valid_max": "", \
            "valid_min": "", \
            "value": "", \
            "z_bounds_factors": "", \
            "z_factors": "", \
            "bounds_values": "", \
            "generic_level_name": ""\
        }, 
  ' ../resources/tables/CMIP6_coordinate.json

  echo
  echo ' Attention: you adjusted the ../resources/tables/CMIP6_coordinate.json file by removing eight pressure levels from the plev19 coordinate, with this the plev19 variables are not longer CMOR compliant.'
  echo
  echo ' For reverting these changes, use:'
  echo ' ' ./revert-nested-cmor-table-branch.sh
  echo

 else
    echo
    echo '  Noting done, no set of variables and / or experiments has been selected to add to the tables.'
    echo
 fi

else
    echo
    echo '  This scripts requires no argument:'
    echo '  ' $0
    echo
fi
