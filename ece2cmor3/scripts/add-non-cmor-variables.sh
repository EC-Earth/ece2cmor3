#!/bin/bash
# Thomas Reerink
#
# This script adds some non-cmor variables (which thus do not exit in
# the CMIP6 data request) to the AERmon cmor table.
#
# This script requires no arguments.
#
# Run example:
#  ./add-non-cmor-variables.sh
#

if [ "$#" -eq 0 ]; then

 add_the_clear_sky_aerosol_free_net_surface_radiation_fluxes=True

 if [ add_the_clear_sky_aerosol_free_net_surface_radiation_fluxes ]; then
  # See #575     https://github.com/EC-Earth/ece2cmor3/issues/575
  # See #403-56  https://dev.ec-earth.org/issues/403-56
  # See #732     https://dev.ec-earth.org/issues/732
  # See #736-7   https://dev.ec-earth.org/issues/736-7

  # rsscsaf  126070  CVEXTR2(11)='clear SW surf', grib 126.70 clear SW surf rsscsaf (r: radiation, s: short wave, s:surface, cs: clear sky, af: aerosol free)
  # rssaf    126071  CVEXTR2(12)='total SW surf', grib 126.71 total SW surf rssaf
  # rlscsaf  126074  CVEXTR2(15)='clear LW surf', grib 126.74 clear LW surf rlscsaf
  # rlsaf    126075  CVEXTR2(16)='total LW surf', grib 126.75 total LW surf rlsaf

  # Also add the AerChem related Ice Crystal variables (see https://dev.ec-earth.org/issues/1079)

  table_path=../resources/cmip6-cmor-tables/Tables/
  table_file_aermon=CMIP6_AERmon.json

  cd ${table_path}
  git checkout ${table_file_aermon}

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
        },                                                                                                                      \
        "icnc": { \
            "frequency": "mon",  \
            "modeling_realm": "aerosol",  \
            "standard_name": "number_concentration_of_cloud_ice_crystal_particles_in_air",  \
            "units": "m-3",  \
            "cell_methods": "area: time: mean",  \
            "cell_measures": "area: areacella",  \
            "long_name": "Ice Crystal Number Concentration",  \
            "comment": "Ice Crystal Number Concentration in ice clouds.",  \
            "dimensions": "longitude latitude alevel time",  \
            "out_name": "icnc",  \
            "type": "real",  \
            "positive": "",  \
            "valid_min": "",  \
            "valid_max": "",  \
            "ok_min_mean_abs": "",  \
            "ok_max_mean_abs": "" \
        },  \
        "icncsip": { \
            "frequency": "mon", \
            "modeling_realm": "aerosol", \
            "standard_name": "number_concentration_of_secondary_cloud_ice_crystal_particles_in_air", \
            "units": "m-3", \
            "cell_methods": "area: time: mean", \
            "cell_measures": "area: areacella", \
            "long_name": "Ice Crystal Number Concentration from secondary formation", \
            "comment": "Ice Crystal Number Concentration formed by secondary ice production processes.", \
            "dimensions": "longitude latitude alevel time", \
            "out_name": "icncsip", \
            "type": "real", \
            "positive": "", \
            "valid_min": "", \
            "valid_max": "", \
            "ok_min_mean_abs": "", \
            "ok_max_mean_abs": "" \
        }, \
        "icncullrichdn": { \
            "frequency": "mon", \
            "modeling_realm": "aerosol", \
            "standard_name": "number_concentration_of_cloud_ice_crystal_particles_in_air_from_ullrich_dn", \
            "units": "m-3", \
            "cell_methods": "area: time: mean", \
            "cell_measures": "area: areacella", \
            "long_name": "Ice Crystal Number Concentration from Ullrich et al. (2017) deposition nucleation of soot and dust parameterization", \
            "comment": "Ice Crystal Number Concentration formed from Ullrich et al. (2017) deposition nucleation of soot and dust parameterization.", \
            "dimensions": "longitude latitude alevel time", \
            "out_name": "icncullrichdn", \
            "type": "real", \
            "positive": "", \
            "valid_min": "", \
            "valid_max": "", \
            "ok_min_mean_abs": "", \
            "ok_max_mean_abs": "" \
        }, \
        "icncharrison": { \
            "frequency": "mon", \
            "modeling_realm": "aerosol", \
            "standard_name": "number_concentration_of_cloud_ice_crystal_particles_in_air_from_harrison", \
            "units": "m-3", \
            "cell_methods": "area: time: mean", \
            "cell_measures": "area: areacella", \
            "long_name": "Ice Crystal Number Concentration from Harrison et al. (2019) immersion freezing of K-feldspar and quartz parameterization", \
            "comment": "Ice Crystal Number Concentration formed from Harrison et al. (2019) immersion freezing of K-feldspar and quartz parameterization.", \
            "dimensions": "longitude latitude alevel time", \
            "out_name": "icncharrison", \
            "type": "real", \
            "positive": "", \
            "valid_min": "", \
            "valid_max": "", \
            "ok_min_mean_abs": "", \
            "ok_max_mean_abs": "" \
        }, \
        "icncwilson": { \
            "frequency": "mon", \
            "modeling_realm": "aerosol", \
            "standard_name": "number_concentration_of_cloud_ice_crystal_particles_in_air_from_wilson", \
            "units": "m-3", \
            "cell_methods": "area: time: mean", \
            "cell_measures": "area: areacella", \
            "long_name": "Ice Crystal Number Concentration from Wilson et al. (2015) immersion freezing of marine organic aerosols parameterization", \
            "comment": "Ice Crystal Number Concentration formed from Wilson et al. (2015) immersion freezing of marine organic aerosols parameterization.", \
            "dimensions": "longitude latitude alevel time", \
            "out_name": "icncwilson", \
            "type": "real", \
            "positive": "", \
            "valid_min": "", \
            "valid_max": "", \
            "ok_min_mean_abs": "", \
            "ok_max_mean_abs": "" \
        }, \
        "icncpip": { \
            "frequency": "mon", \
            "modeling_realm": "aerosol", \
            "standard_name": "number_concentration_of_primary_cloud_ice_crystal_particles_in_air", \
            "units": "m-3", \
            "cell_methods": "area: time: mean", \
            "cell_measures": "area: areacella", \
            "long_name": "Ice Crystal Number Concentration from primary formation", \
            "comment": "Ice Crystal Number Concentration formed as primary ice.", \
            "dimensions": "longitude latitude alevel time", \
            "out_name": "icncpip", \
            "type": "real", \
            "positive": "", \
            "valid_min": "", \
            "valid_max": "", \
            "ok_min_mean_abs": "", \
            "ok_max_mean_abs": ""  \
        },
  ' ${table_file_aermon}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_aermon}

  cd -

  echo
  echo " $0 reports:"
  echo "  The adjusted file is:  ${table_path}/${table_file_aermon}"
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
