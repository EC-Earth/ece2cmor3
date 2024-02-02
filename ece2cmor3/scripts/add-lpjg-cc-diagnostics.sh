#!/bin/bash
# Thomas Reerink
#
# This script adds some non-cmor variables (which thus do not exit in
# the CMIP6 data request) to the Eyr & Emon CMOR tables.
#
# This script requires no arguments.
#
# Run example:
#  ./add-lpjg-cc-diagnostics.sh
#

if [ "$#" -eq 0 ]; then

 add_the_lpjg_cc_diagnostics=True

 if [ add_the_lpjg_cc_diagnostics ]; then
  # See #778      https://github.com/EC-Earth/ece2cmor3/issues/#778
  # See #794      https://github.com/EC-Earth/ece2cmor3/issues/794
  # See #1312-11  https://dev.ec-earth.org/issues/1312#note-11
  # See #1312-76  https://dev.ec-earth.org/issues/1312#note-76

  # Add:
  #  Eyr  cFluxYr
  #  Eyr  cLandYr
  #  Emon cLand_1st

  # Add all water related variables and tsl to new created LPJG CMOR tables,
  # because the same variables delivered by HTESSEL have the preference as
  # they are consistant with the atmosphere.
  #  Amon  evspsbl     => LPJGmon
  #  Emon  evspsblpot  => LPJGmon
  #        evspsblsoi  => LPJGmon
  #  Emon  mrroLut     => LPJGmon
  #        mrsll       => LPJGmon
  #        mrsol       => LPJGmon
  #        mrsoLut     => LPJGmon
  #        mrsosLut    => LPJGmon
  #        mrro        => LPJGmon
  #        mrros       => LPJGmon
  #        mrso        => LPJGmon
  #        mrfso       => LPJGmon
  #        mrsos       => LPJGmon
  #  Llmon snc         => LPJGmon
  #  Llmon snd         => LPJGmon
  #  Llmon snw         => LPJGmon
  #        tran        => LPJGmon
  #        tsl         => LPJGmon

  #  Eday  ec          => LPJGday  prio 1, in ignore file because IFS can't deliver
  #        mrsll       => LPJGday
  #  Eday  mrso        => LPJGday
  #  Eday  mrsol       => LPJGday
  #  Eday  mrsos       => LPJGday
  #  Eday  mrro        => LPJGday
  #        tran        => LPJGday
  #        tsl         => LPJGday

  # Eyr    pastureFrac => LPJGyr

  table_path=../resources/cmip6-cmor-tables/Tables/
  table_file_Eyr=CMIP6_Eyr.json
  table_file_Emon=CMIP6_Emon.json

  cd ${table_path}
  git checkout ${table_file_Eyr}
  git checkout ${table_file_Emon}

  # CHECK metadata: comment - ocean cells
  sed -i  '/"cLitter": {/i \
        "cFluxYr": {                                                                                                                   \
            "frequency": "yr",                                                                                                         \
            "modeling_realm": "land",                                                                                                  \
            "standard_name": "cFluxYr",                                                                                                \
            "units": "kg m-2 yr-1",                                                                                                    \
            "cell_methods": "area: mean where land time: mean",                                                                        \
            "cell_measures": "area: areacella",                                                                                        \
            "long_name": "cFluxYr",                                                                                                    \
            "comment": "Non CMOR standard, but added by the EC-Earth Consortium within the OptimESM project.",                         \
            "dimensions": "longitude latitude time",                                                                                   \
            "out_name": "cFluxYr",                                                                                                     \
            "type": "real",                                                                                                            \
            "positive": "",                                                                                                            \
            "valid_min": "",                                                                                                           \
            "valid_max": "",                                                                                                           \
            "ok_min_mean_abs": "",                                                                                                     \
            "ok_max_mean_abs": ""                                                                                                      \
        },                                                                                                                             \
        "cLandYr": {                                                                                                                   \
            "frequency": "yr",                                                                                                         \
            "modeling_realm": "land",                                                                                                  \
            "standard_name": "mass_content_of_carbon_in_vegetation_and_litter_and_soil_and_forestry_and_agricultural_products",        \
            "units": "kg m-2",                                                                                                         \
            "cell_methods": "area: mean where land time: mean",                                                                        \
            "cell_measures": "area: areacella",                                                                                        \
            "long_name": "Total Carbon in All Terrestrial Carbon Pools",                                                               \
            "comment": "Report missing data over ocean grid cells. For fractional land report value averaged over the land fraction. Non CMOR standard, but added by the EC-Earth Consortium within the OptimESM project.", \
            "dimensions": "longitude latitude time",                                                                                   \
            "out_name": "cLandYr",                                                                                                     \
            "type": "real",                                                                                                            \
            "positive": "",                                                                                                            \
            "valid_min": "",                                                                                                           \
            "valid_max": "",                                                                                                           \
            "ok_min_mean_abs": "",                                                                                                     \
            "ok_max_mean_abs": ""                                                                                                      \
        },
  ' ${table_file_Eyr}

  sed -i  '/"cLitterCwd": {/i \
        "cLand_1st": {                                                                                                                 \
            "frequency": "mon",                                                                                                        \
            "modeling_realm": "land",                                                                                                  \
            "standard_name": "mass_content_of_carbon_in_vegetation_and_litter_and_soil_and_forestry_and_agricultural_products",        \
            "units": "kg m-2",                                                                                                         \
            "cell_methods": "area: mean where land time: mean",                                                                        \
            "cell_measures": "area: areacella",                                                                                        \
            "long_name": "Total Carbon in All Terrestrial Carbon Pools",                                                               \
            "comment": "Report missing data over ocean grid cells. For fractional land report value averaged over the land fraction. Non CMOR standard, but added by the EC-Earth Consortium within the OptimESM project.", \
            "dimensions": "longitude latitude time",                                                                                   \
            "out_name": "cLand_1st",                                                                                                   \
            "type": "real",                                                                                                            \
            "positive": "",                                                                                                            \
            "valid_min": "",                                                                                                           \
            "valid_max": "",                                                                                                           \
            "ok_min_mean_abs": "",                                                                                                     \
            "ok_max_mean_abs": ""                                                                                                      \
        },
  ' ${table_file_Emon}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_Eyr}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_Emon}

  cd -

  echo
  echo " $0 reports:"
  echo "  The adjusted files are:"
  echo "   ${table_path}/${table_file_Eyr}"
  echo "   ${table_path}/${table_file_Emon}"
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
