#!/bin/bash
# Thomas Reerink
#
# This script adds 6hrLev zg for the OptimESM CMIP7-FT project.
#
# This script requires one argument.
#
# For examples how to call this script, run it without arguments.
#

if [ "$#" -eq 1 ]; then

 do_clean=$1

 add_6hrLev_zg_for_OptimESM=True

 if [ add_6hrLev_zg_for_OptimESM ]; then
  # See #875  https://github.com/EC-Earth/ece2cmor3/issues/875

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_6hrLev=CMIP6_6hrLev.json

  cd ${table_path}
  if [ ${do_clean} == 'clean-before' ]; then
   rm -f ${table_file_AER6hrPt}
   git checkout ${table_file_6hrLev}
  fi

  sed -i  '/"va": {/i \
        "zg": {                                                                                                                                                                                                                                                                                                                                                                                                         \
            "frequency": "6hrPt",                                                                                                                                                                                                                                                                                                                                                                                       \
            "modeling_realm": "atmos",                                                                                                                                                                                                                                                                                                                                                                                  \
            "standard_name": "geopotential_height",                                                                                                                                                                                                                                                                                                                                                                     \
            "units": "m",                                                                                                                                                                                                                                                                                                                                                                                               \
            "cell_methods": "time: mean",                                                                                                                                                                                                                                                                                                                                                                               \
            "cell_measures": "area: areacella",                                                                                                                                                                                                                                                                                                                                                                         \
            "long_name": "Geopotential Height",                                                                                                                                                                                                                                                                                                                                                                         \
            "comment": "Geopotential is the sum of the specific gravitational potential energy relative to the geoid and the specific centripetal potential energy. Geopotential height is the geopotential divided by the standard acceleration due to gravity. It is numerically similar to the altitude (or geometric height) and not to the quantity with standard name height, which is relative to the surface.", \
            "dimensions": "longitude latitude alevel time1",                                                                                                                                                                                                                                                                                                                                                            \
            "out_name": "zg",                                                                                                                                                                                                                                                                                                                                                                                           \
            "type": "real",                                                                                                                                                                                                                                                                                                                                                                                             \
            "positive": "",                                                                                                                                                                                                                                                                                                                                                                                             \
            "valid_min": "",                                                                                                                                                                                                                                                                                                                                                                                            \
            "valid_max": "",                                                                                                                                                                                                                                                                                                                                                                                            \
            "ok_min_mean_abs": "",                                                                                                                                                                                                                                                                                                                                                                                      \
            "ok_max_mean_abs": ""                                                                                                                                                                                                                                                                                                                                                                                       \
        },
  ' ${table_file_6hrLev}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_6hrLev}

  cd -

  echo
  echo " Running:"
  echo "  $0"
  echo " has adjusted the files:"
  echo "  ${table_path}/${table_file_6hrLev}"
  echo " which is part of the nested CMOR Table repository. View the diff by running:"
  echo "  cd ${table_path}; git diff; cd -"
  echo " This changes can be reverted by running:"
  echo "  ./revert-nested-cmor-table-branch.sh"
  echo

 else
  echo
  echo " This scripts requires one argument: There are only two options:"
  echo "  $0 clean-before"
  echo "  $0 no-clean-before"
  echo
 fi

else
 echo
 echo " This scripts requires one argument: There are only two options:"
 echo "  $0 clean-before"
 echo "  $0 no-clean-before"
 echo
fi
