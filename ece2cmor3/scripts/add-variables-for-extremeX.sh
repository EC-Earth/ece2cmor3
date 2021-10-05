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

  cd ../resources/
  git checkout ifspar.json
  cd -
  
  cd ../resources/cmip6-cmor-tables
  git checkout Tables/CMIP6_6hrPlevPt.json
  git checkout Tables/CMIP6_Amon.json
  git checkout Tables/CMIP6_CV.json
  git checkout Tables/CMIP6_Lmon.json
  git checkout Tables/CMIP6_coordinate.json
  git checkout Tables/CMIP6_day.json
  cd -


  head --lines=-1 ../resources/ifspar.json                   > extended-ifspar.json

 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json
 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json
 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json
 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json
 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json
 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json
 #echo '  ' | sed 's/\s*$//g' >> extended-ifspar.json

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
  echo '    },                          ' | sed 's/\s*$//g' >> extended-ifspar.json

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

  mv -f extended-ifspar.json ../resources/ifspar.json


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
  ' ../resources/tables/CMIP6_coordinate.json




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
  ' ../resources/tables/CMIP6_6hrPlevPt.json

# "rainmxrat27": {
# "ta27": {
# "ua7h": {
# "va3": {

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
  ' ../resources/tables/CMIP6_Amon.json

# "rlut": {
# "tas": {
# "uas": {
# "vas": {
# "zg": {

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
  ' ../resources/tables/CMIP6_day.json

# "pr": {
# "rsds": {
# "tas": {
# "uas": {
# "zg": {
# "zg": {

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
            "e100":"initialized in 2009",                  
  ' ../resources/tables/CMIP6_CV.json



  sed -i  '/"1pctCO2-4xext":{/i \
            "AISI":{                                                    \
                "activity_id":[                                         \
                    "CMIP"                                              \
                ],                                                      \
                "additional_allowed_model_components":[                 \
                    "AER",                                              \
                    "CHEM",                                             \
                    "BGC"                                               \
                ],                                                      \
                "experiment":"Atmosphere Interactive Soil Interactive", \
                "experiment_id":"AISI",                                 \
                "parent_activity_id":[                                  \
                    "no parent"                                         \
                ],                                                      \
                "parent_experiment_id":[                                \
                    "no parent"                                         \
                ],                                                      \
                "required_model_components":[                           \
                    "AGCM"                                              \
                ],                                                      \
                "sub_experiment_id":[                                   \
                    "C001",                                             \
                    "C002",                                             \
                    "C003",                                             \
                    "C004",                                             \
                    "C005",                                             \
                    "C006",                                             \
                    "C007",                                             \
                    "C008",                                             \
                    "C009",                                             \
                    "C010",                                             \
                    "E001",                                             \
                    "E002",                                             \
                    "E003",                                             \
                    "E004",                                             \
                    "E005",                                             \
                    "E006",                                             \
                    "E007",                                             \
                    "E008",                                             \
                    "E009",                                             \
                    "E010",                                             \
                    "E011",                                             \
                    "E012",                                             \
                    "E013",                                             \
                    "E014",                                             \
                    "E015",                                             \
                    "E016",                                             \
                    "E017",                                             \
                    "E018",                                             \
                    "E019",                                             \
                    "E020",                                             \
                    "E021",                                             \
                    "E022",                                             \
                    "E023",                                             \
                    "E024",                                             \
                    "E025",                                             \
                    "E026",                                             \
                    "E027",                                             \
                    "E028",                                             \
                    "E029",                                             \
                    "E030",                                             \
                    "E031",                                             \
                    "E032",                                             \
                    "E033",                                             \
                    "E034",                                             \
                    "E035",                                             \
                    "E036",                                             \
                    "E037",                                             \
                    "E038",                                             \
                    "E039",                                             \
                    "E040",                                             \
                    "E041",                                             \
                    "E042",                                             \
                    "E043",                                             \
                    "E044",                                             \
                    "E045",                                             \
                    "E046",                                             \
                    "E047",                                             \
                    "E048",                                             \
                    "E049",                                             \
                    "E050",                                             \
                    "E051",                                             \
                    "E052",                                             \
                    "E053",                                             \
                    "E054",                                             \
                    "E055",                                             \
                    "E056",                                             \
                    "E057",                                             \
                    "E058",                                             \
                    "E059",                                             \
                    "E060",                                             \
                    "E061",                                             \
                    "E062",                                             \
                    "E063",                                             \
                    "E064",                                             \
                    "E065",                                             \
                    "E066",                                             \
                    "E067",                                             \
                    "E068",                                             \
                    "E069",                                             \
                    "E070",                                             \
                    "E071",                                             \
                    "E072",                                             \
                    "E073",                                             \
                    "E074",                                             \
                    "E075",                                             \
                    "E076",                                             \
                    "E077",                                             \
                    "E078",                                             \
                    "E079",                                             \
                    "E080",                                             \
                    "E081",                                             \
                    "E082",                                             \
                    "E083",                                             \
                    "E084",                                             \
                    "E085",                                             \
                    "E086",                                             \
                    "E087",                                             \
                    "E088",                                             \
                    "E089",                                             \
                    "E090",                                             \
                    "E091",                                             \
                    "E092",                                             \
                    "E093",                                             \
                    "E094",                                             \
                    "E095",                                             \
                    "E096",                                             \
                    "E097",                                             \
                    "E098",                                             \
                    "E099",                                             \
                    "E100"                                              \
                ]                                                       \
            },                                                          \
            "AISF":{                                                    \
                "activity_id":[                                         \
                    "CMIP"                                              \
                ],                                                      \
                "additional_allowed_model_components":[                 \
                    "AER",                                              \
                    "CHEM",                                             \
                    "BGC"                                               \
                ],                                                      \
                "experiment":"Atmosphere Interactive Soil Fixed",       \
                "experiment_id":"AISF",                                 \
                "parent_activity_id":[                                  \
                    "no parent"                                         \
                ],                                                      \
                "parent_experiment_id":[                                \
                    "no parent"                                         \
                ],                                                      \
                "required_model_components":[                           \
                    "AGCM"                                              \
                ],                                                      \
                "sub_experiment_id":[                                   \
                    "c001",                                             \
                    "c002",                                             \
                    "c003",                                             \
                    "c004",                                             \
                    "c005",                                             \
                    "e001",                                             \
                    "e002",                                             \
                    "e003",                                             \
                    "e004",                                             \
                    "e005",                                             \
                    "e006",                                             \
                    "e007",                                             \
                    "e008",                                             \
                    "e009",                                             \
                    "e010",                                             \
                    "e011",                                             \
                    "e012",                                             \
                    "e013",                                             \
                    "e014",                                             \
                    "e015",                                             \
                    "e016",                                             \
                    "e017",                                             \
                    "e018",                                             \
                    "e019",                                             \
                    "e020",                                             \
                    "e021",                                             \
                    "e022",                                             \
                    "e023",                                             \
                    "e024",                                             \
                    "e025",                                             \
                    "e026",                                             \
                    "e027",                                             \
                    "e028",                                             \
                    "e029",                                             \
                    "e030",                                             \
                    "e031",                                             \
                    "e032",                                             \
                    "e033",                                             \
                    "e034",                                             \
                    "e035",                                             \
                    "e036",                                             \
                    "e037",                                             \
                    "e038",                                             \
                    "e039",                                             \
                    "e040",                                             \
                    "e041",                                             \
                    "e042",                                             \
                    "e043",                                             \
                    "e044",                                             \
                    "e045",                                             \
                    "e046",                                             \
                    "e047",                                             \
                    "e048",                                             \
                    "e049",                                             \
                    "e050",                                             \
                    "e051",                                             \
                    "e052",                                             \
                    "e053",                                             \
                    "e054",                                             \
                    "e055",                                             \
                    "e056",                                             \
                    "e057",                                             \
                    "e058",                                             \
                    "e059",                                             \
                    "e060",                                             \
                    "e061",                                             \
                    "e062",                                             \
                    "e063",                                             \
                    "e064",                                             \
                    "e065",                                             \
                    "e066",                                             \
                    "e067",                                             \
                    "e068",                                             \
                    "e069",                                             \
                    "e070",                                             \
                    "e071",                                             \
                    "e072",                                             \
                    "e073",                                             \
                    "e074",                                             \
                    "e075",                                             \
                    "e076",                                             \
                    "e077",                                             \
                    "e078",                                             \
                    "e079",                                             \
                    "e080",                                             \
                    "e081",                                             \
                    "e082",                                             \
                    "e083",                                             \
                    "e084",                                             \
                    "e085",                                             \
                    "e086",                                             \
                    "e087",                                             \
                    "e088",                                             \
                    "e089",                                             \
                    "e090",                                             \
                    "e091",                                             \
                    "e092",                                             \
                    "e093",                                             \
                    "e094",                                             \
                    "e095",                                             \
                    "e096",                                             \
                    "e097",                                             \
                    "e098",                                             \
                    "e099",                                             \
                    "e100"                                              \
                ]                                                       \
            },                                                          \
            "AFSI":{                                                    \
                "activity_id":[                                         \
                    "CMIP"                                              \
                ],                                                      \
                "additional_allowed_model_components":[                 \
                    "AER",                                              \
                    "CHEM",                                             \
                    "BGC"                                               \
                ],                                                      \
                "experiment":"Atmosphere Fixed Soil Interactive",       \
                "experiment_id":"AFSI",                                 \
                "parent_activity_id":[                                  \
                    "no parent"                                         \
                ],                                                      \
                "parent_experiment_id":[                                \
                    "no parent"                                         \
                ],                                                      \
                "required_model_components":[                           \
                    "AGCM"                                              \
                ],                                                      \
                "sub_experiment_id":[                                   \
                    "AFSI"                                              \
                ]                                                       \
            },                                                          \
            "AFSF":{                                                    \
                "activity_id":[                                         \
                    "CMIP"                                              \
                ],                                                      \
                "additional_allowed_model_components":[                 \
                    "AER",                                              \
                    "CHEM",                                             \
                    "BGC"                                               \
                ],                                                      \
                "experiment":"Atmosphere Fixed, Soil Fixed",            \
                "experiment_id":"AFSF",                                 \
                "parent_activity_id":[                                  \
                    "no parent"                                         \
                ],                                                      \
                "parent_experiment_id":[                                \
                    "no parent"                                         \
                ],                                                      \
                "required_model_components":[                           \
                    "AGCM"                                              \
                ],                                                      \
                "sub_experiment_id":[                                   \
                    "afsf"                                              \
                ]                                                       \
            },                                                          \
            "AFSC":{                                                    \
                "activity_id":[                                         \
                    "CMIP"                                              \
                ],                                                      \
                "additional_allowed_model_components":[                 \
                    "AER",                                              \
                    "CHEM",                                             \
                    "BGC"                                               \
                ],                                                      \
                "experiment":"Atmosphere Fixed , Soil Climate Fixed",   \
                "experiment_id":"AFSC",                                 \
                "parent_activity_id":[                                  \
                    "no parent"                                         \
                ],                                                      \
                "parent_experiment_id":[                                \
                    "no parent"                                         \
                ],                                                      \
                "required_model_components":[                           \
                    "AGCM"                                              \
                ],                                                      \
                "sub_experiment_id":[                                   \
                    "afsc"                                              \
                ]                                                       \
            },                                                          
  ' ../resources/tables/CMIP6_CV.json













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
