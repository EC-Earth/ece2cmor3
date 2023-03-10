#!/bin/bash
# Thomas Reerink
#
# This script adds / inserts some non-cmor variables and coordinates in order to have a set of
# variables with optimal pressure levels for RCM dynamic forcing.
#
# This scripts requires no arguments.
#
# Run example:
#  ./add-variables-with-pressure-levels-for-rcm-forcing.sh
#

if [ "$#" -eq 0 ]; then

 add_variables_with_pressure_levels_for_rcm_forcing=True


 if [ add_variables_with_pressure_levels_for_rcm_forcing ]; then
  # Add two sets of dynamic RCM forcing variables on dedicated pressure levels #664.

  cd ../resources/cmip6-cmor-tables
  git checkout Tables/CMIP6_coordinate.json
  git checkout Tables/CMIP6_6hrPlevPt.json
  git checkout Tables/CMIP6_6hrPlev.json
  cd -

# Adding the plev23r & plev36 coordinates to the CMOR tables:

  sed -i  '/"plev27": {/i \
        "plev23r": {                                                                            \
            "standard_name": "air_pressure",                                                    \
            "units": "Pa",                                                                      \
            "axis": "Z",                                                                        \
            "long_name": "pressure",                                                            \
            "climatology": "",                                                                  \
            "formula": "",                                                                      \
            "must_have_bounds": "no",                                                           \
            "out_name": "plev",                                                                 \
            "positive": "down",                                                                 \
            "requested": [                                                                      \
                "100000.",                                                                      \
                "95000.",                                                                       \
                "90000.",                                                                       \
                "85000.",                                                                       \
                "80000.",                                                                       \
                "75000.",                                                                       \
                "70000.",                                                                       \
                "65000.",                                                                       \
                "60000.",                                                                       \
                "55000.",                                                                       \
                "50000.",                                                                       \
                "45000.",                                                                       \
                "40000.",                                                                       \
                "35000.",                                                                       \
                "30000.",                                                                       \
                "25000.",                                                                       \
                "20000.",                                                                       \
                "15000.",                                                                       \
                "10000.",                                                                       \
                "7000.",                                                                        \
                "5000.",                                                                        \
                "3000.",                                                                        \
                "1000."                                                                         \
            ],                                                                                  \
            "requested_bounds": "",                                                             \
            "stored_direction": "decreasing",                                                   \
            "tolerance": "",                                                                    \
            "type": "double",                                                                   \
            "valid_max": "",                                                                    \
            "valid_min": "",                                                                    \
            "value": "",                                                                        \
            "z_bounds_factors": "",                                                             \
            "z_factors": "",                                                                    \
            "bounds_values": "",                                                                \
            "generic_level_name": ""                                                            \
        },                                                                                      
  ' ../resources/tables/CMIP6_coordinate.json

  sed -i  '/"plev39": {/i \
        "plev36": {                                                                             \
            "standard_name": "air_pressure",                                                    \
            "units": "Pa",                                                                      \
            "axis": "Z",                                                                        \
            "long_name": "pressure",                                                            \
            "climatology": "",                                                                  \
            "formula": "",                                                                      \
            "must_have_bounds": "no",                                                           \
            "out_name": "plev",                                                                 \
            "positive": "down",                                                                 \
            "requested": [                                                                      \
                "103000.",                                                                      \
                "101500.",                                                                      \
                "100000.",                                                                      \
                "97500.",                                                                       \
                "95000.",                                                                       \
                "92500.",                                                                       \
                "90000.",                                                                       \
                "87500.",                                                                       \
                "85000.",                                                                       \
                "82500.",                                                                       \
                "80000.",                                                                       \
                "77500.",                                                                       \
                "75000.",                                                                       \
                "70000.",                                                                       \
                "65000.",                                                                       \
                "60000.",                                                                       \
                "55000.",                                                                       \
                "50000.",                                                                       \
                "45000.",                                                                       \
                "40000.",                                                                       \
                "35000.",                                                                       \
                "30000.",                                                                       \
                "25000.",                                                                       \
                "22500.",                                                                       \
                "20000.",                                                                       \
                "17500.",                                                                       \
                "15000.",                                                                       \
                "12500.",                                                                       \
                "10000.",                                                                       \
                "7000.",                                                                        \
                "5000.",                                                                        \
                "3000.",                                                                        \
                "1000.",                                                                        \
                 "500.",                                                                        \
                 "300.",                                                                        \
                 "100."                                                                         \
            ],                                                                                  \
            "requested_bounds": "",                                                             \
            "stored_direction": "decreasing",                                                   \
            "tolerance": "",                                                                    \
            "type": "double",                                                                   \
            "valid_max": "",                                                                    \
            "valid_min": "",                                                                    \
            "value": "",                                                                        \
            "z_bounds_factors": "",                                                             \
            "z_factors": "",                                                                    \
            "bounds_values": "",                                                                \
            "generic_level_name": ""                                                            \
        },                                                                                      
  ' ../resources/tables/CMIP6_coordinate.json


# Adding the variables to the 6hrPlevPt table:

  sed -i  '/"ta7h": {/i \
        "ta23r": {                                                                              \
            "frequency": "6hrPt",                                                               \
            "modeling_realm": "atmos",                                                          \
            "standard_name": "air_temperature",                                                 \
            "units": "K",                                                                       \
            "cell_methods": "area: mean time: point",                                           \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Air Temperature",                                                     \
            "comment": "Air Temperature",                                                       \
            "dimensions": "longitude latitude plev23r time1",                                   \
            "out_name": "ta",                                                                   \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      \
        "ta36": {                                                                               \
            "frequency": "6hrPt",                                                               \
            "modeling_realm": "atmos",                                                          \
            "standard_name": "air_temperature",                                                 \
            "units": "K",                                                                       \
            "cell_methods": "area: mean time: point",                                           \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Air Temperature",                                                     \
            "comment": "Air Temperature",                                                       \
            "dimensions": "longitude latitude plev36 time1",                                    \
            "out_name": "ta",                                                                   \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      
  ' ../resources/tables/CMIP6_6hrPlevPt.json

  sed -i  '/"ua7h": {/i \
        "ua23r": {                                                                              \
            "frequency": "6hrPt",                                                               \
            "modeling_realm": "atmos",                                                          \
            "standard_name": "eastward_wind",                                                   \
            "units": "m s-1",                                                                   \
            "cell_methods": "area: mean time: point",                                           \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Eastward Wind",                                                       \
            "comment": "Zonal wind (positive in a eastward direction).",                        \
            "dimensions": "longitude latitude plev23r time1",                                   \
            "out_name": "ua",                                                                   \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      \
        "ua36": {                                                                               \
            "frequency": "6hrPt",                                                               \
            "modeling_realm": "atmos",                                                          \
            "standard_name": "eastward_wind",                                                   \
            "units": "m s-1",                                                                   \
            "cell_methods": "area: mean time: point",                                           \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Eastward Wind",                                                       \
            "comment": "Zonal wind (positive in a eastward direction).",                        \
            "dimensions": "longitude latitude plev36 time1",                                    \
            "out_name": "ua",                                                                   \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      
  ' ../resources/tables/CMIP6_6hrPlevPt.json


  sed -i  '/"va7h": {/i \
        "va23r": {                                                                              \
            "frequency": "6hrPt",                                                               \
            "modeling_realm": "atmos",                                                          \
            "standard_name": "northward_wind",                                                  \
            "units": "m s-1",                                                                   \
            "cell_methods": "area: mean time: point",                                           \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Northward Wind",                                                      \
            "comment": "Meridional wind (positive in a northward direction).",                  \
            "dimensions": "longitude latitude plev23r time1",                                   \
            "out_name": "va",                                                                   \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      \
        "va36": {                                                                               \
            "frequency": "6hrPt",                                                               \
            "modeling_realm": "atmos",                                                          \
            "standard_name": "northward_wind",                                                  \
            "units": "m s-1",                                                                   \
            "cell_methods": "area: mean time: point",                                           \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Northward Wind",                                                      \
            "comment": "Meridional wind (positive in a northward direction).",                  \
            "dimensions": "longitude latitude plev36 time1",                                    \
            "out_name": "va",                                                                   \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      
  ' ../resources/tables/CMIP6_6hrPlevPt.json

  sed -i  '/"hus7h": {/i \
        "hus23r": {                                                                             \
            "frequency": "6hrPt",                                                               \
            "modeling_realm": "atmos",                                                          \
            "standard_name": "specific_humidity",                                               \
            "units": "1",                                                                       \
            "cell_methods": "area: mean time: point",                                           \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Specific Humidity",                                                   \
            "comment": "Specific humidity is the mass fraction of water vapor in (moist) air.", \
            "dimensions": "longitude latitude plev23r time1",                                   \
            "out_name": "hus",                                                                  \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      \
        "hus36": {                                                                              \
            "frequency": "6hrPt",                                                               \
            "modeling_realm": "atmos",                                                          \
            "standard_name": "specific_humidity",                                               \
            "units": "1",                                                                       \
            "cell_methods": "area: mean time: point",                                           \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Specific Humidity",                                                   \
            "comment": "Specific humidity is the mass fraction of water vapor in (moist) air.", \
            "dimensions": "longitude latitude plev36 time1",                                    \
            "out_name": "hus",                                                                  \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      
  ' ../resources/tables/CMIP6_6hrPlevPt.json


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
  ' ../resources/tables/CMIP6_6hrPlevPt.json

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
  ' ../resources/tables/CMIP6_6hrPlevPt.json

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
  ' ../resources/tables/CMIP6_6hrPlev.json

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ../resources/tables/CMIP6_coordinate.json
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ../resources/tables/CMIP6_6hrPlevPt.json
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ../resources/tables/CMIP6_6hrPlev.json

 else
    echo '  '
    echo '  Nothing done, no set of variables and / or experiments has been selected to add to the tables.'
    echo '  '
 fi

else
    echo '  '
    echo '  This scripts requires no argument:'
    echo '  ' $0
    echo '  '
fi
