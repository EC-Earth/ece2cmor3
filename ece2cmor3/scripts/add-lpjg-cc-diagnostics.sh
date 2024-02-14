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
  #  Emon cLand1st

  # Add all water related variables and tsl to new created LPJG CMOR tables,
  # because the same variables delivered by HTESSEL have the preference as
  # they are consistant with the atmosphere.

  #  Eday  ec          => LPJGday  prio 1, in ignore file because IFS can't deliver
  #        mrsll       => LPJGday
  #  Eday  mrso        => LPJGday
  #  Eday  mrsol       => LPJGday
  #  Eday  mrsos       => LPJGday
  #  Eday  mrro        => LPJGday
  #        tran        => LPJGday
  #        tsl         => LPJGday

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

  # Eyr    pastureFrac => LPJGyr

  table_path=../resources/cmip6-cmor-tables/Tables/
  table_file_Eyr=CMIP6_Eyr.json
  table_file_Emon=CMIP6_Emon.json
  table_file_cv=CMIP6_CV.json
  table_file_LPJGday=CMIP6_LPJGday.json
  table_file_LPJGmon=CMIP6_LPJGmon.json
  table_file_LPJGyr=CMIP6_LPJGyr.json

  cd ${table_path}
  rm -f ${table_file_LPJGday} ${table_file_LPJGmon} ${table_file_LPJGyr}
  git checkout ${table_file_Eyr}
  git checkout ${table_file_Emon}
  git checkout ${table_file_cv}

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
        "cLand1st": {                                                                                                                  \
            "frequency": "mon",                                                                                                        \
            "modeling_realm": "land",                                                                                                  \
            "standard_name": "mass_content_of_carbon_in_vegetation_and_litter_and_soil_and_forestry_and_agricultural_products",        \
            "units": "kg m-2",                                                                                                         \
            "cell_methods": "area: mean where land time: mean",                                                                        \
            "cell_measures": "area: areacella",                                                                                        \
            "long_name": "Total Carbon in All Terrestrial Carbon Pools",                                                               \
            "comment": "Report missing data over ocean grid cells. For fractional land report value averaged over the land fraction. Non CMOR standard, but added by the EC-Earth Consortium within the OptimESM project.", \
            "dimensions": "longitude latitude time",                                                                                   \
            "out_name": "cLand1st",                                                                                                    \
            "type": "real",                                                                                                            \
            "positive": "",                                                                                                            \
            "valid_min": "",                                                                                                           \
            "valid_max": "",                                                                                                           \
            "ok_min_mean_abs": "",                                                                                                     \
            "ok_max_mean_abs": ""                                                                                                      \
        },
  ' ${table_file_Emon}

  sed -i  '/"Lmon"/i \
            "LPJGday", \
            "LPJGmon", \
            "LPJGyr",
  ' ${table_file_cv}


  # Add CMIP6 LPJGday table header:
  echo '{                                              ' | sed 's/\s*$//g' >  ${table_file_LPJGday}
  echo '    "Header": {                                ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '        "data_specs_version": "01.00.33",      ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '        "cmor_version": "3.5",                 ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '        "table_id": "Table LPJGday",           ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '        "realm": "land",                       ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '        "table_date": "18 November 2020",      ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '        "missing_value": "1e20",               ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '        "int_missing_value": "-999",           ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '        "product": "model-output",             ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '        "approx_interval": "1.00000",          ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '        "generic_levels": "",                  ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '        "mip_era": "CMIP6",                    ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '        "Conventions": "CF-1.7 CMIP-6.2"       ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '    },                                         ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '    "variable_entry": {                        ' | sed 's/\s*$//g' >> ${table_file_LPJGday}

  grep -A 17 -e '"ec":'    CMIP6_Eday.json                                 >> ${table_file_LPJGday}
  grep -A 17 -e '"mrsll":' CMIP6_Eday.json                                 >> ${table_file_LPJGday}
  grep -A 17 -e '"mrso":'  CMIP6_day.json                                  >> ${table_file_LPJGday}
  grep -A 17 -e '"mrsol":' CMIP6_Eday.json                                 >> ${table_file_LPJGday}
  grep -A 17 -e '"mrsos":' CMIP6_day.json                                  >> ${table_file_LPJGday}
  grep -A 17 -e '"mrro":'  CMIP6_day.json                                  >> ${table_file_LPJGday}
  grep -A 17 -e '"tran":'  CMIP6_Eday.json                                 >> ${table_file_LPJGday}
  grep -A 16 -e '"tsl":'   CMIP6_Eday.json                                 >> ${table_file_LPJGday}

  # Add closing part of CMIP6 table json file:
  echo '        }                                      ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '    }                                          ' | sed 's/\s*$//g' >> ${table_file_LPJGday}
  echo '}                                              ' | sed 's/\s*$//g' >> ${table_file_LPJGday}


  # Add CMIP6 LPJGmon table header:
  echo '{                                              ' | sed 's/\s*$//g' >  ${table_file_LPJGmon}
  echo '    "Header": {                                ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '        "data_specs_version": "01.00.33",      ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '        "cmor_version": "3.5",                 ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '        "table_id": "Table LPJGmon",           ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '        "realm": "land",                       ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '        "table_date": "18 November 2020",      ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '        "missing_value": "1e20",               ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '        "int_missing_value": "-999",           ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '        "product": "model-output",             ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '        "approx_interval": "30.00000",         ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '        "generic_levels": "",                  ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '        "mip_era": "CMIP6",                    ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '        "Conventions": "CF-1.7 CMIP-6.2"       ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '    },                                         ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '    "variable_entry": {                        ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}

  grep -A 17 -e '"evspsbl":'    CMIP6_Amon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"evspsblpot":' CMIP6_Emon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"evspsblsoi":' CMIP6_Lmon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"fco2nat":'    CMIP6_Amon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"mrroLut":'    CMIP6_Emon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"mrsll":'      CMIP6_Emon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"mrsol":'      CMIP6_Emon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"mrsoLut":'    CMIP6_Emon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"mrsosLut":'   CMIP6_Emon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"mrro":'       CMIP6_Lmon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"mrros":'      CMIP6_Lmon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"mrso":'       CMIP6_Lmon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"mrfso":'      CMIP6_Lmon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"mrsos":'      CMIP6_Lmon.json                            >> ${table_file_LPJGmon}
  grep -A 17 -e '"snc":'        CMIP6_LImon.json                           >> ${table_file_LPJGmon}
  grep -A 17 -e '"snd":'        CMIP6_LImon.json                           >> ${table_file_LPJGmon}
  grep -A 17 -e '"snw":'        CMIP6_LImon.json                           >> ${table_file_LPJGmon}
  grep -A 17 -e '"tran":'       CMIP6_Lmon.json                            >> ${table_file_LPJGmon}
  grep -A 16 -e '"tsl":'        CMIP6_Lmon.json                            >> ${table_file_LPJGmon}

  # Add closing part of CMIP6 table json file:
  echo '        }                                      ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '    }                                          ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}
  echo '}                                              ' | sed 's/\s*$//g' >> ${table_file_LPJGmon}

  # Add CMIP6 LPJGyr table header:
  echo '{                                              ' | sed 's/\s*$//g' >  ${table_file_LPJGyr}
  echo '    "Header": {                                ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '        "data_specs_version": "01.00.33",      ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '        "cmor_version": "3.5",                 ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '        "table_id": "Table LPJGyr",            ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '        "realm": "land",                       ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '        "table_date": "18 November 2020",      ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '        "missing_value": "1e20",               ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '        "int_missing_value": "-999",           ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '        "product": "model-output",             ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '        "approx_interval": "365",              ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '        "generic_levels": "",                  ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '        "mip_era": "CMIP6",                    ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '        "Conventions": "CF-1.7 CMIP-6.2"       ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '    },                                         ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '    "variable_entry": {                        ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}

  grep -A 16 -e '"pastureFrac":' CMIP6_Lmon.json                           >> ${table_file_LPJGyr}
  sed -i -e 's/mon/yr/'                                                       ${table_file_LPJGyr}

  # Add closing part of CMIP6 table json file:
  echo '        }                                      ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '    }                                          ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}
  echo '}                                              ' | sed 's/\s*$//g' >> ${table_file_LPJGyr}


  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_Eyr}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_Emon}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_LPJGday}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_LPJGmon}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_LPJGyr}
  sed -i -e 's/\s*$//g'                ${table_file_cv}

  cd -

  echo
  echo " $0 reports:"
  echo "  The adjusted files are:"
  echo "   ${table_path}/${table_file_Eyr}"
  echo "   ${table_path}/${table_file_Emon}"
  echo "  Added files are:"
  echo "   ${table_path}/${table_file_LPJGday}"
  echo "   ${table_path}/${table_file_LPJGmon}"
  echo "   ${table_path}/${table_file_LPJGyr}"
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
