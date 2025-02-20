#!/bin/bash
# Thomas Reerink
#
# This script adds / inserts some non-cmor variables and coordinates in order to have a set of
# variables with optimal pressure levels for RCM dynamic forcing.
#
# This scripts requires no arguments.
#

if [ "$#" -eq 0 ]; then

 add_variables_with_pressure_levels_for_rcm_forcing=True

 if [ add_variables_with_pressure_levels_for_rcm_forcing ]; then
  # See #664  https://github.com/EC-Earth/ece2cmor3/issues/664

  # Add two sets of dynamic RCM forcing variables on dedicated pressure levels.

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_coordinate=CMIP6_coordinate.json
  table_file_6hrPlevPt=CMIP6_6hrPlevPt.json
  table_file_6hrPlev=CMIP6_6hrPlev.json

  cd ${table_path}
  git checkout ${table_file_coordinate}
  git checkout ${table_file_6hrPlevPt}
  git checkout ${table_file_6hrPlev}



# Add tosa (tos), tsl4sl (tsl) on 6hrPlevPt table & siconca on 6hrPlev table:

  sed -i  '/"ts": {/i \
        "tosa": {                                                                                                                           \
            "frequency": "6hrPt",                                                                                                           \
            "modeling_realm": "ocean",                                                                                                      \
            "standard_name": "sea_surface_temperature",                                                                                     \
            "units": "degC",                                                                                                                \
            "cell_methods": "area: mean where sea time: point",                                                                             \
            "cell_measures": "area: areacella",                                                                                             \
            "long_name": "Sea Surface Temperature",                                                                                         \
            "comment": "Temperature of upper boundary of the liquid ocean, including temperatures below sea-ice and floating ice shelves.", \
            "dimensions": "longitude latitude time1",                                                                                       \
            "out_name": "tos",                                                                                                              \
            "type": "real",                                                                                                                 \
            "positive": "",                                                                                                                 \
            "valid_min": "",                                                                                                                \
            "valid_max": "",                                                                                                                \
            "ok_min_mean_abs": "",                                                                                                          \
            "ok_max_mean_abs": ""                                                                                                           \
        },                                                                                                                                  
  ' ${table_file_6hrPlevPt}

  sed -i  '/"ua": {/i \
        "tsl4sl": {                                                                             \
            "frequency": "6hrPt",                                                               \
            "modeling_realm": "land",                                                           \
            "standard_name": "soil_temperature",                                                \
            "units": "K",                                                                       \
            "cell_methods": "area: mean where land time: point",                                \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Temperature of Soil",                                                 \
            "comment": "Temperature of soil. Reported as missing for grid cells with no land.", \
            "dimensions": "longitude latitude sdepth time1",                                    \
            "out_name": "tsl",                                                                  \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      
  ' ${table_file_6hrPlevPt}

  sed -i  '/"ua": {/i \
        "swvl4sl": {                                                                              \
            "frequency": "6hrPt",                                                                 \
            "modeling_realm": "land",                                                             \
            "standard_name": "soil_water_volume",                                                 \
            "units": "m3 m-3",                                                                    \
            "cell_methods": "area: mean where land time: point",                                  \
            "cell_measures": "area: areacella",                                                   \
            "long_name": "Volumetric soil water layer",                                           \
            "comment": "Water content of soil. Reported as missing for grid cells with no land.", \
            "dimensions": "longitude latitude sdepth time1",                                      \
            "out_name": "swvl4sl",                                                                \
            "type": "real",                                                                       \
            "positive": "",                                                                       \
            "valid_min": "",                                                                      \
            "valid_max": "",                                                                      \
            "ok_min_mean_abs": "",                                                                \
            "ok_max_mean_abs": ""                                                                 \
        },                                                                                        
  ' ${table_file_6hrPlevPt}

  sed -i  '/"tas": {/i \
        "siconca": {                                                    \
            "frequency": "6hr",                                         \
            "modeling_realm": "seaIce",                                 \
            "standard_name": "sea_ice_area_fraction",                   \
            "units": "%",                                               \
            "cell_methods": "area: time: mean",                         \
            "cell_measures": "area: areacella",                         \
            "long_name": "Sea-Ice Area Percentage (Atmospheric Grid)",  \
            "comment": "Percentage of grid cell covered by sea ice",    \
            "dimensions": "longitude latitude time typesi",             \
            "out_name": "siconca",                                      \
            "type": "real",                                             \
            "positive": "",                                             \
            "valid_min": "",                                            \
            "valid_max": "",                                            \
            "ok_min_mean_abs": "",                                      \
            "ok_max_mean_abs": ""                                       \
        },                                                              
  ' ${table_file_6hrPlev}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_coordinate}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_6hrPlevPt}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_6hrPlev}

  cd -

  echo
  echo " Running:"
  echo "  $0"
  echo " has adjusted the file:"
  echo "  ${table_path}/${table_file_coordinate}"
  echo "  ${table_path}/${table_file_6hrPlevPt}"
  echo "  ${table_path}/${table_file_6hrPlev}"
  echo " which is part of the nested CMOR Table repository. View the diff by running:"
  echo "  cd ${table_path}; git diff; cd -"
  echo " This changes can be reverted by running:"
  echo "  ./revert-nested-cmor-table-branch.sh"
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
