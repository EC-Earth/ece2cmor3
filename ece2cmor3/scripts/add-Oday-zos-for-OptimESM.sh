#!/bin/bash
# Thomas Reerink
#
# This script adds Oday zos for the OptimESM CMIP7-FT project.
#
# This script requires one argument.
#
# For examples how to call this script, run it without arguments.
#

if [ "$#" -eq 1 ]; then

 do_clean=$1

 add_Oday_zos_for_OptimESM=True

 if [ add_Oday_zos_for_OptimESM ]; then
  # See #875  https://github.com/EC-Earth/ece2cmor3/issues/875

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_Oday=CMIP6_Oday.json

  cd ${table_path}
  if [ ${do_clean} == 'clean-before' ]; then
   rm -f ${table_file_AER6hrPt}
   git checkout ${table_file_Oday}
  fi

  sed -i  '/"tossq": {/i \
        "zos": {                                                                                                                                                 \
            "frequency": "day",                                                                                                                                  \
            "modeling_realm": "ocean",                                                                                                                           \
            "standard_name": "sea_surface_height_above_geoid",                                                                                                   \
            "units": "m",                                                                                                                                        \
            "cell_methods": "area: mean where sea time: mean",                                                                                                   \
            "cell_measures": "area: areacello",                                                                                                                  \
            "long_name": "Sea Surface Height Above Geoid",                                                                                                       \
            "comment": "This is the dynamic sea level, so should have zero global area mean. It should not include inverse barometer depressions from sea ice.", \
            "dimensions": "longitude latitude time",                                                                                                             \
            "out_name": "zos",                                                                                                                                   \
            "type": "real",                                                                                                                                      \
            "positive": "",                                                                                                                                      \
            "valid_min": "",                                                                                                                                     \
            "valid_max": "",                                                                                                                                     \
            "ok_min_mean_abs": "",                                                                                                                               \
            "ok_max_mean_abs": ""                                                                                                                                \
        },
  ' ${table_file_Oday}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_Oday}

  cd -

  echo
  echo " Running:"
  echo "  $0"
  echo " has adjusted the files:"
  echo "  ${table_path}/${table_file_Oday}"
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
