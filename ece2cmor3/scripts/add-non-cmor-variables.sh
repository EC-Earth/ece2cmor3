#!/bin/bash
# Thomas Reerink
#
# This script adds some non-cmor variables (which thus do not exit in the CMIP6 data request) in the relevant cmor table.
#
# This scripts requires no arguments.
#
# Run example:
#  ./add-non-cmor-variables.sh
#

if [ "$#" -eq 0 ]; then

 add_the_clear_sky_aerosol_free_net_surface_radiation_fluxes=True

 if [ add_the_clear_sky_aerosol_free_net_surface_radiation_fluxes ]; then
  # See #403-56  https://dev.ec-earth.org/issues/403-56
  # See #732     https://dev.ec-earth.org/issues/732
  # See #736-7   https://dev.ec-earth.org/issues/736-7

  # rsscsaf  126070  CVEXTR2(11)='clear SW surf', grib 126.70 clear SW surf rsscsaf (r: radiation, s: short wave, s:surface, cs: clear sky, af: aerosol free)
  # rssaf    126071  CVEXTR2(12)='total SW surf', grib 126.71 total SW surf rssaf
  # rlscsaf  126074  CVEXTR2(15)='clear LW surf', grib 126.74 clear LW surf rlscsaf
  # rlsaf    126075  CVEXTR2(16)='total LW surf', grib 126.75 total LW surf rlsaf

  cd ../resources/cmip6-cmor-tables
  git checkout Tables/CMIP6_AERmon.json
  cd -

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
  ' ../resources/tables/CMIP6_AERmon.json

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ../resources/tables/CMIP6_AERmon.json

 else
    echo '  '
    echo '  Nothing done, no set of variables has been selected to add to the tables.'
    echo '  '
 fi

else
    echo '  '
    echo '  This scripts requires no argument:'
    echo '  ' $0
    echo '  '
fi
