#!/bin/bash
# Thomas Reerink
#
# This script adds some non-cmor variables (which thus do not exit in
# the CMIP6 data request) to the Amon cmor table.
#
# This script requires no arguments.
#
# Run example:
#  ./add-non-cmor-variables.sh
#

if [ "$#" -eq 0 ]; then

 add_the_su_climvar=True

 if [ add_the_su_climvar ]; then
  # See #775     https://github.com/EC-Earth/ece2cmor3/issues/775

  # fall 128243

  # Also add the AerChem related Ice Crystal variables (see https://dev.ec-earth.org/issues/1079)

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_amon=CMIP6_Amon.json


  cd ../resources/
  git checkout ifspar.json
  cd -

  head --lines=-2 ../resources/ifspar.json                   > extended-ifspar.json

  echo '    },                          ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '    {                           ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        "source": "243.128",    ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        "target": "fal"         ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '    }                           ' | sed 's/\s*$//g' >> extended-ifspar.json

  echo ']'                                                  >> extended-ifspar.json

  mv -f extended-ifspar.json ../resources/ifspar.json


  cd ${table_path}
  git checkout ${table_file_amon}

  sed -i  '/"fco2antt": {/i \
        "fal": {                                       \
            "frequency": "mon",                        \
            "modeling_realm": "atmos",                 \
            "standard_name": "forecast_albedo",        \
            "units": "1",                              \
            "cell_methods": "area: time: mean",        \
            "cell_measures": "area: areacella",        \
            "long_name": "Forecast Albedo",            \
            "comment": "Non official cmor variable",   \
            "dimensions": "longitude latitude time",   \
            "out_name": "fal",                         \
            "type": "real",                            \
            "positive": "",                            \
            "valid_min": "",                           \
            "valid_max": "",                           \
            "ok_min_mean_abs": "",                     \
            "ok_max_mean_abs": ""                      \
        },                                             
  ' ${table_file_amon}
#            "cell_methods": "area: time: mean where cloud", 

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_amon}

  cd -

  echo
  echo " Running:"
  echo "  $0"
  echo " has adjusted the file:"
  echo "  ${table_path}/${table_file_amon}"
  echo " which is part of the nested CMOR Table repository. View the diff by running:"
  echo "  cd ${table_path}; git diff; cd -"
  echo " This changes can be reverted by running:"
  echo "  ./revert-nested-cmor-table-branch.sh"
  echo
  echo " In addition the file:"
  echo "  ../resources/ifspar.json"
  echo " has been adjusted. This one can be reverted by:"
  echo "  git checkout ../resources/ifspar.json"
  echo

 else
  echo
  echo " Nothing done, no set of variables and / or experiments has been selected to add to the tables."
  echo
 fi

else
 echo
 echo " This scripts requires no argument:"
 echo "  $0"
 echo
fi
