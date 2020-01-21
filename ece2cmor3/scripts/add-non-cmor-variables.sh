#!/bin/bash
# Thomas Reerink
#
# This script adds some non-cmor variables (which thus do not exit in the CMIP6 data request) to the end of the cmor table in question.
#
# This scripts requires no arguments.
#
# Run example:
#  ./add-non-cmor-variables.sh
#

if [ "$#" -eq 0 ]; then

 add_the_clear_sky_aerosol_free_net_surface_radiation_fluxes=True             # See 732 & #736-7.
 

 if [ add_the_clear_sky_aerosol_free_net_surface_radiation_fluxes ]; then
  # See #732 & #736-7 and #403-56 about naming.
  # rsscsaf  126070  CVEXTR2(11)='clear SW surf', grib 126.70 clear SW surf rsscsaf (r: radiation, s: short wave, s:surface, cs: clear sky, af: aerosol free)
  # rssaf    126071  CVEXTR2(12)='total SW surf', grib 126.71 total SW surf rssaf
  # rlscsaf  126074  CVEXTR2(15)='clear LW surf', grib 126.74 clear LW surf rlscsaf
  # rlsaf    126075  CVEXTR2(16)='total LW surf', grib 126.75 total LW surf rlsaf

  head --lines=-3 ../resources/tables/CMIP6_AERmon.json                                                                                  >  extended-CMIP6_AERmon.json

  echo '        },                                                                                                                     ' >> extended-CMIP6_AERmon.json
  echo '        "rsscsaf": {                                                                                                           ' >> extended-CMIP6_AERmon.json
  echo '            "frequency": "mon",                                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "modeling_realm": "aerosol",                                                                                       ' >> extended-CMIP6_AERmon.json
  echo '            "standard_name": "surface_net_shortwave_flux_aerosol_free_clear_sky",                                              ' >> extended-CMIP6_AERmon.json
  echo '            "units": "W m-2",                                                                                                  ' >> extended-CMIP6_AERmon.json
  echo '            "cell_methods": "area: time: mean",                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "cell_measures": "area: areacella",                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "long_name": "Surface Net Aerosol-Free Clear-Sky Shortwave Radiation",                                             ' >> extended-CMIP6_AERmon.json
  echo '            "comment": "Flux corresponding to rls resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)",  ' >> extended-CMIP6_AERmon.json 
  echo '            "dimensions": "longitude latitude time",                                                                           ' >> extended-CMIP6_AERmon.json
  echo '            "out_name": "rsscsaf",                                                                                             ' >> extended-CMIP6_AERmon.json
  echo '            "type": "real",                                                                                                    ' >> extended-CMIP6_AERmon.json
  echo '            "positive": "down",                                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "valid_min": "",                                                                                                   ' >> extended-CMIP6_AERmon.json
  echo '            "valid_max": "",                                                                                                   ' >> extended-CMIP6_AERmon.json
  echo '            "ok_min_mean_abs": "",                                                                                             ' >> extended-CMIP6_AERmon.json
  echo '            "ok_max_mean_abs": ""                                                                                              ' >> extended-CMIP6_AERmon.json

  echo '        },                                                                                                                     ' >> extended-CMIP6_AERmon.json
  echo '        "rssaf": {                                                                                                             ' >> extended-CMIP6_AERmon.json
  echo '            "frequency": "mon",                                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "modeling_realm": "aerosol",                                                                                       ' >> extended-CMIP6_AERmon.json
  echo '            "standard_name": "surface_net_shortwave_flux_aerosol_free",                                                        ' >> extended-CMIP6_AERmon.json
  echo '            "units": "W m-2",                                                                                                  ' >> extended-CMIP6_AERmon.json
  echo '            "cell_methods": "area: time: mean",                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "cell_measures": "area: areacella",                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "long_name": "Surface Net Aerosol-Free Shortwave Radiation",                                                       ' >> extended-CMIP6_AERmon.json
  echo '            "comment": "Flux corresponding to rls resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)",  ' >> extended-CMIP6_AERmon.json 
  echo '            "dimensions": "longitude latitude time",                                                                           ' >> extended-CMIP6_AERmon.json
  echo '            "out_name": "rssaf",                                                                                               ' >> extended-CMIP6_AERmon.json
  echo '            "type": "real",                                                                                                    ' >> extended-CMIP6_AERmon.json
  echo '            "positive": "down",                                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "valid_min": "",                                                                                                   ' >> extended-CMIP6_AERmon.json
  echo '            "valid_max": "",                                                                                                   ' >> extended-CMIP6_AERmon.json
  echo '            "ok_min_mean_abs": "",                                                                                             ' >> extended-CMIP6_AERmon.json
  echo '            "ok_max_mean_abs": ""                                                                                              ' >> extended-CMIP6_AERmon.json
  echo '        },                                                                                                                     ' >> extended-CMIP6_AERmon.json


  echo '        "rlscsaf": {                                                                                                           ' >> extended-CMIP6_AERmon.json
  echo '            "frequency": "mon",                                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "modeling_realm": "aerosol",                                                                                       ' >> extended-CMIP6_AERmon.json
  echo '            "standard_name": "surface_net_longwave_flux_aerosol_free_clear_sky",                                               ' >> extended-CMIP6_AERmon.json
  echo '            "units": "W m-2",                                                                                                  ' >> extended-CMIP6_AERmon.json
  echo '            "cell_methods": "area: time: mean",                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "cell_measures": "area: areacella",                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "long_name": "Surface Net Aerosol-Free Clear-Sky Longwave Radiation",                                              ' >> extended-CMIP6_AERmon.json
  echo '            "comment": "Flux corresponding to rls resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)",  ' >> extended-CMIP6_AERmon.json 
  echo '            "dimensions": "longitude latitude time",                                                                           ' >> extended-CMIP6_AERmon.json
  echo '            "out_name": "rlscsaf",                                                                                             ' >> extended-CMIP6_AERmon.json
  echo '            "type": "real",                                                                                                    ' >> extended-CMIP6_AERmon.json
  echo '            "positive": "down",                                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "valid_min": "",                                                                                                   ' >> extended-CMIP6_AERmon.json
  echo '            "valid_max": "",                                                                                                   ' >> extended-CMIP6_AERmon.json
  echo '            "ok_min_mean_abs": "",                                                                                             ' >> extended-CMIP6_AERmon.json
  echo '            "ok_max_mean_abs": ""                                                                                              ' >> extended-CMIP6_AERmon.json

  echo '        },                                                                                                                     ' >> extended-CMIP6_AERmon.json
  echo '        "rlsaf": {                                                                                                             ' >> extended-CMIP6_AERmon.json
  echo '            "frequency": "mon",                                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "modeling_realm": "aerosol",                                                                                       ' >> extended-CMIP6_AERmon.json
  echo '            "standard_name": "surface_net_longwave_flux_aerosol_free",                                                         ' >> extended-CMIP6_AERmon.json
  echo '            "units": "W m-2",                                                                                                  ' >> extended-CMIP6_AERmon.json
  echo '            "cell_methods": "area: time: mean",                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "cell_measures": "area: areacella",                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "long_name": "Surface Net Aerosol-Free Longwave Radiation",                                                        ' >> extended-CMIP6_AERmon.json
  echo '            "comment": "Flux corresponding to rls resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)",  ' >> extended-CMIP6_AERmon.json 
  echo '            "dimensions": "longitude latitude time",                                                                           ' >> extended-CMIP6_AERmon.json
  echo '            "out_name": "rlsaf",                                                                                               ' >> extended-CMIP6_AERmon.json
  echo '            "type": "real",                                                                                                    ' >> extended-CMIP6_AERmon.json
  echo '            "positive": "down",                                                                                                ' >> extended-CMIP6_AERmon.json
  echo '            "valid_min": "",                                                                                                   ' >> extended-CMIP6_AERmon.json
  echo '            "valid_max": "",                                                                                                   ' >> extended-CMIP6_AERmon.json
  echo '            "ok_min_mean_abs": "",                                                                                             ' >> extended-CMIP6_AERmon.json
  echo '            "ok_max_mean_abs": ""                                                                                              ' >> extended-CMIP6_AERmon.json

  echo '        }'                                                                                                                       >> extended-CMIP6_AERmon.json
  echo '    }'                                                                                                                           >> extended-CMIP6_AERmon.json
  echo '}'                                                                                                                               >> extended-CMIP6_AERmon.json

  mv -f extended-CMIP6_AERmon.json ../resources/tables/CMIP6_AERmon.json

 else
    echo '  '
    echo '  Noting done, no set of variables has been selected to add to the tables.'
    echo '  '
 fi

else
    echo '  '
    echo '  This scripts requires n argument:'
    echo '  ' $0
    echo '  '
fi
