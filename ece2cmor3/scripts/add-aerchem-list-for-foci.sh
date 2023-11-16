#!/bin/bash
# Thomas Reerink
#
# This script adds / inserts 77 extra non-cmor TM5 AERchem variables for downscaling within the FOCI project.
#
# This scripts requires no arguments.
#

if [ "$#" -eq 0 ]; then

 add_aerchem_foci_variables=True

 if [ add_aerchem_foci_variables ]; then
  # See #775  https://github.com/EC-Earth/ece2cmor3/issues/775


  # Add 77 TM5 AERchem variables for downscaling within the FOCI project.

  table_path=../resources/cmip6-cmor-tables/Tables/
  table_file_6hrPlevPt=CMIP6_6hrPlevPt.json
  table_file_cv=CMIP6_CV.json
  table_file_AER6hrPt=CMIP6_AER6hrPt.json

  cd ${table_path}
  rm -f ${table_file_AER6hrPt}
  git checkout ${table_file_6hrPlevPt}
  git checkout ${table_file_cv}

  # Add tsl4sl (tsl) on 6hrPlevPt table:
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

  sed -i  '/"AERhr"/i \
            "AER6hrPt",                                                                         
  ' ${table_file_cv}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_6hrPlevPt}
  sed -i -e 's/\s*$//g' ${table_file_cv}


  # Add CMIP6 AER6hrPt table header:
  echo '{                                              ' | sed 's/\s*$//g' >  ${table_file_AER6hrPt}
  echo '    "Header": {                                ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "data_specs_version": "01.00.33",      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "cmor_version": "3.5",                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "table_id": "Table AER6hrPt",          ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "realm": "aerosol",                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "table_date": "18 November 2020",      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "missing_value": "1e20",               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "int_missing_value": "-999",           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "product": "model-output",             ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "approx_interval": "30.00000",         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "generic_levels": "alevel olevel",     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "mip_era": "CMIP6",                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "Conventions": "CF-1.7 CMIP-6.2"       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '    },                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '    "variable_entry": {                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}

  # Add the block of concentration (conc) 6hrPt variables for the AER6hrPt CMIP6 table:
  for i in $(seq 7); do
   echo '        "conccn_'${i}'": {                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "frequency": "6hrPt",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "modeling_realm": "aerosol",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "standard_name": "number_concentration_of_ambient_aerosol_particles_in_air_mode_'${i}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "units": "m-3",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "cell_methods": "area: mean time: point",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "cell_measures": "area: areacella",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "long_name": "Aerosol Number Concentration for mode '${i}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "comment": "'Number concentration' means the number of particles or other specified objects per unit volume. 'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. 'Ambient_aerosol' means that the aerosol is measured or modelled at the ambient state of pressure, temperature and relative humidity that exists in its immediate environment. 'Ambient aerosol particles' are aerosol particles that have taken up ambient water through hygroscopic growth. The extent of hygroscopic growth depends on the relative humidity and the composition of the particles.", ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "dimensions": "longitude latitude alevel time",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "out_name": "conccn_'${i}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "type": "real",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "positive": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "valid_min": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "valid_max": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "ok_min_mean_abs": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "ok_max_mean_abs": ""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '        },                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  done

  # Add the block of mass mixing ratio (mmr) 6hrPt variables for the AER6hrPt CMIP6 table:
  # A one liner to generate script code block below:
  #  for i in {1..29}; do echo "   if [ \"\${i}\" -eq ${i} ]; then varname='conccn_1'; standardname=''; longname=''; fi"; done
  for i in $(seq 7); do
   if [ "${i}" -eq  1 ]; then varname='mmraerh2o_1'; standardname=''; longname=''; fi
   if [ "${i}" -eq  2 ]; then varname='mmraerh2o_2'; standardname=''; longname=''; fi
   if [ "${i}" -eq  3 ]; then varname='mmraerh2o_3'; standardname=''; longname=''; fi
   if [ "${i}" -eq  4 ]; then varname='mmraerh2o_4'; standardname=''; longname=''; fi
   if [ "${i}" -eq  5 ]; then varname='mmrbc_2    '; standardname=''; longname=''; fi
   if [ "${i}" -eq  6 ]; then varname='mmrbc_3    '; standardname=''; longname=''; fi
   if [ "${i}" -eq  7 ]; then varname='mmrbc_4    '; standardname=''; longname=''; fi
   if [ "${i}" -eq  8 ]; then varname='mmrbc_5    '; standardname=''; longname=''; fi
   if [ "${i}" -eq  9 ]; then varname='mmrdust_3  '; standardname=''; longname=''; fi
   if [ "${i}" -eq 10 ]; then varname='mmrdust_4  '; standardname=''; longname=''; fi
   if [ "${i}" -eq 11 ]; then varname='mmrdust_6  '; standardname=''; longname=''; fi
   if [ "${i}" -eq 12 ]; then varname='mmrdust_7  '; standardname=''; longname=''; fi
   if [ "${i}" -eq 13 ]; then varname='mmrnh4     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 14 ]; then varname='mmrno3     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 15 ]; then varname='mmroa_2    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 16 ]; then varname='mmroa_3    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 17 ]; then varname='mmroa_4    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 18 ]; then varname='mmroa_5    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 19 ]; then varname='mmrso4_1   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 20 ]; then varname='mmrso4_2   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 21 ]; then varname='mmrso4_3   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 22 ]; then varname='mmrso4_4   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 23 ]; then varname='mmrsoa_1   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 24 ]; then varname='mmrsoa_2   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 25 ]; then varname='mmrsoa_3   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 26 ]; then varname='mmrsoa_4   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 27 ]; then varname='mmrsoa_5   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 28 ]; then varname='mmrss_3    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 29 ]; then varname='mmrss_4    '; standardname=''; longname=''; fi
   varname=$(echo -e "${varname}" | tr -d '[:space:]')
   echo '        "'${varname}'": {                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "frequency": "6hrPt",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "modeling_realm": "aerosol",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  #echo '            "standard_name": "mass_fraction_of_'${standard}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "standard_name": "mass_fraction_of_'${varname}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "units": "kg kg-1",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "cell_methods": "area: mean time: point",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "cell_measures": "area: areacella",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "long_name": "'${longname}' Aerosol Mass Mixing Ratio",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "comment": "Mass fraction in the atmosphere (dry mass). 'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. 'Ambient_aerosol' means that the aerosol is measured or modelled at the ambient state of pressure, temperature and relative humidity that exists in its immediate environment. 'Ambient aerosol particles' are aerosol particles that have taken up ambient water through hygroscopic growth. The extent of hygroscopic growth depends on the relative humidity and the composition of the particles.", ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "dimensions": "longitude latitude alevel time",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "out_name": "'${varname}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "type": "real",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "positive": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "valid_min": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "valid_max": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "ok_min_mean_abs": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "ok_max_mean_abs": ""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '        },                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  done

  # Add the block of volume mixing ratio (vmr) 6hrPt variables for the AER6hrPt CMIP6 table:
  # A one liner to generate script code block below:
  #  for i in {1..40}; do echo "   if [ \"\${i}\" -eq ${i} ]; then varname='conccn_1'; standardname=''; longname=''; fi"; done
  for i in $(seq 7); do
   if [ "${i}" -eq  1 ]; then varname='ald2    '; standardname=''; longname=''; fi
   if [ "${i}" -eq  2 ]; then varname='c2h4    '; standardname=''; longname=''; fi
   if [ "${i}" -eq  3 ]; then varname='c2h5oh  '; standardname=''; longname=''; fi
   if [ "${i}" -eq  4 ]; then varname='c2h6    '; standardname=''; longname=''; fi
   if [ "${i}" -eq  5 ]; then varname='c3h6    '; standardname=''; longname=''; fi
   if [ "${i}" -eq  6 ]; then varname='c3h8    '; standardname=''; longname=''; fi
   if [ "${i}" -eq  7 ]; then varname='ch3coch3'; standardname=''; longname=''; fi
   if [ "${i}" -eq  8 ]; then varname='ch3cocho'; standardname=''; longname=''; fi
   if [ "${i}" -eq  9 ]; then varname='ch3o2h  '; standardname=''; longname=''; fi
   if [ "${i}" -eq 10 ]; then varname='ch3o2no2'; standardname=''; longname=''; fi
   if [ "${i}" -eq 11 ]; then varname='ch3oh   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 12 ]; then varname='ch4     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 13 ]; then varname='co      '; standardname=''; longname=''; fi
   if [ "${i}" -eq 14 ]; then varname='dms     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 15 ]; then varname='h2o2    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 16 ]; then varname='h2so4   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 17 ]; then varname='hcho    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 18 ]; then varname='hcooh   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 19 ]; then varname='hno3    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 20 ]; then varname='hno4    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 21 ]; then varname='ho2     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 22 ]; then varname='hono    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 23 ]; then varname='isop    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 24 ]; then varname='ispd    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 25 ]; then varname='mcooh   '; standardname=''; longname=''; fi
   if [ "${i}" -eq 26 ]; then varname='msa     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 27 ]; then varname='n2o5    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 28 ]; then varname='nh3     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 29 ]; then varname='no2     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 30 ]; then varname='no3     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 31 ]; then varname='no      '; standardname=''; longname=''; fi
   if [ "${i}" -eq 32 ]; then varname='o3      '; standardname=''; longname=''; fi
   if [ "${i}" -eq 33 ]; then varname='oh      '; standardname=''; longname=''; fi
   if [ "${i}" -eq 34 ]; then varname='ole     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 35 ]; then varname='orgntr  '; standardname=''; longname=''; fi
   if [ "${i}" -eq 36 ]; then varname='pan     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 37 ]; then varname='par     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 38 ]; then varname='rooh    '; standardname=''; longname=''; fi
   if [ "${i}" -eq 39 ]; then varname='so2     '; standardname=''; longname=''; fi
   if [ "${i}" -eq 40 ]; then varname='terp    '; standardname=''; longname=''; fi
   varname=$(echo -e "${varname}" | tr -d '[:space:]')
   echo '        "'${varname}'": {                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "frequency": "6hrPt",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "modeling_realm": "aerosol",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  #echo '            "standard_name": "mole_fraction_of_'${standard}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "standard_name": "mole_fraction_of_'${varname}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "units": "mol mol-1",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "cell_methods": "area: mean time: point",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "cell_measures": "area: areacella",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "long_name": "Mole Fraction of '${longname}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "comment": "Mole fraction is used in the construction mole_fraction_of_X_in_Y, where X is a material constituent of Y. 'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. 'Ambient_aerosol' means that the aerosol is measured or modelled at the ambient state of pressure, temperature and relative humidity that exists in its immediate environment. 'Ambient aerosol particles' are aerosol particles that have taken up ambient water through hygroscopic growth. The extent of hygroscopic growth depends on the relative humidity and the composition of the particles.", ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "dimensions": "longitude latitude alevel time",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "out_name": "'${varname}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "type": "real",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "positive": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "valid_min": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "valid_max": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "ok_min_mean_abs": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "ok_max_mean_abs": ""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '        },                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  done

  # Add surface air pressure (ps) 6hrPt variables for the AER6hrPt CMIP6 table:
  echo '        "ps": {                                                                                                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "frequency": "6hrPt",                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "modeling_realm": "atmos",                                                                                                          ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "standard_name": "surface_air_pressure",                                                                                            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "units": "Pa",                                                                                                                      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "cell_methods": "area: mean time: point",                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "cell_measures": "area: areacella",                                                                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "long_name": "Surface Air Pressure",                                                                                                ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "comment": "surface pressure (not mean sea-level pressure), 2-D field to calculate the 3-D pressure field from hybrid coordinates", ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "dimensions": "longitude latitude time1",                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "out_name": "ps",                                                                                                                   ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "type": "real",                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "positive": "",                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "valid_min": "",                                                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "valid_max": "",                                                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "ok_min_mean_abs": "",                                                                                                              ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "ok_max_mean_abs": ""                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        },                                                                                                                                      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}

  # Add closing part of CMIP6 table json file:
  echo '    }                                                                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '}                                                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}

  cd -

  echo
  echo " $0 reports:"
  echo "  The adjusted files are:"
  echo "   ${table_path}/${table_file_6hrPlevPt}"
  echo "   ${table_path}/${table_file_cv}"
  echo "  One added file is:"
  echo "   ${table_path}/${table_file_AER6hrPt}"
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


 # ls /ec/res4/scratch/nks/ecearth3/fot2/output/tm5/001/*downscaling* | sed -e 's/.*001.//' -e 's/downscaling_//' -e 's/_EC-Earth3.*//' -e 's/_AER6hr//'
 # Sligtly reordered version of this ls:

 # conccn_1
 # conccn_2
 # conccn_3
 # conccn_4
 # conccn_5
 # conccn_6
 # conccn_7

 # mmraerh2o_1
 # mmraerh2o_2
 # mmraerh2o_3
 # mmraerh2o_4
 # mmrbc_2
 # mmrbc_3
 # mmrbc_4
 # mmrbc_5
 # mmrdust_3
 # mmrdust_4
 # mmrdust_6
 # mmrdust_7
 # mmrnh4
 # mmrno3
 # mmroa_2
 # mmroa_3
 # mmroa_4
 # mmroa_5
 # mmrso4_1
 # mmrso4_2
 # mmrso4_3
 # mmrso4_4
 # mmrsoa_1
 # mmrsoa_2
 # mmrsoa_3
 # mmrsoa_4
 # mmrsoa_5
 # mmrss_3
 # mmrss_4

 # ald2
 # c2h4
 # c2h5oh
 # c2h6
 # c3h6
 # c3h8
 # ch3coch3
 # ch3cocho
 # ch3o2h
 # ch3o2no2
 # ch3oh
 # ch4
 # co
 # dms
 # h2o2
 # h2so4
 # hcho
 # hcooh
 # hno3
 # hno4
 # ho2
 # hono
 # isop
 # ispd
 # mcooh
 # msa
 # n2o5
 # nh3
 # no2
 # no3
 # no
 # o3
 # oh
 # ole
 # orgntr
 # pan
 # par
 # rooh
 # so2
 # terp

 # ps
