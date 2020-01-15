#!/bin/bash
# Thomas Reerink
#
# This script adds some non-cmor variables (which thus do not exit in the CMIP6 data request) to the end of the cmor table in question.
#
# This scripts requires no arguments:
#
# ${1} the first   argument is  
#
# Run example:
#  ./add-non-cmor-variables.sh
#

if [ "$#" -eq 0 ]; then

 add_the_four_aerchem_variables=True
 
 if [ add_the_four_aerchem_variables ]; then

  # clear-sky aerosol-free surface radiation fluxes, see issue #732 & #736-7:

  head --lines=-3 ../resources/tables/CMIP6_AERmon.json                                                                                  >  extended-CMIP6_AERmon.json

  echo '        }, '                                                                                                                     >> extended-CMIP6_AERmon.json
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

  echo '        }, '                                                                                                                     >> extended-CMIP6_AERmon.json
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
  echo '        }, '                                                                                                                     >> extended-CMIP6_AERmon.json


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

  echo '        }, '                                                                                                                     >> extended-CMIP6_AERmon.json
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

#elif [ $1 == 'deactivate-pextra-mode' ]; then
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


# 126070         ! CVEXTR2(11)='clear SW surf', grib 126.70clear SW surf rsscsaf (r: rad, s: short, s:surface, cs: clear sky, af: aerosol free)
# 126071         ! CVEXTR2(12)='total SW surf', grib 126.71total SW surf rssaf
# 126074         ! CVEXTR2(15)='clear LW surf', grib 126.74clear LW surf rlscsaf
# 126075         ! CVEXTR2(16)='total LW surf', grib 126.75total LW surf rlsaf

# AERmon  rlutaf          1       longitude latitude time TOA Upwelliing Aerosol-Free Longwave Radiation  web     grib 126.73     grib 126.73     MFPPHY  Available from double radiation call in IFS. See also PEXTRA issue #403   aerosol free  Twan & Thomas   Flux corresponding to rlut resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)    AerChemMIP,DAMIP,HighResMIP                                                                                                                             
# AERmon  rlutcsaf        1       longitude latitude time TOA Upwelling Clear-Sky, Aerosol-Free Longwave Radiation        web     grib 126.72     grib 126.72     MFPPHY  Available from double radiation call in IFS. See also PEXTRA issue #403   aerosol free  Twan & Thomas   Flux corresponding to rlutcs resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)  AerChemMIP,DAMIP,HighResMIP                                                                                                                             
# AERmon  rsutaf          1       longitude latitude time toa upwellingshortwave radiation        web     grib 126.76     grib 128.212-126.069    MFPPHY  Available from double radiation call in IFS. See also PEXTRA issue #403   aerosol free  Twan & Thomas   Flux corresponding to rsut resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)    AerChemMIP,DAMIP,GeoMIP,HighResMIP                                                                                                                              
# E3hrPt  rsutcsaf        1       longitude latitude time1        toa upwelling clear-sky shortwave radiation     web     grib 126.77     Ignore because part of RFMIP-IRF and we don't participate in that experiment of RFMIP. Moreover grib 128.212-126.068 won't work here, because then accumulated and instantaneous fluxes are mixed.      -       Available from double radiation call in IFS. See also PEXTRA issue #403   aerosol free  Twan & Thomas   Flux corresponding to rsutcs resulting from aerosol-free call to radiation, following Ghan (ACP, 2013)  RFMIP                                                                                                                           
# E3hrPt  rsdscsaf        1       longitude latitude time1        Surface Downwelling Clear-Sky, Aerosol-Free Shortwave Radiation web     grib 126.78     not available, moreover they can be ignored because part of RFMIP-IRF and we don't participate in that experiment of RFMIP.     -       Available from double radiation call in IFS. See also PEXTRA issue #403   aerosol free  Twan & Thomas   Calculated in the absence of aerosols and clouds.       RFMIP                                                                                                                           
# E3hrPt  rsuscsaf        1       longitude latitude time1        Surface Upwelling Clean Clear-Sky Shortwave Radiation   web     grib 126.70  - 126.78   not available, moreover they can be ignored because part of RFMIP-IRF and we don't participate in that experiment of RFMIP.     -       Available from double radiation call in IFS. See also PEXTRA issue #403   aerosol free  Twan & Thomas   Surface Upwelling Clear-sky, Aerosol Free Shortwave Radiation   RFMIP                                                                                                                           

#  rsscsaf     rsscsaf 
#  rssaf       rssaf
#  rlscsaf     rlscsaf
#  rlsaf       rlsaf

# ut upwelling toa
#
# 403-56 about naming

# These four vars are at the portal mentioned in #736-7

