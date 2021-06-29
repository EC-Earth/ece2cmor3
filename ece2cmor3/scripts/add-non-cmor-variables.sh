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

  head --lines=-3 ../resources/tables/CMIP6_AERmon.json                                                                                                     >  extended-CMIP6_AERmon.json

  echo '        },                                                                                                                     ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '        "rsscsaf": {                                                                                                           ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "frequency": "mon",                                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "modeling_realm": "aerosol",                                                                                       ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "standard_name": "surface_net_shortwave_flux_aerosol_free_clear_sky",                                              ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "units": "W m-2",                                                                                                  ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "cell_methods": "area: time: mean",                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "cell_measures": "area: areacella",                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "long_name": "Surface Net Aerosol-Free Clear-Sky Shortwave Radiation",                                             ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "comment": "Flux corresponding to rls resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)",  ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json 
  echo '            "dimensions": "longitude latitude time",                                                                           ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "out_name": "rsscsaf",                                                                                             ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "type": "real",                                                                                                    ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "positive": "down",                                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "valid_min": "",                                                                                                   ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "valid_max": "",                                                                                                   ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "ok_min_mean_abs": "",                                                                                             ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "ok_max_mean_abs": ""                                                                                              ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json

  echo '        },                                                                                                                     ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '        "rssaf": {                                                                                                             ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "frequency": "mon",                                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "modeling_realm": "aerosol",                                                                                       ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "standard_name": "surface_net_shortwave_flux_aerosol_free",                                                        ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "units": "W m-2",                                                                                                  ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "cell_methods": "area: time: mean",                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "cell_measures": "area: areacella",                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "long_name": "Surface Net Aerosol-Free Shortwave Radiation",                                                       ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "comment": "Flux corresponding to rls resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)",  ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json 
  echo '            "dimensions": "longitude latitude time",                                                                           ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "out_name": "rssaf",                                                                                               ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "type": "real",                                                                                                    ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "positive": "down",                                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "valid_min": "",                                                                                                   ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "valid_max": "",                                                                                                   ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "ok_min_mean_abs": "",                                                                                             ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "ok_max_mean_abs": ""                                                                                              ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '        },                                                                                                                     ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json


  echo '        "rlscsaf": {                                                                                                           ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "frequency": "mon",                                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "modeling_realm": "aerosol",                                                                                       ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "standard_name": "surface_net_longwave_flux_aerosol_free_clear_sky",                                               ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "units": "W m-2",                                                                                                  ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "cell_methods": "area: time: mean",                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "cell_measures": "area: areacella",                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "long_name": "Surface Net Aerosol-Free Clear-Sky Longwave Radiation",                                              ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "comment": "Flux corresponding to rls resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)",  ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json 
  echo '            "dimensions": "longitude latitude time",                                                                           ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "out_name": "rlscsaf",                                                                                             ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "type": "real",                                                                                                    ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "positive": "down",                                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "valid_min": "",                                                                                                   ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "valid_max": "",                                                                                                   ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "ok_min_mean_abs": "",                                                                                             ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "ok_max_mean_abs": ""                                                                                              ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json

  echo '        },                                                                                                                     ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '        "rlsaf": {                                                                                                             ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "frequency": "mon",                                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "modeling_realm": "aerosol",                                                                                       ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "standard_name": "surface_net_longwave_flux_aerosol_free",                                                         ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "units": "W m-2",                                                                                                  ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "cell_methods": "area: time: mean",                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "cell_measures": "area: areacella",                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "long_name": "Surface Net Aerosol-Free Longwave Radiation",                                                        ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "comment": "Flux corresponding to rls resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)",  ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json 
  echo '            "dimensions": "longitude latitude time",                                                                           ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "out_name": "rlsaf",                                                                                               ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "type": "real",                                                                                                    ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "positive": "down",                                                                                                ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "valid_min": "",                                                                                                   ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "valid_max": "",                                                                                                   ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "ok_min_mean_abs": "",                                                                                             ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json
  echo '            "ok_max_mean_abs": ""                                                                                              ' | sed 's/\s*$//g' >> extended-CMIP6_AERmon.json

  echo '        }'                                                                                                                                         >> extended-CMIP6_AERmon.json
  echo '    }'                                                                                                                                             >> extended-CMIP6_AERmon.json
  echo '}'                                                                                                                                                 >> extended-CMIP6_AERmon.json

  mv -f extended-CMIP6_AERmon.json ../resources/tables/CMIP6_AERmon.json

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
