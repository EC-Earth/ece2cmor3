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
  # See #830  https://github.com/EC-Earth/ece2cmor3/issues/830


  # Add 77 TM5 AERchem variables for downscaling within the FOCI project.

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_cv=CMIP6_CV.json
  table_file_3hr=CMIP6_3hr.json
  table_file_6hrLev=CMIP6_6hrLev.json
  table_file_6hrPlevPt=CMIP6_6hrPlevPt.json
  table_file_6hrPlev=CMIP6_6hrPlev.json
  table_file_AER6hrPt=CMIP6_AER6hrPt.json
  table_file_aermon=CMIP6_AERmon.json

  cd ${table_path}
  rm -f ${table_file_AER6hrPt}
  git checkout ${table_file_cv}
  git checkout ${table_file_3hr}
  git checkout ${table_file_6hrLev}
  git checkout ${table_file_6hrPlevPt}
  git checkout ${table_file_6hrPlev}
  git checkout ${table_file_aermon}


  sed -i  '/"tslsi": {/i \
        "tosa": {                                                                                                                           \
            "frequency": "3hr",                                                                                                             \
            "modeling_realm": "ocean",                                                                                                      \
            "standard_name": "sea_surface_temperature",                                                                                     \
            "units": "degC",                                                                                                                \
            "cell_methods": "area: mean where sea time: point",                                                                             \
            "cell_measures": "area: areacella",                                                                                             \
            "long_name": "Sea Surface Temperature",                                                                                         \
            "comment": "Temperature of upper boundary of the liquid ocean, including temperatures below sea-ice and floating ice shelves.", \
            "dimensions": "longitude latitude time1",                                                                                       \
            "out_name": "tosa",                                                                                                             \
            "type": "real",                                                                                                                 \
            "positive": "",                                                                                                                 \
            "valid_min": "",                                                                                                                \
            "valid_max": "",                                                                                                                \
            "ok_min_mean_abs": "",                                                                                                          \
            "ok_max_mean_abs": ""                                                                                                           \
        },                                                                                                                                  
  ' ${table_file_3hr}

  sed -i  '/"va": {/i \
        "zg": {                                                                                                                                                                                                                                                                                                                                                                                                         \
            "frequency": "6hrPt",                                                                                                                                                                                                                                                                                                                                                                                       \
            "modeling_realm": "atmos",                                                                                                                                                                                                                                                                                                                                                                                  \
            "standard_name": "geopotential_height",                                                                                                                                                                                                                                                                                                                                                                     \
            "units": "m",                                                                                                                                                                                                                                                                                                                                                                                               \
            "cell_methods": "time: mean",                                                                                                                                                                                                                                                                                                                                                                               \
            "cell_measures": "area: areacella",                                                                                                                                                                                                                                                                                                                                                                         \
            "long_name": "Geopotential Height",                                                                                                                                                                                                                                                                                                                                                                         \
            "comment": "Geopotential is the sum of the specific gravitational potential energy relative to the geoid and the specific centripetal potential energy. Geopotential height is the geopotential divided by the standard acceleration due to gravity. It is numerically similar to the altitude (or geometric height) and not to the quantity with standard name height, which is relative to the surface.", \
            "dimensions": "longitude latitude alevel time1",                                                                                                                                                                                                                                                                                                                                                            \
            "out_name": "zg",                                                                                                                                                                                                                                                                                                                                                                                           \
            "type": "real",                                                                                                                                                                                                                                                                                                                                                                                             \
            "positive": "",                                                                                                                                                                                                                                                                                                                                                                                             \
            "valid_min": "",                                                                                                                                                                                                                                                                                                                                                                                            \
            "valid_max": "",                                                                                                                                                                                                                                                                                                                                                                                            \
            "ok_min_mean_abs": "",                                                                                                                                                                                                                                                                                                                                                                                      \
            "ok_max_mean_abs": ""                                                                                                                                                                                                                                                                                                                                                                                       \
        },
  ' ${table_file_6hrLev}

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
            "out_name": "tosa",                                                                                                             \
            "type": "real",                                                                                                                 \
            "positive": "",                                                                                                                 \
            "valid_min": "",                                                                                                                \
            "valid_max": "",                                                                                                                \
            "ok_min_mean_abs": "",                                                                                                          \
            "ok_max_mean_abs": ""                                                                                                           \
        },                                                                                                                                  
  ' ${table_file_6hrPlevPt}

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

  # Add siconca on 6hrPlev table:
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

  # rsscsaf  126070  CVEXTR2(11)='clear SW surf', grib 126.70 clear SW surf rsscsaf (r: radiation, s: short wave, s:surface, cs: clear sky, af: aerosol free)
  # rssaf    126071  CVEXTR2(12)='total SW surf', grib 126.71 total SW surf rssaf
  # rlscsaf  126074  CVEXTR2(15)='clear LW surf', grib 126.74 clear LW surf rlscsaf
  # rlsaf    126075  CVEXTR2(16)='total LW surf', grib 126.75 total LW surf rlsaf
  sed -i  '/"so2": {/i \
        "rsscsaf": {                                                                                                            \
            "frequency": "mon",                                                                                                 \
            "modeling_realm": "aerosol",                                                                                        \
            "standard_name": "surface_net_shortwave_flux_aerosol_free_clear_sky",                                               \
            "units": "W m-2",                                                                                                   \
            "cell_methods": "area: time: mean",                                                                                 \
            "cell_measures": "area: areacella",                                                                                 \
            "long_name": "Surface Net Aerosol-Free Clear-Sky Shortwave Radiation",                                              \
            "comment": "Flux corresponding to rls resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)",   \
            "dimensions": "longitude latitude time",                                                                            \
            "out_name": "rsscsaf",                                                                                              \
            "type": "real",                                                                                                     \
            "positive": "down",                                                                                                 \
            "valid_min": "",                                                                                                    \
            "valid_max": "",                                                                                                    \
            "ok_min_mean_abs": "",                                                                                              \
            "ok_max_mean_abs": ""                                                                                               \
        },                                                                                                                      \
        "rssaf": {                                                                                                              \
            "frequency": "mon",                                                                                                 \
            "modeling_realm": "aerosol",                                                                                        \
            "standard_name": "surface_net_shortwave_flux_aerosol_free",                                                         \
            "units": "W m-2",                                                                                                   \
            "cell_methods": "area: time: mean",                                                                                 \
            "cell_measures": "area: areacella",                                                                                 \
            "long_name": "Surface Net Aerosol-Free Shortwave Radiation",                                                        \
            "comment": "Flux corresponding to rls resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)",   \
            "dimensions": "longitude latitude time",                                                                            \
            "out_name": "rssaf",                                                                                                \
            "type": "real",                                                                                                     \
            "positive": "down",                                                                                                 \
            "valid_min": "",                                                                                                    \
            "valid_max": "",                                                                                                    \
            "ok_min_mean_abs": "",                                                                                              \
            "ok_max_mean_abs": ""                                                                                               \
        },                                                                                                                      \
        "rlscsaf": {                                                                                                            \
            "frequency": "mon",                                                                                                 \
            "modeling_realm": "aerosol",                                                                                        \
            "standard_name": "surface_net_longwave_flux_aerosol_free_clear_sky",                                                \
            "units": "W m-2",                                                                                                   \
            "cell_methods": "area: time: mean",                                                                                 \
            "cell_measures": "area: areacella",                                                                                 \
            "long_name": "Surface Net Aerosol-Free Clear-Sky Longwave Radiation",                                               \
            "comment": "Flux corresponding to rls resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)",   \
            "dimensions": "longitude latitude time",                                                                            \
            "out_name": "rlscsaf",                                                                                              \
            "type": "real",                                                                                                     \
            "positive": "down",                                                                                                 \
            "valid_min": "",                                                                                                    \
            "valid_max": "",                                                                                                    \
            "ok_min_mean_abs": "",                                                                                              \
            "ok_max_mean_abs": ""                                                                                               \
        },                                                                                                                      \
        "rlsaf": {                                                                                                              \
            "frequency": "mon",                                                                                                 \
            "modeling_realm": "aerosol",                                                                                        \
            "standard_name": "surface_net_longwave_flux_aerosol_free",                                                          \
            "units": "W m-2",                                                                                                   \
            "cell_methods": "area: time: mean",                                                                                 \
            "cell_measures": "area: areacella",                                                                                 \
            "long_name": "Surface Net Aerosol-Free Longwave Radiation",                                                         \
            "comment": "Flux corresponding to rls resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)",   \
            "dimensions": "longitude latitude time",                                                                            \
            "out_name": "rlsaf",                                                                                                \
            "type": "real",                                                                                                     \
            "positive": "down",                                                                                                 \
            "valid_min": "",                                                                                                    \
            "valid_max": "",                                                                                                    \
            "ok_min_mean_abs": "",                                                                                              \
            "ok_max_mean_abs": ""                                                                                               \
        },
  ' ${table_file_aermon}

  sed -i  '/"AERhr"/i \
            "AER6hrPt",
  ' ${table_file_cv}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g'                ${table_file_cv}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_3hr}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_6hrLev}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_6hrPlevPt}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_6hrPlev}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_aermon}


  # Add CMIP6 AER6hrPt table header:
  echo '{                                              ' | sed 's/\s*$//g' >  ${table_file_AER6hrPt}
  echo '    "Header": {                                ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "data_specs_version": "01.00.33",      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "cmor_version": "3.5",                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "table_id": "Table AER6hrPt",          ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "realm": "aerosol atmosChem",          ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "table_date": "18 November 2020",      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "missing_value": "1e20",               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "int_missing_value": "-999",           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "product": "model-output",             ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "approx_interval": "30.00000",         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "generic_levels": "alevel",            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "mip_era": "CMIP6",                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        "Conventions": "CF-1.7 CMIP-6.2"       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '    },                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '    "variable_entry": {                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}

  # Add the block of concentration (conc) 6hrPt variables for the AER6hrPt CMIP6 table:
  for i in $(seq 7); do
   echo '        "conccnmode0'${i}'": {                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "frequency": "6hrPt",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "modeling_realm": "aerosol",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "standard_name": "number_concentration_of_ambient_aerosol_particles_in_air_for_mode_'${i}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "units": "m-3",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "cell_methods": "area: mean time: point",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "cell_measures": "area: areacella",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "long_name": "Aerosol Number Concentration for Mode '${i}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "comment": "'Number concentration' means the number of particles or other specified objects per unit volume. 'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. 'Ambient_aerosol' means that the aerosol is measured or modelled at the ambient state of pressure, temperature and relative humidity that exists in its immediate environment. 'Ambient aerosol particles' are aerosol particles that have taken up ambient water through hygroscopic growth. The extent of hygroscopic growth depends on the relative humidity and the composition of the particles. 'Mode' refers to the mode of the M7 aerosol scheme (Vignati et al., 2004).", ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "dimensions": "longitude latitude alevel time1",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "out_name": "conccnmode0'${i}'",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "type": "real",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "positive": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "valid_min": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "valid_max": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "ok_min_mean_abs": "",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "ok_max_mean_abs": ""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '        },                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  done

  # Add the block of mass mixing ratio (mmr) 6hrPt variables for the AER6hrPt CMIP6 table:
  # A one liner to generate script code block below:
  #  for i in {1..29}; do echo "   if [ \"\${i}\" -eq ${i} ]; then varname='conccnmode01'; standardname=''; longname=''; fi"; done
  for i in $(seq 29); do
   if [ "${i}" -eq  1 ]; then varname='mmraerh2omode01'; standardname='water_in_ambient_aerosol                           '; longname='Aerosol Water               '; fi
   if [ "${i}" -eq  2 ]; then varname='mmraerh2omode02'; standardname='water_in_ambient_aerosol                           '; longname='Aerosol Water               '; fi
   if [ "${i}" -eq  3 ]; then varname='mmraerh2omode03'; standardname='water_in_ambient_aerosol                           '; longname='Aerosol Water               '; fi
   if [ "${i}" -eq  4 ]; then varname='mmraerh2omode04'; standardname='water_in_ambient_aerosol                           '; longname='Aerosol Water               '; fi
   if [ "${i}" -eq  5 ]; then varname='mmrbcmode02    '; standardname='elemental_carbon_dry_aerosol                       '; longname='Elemental Carbon            '; fi
   if [ "${i}" -eq  6 ]; then varname='mmrbcmode03    '; standardname='elemental_carbon_dry_aerosol                       '; longname='Elemental Carbon            '; fi
   if [ "${i}" -eq  7 ]; then varname='mmrbcmode04    '; standardname='elemental_carbon_dry_aerosol                       '; longname='Elemental Carbon            '; fi
   if [ "${i}" -eq  8 ]; then varname='mmrbcmode05    '; standardname='elemental_carbon_dry_aerosol                       '; longname='Elemental Carbon            '; fi
   if [ "${i}" -eq  9 ]; then varname='mmrdustmode03  '; standardname='dust_dry_aerosol                                   '; longname='Dust Aerosol                '; fi
   if [ "${i}" -eq 10 ]; then varname='mmrdustmode04  '; standardname='dust_dry_aerosol                                   '; longname='Dust Aerosol                '; fi
   if [ "${i}" -eq 11 ]; then varname='mmrdustmode06  '; standardname='dust_dry_aerosol                                   '; longname='Dust Aerosol                '; fi
   if [ "${i}" -eq 12 ]; then varname='mmrdustmode07  '; standardname='dust_dry_aerosol                                   '; longname='Dust Aerosol                '; fi
   if [ "${i}" -eq 13 ]; then varname='mmrnh4         '; standardname='ammonium_dry_aerosol                               '; longname='NH4                         '; fi
   if [ "${i}" -eq 14 ]; then varname='mmrno3         '; standardname='nitrate_dry_aerosol                                '; longname='NO3 Aerosol                 '; fi
   if [ "${i}" -eq 15 ]; then varname='mmroamode02    '; standardname='particulate_organic_matter_dry_aerosol             '; longname='Total Organic Aerosol       '; fi
   if [ "${i}" -eq 16 ]; then varname='mmroamode03    '; standardname='particulate_organic_matter_dry_aerosol             '; longname='Total Organic Aerosol       '; fi
   if [ "${i}" -eq 17 ]; then varname='mmroamode04    '; standardname='particulate_organic_matter_dry_aerosol             '; longname='Total Organic Aerosol       '; fi
   if [ "${i}" -eq 18 ]; then varname='mmroamode05    '; standardname='particulate_organic_matter_dry_aerosol             '; longname='Total Organic Aerosol       '; fi
   if [ "${i}" -eq 19 ]; then varname='mmrso4mode01   '; standardname='sulfate_dry_aerosol                                '; longname='Aerosol Sulfate             '; fi
   if [ "${i}" -eq 20 ]; then varname='mmrso4mode02   '; standardname='sulfate_dry_aerosol                                '; longname='Aerosol Sulfatei            '; fi
   if [ "${i}" -eq 21 ]; then varname='mmrso4mode03   '; standardname='sulfate_dry_aerosol                                '; longname='Aerosol Sulfatei            '; fi
   if [ "${i}" -eq 22 ]; then varname='mmrso4mode04   '; standardname='sulfate_dry_aerosol                                '; longname='Aerosol Sulfatei            '; fi
   if [ "${i}" -eq 23 ]; then varname='mmrsoamode01   '; standardname='secondary_particulate_organic_matter_dry_aerosol   '; longname='Secondary Organic Aerosol   '; fi
   if [ "${i}" -eq 24 ]; then varname='mmrsoamode02   '; standardname='secondary_particulate_organic_matter_dry_aerosol   '; longname='Secondary Organic Aerosol   '; fi
   if [ "${i}" -eq 25 ]; then varname='mmrsoamode03   '; standardname='secondary_particulate_organic_matter_dry_aerosol   '; longname='Secondary Organic Aerosol   '; fi
   if [ "${i}" -eq 26 ]; then varname='mmrsoamode04   '; standardname='secondary_particulate_organic_matter_dry_aerosol   '; longname='Secondary Organic Aerosol   '; fi
   if [ "${i}" -eq 27 ]; then varname='mmrsoamode05   '; standardname='secondary_particulate_organic_matter_dry_aerosol   '; longname='Secondary Organic Aerosol   '; fi
   if [ "${i}" -eq 28 ]; then varname='mmrssmode03    '; standardname='sea_salt_dry_aerosol                               '; longname='Sea-Salt Aerosol            '; fi
   if [ "${i}" -eq 29 ]; then varname='mmrssmode04    '; standardname='sea_salt_dry_aerosol                               '; longname='Sea-Salt Aerosol            '; fi

   if [ "${i}" -eq  1 ] || [ "${i}" -eq  2 ] || [ "${i}" -eq  3 ] || [ "${i}" -eq  4 ]; then
    shortcomment="'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. 'Ambient_aerosol' means that the aerosol is measured or modelled at the ambient state of pressure, temperature and relative humidity that exists in its immediate environment. 'Ambient aerosol particles' are aerosol particles that have taken up ambient water through hygroscopic growth. The extent of hygroscopic growth depends on the relative humidity and the composition of the particles."
   elif [ "${i}" -eq  5 ] || [ "${i}" -eq  6 ] || [ "${i}" -eq  7 ] || [ "${i}" -eq  8 ]; then
    shortcomment="'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. Aerosol takes up ambient water (a process known as hygroscopic growth) depending on the relative humidity and the composition of the aerosol. 'Dry aerosol particles' means aerosol particles without any water uptake. Chemically, 'elemental carbon' is the carbonaceous fraction of particulate matter that is thermally stable in an inert atmosphere to high temperatures near 4000K and can only be gasified by oxidation starting at temperatures above 340 C. It is assumed to be inert and non-volatile under atmospheric conditions and insoluble in any solvent (Ogren and Charlson, 1983)."
   elif [ "${i}" -eq  9 ] || [ "${i}" -eq 10 ] || [ "${i}" -eq 11 ] || [ "${i}" -eq 12 ]; then
    shortcomment="'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. Aerosol particles take up ambient water (a process known as hygroscopic growth) depending on the relative humidity and the composition of the particles. 'Dry aerosol particles' means aerosol particles without any water uptake."
   elif [ "${i}" -eq 13 ]; then
    shortcomment="'Mass_fraction_of_ammonium' means that the mass is expressed as mass of NH4. 'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. Aerosol particles take up ambient water (a process known as hygroscopic growth) depending on the relative humidity and the composition of the particles. 'Dry aerosol particles' means aerosol particles without any water uptake."
   elif [ "${i}" -eq 14 ]; then
    shortcomment="'Mass_fraction_of_nitrate' means that the mass is expressed as mass of NO3. 'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. Aerosol particles take up ambient water (a process known as hygroscopic growth) depending on the relative humidity and the composition of the particles. 'Dry aerosol particles' means aerosol particles without any water uptake."
   elif [ "${i}" -eq 15 ] || [ "${i}" -eq 16 ] || [ "${i}" -eq 17 ] || [ "${i}" -eq 18 ]; then
    shortcomment="'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. Aerosol takes up ambient water (a process known as hygroscopic growth) depending on the relative humidity and the composition of the aerosol. 'Dry aerosol particles' means aerosol particles without any water uptake. 'particulate_organic_matter_dry_aerosol' means all particulate organic matter dry aerosol except elemental carbon. It is the sum of primary_particulate_organic_matter_dry_aerosol and secondary_particulate_organic_matter_dry_aerosol."
   elif [ "${i}" -eq 19 ] || [ "${i}" -eq 20 ] || [ "${i}" -eq 21 ] || [ "${i}" -eq 22 ]; then
    shortcomment="'Mass_fraction_of_sulfate' means that the mass is expressed as mass of SO4. 'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. Aerosol particles take up ambient water (a process known as hygroscopic growth) depending on the relative humidity and the composition of the particles. 'Dry aerosol particles' means aerosol particles without any water uptake."
   elif [ "${i}" -eq 23 ] || [ "${i}" -eq 24 ] || [ "${i}" -eq 25 ] || [ "${i}" -eq 26 ] || [ "${i}" -eq 27 ]; then
    shortcomment="'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. Aerosol particles take up ambient water (a process known as hygroscopic growth) depending on the relative humidity and the composition of the particles. 'Dry aerosol particles' means aerosol particles without any water uptake. 'Secondary particulate organic matter' means particulate organic matter formed within the atmosphere from gaseous precursors. The sum of primary_particulate_organic_matter_dry_aerosol and secondary_particulate_organic_matter_dry_aerosol is particulate_organic_matter_dry_aerosol."
   elif [ "${i}" -eq 28 ] || [ "${i}" -eq 29 ]; then
    shortcomment="'Aerosol' means the system of suspended liquid or solid particles in air (except cloud droplets) and their carrier gas, the air itself. Aerosol particles take up ambient water (a process known as hygroscopic growth) depending on the relative humidity and the composition of the particles. 'Dry aerosol particles' means aerosol particles without any water uptake." 
   fi

   varname=$(echo -e "${varname}" | tr -d '[:space:]')
   standardname=$(echo -e "${standardname}" | tr -d '[:space:]')
   longname=$(echo -e "${longname}" | tr -d '[:space:]')
   index=${varname:0-1}
   echo '        "'${varname}'": {                                                                                                                                                                                                                                                                              ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "frequency": "6hrPt",                                                                                                                                                                                                                                                                      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "modeling_realm": "aerosol",                                                                                                                                                                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   if [ "${i}" -eq 13 ] || [ "${i}" -eq 14 ]; then
    echo '            "standard_name": "mass_fraction_of_'${standardname}'_particles_in_air",                                                                                                                                                                                                                   ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   else
    echo '            "standard_name": "mass_fraction_of_'${standardname}'_for_mode_'${index}'",                                                                                                                                                                                                                ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   fi
   echo '            "units": "kg kg-1",                                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "cell_methods": "area: mean time: point",                                                                                                                                                                                                                                                  ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "cell_measures": "area: areacella",                                                                                                                                                                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   if [ "${i}" -eq 13 ] || [ "${i}" -eq 14 ]; then
    echo '            "long_name": "'${longname}' Mass Mixing Ratio",                                                                                                                                                                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
    echo '            "comment": "Mass fraction is used in the construction mass_fraction_of_X_in_Y, where X is a material constituent of Y. It means the ratio of the mass of X to the mass of Y (including X). '${shortcomment}'",                                                                            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   else
    echo '            "long_name": "'${longname}' Mass Mixing Ratio for Mode '${index}'",                                                                                                                                                                                                                       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
    echo '            "comment": "Mass fraction is used in the construction mass_fraction_of_X_in_Y, where X is a material constituent of Y. It means the ratio of the mass of X to the mass of Y (including X). '${shortcomment}' 'Mode' refers to the mode of the M7 aerosol scheme (Vignati et al., 2004).", ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   fi
   echo '            "dimensions": "longitude latitude alevel time1",                                                                                                                                                                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "out_name": "'${varname}'",                                                                                                                                                                                                                                                                ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "type": "real",                                                                                                                                                                                                                                                                            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "positive": "",                                                                                                                                                                                                                                                                            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "valid_min": "",                                                                                                                                                                                                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "valid_max": "",                                                                                                                                                                                                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "ok_min_mean_abs": "",                                                                                                                                                                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "ok_max_mean_abs": ""                                                                                                                                                                                                                                                                      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '        },                                                                                                                                                                                                                                                                                             ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  done

  # Add the block of volume mixing ratio (vmr) 6hrPt variables for the AER6hrPt CMIP6 table:
  # A one liner to generate script code block below:
  #  for i in {1..40}; do echo "   if [ \"\${i}\" -eq ${i} ]; then varname='conccnmode01'; standardname=''; longname=''; fi"; done
  for i in $(seq 40); do
   if [ "${i}" -eq  1 ]; then varname='ald2    '; standardname='acetaldehyde_and_higher_aldehydes '; longname='ALD2                   '; fi
   if [ "${i}" -eq  2 ]; then varname='c2h4    '; standardname='ethene                            '; longname='C2H4                   '; fi
   if [ "${i}" -eq  3 ]; then varname='c2h5oh  '; standardname='ethanol                           '; longname='C2H5OH                 '; fi
   if [ "${i}" -eq  4 ]; then varname='c2h6    '; standardname='ethane                            '; longname='C2H6                   '; fi
   if [ "${i}" -eq  5 ]; then varname='c3h6    '; standardname='propene                           '; longname='C3H6                   '; fi
   if [ "${i}" -eq  6 ]; then varname='c3h8    '; standardname='propane                           '; longname='C3H8                   '; fi
   if [ "${i}" -eq  7 ]; then varname='ch3coch3'; standardname='acetone                           '; longname='CH3COCH3               '; fi
   if [ "${i}" -eq  8 ]; then varname='ch3cocho'; standardname='methyl_glyoxal                    '; longname='CH3COCHO               '; fi
   if [ "${i}" -eq  9 ]; then varname='ch3o2h  '; standardname='methyl_hydroperoxide              '; longname='CH3O2H                 '; fi
   if [ "${i}" -eq 10 ]; then varname='ch3o2no2'; standardname='methyl_peroxy_nitrate             '; longname='CH3O2NO2               '; fi
   if [ "${i}" -eq 11 ]; then varname='ch3oh   '; standardname='methanol                          '; longname='CH3OH                  '; fi
   if [ "${i}" -eq 12 ]; then varname='ch4     '; standardname='methane                           '; longname='CH4                    '; fi
   if [ "${i}" -eq 13 ]; then varname='co      '; standardname='carbon_monoxide                   '; longname='CO                     '; fi
   if [ "${i}" -eq 14 ]; then varname='dms     '; standardname='dimethyl_sulfide                  '; longname='Dimethyl Sulphide (DMS)'; fi
   if [ "${i}" -eq 15 ]; then varname='h2o2    '; standardname='hydrogen_peroxide                 '; longname='H2O2                   '; fi
   if [ "${i}" -eq 16 ]; then varname='h2so4   '; standardname='sulfuric_acid                     '; longname='H2SO4                  '; fi
   if [ "${i}" -eq 17 ]; then varname='hcho    '; standardname='formaldehyde                      '; longname='HCHO                   '; fi
   if [ "${i}" -eq 18 ]; then varname='hcooh   '; standardname='formic_acid                       '; longname='HCOOH                  '; fi
   if [ "${i}" -eq 19 ]; then varname='hno3    '; standardname='nitric_acid                       '; longname='HNO3                   '; fi
   if [ "${i}" -eq 20 ]; then varname='hno4    '; standardname='peroxynitric_acid                 '; longname='HNO4                   '; fi
   if [ "${i}" -eq 21 ]; then varname='ho2     '; standardname='hydroperoxy_radical               '; longname='HO2                    '; fi
   if [ "${i}" -eq 22 ]; then varname='hono    '; standardname='nitrous_acid                      '; longname='HONO                   '; fi
   if [ "${i}" -eq 23 ]; then varname='isop    '; standardname='isoprene                          '; longname='Isoprene               '; fi
   if [ "${i}" -eq 24 ]; then varname='ispd    '; standardname='isoprene_product                  '; longname='ISPD                   '; fi
   if [ "${i}" -eq 25 ]; then varname='mcooh   '; standardname='acetic_acid                       '; longname='CH3COOH                '; fi
   if [ "${i}" -eq 26 ]; then varname='msa     '; standardname='methanesulfonic_acid              '; longname='MSA                    '; fi
   if [ "${i}" -eq 27 ]; then varname='n2o5    '; standardname='dinitrogen_pentoxide              '; longname='N2O5                   '; fi
   if [ "${i}" -eq 28 ]; then varname='nh3     '; standardname='ammonia                           '; longname='NH3                    '; fi
   if [ "${i}" -eq 29 ]; then varname='no2     '; standardname='nitrogen_dioxide                  '; longname='NO2                    '; fi
   if [ "${i}" -eq 30 ]; then varname='no3     '; standardname='nitrate_radical                   '; longname='NO3                    '; fi
   if [ "${i}" -eq 31 ]; then varname='no      '; standardname='nitrogen_monoxide                 '; longname='NO                     '; fi
   if [ "${i}" -eq 32 ]; then varname='o3      '; standardname='ozone                             '; longname='O3                     '; fi
   if [ "${i}" -eq 33 ]; then varname='oh      '; standardname='hydroxyl_radical                  '; longname='OH                     '; fi
   if [ "${i}" -eq 34 ]; then varname='ole     '; standardname='olefinic_carbon_bonds             '; longname='OLE                    '; fi
   if [ "${i}" -eq 35 ]; then varname='orgntr  '; standardname='organic_nitrates                  '; longname='Organic Nitrates       '; fi
   if [ "${i}" -eq 36 ]; then varname='pan     '; standardname='peroxyacetyl_nitrate              '; longname='PAN                    '; fi
   if [ "${i}" -eq 37 ]; then varname='par     '; standardname='paraffinic_carbon_atoms           '; longname='PAR                    '; fi
   if [ "${i}" -eq 38 ]; then varname='rooh    '; standardname='higher_organic_peroxide           '; longname='ROOH                   '; fi
   if [ "${i}" -eq 39 ]; then varname='so2     '; standardname='sulfur_dioxide                    '; longname='SO2                    '; fi
   if [ "${i}" -eq 40 ]; then varname='terp    '; standardname='monoterpene                       '; longname='Monoterpene            '; fi
   varname=$(echo -e "${varname}" | tr -d '[:space:]')
   standardname=$(echo -e "${standardname}" | tr -d '[:space:]')
   longname=$(echo -e "${longname}" | tr -d '[:space:]')
   echo '        "'${varname}'": {                                                                                                                      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "frequency": "6hrPt",                                                                                                              ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "modeling_realm": "atmosChem",                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "standard_name": "mole_fraction_of_'${standardname}'_in_air",                                                                      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "units": "mol mol-1",                                                                                                              ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "cell_methods": "area: mean time: point",                                                                                          ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "cell_measures": "area: areacella",                                                                                                ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   if [ "${i}" -eq 14 ]; then
    echo '            "long_name": "'${longname}' Mole Fraction",                                                                                       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   elif  [ "${i}" -eq 12 ] || [ "${i}" -eq 32 ]; then
    echo '            "long_name": "Mole Fraction of '${longname}'",                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   else
     echo '           "long_name": "'${longname}' Volume Mixing Ratio",                                                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   fi
   echo '            "comment": "Mole fraction is used in the construction mole_fraction_of_X_in_Y, where X is a material constituent of Y. ",          ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "dimensions": "longitude latitude alevel time1",                                                                                   ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "out_name": "'${varname}'",                                                                                                        ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "type": "real",                                                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "positive": "",                                                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "valid_min": "",                                                                                                                   ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "valid_max": "",                                                                                                                   ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "ok_min_mean_abs": "",                                                                                                             ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '            "ok_max_mean_abs": ""                                                                                                              ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
   echo '        },                                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  done

  # Add 3D Specific Humidity (hus) 6hrPt variable for the AER6hrPt CMIP6 table:
  echo '        "hus": {                                                                                                                                ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "frequency": "6hrPt",                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "modeling_realm": "atmos",                                                                                                          ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "standard_name": "specific_humidity",                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "units": "1",                                                                                                                       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "cell_methods": "area: mean time: point",                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "cell_measures": "area: areacella",                                                                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "long_name": "Specific Humidity",                                                                                                   ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "comment": "Specific humidity is the mass fraction of water vapor in (moist) air.",                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "dimensions": "longitude latitude alevel time1",                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "out_name": "hus",                                                                                                                  ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "type": "real",                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "positive": "",                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "valid_min": "",                                                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "valid_max": "",                                                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "ok_min_mean_abs": "",                                                                                                              ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "ok_max_mean_abs": ""                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        },                                                                                                                                      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}

  # Add surface air pressure (ps) 6hrPt variable for the AER6hrPt CMIP6 table:
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

  # Add 3D Air Temperature (ta) 6hrPt variable for the AER6hrPt CMIP6 table:
  echo '        "ta": {                                                                                                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "frequency": "6hrPt",                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "modeling_realm": "atmos",                                                                                                          ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "standard_name": "air_temperature",                                                                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "units": "K",                                                                                                                       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "cell_methods": "area: mean time: point",                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "cell_measures": "area: areacella",                                                                                                 ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "long_name": "Air Temperature",                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "comment": "Air Temperature",                                                                                                       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "dimensions": "longitude latitude alevel time1",                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "out_name": "ta",                                                                                                                   ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "type": "real",                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "positive": "",                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "valid_min": "",                                                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "valid_max": "",                                                                                                                    ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "ok_min_mean_abs": "",                                                                                                              ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "ok_max_mean_abs": ""                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        },                                                                                                                                      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}

  # Add 3D Geopotential Height (zg) 6hrPt variable for the AER6hrPt CMIP6 table:
  echo '        "zg": {                                                                                                                                                                                                                                                                                                                                                                                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "frequency": "6hrPt",                                                                                                                                                                                                                                                                                                                                                                                       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "modeling_realm": "atmos",                                                                                                                                                                                                                                                                                                                                                                                  ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "standard_name": "geopotential_height",                                                                                                                                                                                                                                                                                                                                                                     ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "units": "m",                                                                                                                                                                                                                                                                                                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "cell_methods": "time: mean",                                                                                                                                                                                                                                                                                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "cell_measures": "area: areacella",                                                                                                                                                                                                                                                                                                                                                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "long_name": "Geopotential Height",                                                                                                                                                                                                                                                                                                                                                                         ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "comment": "Geopotential is the sum of the specific gravitational potential energy relative to the geoid and the specific centripetal potential energy. Geopotential height is the geopotential divided by the standard acceleration due to gravity. It is numerically similar to the altitude (or geometric height) and not to the quantity with standard name height, which is relative to the surface.", ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "dimensions": "longitude latitude alevel time1",                                                                                                                                                                                                                                                                                                                                                            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "out_name": "zg",                                                                                                                                                                                                                                                                                                                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "type": "real",                                                                                                                                                                                                                                                                                                                                                                                             ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "positive": "",                                                                                                                                                                                                                                                                                                                                                                                             ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "valid_min": "",                                                                                                                                                                                                                                                                                                                                                                                            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "valid_max": "",                                                                                                                                                                                                                                                                                                                                                                                            ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "ok_min_mean_abs": "",                                                                                                                                                                                                                                                                                                                                                                                      ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '            "ok_max_mean_abs": ""                                                                                                                                                                                                                                                                                                                                                                                       ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '        }                                                                                                                                                                                                                                                                                                                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}

  # Add closing part of CMIP6 table json file:
  echo '    }                                                                                                                                           ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}
  echo '}                                                                                                                                               ' | sed 's/\s*$//g' >> ${table_file_AER6hrPt}

  cd -

  echo
  echo " Running:"
  echo "  $0"
  echo " has adjusted the files:"
  echo "  ${table_path}/${table_file_cv}"
  echo "  ${table_path}/${table_file_3hr}"
  echo "  ${table_path}/${table_file_6hrLev}"
  echo "  ${table_path}/${table_file_6hrPlevPt}"
  echo "  ${table_path}/${table_file_6hrPlev}"
  echo "  ${table_path}/${table_file_aermon}"
  echo " and added the file:"
  echo "  ${table_path}/${table_file_AER6hrPt}"
  echo " which is part of the nested CMOR Table repository. View the diff by running:"
  echo "  cd ${table_path}; git diff; cd -"
  echo " This changes can be reverted by running:"
  echo "  ./revert-nested-cmor-table-branch.sh"
  echo


  # Create the foci-tm5par.json & foci-request.json files if desired (used at time of implementing this work).
  do_create_foci_tm5par_and_request_files=False

  if [ "$do_create_foci_tm5par_and_request_files" = "True" ]; then
   # Create a foci-tm5par.json file. The code below is following the code in the generate-tm5par.json.sh script.

   # Declare an array variable with all the nemo cmor variable names:
   declare -a arr=(
   "conccnmode01"
   "conccnmode02"
   "conccnmode03"
   "conccnmode04"
   "conccnmode05"
   "conccnmode06"
   "conccnmode07"
   "mmraerh2omode01"
   "mmraerh2omode02"
   "mmraerh2omode03"
   "mmraerh2omode04"
   "mmrbcmode02"
   "mmrbcmode03"
   "mmrbcmode04"
   "mmrbcmode05"
   "mmrdustmode03"
   "mmrdustmode04"
   "mmrdustmode06"
   "mmrdustmode07"
   "mmrnh4"
   "mmrno3"
   "mmroamode02"
   "mmroamode03"
   "mmroamode04"
   "mmroamode05"
   "mmrso4mode01"
   "mmrso4mode02"
   "mmrso4mode03"
   "mmrso4mode04"
   "mmrsoamode01"
   "mmrsoamode02"
   "mmrsoamode03"
   "mmrsoamode04"
   "mmrsoamode05"
   "mmrssmode03"
   "mmrssmode04"
   "ald2"
   "c2h4"
   "c2h5oh"
   "c2h6"
   "c3h6"
   "c3h8"
   "ch3coch3"
   "ch3cocho"
   "ch3o2h"
   "ch3o2no2"
   "ch3oh"
   "ch4"
   "co"
   "dms"
   "h2o2"
   "h2so4"
   "hcho"
   "hcooh"
   "hno3"
   "hno4"
   "ho2"
   "hono"
   "isop"
   "ispd"
   "mcooh"
   "msa"
   "n2o5"
   "nh3"
   "no2"
   "no3"
   "no"
   "o3"
   "oh"
   "ole"
   "orgntr"
   "pan"
   "par"
   "rooh"
   "so2"
   "terp"
   "hus"
   "ps"
   "ta"
   "zg"
   )

   output_file=foci-tm5par.json

   function add_item {
    echo '    {'                     >> ${output_file}
    echo '        "source": "'$1'",' >> ${output_file}
    echo '        "target": "'$1'"'  >> ${output_file}
    echo '    },'                    >> ${output_file}
   }

   function add_last_item {
    echo '    {'                     >> ${output_file}
    echo '        "source": "'$1'",' >> ${output_file}
    echo '        "target": "'$1'"'  >> ${output_file}
    echo '    }'                     >> ${output_file}
   }

   echo '['                         > ${output_file}

   # Loop through the array with all the TM5 cmor variable names:
   # (Note individual array elements can be accessed by using "${arr[0]}", "${arr[1]}")

   N=${#arr[@]} # array length
   last_item="${arr[N-1]}"
   for i in "${arr[@]}"
   do
      if [ "$i" == ${last_item} ]; then
       add_last_item "$i"
      else
       add_item "$i"
      fi
   done

   echo ']'                         >> ${output_file}

   echo ' The file ' ${output_file} ' is created.'
   echo


   # Create a foci-request.json file:
   request_file=foci-request.json

   function add_variable_item {
    echo '            "'$1'",' >> ${request_file}
   }

   function add_variable_last_item {
    echo '            "'$1'"' >> ${request_file}
   }

    echo '{'                      >  ${request_file}
   #echo '    "ifs": {},'         >> ${request_file}
    echo '    "ifs": {'           >> ${request_file}
    echo '        "6hrPlevPt": [' >> ${request_file}
    echo '            "tsl4sl"'   >> ${request_file}
    echo '        ]'              >> ${request_file}
    echo '    },'                 >> ${request_file}
    echo '    "lpjg": {},'        >> ${request_file}
    echo '    "nemo": {},'        >> ${request_file}
    echo '    "tm5": {'           >> ${request_file}
    echo '        "AER6hrPt": ['  >> ${request_file}

    N=${#arr[@]} # array length
    last_item="${arr[N-1]}"
    for i in "${arr[@]}"
    do
       if [ "$i" == ${last_item} ]; then
        add_variable_last_item "$i"
       else
        add_variable_item "$i"
       fi
    done

    echo '        ]'              >> ${request_file}
    echo '    }'                  >> ${request_file}
    echo '}'                      >> ${request_file}

   echo ' The file ' ${request_file} ' is created.'
   echo
  fi

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
