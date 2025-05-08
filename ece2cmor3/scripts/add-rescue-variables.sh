#!/bin/bash
# Thomas Reerink
#
# This script adds some non-cmor variables (which thus do not exit in
# the CMIP6 data request) to the Eyr cmor table.
#
# This script requires no arguments.
#
# Run example:
#  ./add-rescue-variables.sh
#

if [ "$#" -eq 0 ]; then

 add_rescue_variables=True

 if [ add_rescue_variables ]; then
  # See #835   https://github.com/EC-Earth/ece2cmor3/issues/835
  # See #1377  https://dev.ec-earth.org/issues/1377

  #  Added variables:
  #  From LPJ-GUESS:
  #  cBECCS                 Carbon content in CCS from Bioenergy crops (Carbon mass from BE in storage)
  #  fBECCS                 Carbon flux from Bioenergy crops harvested into CCS
  #  fBEatm                 Carbon Flux from Bioenergy crops harvested but not stored (going back into the atmosphere)

  #  From the CO2-Boxmodel:
  #  cDACCS                 Carbon content in CCS from direct Air capture
  #  fDACCS                 Carbon flux into CCS from direct Air capture

  #  Explanation
  #  BioEnergy - Carbon Capture and Storage (BECCS)
  #  Direct Air-Carbon Capture and Storage  (DACCS)

  #  Template variables:
  #  cBECCS:    cVeg  (annual)
  #  fBECCS:    fFire (annual)
  #  fBEatm:    fFire (annual)
  #  cDACCS:    co2mass
  #  fDACCS:    This one is a global single value no template yet

  #  The RESCUE branch equals the optimESM branch with the added CDR (Carbon-Dioxide Removal technologies) enabled for the RESCUE project

  # Apply first all optimesm additions:
  ./add-optimesm-variables.sh

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_LPJGyr=CMIP6_LPJGyr.json
  table_file_Eyr=CMIP6_Eyr.json

  cd ${table_path}
 #rm -f ${table_file_LPJGyr}      # Do not apply because of the optimes modifications
 #git checkout ${table_file_Eyr}  # Do not apply because of the optimes modifications

  # CHECK UNITS
  sed -i  '/"pastureFrac": {/i \
        "cBECCS": {                                                                                    \
            "frequency": "yrPt",                                                                       \
            "modeling_realm": "land",                                                                  \
            "standard_name": "carbon_content_in_ccs_from_bioenergy_crops",                             \
            "units": "kg m-2",                                                                         \
            "cell_methods": "area: mean where land time: point",                                       \
            "cell_measures": "area: areacella",                                                        \
            "long_name": "Carbon Mass in Vegetation",                                                  \
            "comment": "Carbon content in CCS from Bioenergy crops (Carbon mass from BE in storage)",  \
            "dimensions": "longitude latitude time1",                                                  \
            "out_name": "cBECCS",                                                                      \
            "type": "real",                                                                            \
            "positive": "",                                                                            \
            "valid_min": "",                                                                           \
            "valid_max": "",                                                                           \
            "ok_min_mean_abs": "",                                                                     \
            "ok_max_mean_abs": ""                                                                      \
        },                                                                                             \
        "fBECCS": {                                                                                    \
            "frequency": "yr",                                                                         \
            "modeling_realm": "land",                                                                  \
            "standard_name": "carbon_flux_from_bioenergy_crops_harvested_into_ccs",                    \
            "units": "kg m-2 s-1",                                                                     \
            "cell_methods": "area: mean where land time: mean",                                        \
            "cell_measures": "area: areacella",                                                        \
            "long_name": "Carbon flux from Bioenergy crops harvested into CCS [kgC m-2 s-1]",          \
            "comment": "",                                                                             \
            "dimensions": "longitude latitude time",                                                   \
            "out_name": "fBECCS",                                                                      \
            "type": "real",                                                                            \
            "positive": "up",                                                                          \
            "valid_min": "",                                                                           \
            "valid_max": "",                                                                           \
            "ok_min_mean_abs": "",                                                                     \
            "ok_max_mean_abs": ""                                                                      \
        },                                                                                             \
        "fBEatm": {                                                                                    \
            "frequency": "yr",                                                                         \
            "modeling_realm": "land",                                                                  \
            "standard_name": "carbon_flux_from_bioenergy_crops_harvested_but_not_stored",              \
            "units": "kg m-2 s-1",                                                                     \
            "cell_methods": "area: mean where land time: mean",                                        \
            "cell_measures": "area: areacella",                                                        \
            "long_name": "Carbon Flux from Bioenergy crops harvested but not stored (going back into the atmosphere) [kgC m-2 s-1]", \
            "comment": "",                                                                             \
            "dimensions": "longitude latitude time",                                                   \
            "out_name": "fBEatm",                                                                      \
            "type": "real",                                                                            \
            "positive": "up",                                                                          \
            "valid_min": "",                                                                           \
            "valid_max": "",                                                                           \
            "ok_min_mean_abs": "",                                                                     \
            "ok_max_mean_abs": ""                                                                      \
        },
  ' ${table_file_LPJGyr}

  sed -i  '/"cLitter": {/i \
        "cDACCS": {                                                           \
            "frequency": "yr",                                                \
            "modeling_realm": "atmos",                                        \
            "standard_name": "carbon_content_in_ccs_from_direct_air_capture", \
            "units": "kg",                                                    \
            "cell_methods": "area: time: mean",                               \
            "cell_measures": "",                                              \
            "long_name": "Carbon content in CCS from direct Air capture",     \
            "comment": "Direct Air-Carbon Capture and Storage (DACCS)",       \
            "dimensions": "time",                                             \
            "out_name": "cDACCS",                                             \
            "type": "real",                                                   \
            "positive": "",                                                   \
            "valid_min": "",                                                  \
            "valid_max": "",                                                  \
            "ok_min_mean_abs": "",                                            \
            "ok_max_mean_abs": ""                                             \
        },                                                                    \
        "fDACCS": {                                                           \
            "frequency": "yr",                                                \
            "modeling_realm": "atmos",                                        \
            "standard_name": "carbon_flux_into_ccs_from_direct_air_capture",  \
            "units": "1e-06",                                                 \
            "cell_methods": "time: mean",                                     \
            "cell_measures": "area: areacella",                               \
            "long_name": "Carbon flux into CCS from direct Air capture",      \
            "comment": "Direct Air-Carbon Capture and Storage (DACCS)",       \
            "dimensions": "longitude latitude time",                          \
            "out_name": "fDACCS",                                             \
            "type": "real",                                                   \
            "positive": "",                                                   \
            "valid_min": "",                                                  \
            "valid_max": "",                                                  \
            "ok_min_mean_abs": "",                                            \
            "ok_max_mean_abs": ""                                             \
        },
  ' ${table_file_Eyr}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_LPJGyr}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_Eyr}

  cd -

  echo
  echo " Running:"
  echo "  $0"
  echo " has adjusted the file:"
  echo "  ${table_path}/${table_file_LPJGyr}"
  echo "  ${table_path}/${table_file_Eyr}"
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
