#!/bin/bash
# Thomas Reerink
#
# This script adds some non-cmor variables (which thus do not exit in
# the CMIP6 data request) to the Eyr cmor table.
#
# This script requires no arguments.
#
# Run example:
#  ./add-variables-for-co2box.sh
#

if [ "$#" -eq 0 ]; then

 add_variables_for_co2box=True

 if [ add_variables_for_co2box ]; then
  # See #785  https://github.com/EC-Earth/ece2cmor3/issues/785
  # See #792  https://github.com/EC-Earth/ece2cmor3/pull/792

  # co2mass
  # co2s

  table_path=../resources/cmip6-cmor-tables/Tables/
  table_file_day=CMIP6_day.json

  cd ${table_path}
  git checkout ${table_file_day}

  sed -i  '/"hfls": {/i \
        "co2mass": {                                                   \
            "frequency": "day",                                        \
            "modeling_realm": "atmos",                                 \
            "standard_name": "atmosphere_mass_of_carbon_dioxide",      \
            "units": "kg",                                             \
            "cell_methods": "area: time: mean",                        \
            "cell_measures": "",                                       \
            "long_name": "Total Atmospheric Mass of CO2",              \
            "comment": "Total atmospheric mass of Carbon Dioxide",     \
            "dimensions": "time",                                      \
            "out_name": "co2mass",                                     \
            "type": "real",                                            \
            "positive": "",                                            \
            "valid_min": "",                                           \
            "valid_max": "",                                           \
            "ok_min_mean_abs": "",                                     \
            "ok_max_mean_abs": ""                                      \
        },                                                             \
        "co2s": {                                                      \
            "frequency": "day",                                        \
            "modeling_realm": "atmos",                                 \
            "standard_name": "mole_fraction_of_carbon_dioxide_in_air", \
            "units": "1e-06",                                          \
            "cell_methods": "time: mean",                              \
            "cell_measures": "area: areacella",                        \
            "long_name": "Atmosphere CO2",                             \
            "comment": "As co2, but only at the surface",              \
            "dimensions": "longitude latitude time",                   \
            "out_name": "co2s",                                        \
            "type": "real",                                            \
            "positive": "",                                            \
            "valid_min": "",                                           \
            "valid_max": "",                                           \
            "ok_min_mean_abs": "",                                     \
            "ok_max_mean_abs": ""                                      \
        },
  ' ${table_file_day}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_day}

  cd -

  echo
  echo " $0 reports:"
  echo "  The adjusted file is:"
  echo "   ${table_path}/${table_file_day}"
  echo "  Which is part of a nested repository, therefore to view the diff, run:"
  echo "  cd ${table_path}; git diff; cd -"
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
