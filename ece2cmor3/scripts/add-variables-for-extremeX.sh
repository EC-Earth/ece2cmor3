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
  # See #717 https://github.com/EC-Earth/ece2cmor3/issues/717

  table_path=../resources/cmip6-cmor-tables/Tables/
  table_file_coordinate=CMIP6_coordinate.json
  table_file_6hrPlevPt=CMIP6_6hrPlevPt.json
  table_file_Amon=CMIP6_Amon.json
  table_file_day=CMIP6_day.json
  table_file_Lmon=CMIP6_Lmon.json
  table_file_CV=CMIP6_CV.json

  cd ../resources/
  git checkout ifspar.json
  cd -

  head --lines=-2 ../resources/ifspar.json                   > extended-ifspar.json

 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json
 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json
 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json
 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json
 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json
 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json
 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json

  echo '    },                          ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '    {                           ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        "source": "59.128",     ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        "target": "cape"        ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '    },                          ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '    {                           ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        "source": "60.128",     ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        "target": "pv"          ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '    },                          ' | sed 's/\s*$//g' >> extended-ifspar.json

  echo '    {                           ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        "source": "178.128",    ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        "convert": "cum2inst",  ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        "target": "fsntoa"      ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '    },                          ' | sed 's/\s*$//g' >> extended-ifspar.json

  echo '    {                           ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        "source": "213.128",    ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        "convert": "cum2inst",  ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        "target": [             ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '          "vimd"                ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '        ]                       ' | sed 's/\s*$//g' >> extended-ifspar.json
  echo '    }                           ' | sed 's/\s*$//g' >> extended-ifspar.json

  echo ']'                                                  >> extended-ifspar.json

  sed -i  '/"areacella",/i \
            "zg9",         \
            "zg200",       \
            "zg850",       '                                   extended-ifspar.json


  sed -i  '/"ta",/i \
            "ta3",         \
            "ta9",         '                                   extended-ifspar.json

  sed -i  '/"ua",/i \
            "ua3",         \
            "ua9",         \
            "ua850",       '                                   extended-ifspar.json

  sed -i  '/"va",/i \
            "va3",         \
            "va9",         \
            "va850",       '                                   extended-ifspar.json

  sed -i  '/"hus",/i \
            "hus3",        \
            "hus9",        '                                   extended-ifspar.json

  sed -i  '/"wap",/i \
            "wap850",      '                                   extended-ifspar.json

  # Remove the trailing spaces of the inserted blocks:
  sed -i -e 's/\s*$//g' -e 's/,$/,/g' extended-ifspar.json
  mv -f extended-ifspar.json ../resources/ifspar.json


  cd ${table_path}
  git checkout ${table_file_coordinate}
  git checkout ${table_file_6hrPlevPt}
  git checkout ${table_file_Amon}
  git checkout ${table_file_day}
  git checkout ${table_file_Lmon}
  git checkout ${table_file_CV}

# Adding the plev9 coordinate to the CMOR tables:

  sed -i  '/"plev39": {/i \
        "plev9": {                            \
            "standard_name": "air_pressure",  \
            "units": "Pa",                    \
            "axis": "Z",                      \
            "long_name": "pressure",          \
            "climatology": "",                \
            "formula": "",                    \
            "must_have_bounds": "no",         \
            "out_name": "plev",               \
            "positive": "down",               \
            "requested": [                    \
                "92500.",                     \
                "85000.",                     \
                "70000.",                     \
                "50000.",                     \
                "40000.",                     \
                "30000.",                     \
                "25000.",                     \
                "20000.",                     \
                "15000."                      \
            ],                                \
            "requested_bounds": "",           \
            "stored_direction": "decreasing", \
            "tolerance": "",                  \
            "type": "double",                 \
            "valid_max": "",                  \
            "valid_min": "",                  \
            "value": "",                      \
            "z_bounds_factors": "",           \
            "z_factors": "",                  \
            "bounds_values": "",              \
            "generic_level_name": ""          \
        },                                    
  ' ${table_file_coordinate}



# Additions to CMIP6_6hrPlevPt.json:

  sed -i  '/"hus7h": {/i \
                "hus": {                                                                                \
                    "frequency": "6hrPt",                                                               \
                    "modeling_realm": "atmos",                                                          \
                    "standard_name": "specific_humidity",                                               \
                    "units": "1",                                                                       \
                    "cell_methods": "area: mean time: point",                                           \
                    "cell_measures": "area: areacella",                                                 \
                    "long_name": "Specific Humidity",                                                   \
                    "comment": "Specific humidity is the mass fraction of water vapor in (moist) air.", \
                    "dimensions": "longitude latitude plev3 time1",                                     \
                    "out_name": "hus",                                                                  \
                    "type": "real",                                                                     \
                    "positive": "",                                                                     \
                    "valid_min": "",                                                                    \
                    "valid_max": "",                                                                    \
                    "ok_min_mean_abs": "",                                                              \
                    "ok_max_mean_abs": ""                                                               \
                },                                                                                      \
                "hus3": {                                                                               \
                    "frequency": "6hrPt",                                                               \
                    "modeling_realm": "atmos",                                                          \
                    "standard_name": "specific_humidity",                                               \
                    "units": "1",                                                                       \
                    "cell_methods": "area: mean time: point",                                           \
                    "cell_measures": "area: areacella",                                                 \
                    "long_name": "Specific Humidity",                                                   \
                    "comment": "Specific humidity is the mass fraction of water vapor in (moist) air.", \
                    "dimensions": "longitude latitude plev3 time1",                                     \
                    "out_name": "hus",                                                                  \
                    "type": "real",                                                                     \
                    "positive": "",                                                                     \
                    "valid_min": "",                                                                    \
                    "valid_max": "",                                                                    \
                    "ok_min_mean_abs": "",                                                              \
                    "ok_max_mean_abs": ""                                                               \
                },                                                                                      
  ' ${table_file_6hrPlevPt}

  sed -i  '/"rainmxrat27": {/i \
        "ps": {                                                                                                                                 \
            "frequency": "6hrPt",                                                                                                               \
            "modeling_realm": "atmos",                                                                                                          \
            "standard_name": "surface_air_pressure",                                                                                            \
            "units": "Pa",                                                                                                                      \
            "cell_methods": "area: mean time: point",                                                                                           \
            "cell_measures": "area: areacella",                                                                                                 \
            "long_name": "Surface Air Pressure",                                                                                                \
            "comment": "surface pressure (not mean sea-level pressure), 2-D field to calculate the 3-D pressure field from hybrid coordinates", \
            "dimensions": "longitude latitude time1",                                                                                           \
            "out_name": "ps",                                                                                                                   \
            "type": "real",                                                                                                                     \
            "positive": "",                                                                                                                     \
            "valid_min": "",                                                                                                                    \
            "valid_max": "",                                                                                                                    \
            "ok_min_mean_abs": "",                                                                                                              \
            "ok_max_mean_abs": ""                                                                                                               \
        },                                                                                                                                      \
        "pv": {                                                                                                                                 \
            "frequency": "6hrPt",                                                                                                               \
            "modeling_realm": "atmos",                                                                                                          \
            "standard_name": "potential_vorticity",                                                                                             \
            "units": "K m2 kg-1 s-1",                                                                                                           \
            "cell_methods": "area: mean time: point",                                                                                           \
            "cell_measures": "area: areacella",                                                                                                 \
            "long_name": "Potential Vorticity",                                                                                                 \
            "comment": "Ertel potential vorticity",                                                                                             \
            "dimensions": "longitude latitude plev9 time1",                                                                                     \
            "out_name": "pv",                                                                                                                   \
            "type": "real",                                                                                                                     \
            "positive": "",                                                                                                                     \
            "valid_min": "",                                                                                                                    \
            "valid_max": "",                                                                                                                    \
            "ok_min_mean_abs": "",                                                                                                              \
            "ok_max_mean_abs": ""                                                                                                               \
        },                                                                                                                                      \
        "cape": {                                                                                                                               \
            "frequency": "6hrPt",                                                                                                               \
            "modeling_realm": "atmos",                                                                                                          \
            "standard_name": "cape",                                                                                                            \
            "units": "J kg-1",                                                                                                                  \
            "cell_methods": "area: mean time: point",                                                                                           \
            "cell_measures": "area: areacella",                                                                                                 \
            "long_name": "Convective available potential energy",                                                                               \
            "comment": "Convective available potential energy",                                                                                 \
            "dimensions": "longitude latitude time1",                                                                                           \
            "out_name": "cape",                                                                                                                 \
            "type": "real",                                                                                                                     \
            "positive": "",                                                                                                                     \
            "valid_min": "",                                                                                                                    \
            "valid_max": "",                                                                                                                    \
            "ok_min_mean_abs": "",                                                                                                              \
            "ok_max_mean_abs": ""                                                                                                               \
        },                                                                                                                                      
  ' ${table_file_6hrPlevPt}

  sed -i  '/"ta27": {/i \
        "ta3": {                                            \
            "frequency": "6hrPt",                           \
            "modeling_realm": "atmos",                      \
            "standard_name": "air_temperature",             \
            "units": "K",                                   \
            "cell_methods": "area: mean time: point",       \
            "cell_measures": "area: areacella",             \
            "long_name": "Air Temperature",                 \
            "comment": "Air Temperature",                   \
            "dimensions": "longitude latitude plev3 time1", \
            "out_name": "ta",                               \
            "type": "real",                                 \
            "positive": "",                                 \
            "valid_min": "",                                \
            "valid_max": "",                                \
            "ok_min_mean_abs": "",                          \
            "ok_max_mean_abs": ""                           \
        },                                                  
  ' ${table_file_6hrPlevPt}

  sed -i  '/"ua7h": {/i \
        "ua3": {                                                         \
            "frequency": "6hrPt",                                        \
            "modeling_realm": "atmos",                                   \
            "standard_name": "eastward_wind",                            \
            "units": "m s-1",                                            \
            "cell_methods": "area: mean time: point",                    \
            "cell_measures": "area: areacella",                          \
            "long_name": "Eastward Wind",                                \
            "comment": "Zonal wind (positive in a eastward direction).", \
            "dimensions": "longitude latitude plev3 time1",              \
            "out_name": "ua",                                            \
            "type": "real",                                              \
            "positive": "",                                              \
            "valid_min": "",                                             \
            "valid_max": "",                                             \
            "ok_min_mean_abs": "",                                       \
            "ok_max_mean_abs": ""                                        \
        },                                                               
  ' ${table_file_6hrPlevPt}

  sed -i  '/"va7h": {/i \
        "va3": {                                                               \
            "frequency": "6hrPt",                                              \
            "modeling_realm": "atmos",                                         \
            "standard_name": "northward_wind",                                 \
            "units": "m s-1",                                                  \
            "cell_methods": "area: mean time: point",                          \
            "cell_measures": "area: areacella",                                \
            "long_name": "Northward Wind",                                     \
            "comment": "Meridional wind (positive in a northward direction).", \
            "dimensions": "longitude latitude plev3 time1",                    \
            "out_name": "va",                                                  \
            "type": "real",                                                    \
            "positive": "",                                                    \
            "valid_min": "",                                                   \
            "valid_max": "",                                                   \
            "ok_min_mean_abs": "",                                             \
            "ok_max_mean_abs": ""                                              \
        },                                                                     
  ' ${table_file_6hrPlevPt}



# Additions to CMIP6_Amon.json:

  sed -i  '/"huss": {/i \
        "hus9": {                                                                               \
            "frequency": "mon",                                                                 \
            "modeling_realm": "atmos",                                                          \
            "standard_name": "specific_humidity",                                               \
            "units": "1",                                                                       \
            "cell_methods": "time: mean",                                                       \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Specific Humidity",                                                   \
            "comment": "Specific humidity is the mass fraction of water vapor in (moist) air.", \
            "dimensions": "longitude latitude plev9 time",                                      \
            "out_name": "hus",                                                                  \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      
  ' ${table_file_Amon}

  sed -i  '/"rlut": {/i \
        "fsntoa": {                                                                                 \
            "frequency": "mon",                                                                     \
            "modeling_realm": "atmos",                                                              \
            "standard_name": "toa_net_shortwave_flux",                                              \
            "units": "W m-2",                                                                       \
            "cell_methods": "area: time: mean",                                                     \
            "cell_measures": "area: areacella",                                                     \
            "long_name": "TOA Net Solar Radiation",                                                 \
            "comment": "at the top of the atmosphere (to be compared with satellite measurements)", \
            "dimensions": "longitude latitude time",                                                \
            "out_name": "fsntoa",                                                                   \
            "type": "real",                                                                         \
            "positive": "up",                                                                       \
            "valid_min": "",                                                                        \
            "valid_max": "",                                                                        \
            "ok_min_mean_abs": "",                                                                  \
            "ok_max_mean_abs": ""                                                                   \
        },                                                                                          
  ' ${table_file_Amon}

  sed -i  '/"tas": {/i \
        "ta9": {                                           \
            "frequency": "mon",                            \
            "modeling_realm": "atmos",                     \
            "standard_name": "air_temperature",            \
            "units": "K",                                  \
            "cell_methods": "time: mean",                  \
            "cell_measures": "area: areacella",            \
            "long_name": "Air Temperature",                \
            "comment": "Air Temperature",                  \
            "dimensions": "longitude latitude plev9 time", \
            "out_name": "ta",                              \
            "type": "real",                                \
            "positive": "",                                \
            "valid_min": "",                               \
            "valid_max": "",                               \
            "ok_min_mean_abs": "",                         \
            "ok_max_mean_abs": ""                          \
        },                                                 
  ' ${table_file_Amon}

  sed -i  '/"uas": {/i \
        "ua9": {                                                         \
            "frequency": "mon",                                          \
            "modeling_realm": "atmos",                                   \
            "standard_name": "eastward_wind",                            \
            "units": "m s-1",                                            \
            "cell_methods": "time: mean",                                \
            "cell_measures": "area: areacella",                          \
            "long_name": "Eastward Wind",                                \
            "comment": "Zonal wind (positive in a eastward direction).", \
            "dimensions": "longitude latitude plev9 time",               \
            "out_name": "ua",                                            \
            "type": "real",                                              \
            "positive": "",                                              \
            "valid_min": "",                                             \
            "valid_max": "",                                             \
            "ok_min_mean_abs": "",                                       \
            "ok_max_mean_abs": ""                                        \
        },                                                               
  ' ${table_file_Amon}

  sed -i  '/"vas": {/i \
        "va9": {                                                               \
            "frequency": "mon",                                                \
            "modeling_realm": "atmos",                                         \
            "standard_name": "northward_wind",                                 \
            "units": "m s-1",                                                  \
            "cell_methods": "time: mean",                                      \
            "cell_measures": "area: areacella",                                \
            "long_name": "Northward Wind",                                     \
            "comment": "Meridional wind (positive in a northward direction).", \
            "dimensions": "longitude latitude plev9 time",                     \
            "out_name": "va",                                                  \
            "type": "real",                                                    \
            "positive": "",                                                    \
            "valid_min": "",                                                   \
            "valid_max": "",                                                   \
            "ok_min_mean_abs": "",                                             \
            "ok_max_mean_abs": ""                                              \
        },                                                                     
  ' ${table_file_Amon}

  sed -i  '/"zg": {/i \
        "zg9": {                                                                                                                           \
            "frequency": "mon",                                                                                                            \
            "modeling_realm": "atmos",                                                                                                     \
            "standard_name": "geopotential_height",                                                                                        \
            "units": "m",                                                                                                                  \
            "cell_methods": "time: mean",                                                                                                  \
            "cell_measures": "area: areacella",                                                                                            \
            "long_name": "Geopotential Height",                                                                                            \
            "comment": "Geopotential is the sum of the specific gravitational potential energy relative to the geoid and the specific centripetal potential energy. Geopotential height is the geopotential divided by the standard acceleration due to gravity. It is numerically similar to the altitude (or geometric height) and not to the quantity with standard name height, which is relative to the surface.",\
            "dimensions": "longitude latitude plev9 time",                                                                                 \
            "out_name": "zg",                                                                                                              \
            "type": "real",                                                                                                                \
            "positive": "",                                                                                                                \
            "valid_min": "",                                                                                                               \
            "valid_max": "",                                                                                                               \
            "ok_min_mean_abs": "",                                                                                                         \
            "ok_max_mean_abs": ""                                                                                                          \
        },                                                                                                                                 \
        "zmla": {                                                                                                                          \
            "frequency": "mon",                                                                                                            \
            "modeling_realm": "atmos",                                                                                                     \
            "standard_name": "atmosphere_boundary_layer_thickness",                                                                        \
            "units": "m",                                                                                                                  \
            "cell_methods": "area: time: mean",                                                                                            \
            "cell_measures": "area: areacella",                                                                                            \
            "long_name": "Height of Boundary Layer",                                                                                       \
            "comment": "The atmosphere boundary layer thickness is the \x27depth\x27 or \x27height\x27 of the (atmosphere) planetary boundary layer.", \
            "dimensions": "longitude latitude time",                                                                                       \
            "out_name": "zmla",                                                                                                            \
            "type": "real",                                                                                                                \
            "positive": "",                                                                                                                \
            "valid_min": "",                                                                                                               \
            "valid_max": "",                                                                                                               \
            "ok_min_mean_abs": "",                                                                                                         \
            "ok_max_mean_abs": ""                                                                                                          \
        },                                                                                                                                 
  ' ${table_file_Amon}



# Additions to CMIP6_day.json:

  sed -i  '/"hfls": {/i \
       "evspsbl": {                                                                             \
            "frequency": "day",                                                                 \
            "modeling_realm": "atmos",                                                          \
            "standard_name": "water_evapotranspiration_flux",                                   \
            "units": "kg m-2 s-1",                                                              \
            "cell_methods": "area: time: mean",                                                 \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Evaporation Including Sublimation and Transpiration",                 \
            "comment": "Evaporation at surface (also known as evapotranspiration): flux of water into the atmosphere due to conversion of both liquid and solid phases to vapor (from underlying surface and vegetation)",\
            "dimensions": "longitude latitude time",                                            \
            "out_name": "evspsbl",                                                              \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      \
       "vimd": {                                                                                \
            "frequency": "day",                                                                 \
            "modeling_realm": "atmos",                                                          \
            "standard_name": "vertically_integrated_moisture_flux_divergence",                  \
            "units": "kg m-2 s-1",                                                              \
            "cell_methods": "area: time: mean",                                                 \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Vertically integrated moisture flux divergence",                      \
            "comment": "The vertical integral of the moisture flux is the horizontal rate of flow of moisture (water vapour, cloud liquid and cloud ice), per metre across the flow, for a column of air extending from the surface of the Earth to the top of the atmosphere. Its horizontal divergence is the rate of moisture spreading outward from a point, per square metre.",\
            "dimensions": "longitude latitude time",                                            \
            "out_name": "vimd",                                                                 \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      
  ' ${table_file_day}

  sed -i  '/"pr": {/i \
        "mrsol": {                                                                                                                                             \
            "frequency": "day",                                                                                                                                \
            "modeling_realm": "land",                                                                                                                          \
            "standard_name": "mass_content_of_water_in_soil_layer",                                                                                            \
            "units": "kg m-2",                                                                                                                                 \
            "cell_methods": "area: mean time: point",                                                                                                          \
            "cell_measures": "area: areacella",                                                                                                                \
            "long_name": "Total Water Content of Soil Layer",                                                                                                  \
            "comment": "in each soil layer, the mass of water in all phases, including ice.  Reported as \x27missing\x27 for grid cells occupied entirely by \x27sea\x27", \
            "dimensions": "longitude latitude sdepth time1",                                                                                                   \
            "out_name": "mrsol",                                                                                                                               \
            "type": "real",                                                                                                                                    \
            "positive": "",                                                                                                                                    \
            "valid_min": "",                                                                                                                                   \
            "valid_max": "",                                                                                                                                   \
            "ok_min_mean_abs": "",                                                                                                                             \
            "ok_max_mean_abs": ""                                                                                                                              \
        },                                                                                                                                                     
  ' ${table_file_day}

  sed -i  '/"rsds": {/i \
         "fsntoa": {                                                                                \
            "frequency": "day",                                                                     \
            "modeling_realm": "atmos",                                                              \
            "standard_name": "toa_net_shortwave_flux",                                              \
            "units": "W m-2",                                                                       \
            "cell_methods": "area: time: mean",                                                     \
            "cell_measures": "area: areacella",                                                     \
            "long_name": "TOA Net Solar Radiation",                                                 \
            "comment": "at the top of the atmosphere (to be compared with satellite measurements)", \
            "dimensions": "longitude latitude time",                                                \
            "out_name": "fsntoa",                                                                   \
            "type": "real",                                                                         \
            "positive": "up",                                                                       \
            "valid_min": "",                                                                        \
            "valid_max": "",                                                                        \
            "ok_min_mean_abs": "",                                                                  \
            "ok_max_mean_abs": ""                                                                   \
        },                                                                                          
  ' ${table_file_day}

  sed -i  '/"tas": {/i \
        "ta9": {                                           \
            "frequency": "day",                            \
            "modeling_realm": "atmos",                     \
            "standard_name": "air_temperature",            \
            "units": "K",                                  \
            "cell_methods": "time: mean",                  \
            "cell_measures": "area: areacella",            \
            "long_name": "Air Temperature",                \
            "comment": "Air Temperature",                  \
            "dimensions": "longitude latitude plev9 time", \
            "out_name": "ta",                              \
            "type": "real",                                \
            "positive": "",                                \
            "valid_min": "",                               \
            "valid_max": "",                               \
            "ok_min_mean_abs": "",                         \
            "ok_max_mean_abs": ""                          \
        },                                                 
  ' ${table_file_day}

  sed -i  '/"uas": {/i \
        "ua9": {                                                         \
            "frequency": "day",                                          \
            "modeling_realm": "atmos",                                   \
            "standard_name": "eastward_wind",                            \
            "units": "m s-1",                                            \
            "cell_methods": "time: mean",                                \
            "cell_measures": "area: areacella",                          \
            "long_name": "Eastward Wind",                                \
            "comment": "Zonal wind (positive in a eastward direction).", \
            "dimensions": "longitude latitude plev9 time",               \
            "out_name": "ua",                                            \
            "type": "real",                                              \
            "positive": "",                                              \
            "valid_min": "",                                             \
            "valid_max": "",                                             \
            "ok_min_mean_abs": "",                                       \
            "ok_max_mean_abs": ""                                        \
        },                                                               
  ' ${table_file_day}

  sed -i  '/"zg": {/i \
        "wap850": {                                                                             \
            "frequency": "day",                                                                 \
            "modeling_realm": "atmos",                                                          \
            "standard_name": "lagrangian_tendency_of_air_pressure",                             \
            "units": "Pa s-1",                                                                  \
            "cell_methods": "time: mean",                                                       \
            "cell_measures": "area: areacella",                                                 \
            "long_name": "Omega (=dp/dt)",                                                      \
            "comment": "Omega (vertical velocity in pressure coordinates, positive downwards)", \
            "dimensions": "longitude latitude p850 time",                                       \
            "out_name": "wap",                                                                  \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },                                                                                      
  ' ${table_file_day}

  sed -i  '/"zg": {/i \
        "zg200": {                                                                                                                                     \
            "frequency": "day",                                                                                                                        \
            "modeling_realm": "atmos",                                                                                                                 \
            "standard_name": "geopotential_height",                                                                                                    \
            "units": "m",                                                                                                                              \
            "cell_methods": "time: mean",                                                                                                              \
            "cell_measures": "area: areacella",                                                                                                        \
            "long_name": "Geopotential Height",                                                                                                        \
            "comment": "Geopotential is the sum of the specific gravitational potential energy relative to the geoid and the specific centripetal potential energy. Geopotential height is the geopotential divided by the standard acceleration due to gravity. It is numerically similar to the altitude (or geometric height) and not to the quantity with standard name height, which is relative to the surface.",\
            "dimensions": "longitude latitude p200 time",                                                                                              \
            "out_name": "zg200",                                                                                                                       \
            "type": "real",                                                                                                                            \
            "positive": "",                                                                                                                            \
            "valid_min": "",                                                                                                                           \
            "valid_max": "",                                                                                                                           \
            "ok_min_mean_abs": "",                                                                                                                     \
            "ok_max_mean_abs": ""                                                                                                                      \
        },                                                                                                                                             \
        "zg500": {                                                                                                                                     \
            "frequency": "day",                                                                                                                        \
            "modeling_realm": "atmos",                                                                                                                 \
            "standard_name": "geopotential_height",                                                                                                    \
            "units": "m",                                                                                                                              \
            "cell_methods": "time: mean",                                                                                                              \
            "cell_measures": "area: areacella",                                                                                                        \
            "long_name": "Geopotential Height",                                                                                                        \
            "comment": "Geopotential is the sum of the specific gravitational potential energy relative to the geoid and the specific centripetal potential energy. Geopotential height is the geopotential divided by the standard acceleration due to gravity. It is numerically similar to the altitude (or geometric height) and not to the quantity with standard name height, which is relative to the surface.",\
            "dimensions": "longitude latitude p500 time",                                                                                              \
            "out_name": "zg500",                                                                                                                       \
            "type": "real",                                                                                                                            \
            "positive": "",                                                                                                                            \
            "valid_min": "",                                                                                                                           \
            "valid_max": "",                                                                                                                           \
            "ok_min_mean_abs": "",                                                                                                                     \
            "ok_max_mean_abs": ""                                                                                                                      \
        },                                                                                                                                             \
        "zg850": {                                                                                                                                     \
            "frequency": "day",                                                                                                                        \
            "modeling_realm": "atmos",                                                                                                                 \
            "standard_name": "geopotential_height",                                                                                                    \
            "units": "m",                                                                                                                              \
            "cell_methods": "time: mean",                                                                                                              \
            "cell_measures": "area: areacella",                                                                                                        \
            "long_name": "Geopotential Height",                                                                                                        \
            "comment": "Geopotential is the sum of the specific gravitational potential energy relative to the geoid and the specific centripetal potential energy. Geopotential height is the geopotential divided by the standard acceleration due to gravity. It is numerically similar to the altitude (or geometric height) and not to the quantity with standard name height, which is relative to the surface.",\
            "dimensions": "longitude latitude p850 time",                                                                                              \
            "out_name": "zg850",                                                                                                                       \
            "type": "real",                                                                                                                            \
            "positive": "",                                                                                                                            \
            "valid_min": "",                                                                                                                           \
            "valid_max": "",                                                                                                                           \
            "ok_min_mean_abs": "",                                                                                                                     \
            "ok_max_mean_abs": ""                                                                                                                      \
        },                                                                                                                                             \
       "mrros": {                                                                                                                                      \
            "frequency": "day",                                                                                                                        \
            "modeling_realm": "land",                                                                                                                  \
            "standard_name": "surface_runoff_flux",                                                                                                    \
            "units": "kg m-2 s-1",                                                                                                                     \
            "cell_methods": "area: mean where land time: mean",                                                                                        \
            "cell_measures": "area: areacella",                                                                                                        \
            "long_name": "Surface Runoff",                                                                                                             \
            "comment": "The total surface run off leaving the land portion of the grid cell (excluding drainage through the base of the soil model).", \
            "dimensions": "longitude latitude time",                                                                                                   \
            "out_name": "mrros",                                                                                                                       \
            "type": "real",                                                                                                                            \
            "positive": "",                                                                                                                            \
            "valid_min": "",                                                                                                                           \
            "valid_max": "",                                                                                                                           \
            "ok_min_mean_abs": "",                                                                                                                     \
            "ok_max_mean_abs": ""                                                                                                                      \
        },                                                                                                                                             \
        "mrfso": {                                                                                                                                     \
            "frequency": "day",                                                                                                                        \
            "modeling_realm": "land landIce",                                                                                                          \
            "standard_name": "soil_frozen_water_content",                                                                                              \
            "units": "kg m-2",                                                                                                                         \
            "cell_methods": "area: mean where land time: mean",                                                                                        \
            "cell_measures": "area: areacella",                                                                                                        \
            "long_name": "Soil Frozen Water Content",                                                                                                  \
            "comment": "The mass per unit area (summed over all model layers) of frozen water.",                                                       \
            "dimensions": "longitude latitude time",                                                                                                   \
            "out_name": "mrfso",                                                                                                                       \
            "type": "real",                                                                                                                            \
            "positive": "",                                                                                                                            \
            "valid_min": "",                                                                                                                           \
            "valid_max": "",                                                                                                                           \
            "ok_min_mean_abs": "",                                                                                                                     \
            "ok_max_mean_abs": ""                                                                                                                      \
        },                                                                                                                                             \
        "tsl": {                                                                                                                                       \
            "frequency": "day",                                                                                                                        \
            "modeling_realm": "land",                                                                                                                  \
            "standard_name": "soil_temperature",                                                                                                       \
            "units": "K",                                                                                                                              \
            "cell_methods": "area: mean where land time: mean",                                                                                        \
            "cell_measures": "area: areacella",                                                                                                        \
            "long_name": "Temperature of Soil",                                                                                                        \
            "comment": "Temperature of soil. Reported as missing for grid cells with no land.",                                                        \
            "dimensions": "longitude latitude sdepth time",                                                                                            \
            "out_name": "tsl",                                                                                                                         \
            "type": "real",                                                                                                                            \
            "positive": "",                                                                                                                            \
            "valid_min": "",                                                                                                                           \
            "valid_max": "",                                                                                                                           \
            "ok_min_mean_abs": "",                                                                                                                     \
            "ok_max_mean_abs": ""                                                                                                                      \
        },                                                                                                                                             
  ' ${table_file_day}



# Additions to CMIP6_Lmon.json:

  sed -i  '/"nbp": {/i \
        "mrsol": {                                                                                                                                             \
            "frequency": "mon",                                                                                                                                \
            "modeling_realm": "land",                                                                                                                          \
            "standard_name": "mass_content_of_water_in_soil_layer",                                                                                            \
            "units": "kg m-2",                                                                                                                                 \
            "cell_methods": "area: mean time: point",                                                                                                          \
            "cell_measures": "area: areacella",                                                                                                                \
            "long_name": "Total Water Content of Soil Layer",                                                                                                  \
            "comment": "in each soil layer, the mass of water in all phases, including ice.  Reported as \x27missing\x27 for grid cells occupied entirely by \x27sea\x27", \
            "dimensions": "longitude latitude sdepth time1",                                                                                                   \
            "out_name": "mrsol",                                                                                                                               \
            "type": "real",                                                                                                                                    \
            "positive": "",                                                                                                                                    \
            "valid_min": "",                                                                                                                                   \
            "valid_max": "",                                                                                                                                   \
            "ok_min_mean_abs": "",                                                                                                                             \
            "ok_max_mean_abs": ""                                                                                                                              \
        },                                                                                                                                                     
  ' ${table_file_Lmon}

  sed -i  '/"tsl": {/i \
        "tslsi": {                                                               \
            "frequency": "mon",                                                  \
            "modeling_realm": "land",                                            \
            "standard_name": "surface_temperature",                              \
            "units": "K",                                                        \
            "cell_methods": "area: time: mean (comment: over land and sea ice)", \
            "cell_measures": "area: areacella",                                  \
            "long_name": "Surface Temperature Where Land or Sea Ice",            \
            "comment": "Surface temperature of all surfaces except open ocean.", \
            "dimensions": "longitude latitude time",                             \
            "out_name": "tslsi",                                                 \
            "type": "real",                                                      \
            "positive": "",                                                      \
            "valid_min": "",                                                     \
            "valid_max": "",                                                     \
            "ok_min_mean_abs": "",                                               \
            "ok_max_mean_abs": ""                                                \
        },                                                                       
  ' ${table_file_Lmon}



# Additions to CMIP6_CV.json:

  sed -i  '/"s1910":"initialized near end of year 1910",/i \
            "afsf":"initialized in 1979",                  \
            "afsc":"initialized in 1979",                  \
            "AFSI":"initialized in 1979",                  \
            "C001":"initialized in 1979",                  \
            "C002":"initialized in 1979",                  \
            "C003":"initialized in 1979",                  \
            "C004":"initialized in 1979",                  \
            "C005":"initialized in 1979",                  \
            "c001":"initialized in 1979",                  \
            "c002":"initialized in 1979",                  \
            "c003":"initialized in 1979",                  \
            "c004":"initialized in 1979",                  \
            "c005":"initialized in 1979",                  \
            "C006":"initialized in 1979",                  \
            "C007":"initialized in 1979",                  \
            "C008":"initialized in 1979",                  \
            "C009":"initialized in 1979",                  \
            "C010":"initialized in 1979",                  \
            "E001":"initialized in 2009",                  \
            "E002":"initialized in 2009",                  \
            "E003":"initialized in 2009",                  \
            "E004":"initialized in 2009",                  \
            "E005":"initialized in 2009",                  \
            "E006":"initialized in 2009",                  \
            "E007":"initialized in 2009",                  \
            "E008":"initialized in 2009",                  \
            "E009":"initialized in 2009",                  \
            "E010":"initialized in 2009",                  \
            "E011":"initialized in 2009",                  \
            "E012":"initialized in 2009",                  \
            "E013":"initialized in 2009",                  \
            "E014":"initialized in 2009",                  \
            "E015":"initialized in 2009",                  \
            "E016":"initialized in 2009",                  \
            "E017":"initialized in 2009",                  \
            "E018":"initialized in 2009",                  \
            "E019":"initialized in 2009",                  \
            "E020":"initialized in 2009",                  \
            "E021":"initialized in 2009",                  \
            "E022":"initialized in 2009",                  \
            "E023":"initialized in 2009",                  \
            "E024":"initialized in 2009",                  \
            "E025":"initialized in 2009",                  \
            "E026":"initialized in 2009",                  \
            "E027":"initialized in 2009",                  \
            "E028":"initialized in 2009",                  \
            "E029":"initialized in 2009",                  \
            "E030":"initialized in 2009",                  \
            "E031":"initialized in 2009",                  \
            "E032":"initialized in 2009",                  \
            "E033":"initialized in 2009",                  \
            "E034":"initialized in 2009",                  \
            "E035":"initialized in 2009",                  \
            "E036":"initialized in 2009",                  \
            "E037":"initialized in 2009",                  \
            "E038":"initialized in 2009",                  \
            "E039":"initialized in 2009",                  \
            "E040":"initialized in 2009",                  \
            "E041":"initialized in 2009",                  \
            "E042":"initialized in 2009",                  \
            "E043":"initialized in 2009",                  \
            "E044":"initialized in 2009",                  \
            "E045":"initialized in 2009",                  \
            "E046":"initialized in 2009",                  \
            "E047":"initialized in 2009",                  \
            "E048":"initialized in 2009",                  \
            "E049":"initialized in 2009",                  \
            "E050":"initialized in 2009",                  \
            "E051":"initialized in 2009",                  \
            "E052":"initialized in 2009",                  \
            "E053":"initialized in 2009",                  \
            "E054":"initialized in 2009",                  \
            "E055":"initialized in 2009",                  \
            "E056":"initialized in 2009",                  \
            "E057":"initialized in 2009",                  \
            "E058":"initialized in 2009",                  \
            "E059":"initialized in 2009",                  \
            "E060":"initialized in 2009",                  \
            "E061":"initialized in 2009",                  \
            "E062":"initialized in 2009",                  \
            "E063":"initialized in 2009",                  \
            "E064":"initialized in 2009",                  \
            "E065":"initialized in 2009",                  \
            "E066":"initialized in 2009",                  \
            "E067":"initialized in 2009",                  \
            "E068":"initialized in 2009",                  \
            "E069":"initialized in 2009",                  \
            "E070":"initialized in 2009",                  \
            "E071":"initialized in 2009",                  \
            "E072":"initialized in 2009",                  \
            "E073":"initialized in 2009",                  \
            "E074":"initialized in 2009",                  \
            "E075":"initialized in 2009",                  \
            "E076":"initialized in 2009",                  \
            "E077":"initialized in 2009",                  \
            "E078":"initialized in 2009",                  \
            "E079":"initialized in 2009",                  \
            "E080":"initialized in 2009",                  \
            "E081":"initialized in 2009",                  \
            "E082":"initialized in 2009",                  \
            "E083":"initialized in 2009",                  \
            "E084":"initialized in 2009",                  \
            "E085":"initialized in 2009",                  \
            "E086":"initialized in 2009",                  \
            "E087":"initialized in 2009",                  \
            "E088":"initialized in 2009",                  \
            "E089":"initialized in 2009",                  \
            "E090":"initialized in 2009",                  \
            "E091":"initialized in 2009",                  \
            "E092":"initialized in 2009",                  \
            "E093":"initialized in 2009",                  \
            "E094":"initialized in 2009",                  \
            "E095":"initialized in 2009",                  \
            "E096":"initialized in 2009",                  \
            "E097":"initialized in 2009",                  \
            "E098":"initialized in 2009",                  \
            "E099":"initialized in 2009",                  \
            "E100":"initialized in 2009",                  \
            "e001":"initialized in 2009",                  \
            "e002":"initialized in 2009",                  \
            "e003":"initialized in 2009",                  \
            "e004":"initialized in 2009",                  \
            "e005":"initialized in 2009",                  \
            "e006":"initialized in 2009",                  \
            "e007":"initialized in 2009",                  \
            "e008":"initialized in 2009",                  \
            "e009":"initialized in 2009",                  \
            "e010":"initialized in 2009",                  \
            "e011":"initialized in 2009",                  \
            "e012":"initialized in 2009",                  \
            "e013":"initialized in 2009",                  \
            "e014":"initialized in 2009",                  \
            "e015":"initialized in 2009",                  \
            "e016":"initialized in 2009",                  \
            "e017":"initialized in 2009",                  \
            "e018":"initialized in 2009",                  \
            "e019":"initialized in 2009",                  \
            "e020":"initialized in 2009",                  \
            "e021":"initialized in 2009",                  \
            "e022":"initialized in 2009",                  \
            "e023":"initialized in 2009",                  \
            "e024":"initialized in 2009",                  \
            "e025":"initialized in 2009",                  \
            "e026":"initialized in 2009",                  \
            "e027":"initialized in 2009",                  \
            "e028":"initialized in 2009",                  \
            "e029":"initialized in 2009",                  \
            "e030":"initialized in 2009",                  \
            "e031":"initialized in 2009",                  \
            "e032":"initialized in 2009",                  \
            "e033":"initialized in 2009",                  \
            "e034":"initialized in 2009",                  \
            "e035":"initialized in 2009",                  \
            "e036":"initialized in 2009",                  \
            "e037":"initialized in 2009",                  \
            "e038":"initialized in 2009",                  \
            "e039":"initialized in 2009",                  \
            "e040":"initialized in 2009",                  \
            "e041":"initialized in 2009",                  \
            "e042":"initialized in 2009",                  \
            "e043":"initialized in 2009",                  \
            "e044":"initialized in 2009",                  \
            "e045":"initialized in 2009",                  \
            "e046":"initialized in 2009",                  \
            "e047":"initialized in 2009",                  \
            "e048":"initialized in 2009",                  \
            "e049":"initialized in 2009",                  \
            "e050":"initialized in 2009",                  \
            "e051":"initialized in 2009",                  \
            "e052":"initialized in 2009",                  \
            "e053":"initialized in 2009",                  \
            "e054":"initialized in 2009",                  \
            "e055":"initialized in 2009",                  \
            "e056":"initialized in 2009",                  \
            "e057":"initialized in 2009",                  \
            "e058":"initialized in 2009",                  \
            "e059":"initialized in 2009",                  \
            "e060":"initialized in 2009",                  \
            "e061":"initialized in 2009",                  \
            "e062":"initialized in 2009",                  \
            "e063":"initialized in 2009",                  \
            "e064":"initialized in 2009",                  \
            "e065":"initialized in 2009",                  \
            "e066":"initialized in 2009",                  \
            "e067":"initialized in 2009",                  \
            "e068":"initialized in 2009",                  \
            "e069":"initialized in 2009",                  \
            "e070":"initialized in 2009",                  \
            "e071":"initialized in 2009",                  \
            "e072":"initialized in 2009",                  \
            "e073":"initialized in 2009",                  \
            "e074":"initialized in 2009",                  \
            "e075":"initialized in 2009",                  \
            "e076":"initialized in 2009",                  \
            "e077":"initialized in 2009",                  \
            "e078":"initialized in 2009",                  \
            "e079":"initialized in 2009",                  \
            "e080":"initialized in 2009",                  \
            "e081":"initialized in 2009",                  \
            "e082":"initialized in 2009",                  \
            "e083":"initialized in 2009",                  \
            "e084":"initialized in 2009",                  \
            "e085":"initialized in 2009",                  \
            "e086":"initialized in 2009",                  \
            "e087":"initialized in 2009",                  \
            "e088":"initialized in 2009",                  \
            "e089":"initialized in 2009",                  \
            "e090":"initialized in 2009",                  \
            "e091":"initialized in 2009",                  \
            "e092":"initialized in 2009",                  \
            "e093":"initialized in 2009",                  \
            "e094":"initialized in 2009",                  \
            "e095":"initialized in 2009",                  \
            "e096":"initialized in 2009",                  \
            "e097":"initialized in 2009",                  \
            "e098":"initialized in 2009",                  \
            "e099":"initialized in 2009",                  \
            "e100":"initialized in 2009",                  \
            "AISC":"initialized in 1979",                  \
            "S001":"initialized in 2009",                  \
            "S002":"initialized in 2009",                  \
            "S003":"initialized in 2009",                  \
            "S004":"initialized in 2009",                  \
            "S005":"initialized in 2009",                  \
            "S006":"initialized in 2009",                  \
            "S007":"initialized in 2009",                  \
            "S008":"initialized in 2009",                  \
            "S009":"initialized in 2009",                  \
            "S010":"initialized in 2009",                  \
            "S011":"initialized in 2009",                  \
            "S012":"initialized in 2009",                  \
            "S013":"initialized in 2009",                  \
            "S014":"initialized in 2009",                  \
            "S015":"initialized in 2009",                  \
            "S016":"initialized in 2009",                  \
            "S017":"initialized in 2009",                  \
            "S018":"initialized in 2009",                  \
            "S019":"initialized in 2009",                  \
            "S020":"initialized in 2009",                  \
            "S021":"initialized in 2009",                  \
            "S022":"initialized in 2009",                  \
            "S023":"initialized in 2009",                  \
            "S024":"initialized in 2009",                  \
            "S025":"initialized in 2009",                  \
            "S026":"initialized in 2009",                  \
            "S027":"initialized in 2009",                  \
            "S028":"initialized in 2009",                  \
            "S029":"initialized in 2009",                  \
            "S030":"initialized in 2009",                  \
            "S031":"initialized in 2009",                  \
            "S032":"initialized in 2009",                  \
            "S033":"initialized in 2009",                  \
            "S034":"initialized in 2009",                  \
            "S035":"initialized in 2009",                  \
            "S036":"initialized in 2009",                  \
            "S037":"initialized in 2009",                  \
            "S038":"initialized in 2009",                  \
            "S039":"initialized in 2009",                  \
            "S040":"initialized in 2009",                  \
            "S041":"initialized in 2009",                  \
            "S042":"initialized in 2009",                  \
            "S043":"initialized in 2009",                  \
            "S044":"initialized in 2009",                  \
            "S045":"initialized in 2009",                  \
            "S046":"initialized in 2009",                  \
            "S047":"initialized in 2009",                  \
            "S048":"initialized in 2009",                  \
            "S049":"initialized in 2009",                  \
            "S050":"initialized in 2009",                  \
            "S051":"initialized in 2009",                  \
            "S052":"initialized in 2009",                  \
            "S053":"initialized in 2009",                  \
            "S054":"initialized in 2009",                  \
            "S055":"initialized in 2009",                  \
            "S056":"initialized in 2009",                  \
            "S057":"initialized in 2009",                  \
            "S058":"initialized in 2009",                  \
            "S059":"initialized in 2009",                  \
            "S060":"initialized in 2009",                  \
            "S061":"initialized in 2009",                  \
            "S062":"initialized in 2009",                  \
            "S063":"initialized in 2009",                  \
            "S064":"initialized in 2009",                  \
            "S065":"initialized in 2009",                  \
            "S066":"initialized in 2009",                  \
            "S067":"initialized in 2009",                  \
            "S068":"initialized in 2009",                  \
            "S069":"initialized in 2009",                  \
            "S070":"initialized in 2009",                  \
            "S071":"initialized in 2009",                  \
            "S072":"initialized in 2009",                  \
            "S073":"initialized in 2009",                  \
            "S074":"initialized in 2009",                  \
            "S075":"initialized in 2009",                  \
            "S076":"initialized in 2009",                  \
            "S077":"initialized in 2009",                  \
            "S078":"initialized in 2009",                  \
            "S079":"initialized in 2009",                  \
            "S080":"initialized in 2009",                  \
            "S081":"initialized in 2009",                  \
            "S082":"initialized in 2009",                  \
            "S083":"initialized in 2009",                  \
            "S084":"initialized in 2009",                  \
            "S085":"initialized in 2009",                  \
            "S086":"initialized in 2009",                  \
            "S087":"initialized in 2009",                  \
            "S088":"initialized in 2009",                  \
            "S089":"initialized in 2009",                  \
            "S090":"initialized in 2009",                  \
            "S091":"initialized in 2009",                  \
            "S092":"initialized in 2009",                  \
            "S093":"initialized in 2009",                  \
            "S094":"initialized in 2009",                  \
            "S095":"initialized in 2009",                  \
            "S096":"initialized in 2009",                  \
            "S097":"initialized in 2009",                  \
            "S098":"initialized in 2009",                  \
            "S099":"initialized in 2009",                  \
            "S100":"initialized in 2009",                  \
            "s001":"initialized in 2009",                  \
            "s002":"initialized in 2009",                  \
            "s003":"initialized in 2009",                  \
            "s004":"initialized in 2009",                  \
            "s005":"initialized in 2009",                  \
            "s006":"initialized in 2009",                  \
            "s007":"initialized in 2009",                  \
            "s008":"initialized in 2009",                  \
            "s009":"initialized in 2009",                  \
            "s010":"initialized in 2009",                  \
            "s011":"initialized in 2009",                  \
            "s012":"initialized in 2009",                  \
            "s013":"initialized in 2009",                  \
            "s014":"initialized in 2009",                  \
            "s015":"initialized in 2009",                  \
            "s016":"initialized in 2009",                  \
            "s017":"initialized in 2009",                  \
            "s018":"initialized in 2009",                  \
            "s019":"initialized in 2009",                  \
            "s020":"initialized in 2009",                  \
            "s021":"initialized in 2009",                  \
            "s022":"initialized in 2009",                  \
            "s023":"initialized in 2009",                  \
            "s024":"initialized in 2009",                  \
            "s025":"initialized in 2009",                  \
            "s026":"initialized in 2009",                  \
            "s027":"initialized in 2009",                  \
            "s028":"initialized in 2009",                  \
            "s029":"initialized in 2009",                  \
            "s030":"initialized in 2009",                  \
            "s031":"initialized in 2009",                  \
            "s032":"initialized in 2009",                  \
            "s033":"initialized in 2009",                  \
            "s034":"initialized in 2009",                  \
            "s035":"initialized in 2009",                  \
            "s036":"initialized in 2009",                  \
            "s037":"initialized in 2009",                  \
            "s038":"initialized in 2009",                  \
            "s039":"initialized in 2009",                  \
            "s040":"initialized in 2009",                  \
            "s041":"initialized in 2009",                  \
            "s042":"initialized in 2009",                  \
            "s043":"initialized in 2009",                  \
            "s044":"initialized in 2009",                  \
            "s045":"initialized in 2009",                  \
            "s046":"initialized in 2009",                  \
            "s047":"initialized in 2009",                  \
            "s048":"initialized in 2009",                  \
            "s049":"initialized in 2009",                  \
            "s050":"initialized in 2009",                  \
            "s051":"initialized in 2009",                  \
            "s052":"initialized in 2009",                  \
            "s053":"initialized in 2009",                  \
            "s054":"initialized in 2009",                  \
            "s055":"initialized in 2009",                  \
            "s056":"initialized in 2009",                  \
            "s057":"initialized in 2009",                  \
            "s058":"initialized in 2009",                  \
            "s059":"initialized in 2009",                  \
            "s060":"initialized in 2009",                  \
            "s061":"initialized in 2009",                  \
            "s062":"initialized in 2009",                  \
            "s063":"initialized in 2009",                  \
            "s064":"initialized in 2009",                  \
            "s065":"initialized in 2009",                  \
            "s066":"initialized in 2009",                  \
            "s067":"initialized in 2009",                  \
            "s068":"initialized in 2009",                  \
            "s069":"initialized in 2009",                  \
            "s070":"initialized in 2009",                  \
            "s071":"initialized in 2009",                  \
            "s072":"initialized in 2009",                  \
            "s073":"initialized in 2009",                  \
            "s074":"initialized in 2009",                  \
            "s075":"initialized in 2009",                  \
            "s076":"initialized in 2009",                  \
            "s077":"initialized in 2009",                  \
            "s078":"initialized in 2009",                  \
            "s079":"initialized in 2009",                  \
            "s080":"initialized in 2009",                  \
            "s081":"initialized in 2009",                  \
            "s082":"initialized in 2009",                  \
            "s083":"initialized in 2009",                  \
            "s084":"initialized in 2009",                  \
            "s085":"initialized in 2009",                  \
            "s086":"initialized in 2009",                  \
            "s087":"initialized in 2009",                  \
            "s088":"initialized in 2009",                  \
            "s089":"initialized in 2009",                  \
            "s090":"initialized in 2009",                  \
            "s091":"initialized in 2009",                  \
            "s092":"initialized in 2009",                  \
            "s093":"initialized in 2009",                  \
            "s094":"initialized in 2009",                  \
            "s095":"initialized in 2009",                  \
            "s096":"initialized in 2009",                  \
            "s097":"initialized in 2009",                  \
            "s098":"initialized in 2009",                  \
            "s099":"initialized in 2009",                  \
            "s100":"initialized in 2009",                  
  ' ${table_file_CV}



  sed -i  '/"1pctCO2-4xext":{/i \
            "AISC":{                                                                                 \
                "activity_id":[                                                                      \
                    "CMIP"                                                                           \
                ],                                                                                   \
                "additional_allowed_model_components":[                                              \
                    "AER",                                                                           \
                    "CHEM",                                                                          \
                    "BGC"                                                                            \
                ],                                                                                   \
                "experiment":"Atmosphere Interactive ERA_Land SM climatology Fixed ",                \
                "experiment_id":"AISC",                                                              \
                "parent_activity_id":[                                                               \
                    "no parent"                                                                      \
                ],                                                                                   \
                "parent_experiment_id":[                                                             \
                    "no parent"                                                                      \
                ],                                                                                   \
                "required_model_components":[                                                        \
                    "AGCM"                                                                           \
                ],                                                                                   \
                "sub_experiment_id":[                                                                \
                    "AISC",                                                                          \
                    "S001",                                                                          \
                    "S002",                                                                          \
                    "S003",                                                                          \
                    "S004",                                                                          \
                    "S005",                                                                          \
                    "S006",                                                                          \
                    "S007",                                                                          \
                    "S008",                                                                          \
                    "S009",                                                                          \
                    "S010",                                                                          \
                    "S011",                                                                          \
                    "S012",                                                                          \
                    "S013",                                                                          \
                    "S014",                                                                          \
                    "S015",                                                                          \
                    "S016",                                                                          \
                    "S017",                                                                          \
                    "S018",                                                                          \
                    "S019",                                                                          \
                    "S020",                                                                          \
                    "S021",                                                                          \
                    "S022",                                                                          \
                    "S023",                                                                          \
                    "S024",                                                                          \
                    "S025",                                                                          \
                    "S026",                                                                          \
                    "S027",                                                                          \
                    "S028",                                                                          \
                    "S029",                                                                          \
                    "S030",                                                                          \
                    "S031",                                                                          \
                    "S032",                                                                          \
                    "S033",                                                                          \
                    "S034",                                                                          \
                    "S035",                                                                          \
                    "S036",                                                                          \
                    "S037",                                                                          \
                    "S038",                                                                          \
                    "S039",                                                                          \
                    "S040",                                                                          \
                    "S041",                                                                          \
                    "S042",                                                                          \
                    "S043",                                                                          \
                    "S044",                                                                          \
                    "S045",                                                                          \
                    "S046",                                                                          \
                    "S047",                                                                          \
                    "S048",                                                                          \
                    "S049",                                                                          \
                    "S050",                                                                          \
                    "S051",                                                                          \
                    "S052",                                                                          \
                    "S053",                                                                          \
                    "S054",                                                                          \
                    "S055",                                                                          \
                    "S056",                                                                          \
                    "S057",                                                                          \
                    "S058",                                                                          \
                    "S059",                                                                          \
                    "S060",                                                                          \
                    "S061",                                                                          \
                    "S062",                                                                          \
                    "S063",                                                                          \
                    "S064",                                                                          \
                    "S065",                                                                          \
                    "S066",                                                                          \
                    "S067",                                                                          \
                    "S068",                                                                          \
                    "S069",                                                                          \
                    "S070",                                                                          \
                    "S071",                                                                          \
                    "S072",                                                                          \
                    "S073",                                                                          \
                    "S074",                                                                          \
                    "S075",                                                                          \
                    "S076",                                                                          \
                    "S077",                                                                          \
                    "S078",                                                                          \
                    "S079",                                                                          \
                    "S080",                                                                          \
                    "S081",                                                                          \
                    "S082",                                                                          \
                    "S083",                                                                          \
                    "S084",                                                                          \
                    "S085",                                                                          \
                    "S086",                                                                          \
                    "S087",                                                                          \
                    "S088",                                                                          \
                    "S089",                                                                          \
                    "S090",                                                                          \
                    "S091",                                                                          \
                    "S092",                                                                          \
                    "S093",                                                                          \
                    "S094",                                                                          \
                    "S095",                                                                          \
                    "S096",                                                                          \
                    "S097",                                                                          \
                    "S098",                                                                          \
                    "S099",                                                                          \
                    "S100"                                                                           \
                ]                                                                                    \
            },                                                                                       \
            "AISI":{                                                                                 \
                "activity_id":[                                                                      \
                    "CMIP"                                                                           \
                ],                                                                                   \
                "additional_allowed_model_components":[                                              \
                    "AER",                                                                           \
                    "CHEM",                                                                          \
                    "BGC"                                                                            \
                ],                                                                                   \
                "experiment":"Atmosphere Interactive Soil Interactive",                              \
                "experiment_id":"AISI",                                                              \
                "parent_activity_id":[                                                               \
                    "no parent"                                                                      \
                ],                                                                                   \
                "parent_experiment_id":[                                                             \
                    "no parent"                                                                      \
                ],                                                                                   \
                "required_model_components":[                                                        \
                    "AGCM"                                                                           \
                ],                                                                                   \
                "sub_experiment_id":[                                                                \
                    "C001",                                                                          \
                    "C002",                                                                          \
                    "C003",                                                                          \
                    "C004",                                                                          \
                    "C005",                                                                          \
                    "C006",                                                                          \
                    "C007",                                                                          \
                    "C008",                                                                          \
                    "C009",                                                                          \
                    "C010",                                                                          \
                    "E001",                                                                          \
                    "E002",                                                                          \
                    "E003",                                                                          \
                    "E004",                                                                          \
                    "E005",                                                                          \
                    "E006",                                                                          \
                    "E007",                                                                          \
                    "E008",                                                                          \
                    "E009",                                                                          \
                    "E010",                                                                          \
                    "E011",                                                                          \
                    "E012",                                                                          \
                    "E013",                                                                          \
                    "E014",                                                                          \
                    "E015",                                                                          \
                    "E016",                                                                          \
                    "E017",                                                                          \
                    "E018",                                                                          \
                    "E019",                                                                          \
                    "E020",                                                                          \
                    "E021",                                                                          \
                    "E022",                                                                          \
                    "E023",                                                                          \
                    "E024",                                                                          \
                    "E025",                                                                          \
                    "E026",                                                                          \
                    "E027",                                                                          \
                    "E028",                                                                          \
                    "E029",                                                                          \
                    "E030",                                                                          \
                    "E031",                                                                          \
                    "E032",                                                                          \
                    "E033",                                                                          \
                    "E034",                                                                          \
                    "E035",                                                                          \
                    "E036",                                                                          \
                    "E037",                                                                          \
                    "E038",                                                                          \
                    "E039",                                                                          \
                    "E040",                                                                          \
                    "E041",                                                                          \
                    "E042",                                                                          \
                    "E043",                                                                          \
                    "E044",                                                                          \
                    "E045",                                                                          \
                    "E046",                                                                          \
                    "E047",                                                                          \
                    "E048",                                                                          \
                    "E049",                                                                          \
                    "E050",                                                                          \
                    "E051",                                                                          \
                    "E052",                                                                          \
                    "E053",                                                                          \
                    "E054",                                                                          \
                    "E055",                                                                          \
                    "E056",                                                                          \
                    "E057",                                                                          \
                    "E058",                                                                          \
                    "E059",                                                                          \
                    "E060",                                                                          \
                    "E061",                                                                          \
                    "E062",                                                                          \
                    "E063",                                                                          \
                    "E064",                                                                          \
                    "E065",                                                                          \
                    "E066",                                                                          \
                    "E067",                                                                          \
                    "E068",                                                                          \
                    "E069",                                                                          \
                    "E070",                                                                          \
                    "E071",                                                                          \
                    "E072",                                                                          \
                    "E073",                                                                          \
                    "E074",                                                                          \
                    "E075",                                                                          \
                    "E076",                                                                          \
                    "E077",                                                                          \
                    "E078",                                                                          \
                    "E079",                                                                          \
                    "E080",                                                                          \
                    "E081",                                                                          \
                    "E082",                                                                          \
                    "E083",                                                                          \
                    "E084",                                                                          \
                    "E085",                                                                          \
                    "E086",                                                                          \
                    "E087",                                                                          \
                    "E088",                                                                          \
                    "E089",                                                                          \
                    "E090",                                                                          \
                    "E091",                                                                          \
                    "E092",                                                                          \
                    "E093",                                                                          \
                    "E094",                                                                          \
                    "E095",                                                                          \
                    "E096",                                                                          \
                    "E097",                                                                          \
                    "E098",                                                                          \
                    "E099",                                                                          \
                    "E100"                                                                           \
                ]                                                                                    \
            },                                                                                       \
            "AISE":{                                                                                 \
                "activity_id":[                                                                      \
                    "CMIP"                                                                           \
                ],                                                                                   \
                "additional_allowed_model_components":[                                              \
                    "AER",                                                                           \
                    "CHEM",                                                                          \
                    "BGC"                                                                            \
                ],                                                                                   \
                "experiment":"Atmosphere Interactive EC-Earth3 AISI ensemble SM climatology Fixed ", \
                "experiment_id":"AISE",                                                              \
                "parent_activity_id":[                                                               \
                    "no parent"                                                                      \
                ],                                                                                   \
                "parent_experiment_id":[                                                             \
                    "no parent"                                                                      \
                ],                                                                                   \
                "required_model_components":[                                                        \
                    "AGCM"                                                                           \
                ],                                                                                   \
                "sub_experiment_id":[                                                                \
                    "s001",                                                                          \
                    "s002",                                                                          \
                    "s003",                                                                          \
                    "s004",                                                                          \
                    "s005",                                                                          \
                    "s006",                                                                          \
                    "s007",                                                                          \
                    "s008",                                                                          \
                    "s009",                                                                          \
                    "s010",                                                                          \
                    "s011",                                                                          \
                    "s012",                                                                          \
                    "s013",                                                                          \
                    "s014",                                                                          \
                    "s015",                                                                          \
                    "s016",                                                                          \
                    "s017",                                                                          \
                    "s018",                                                                          \
                    "s019",                                                                          \
                    "s020",                                                                          \
                    "s021",                                                                          \
                    "s022",                                                                          \
                    "s023",                                                                          \
                    "s024",                                                                          \
                    "s025",                                                                          \
                    "s026",                                                                          \
                    "s027",                                                                          \
                    "s028",                                                                          \
                    "s029",                                                                          \
                    "s030",                                                                          \
                    "s031",                                                                          \
                    "s032",                                                                          \
                    "s033",                                                                          \
                    "s034",                                                                          \
                    "s035",                                                                          \
                    "s036",                                                                          \
                    "s037",                                                                          \
                    "s038",                                                                          \
                    "s039",                                                                          \
                    "s040",                                                                          \
                    "s041",                                                                          \
                    "s042",                                                                          \
                    "s043",                                                                          \
                    "s044",                                                                          \
                    "s045",                                                                          \
                    "s046",                                                                          \
                    "s047",                                                                          \
                    "s048",                                                                          \
                    "s049",                                                                          \
                    "s050",                                                                          \
                    "s051",                                                                          \
                    "s052",                                                                          \
                    "s053",                                                                          \
                    "s054",                                                                          \
                    "s055",                                                                          \
                    "s056",                                                                          \
                    "s057",                                                                          \
                    "s058",                                                                          \
                    "s059",                                                                          \
                    "s060",                                                                          \
                    "s061",                                                                          \
                    "s062",                                                                          \
                    "s063",                                                                          \
                    "s064",                                                                          \
                    "s065",                                                                          \
                    "s066",                                                                          \
                    "s067",                                                                          \
                    "s068",                                                                          \
                    "s069",                                                                          \
                    "s070",                                                                          \
                    "s071",                                                                          \
                    "s072",                                                                          \
                    "s073",                                                                          \
                    "s074",                                                                          \
                    "s075",                                                                          \
                    "s076",                                                                          \
                    "s077",                                                                          \
                    "s078",                                                                          \
                    "s079",                                                                          \
                    "s080",                                                                          \
                    "s081",                                                                          \
                    "s082",                                                                          \
                    "s083",                                                                          \
                    "s084",                                                                          \
                    "s085",                                                                          \
                    "s086",                                                                          \
                    "s087",                                                                          \
                    "s088",                                                                          \
                    "s089",                                                                          \
                    "s090",                                                                          \
                    "s091",                                                                          \
                    "s092",                                                                          \
                    "s093",                                                                          \
                    "s094",                                                                          \
                    "s095",                                                                          \
                    "s096",                                                                          \
                    "s097",                                                                          \
                    "s098",                                                                          \
                    "s099",                                                                          \
                    "s100"                                                                           \
                ]                                                                                    \
            },                                                                                       \
            "AISF":{                                                                                 \
                "activity_id":[                                                                      \
                    "CMIP"                                                                           \
                ],                                                                                   \
                "additional_allowed_model_components":[                                              \
                    "AER",                                                                           \
                    "CHEM",                                                                          \
                    "BGC"                                                                            \
                ],                                                                                   \
                "experiment":"Atmosphere Interactive Soil Fixed",                                    \
                "experiment_id":"AISF",                                                              \
                "parent_activity_id":[                                                               \
                    "no parent"                                                                      \
                ],                                                                                   \
                "parent_experiment_id":[                                                             \
                    "no parent"                                                                      \
                ],                                                                                   \
                "required_model_components":[                                                        \
                    "AGCM"                                                                           \
                ],                                                                                   \
                "sub_experiment_id":[                                                                \
                    "c001",                                                                          \
                    "c002",                                                                          \
                    "c003",                                                                          \
                    "c004",                                                                          \
                    "c005",                                                                          \
                    "e001",                                                                          \
                    "e002",                                                                          \
                    "e003",                                                                          \
                    "e004",                                                                          \
                    "e005",                                                                          \
                    "e006",                                                                          \
                    "e007",                                                                          \
                    "e008",                                                                          \
                    "e009",                                                                          \
                    "e010",                                                                          \
                    "e011",                                                                          \
                    "e012",                                                                          \
                    "e013",                                                                          \
                    "e014",                                                                          \
                    "e015",                                                                          \
                    "e016",                                                                          \
                    "e017",                                                                          \
                    "e018",                                                                          \
                    "e019",                                                                          \
                    "e020",                                                                          \
                    "e021",                                                                          \
                    "e022",                                                                          \
                    "e023",                                                                          \
                    "e024",                                                                          \
                    "e025",                                                                          \
                    "e026",                                                                          \
                    "e027",                                                                          \
                    "e028",                                                                          \
                    "e029",                                                                          \
                    "e030",                                                                          \
                    "e031",                                                                          \
                    "e032",                                                                          \
                    "e033",                                                                          \
                    "e034",                                                                          \
                    "e035",                                                                          \
                    "e036",                                                                          \
                    "e037",                                                                          \
                    "e038",                                                                          \
                    "e039",                                                                          \
                    "e040",                                                                          \
                    "e041",                                                                          \
                    "e042",                                                                          \
                    "e043",                                                                          \
                    "e044",                                                                          \
                    "e045",                                                                          \
                    "e046",                                                                          \
                    "e047",                                                                          \
                    "e048",                                                                          \
                    "e049",                                                                          \
                    "e050",                                                                          \
                    "e051",                                                                          \
                    "e052",                                                                          \
                    "e053",                                                                          \
                    "e054",                                                                          \
                    "e055",                                                                          \
                    "e056",                                                                          \
                    "e057",                                                                          \
                    "e058",                                                                          \
                    "e059",                                                                          \
                    "e060",                                                                          \
                    "e061",                                                                          \
                    "e062",                                                                          \
                    "e063",                                                                          \
                    "e064",                                                                          \
                    "e065",                                                                          \
                    "e066",                                                                          \
                    "e067",                                                                          \
                    "e068",                                                                          \
                    "e069",                                                                          \
                    "e070",                                                                          \
                    "e071",                                                                          \
                    "e072",                                                                          \
                    "e073",                                                                          \
                    "e074",                                                                          \
                    "e075",                                                                          \
                    "e076",                                                                          \
                    "e077",                                                                          \
                    "e078",                                                                          \
                    "e079",                                                                          \
                    "e080",                                                                          \
                    "e081",                                                                          \
                    "e082",                                                                          \
                    "e083",                                                                          \
                    "e084",                                                                          \
                    "e085",                                                                          \
                    "e086",                                                                          \
                    "e087",                                                                          \
                    "e088",                                                                          \
                    "e089",                                                                          \
                    "e090",                                                                          \
                    "e091",                                                                          \
                    "e092",                                                                          \
                    "e093",                                                                          \
                    "e094",                                                                          \
                    "e095",                                                                          \
                    "e096",                                                                          \
                    "e097",                                                                          \
                    "e098",                                                                          \
                    "e099",                                                                          \
                    "e100"                                                                           \
                ]                                                                                    \
            },                                                                                       \
            "AFSI":{                                                                                 \
                "activity_id":[                                                                      \
                    "CMIP"                                                                           \
                ],                                                                                   \
                "additional_allowed_model_components":[                                              \
                    "AER",                                                                           \
                    "CHEM",                                                                          \
                    "BGC"                                                                            \
                ],                                                                                   \
                "experiment":"Atmosphere Fixed Soil Interactive",                                    \
                "experiment_id":"AFSI",                                                              \
                "parent_activity_id":[                                                               \
                    "no parent"                                                                      \
                ],                                                                                   \
                "parent_experiment_id":[                                                             \
                    "no parent"                                                                      \
                ],                                                                                   \
                "required_model_components":[                                                        \
                    "AGCM"                                                                           \
                ],                                                                                   \
                "sub_experiment_id":[                                                                \
                    "AFSI"                                                                           \
                ]                                                                                    \
            },                                                                                       \
            "AFSF":{                                                                                 \
                "activity_id":[                                                                      \
                    "CMIP"                                                                           \
                ],                                                                                   \
                "additional_allowed_model_components":[                                              \
                    "AER",                                                                           \
                    "CHEM",                                                                          \
                    "BGC"                                                                            \
                ],                                                                                   \
                "experiment":"Atmosphere Fixed, Soil Fixed",                                         \
                "experiment_id":"AFSF",                                                              \
                "parent_activity_id":[                                                               \
                    "no parent"                                                                      \
                ],                                                                                   \
                "parent_experiment_id":[                                                             \
                    "no parent"                                                                      \
                ],                                                                                   \
                "required_model_components":[                                                        \
                    "AGCM"                                                                           \
                ],                                                                                   \
                "sub_experiment_id":[                                                                \
                    "afsf"                                                                           \
                ]                                                                                    \
            },                                                                                       \
            "AFSC":{                                                                                 \
                "activity_id":[                                                                      \
                    "CMIP"                                                                           \
                ],                                                                                   \
                "additional_allowed_model_components":[                                              \
                    "AER",                                                                           \
                    "CHEM",                                                                          \
                    "BGC"                                                                            \
                ],                                                                                   \
                "experiment":"Atmosphere Fixed , Soil Climate Fixed",                                \
                "experiment_id":"AFSC",                                                              \
                "parent_activity_id":[                                                               \
                    "no parent"                                                                      \
                ],                                                                                   \
                "parent_experiment_id":[                                                             \
                    "no parent"                                                                      \
                ],                                                                                   \
                "required_model_components":[                                                        \
                    "AGCM"                                                                           \
                ],                                                                                   \
                "sub_experiment_id":[                                                                \
                    "afsc"                                                                           \
                ]                                                                                    \
            },                                                                                       
  ' ${table_file_CV}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_coordinate}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_6hrPlevPt}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_Amon}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_day}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_Lmon}
  sed -i -e 's/\s*$//g'                ${table_file_CV}

  cd -

  echo
  echo " $0 reports:"
  echo "  The adjusted files are:"
  echo "   ${table_path}/${table_file_coordinate}"
  echo "   ${table_path}/${table_file_6hrPlevPt}"
  echo "   ${table_path}/${table_file_Amon}"
  echo "   ${table_path}/${table_file_day}"
  echo "   ${table_path}/${table_file_Lmon}"
  echo "   ${table_path}/${table_file_CV}"
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
