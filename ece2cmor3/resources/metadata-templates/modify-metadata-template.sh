#!/bin/bash
# Thomas Reerink
#
# This scripts needs four or five arguments
#
# ${1} the first   argument is the MIP name
# ${2} the second  argument is the experiment name or MIP name in the latter case all MIP experiments are taken.
# ${3} the third   argument is the ec-earth model configuration
# ${4} the fourth  argument is the meta data template json file which is used as input, the file: resources/metadata-templates/cmip6-CMIP-piControl-metadata-template.json
# ${5} the fifth   argument is the component, e.g.: ifs, nemo, tm5, or lpjg.
#
#
# Run example:
#  rm -rf metadata*; ./modify-metadata-template.sh CMIP piControl EC-EARTH-HR cmip6-CMIP-piControl-metadata-template.json ifs; diff metadata-* cmip6-CMIP-piControl-metadata-template.json
#
# With this script it is possible to generate a dedicated metadata template json file for each ec-earth3 cmip6 MIP experiment.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.
#
# Note that this script is called in a loop over the MIP experiments by the script:
#  genecec.py

if [ "$#" -eq 4 ] || [ "$#" -eq 5 ]; then
#if [ "$#" -eq 5 ]; then
 mip=$1
 experiment=$2
 ececonf=$3
 input_template=$4
 component=$5
 
 echo
 echo ' Running ' $0 'by:'
 echo ' ' $0 ${mip} ${experiment} ${ececonf} ${input_template}
 echo


 if [ "${ececonf}" != 'EC-EARTH-AOGCM' ] && [ "${ececonf}" != 'EC-EARTH-HR' ] && [ "${ececonf}" != 'EC-EARTH-LR' ] && [ "${ececonf}" != 'EC-EARTH-CC' ] && [ "${ececonf}" != 'EC-EARTH-GrisIS' ] && [ "${ececonf}" != 'EC-EARTH-AerChem' ] && [ "${ececonf}" != 'EC-EARTH-Veg' ] && [ "${ececonf}" != 'EC-EARTH-Veg-LR' ]; then
  echo ' Error in ' $0 ': unkown ec-earth configuration: '  ${ececonf}
  exit
 fi

 if [ "$#" -eq 5 ]; then
  if [ "${component}" != 'ifs' ] && [ "${component}" != 'nemo' ] && [ "${component}" != 'tm5' ] && [ "${component}" != 'lpjg' ] ]; then
   echo ' Error in ' $0 ': unkown ec-earth component: '  ${component} '  Valid options: ifs, nemo, tm5, or lpjg'
   exit
  fi
 fi

 if [ "${ececonf}" = 'EC-EARTH-AOGCM'   ]; then declare -a model_components=('ifs' 'nemo'             ); fi
 if [ "${ececonf}" = 'EC-EARTH-HR'      ]; then declare -a model_components=('ifs' 'nemo'             ); fi
 if [ "${ececonf}" = 'EC-EARTH-LR'      ]; then declare -a model_components=('ifs' 'nemo'             ); fi
 if [ "${ececonf}" = 'EC-EARTH-CC'      ]; then declare -a model_components=('ifs' 'nemo' 'tm5' 'lpjg'); fi
 if [ "${ececonf}" = 'EC-EARTH-GrisIS'  ]; then declare -a model_components=('ifs' 'nemo'             ); fi
 if [ "${ececonf}" = 'EC-EARTH-AerChem' ]; then declare -a model_components=('ifs' 'nemo' 'tm5'       ); fi
 if [ "${ececonf}" = 'EC-EARTH-Veg'     ]; then declare -a model_components=('ifs' 'nemo'       'lpjg'); fi
 if [ "${ececonf}" = 'EC-EARTH-Veg-LR'  ]; then declare -a model_components=('ifs' 'nemo'       'lpjg'); fi

 #                    NAME IN SCRIPT                                 ECE CONF NAME       IFS RES     NEMO RES      TM5 RES                                  LPJG RES   PISCES RES  PISM RES    source_type
 if [ "${ececonf}" = 'EC-EARTH-AOGCM'   ]; then declare -a ece_res=('EC-Earth3'          'T255L91'  'ORCA1L75'    'none'                                    'none'     'none'      'none'      'AOGCM'          ); fi
 if [ "${ececonf}" = 'EC-EARTH-HR'      ]; then declare -a ece_res=('EC-Earth3-HR'       'T511L91'  'ORCA025L75'  'none'                                    'none'     'none'      'none'      'AOGCM'          ); fi
 if [ "${ececonf}" = 'EC-EARTH-LR'      ]; then declare -a ece_res=('EC-Earth3-LR'       'T159L91'  'ORCA1L75'    'none'                                    'none'     'none'      'none'      'AOGCM'          ); fi
 if [ "${ececonf}" = 'EC-EARTH-CC'      ]; then declare -a ece_res=('EC-Earth3-CC'       'T255L91'  'ORCA1L75'    'native regular 2x3 degree latxlon grid'  'T255L91'  'ORCA1L75'  'none'      'AOGCM BGC'      ); fi
 if [ "${ececonf}" = 'EC-EARTH-GrisIS'  ]; then declare -a ece_res=('EC-Earth3-GrIS'     'T255L91'  'ORCA1L75'    'none'                                    'none'     'none'      '5 x 5 km'  'AOGCM ISM'      ); fi
 if [ "${ececonf}" = 'EC-EARTH-AerChem' ]; then declare -a ece_res=('EC-Earth3-AerChem'  'T255L91'  'ORCA1L75'    'native regular 2x3 degree latxlon grid'  'none'     'none'      'none'      'AOGCM AER CHEM' ); fi
 if [ "${ececonf}" = 'EC-EARTH-Veg'     ]; then declare -a ece_res=('EC-Earth3-Veg'      'T255L91'  'ORCA1L75'    'none'                                    'T255L91'  'none'      'none'      'AOGCM'          ); fi 
 if [ "${ececonf}" = 'EC-EARTH-Veg-LR'  ]; then declare -a ece_res=('EC-Earth3-Veg-LR'   'T159L91'  'ORCA1L75'    'none'                                    'T159L91'  'none'      'none'      'AOGCM'          ); fi 

 if [ "${ececonf}" = 'EC-EARTH-AOGCM'   ]; then declare -a nom_res=('EC-Earth3'          '100 km'   '50 km'       'none'                                    'none'     'none'      'none'      'AOGCM'          ); fi
 if [ "${ececonf}" = 'EC-EARTH-HR'      ]; then declare -a nom_res=('EC-Earth3-HR'       '50 km'    '10 km'       'none'                                    'none'     'none'      'none'      'AOGCM'          ); fi
 if [ "${ececonf}" = 'EC-EARTH-LR'      ]; then declare -a nom_res=('EC-Earth3-LR'       '100 km'   '50 km'       'none'                                    'none'     'none'      'none'      'AOGCM'          ); fi
 if [ "${ececonf}" = 'EC-EARTH-CC'      ]; then declare -a nom_res=('EC-Earth3-CC'       '100 km'   '50 km'       '250 km'                                  '100 km'   '50 km'     'none'      'AOGCM BGC'      ); fi
 if [ "${ececonf}" = 'EC-EARTH-GrisIS'  ]; then declare -a nom_res=('EC-Earth3-GrIS'     '100 km'   '50 km'       'none'                                    'none'     'none'      '5 km'      'AOGCM ISM'      ); fi
 if [ "${ececonf}" = 'EC-EARTH-AerChem' ]; then declare -a nom_res=('EC-Earth3-AerChem'  '100 km'   '50 km'       '250 km'                                  'none'     'none'      'none'      'AOGCM AER CHEM' ); fi
 if [ "${ececonf}" = 'EC-EARTH-Veg'     ]; then declare -a nom_res=('EC-Earth3-Veg'      '100 km'   '50 km'       'none'                                    '100 km'   'none'      'none'      'AOGCM'          ); fi
 if [ "${ececonf}" = 'EC-EARTH-Veg-LR'  ]; then declare -a nom_res=('EC-Earth3-Veg-LR'   '100 km'   '50 km'       'none'                                    '100 km'   'none'      'none'      'AOGCM'          ); fi
 # https://www.earthsystemcog.org/site_media/projects/wip/CMIP6_global_attributes_filenames_CVs_v6.2.6.pdf
 # IFS  T511   T255   T159       ORCA1            ORCA0.25                TM5       LPJG=IFS
 #      40 km  80 km  125 km     0.67 * 111 km    0.25 * 0.67 * 111 km

 for i in "${model_components[@]}"
 do
    echo ' Running for: ' "$i"
 done
  
 if [ "$#" -eq 5 ]; then
  if [ "${component}" = 'ifs' ]; then
   grid_label='gr'
  elif [ "${component}" = 'nemo' ]; then
   grid_label='gn'
  elif [ "${component}" = 'tm5' ]; then
   grid_label='gn'
  elif [ "${component}" = 'lpjg' ]; then
   grid_label='gr'
  fi
 fi

 output_template=metadata-cmip6-${mip}-${experiment}-${ececonf}-${component}-template.json

 # Creating and adjusting with sed the output meta data template json file:
 sed    's/"activity_id":                  "CMIP"/"activity_id":                  "'${mip}'"/' ${input_template} >       ${output_template}
 sed -i 's/"experiment_id":                "piControl"/"experiment_id":                "'${experiment}'"/'               ${output_template}
 sed -i 's/"source_id":                    "EC-Earth3"/"source_id":                    "'${ece_res[0]}'"/'               ${output_template}
 sed -i 's/"source":                       "EC-Earth3 (2019)"/"source":                       "'${ece_res[0]}'" (2019)/' ${output_template}  # The 2019 is correct as long no P verison from 2017 is taken.
 sed -i 's/"source_type":                  "AOGCM"/"source_type":                  "'"${ece_res[7]}"'"/'                 ${output_template}  # Note the double quote for the spaces in the variable
 sed -i 's/"grid":                         "T255L91"/"grid":                         "'${ece_res[1]}'"/'                 ${output_template}
 sed -i 's/"grid_label":                   "gr"/"grid_label":                   "'${grid_label}'"/'                      ${output_template}
 sed -i 's/"nominal_resolution":           "100 km"/"nominal_resolution":           "'"${nom_res[1]}"'"/'                ${output_template}

#for i in "${ece_res[@]}"
#do
#   echo "$i"
#done

#for i in "${nom_res[@]}"
#do
#   echo "$i"
#done

else
    echo '  '
    echo '  This scripts requires  variable, e.g.:'
    echo '  ' $0 CMIP piControl EC-EARTH-AOGCM cmip6-CMIP-piControl-metadata-template.json
    echo '  '
fi



#  "AER":"aerosol treatment in an atmospheric model where concentrations are calculated based on emissions, transformation, and removal processes (rather than being prescribed or omitted entirely)",
#  "AGCM":"atmospheric general circulation model run with prescribed ocean surface conditions and usually a model of the land surface",
#  "AOGCM":"coupled atmosphere-ocean global climate model, additionally including explicit representation of at least the land and sea ice",
#  "BGC":"biogeochemistry model component that at the very least accounts for carbon reservoirs and fluxes in the atmosphere, terrestrial biosphere, and ocean",
#  "CHEM":"chemistry treatment in an atmospheric model that calculates atmospheric oxidant concentrations (including at least ozone), rather than prescribing them",
#  "ISM":"ice-sheet model that includes ice-flow",
#  "LAND":"land model run uncoupled from the atmosphere",

#       "source_type":{
#           "AER":"aerosol treatment in an atmospheric model where concentrations are calculated based on emissions, transformation, and removal processes (rather than being prescribed or omitted entirely)",
#           "AGCM":"atmospheric general circulation model run with prescribed ocean surface conditions and usually a model of the land surface",
#           "AOGCM":"coupled atmosphere-ocean global climate model, additionally including explicit representation of at least the land and sea ice",
#           "BGC":"biogeochemistry model component that at the very least accounts for carbon reservoirs and fluxes in the atmosphere, terrestrial biosphere, and ocean",
#           "CHEM":"chemistry treatment in an atmospheric model that calculates atmospheric oxidant concentrations (including at least ozone), rather than prescribing them",
#           "ISM":"ice-sheet model that includes ice-flow",
#           "LAND":"land model run uncoupled from the atmosphere",
#           "OGCM":"ocean general circulation model run uncoupled from an AGCM but, usually including a sea-ice model",
#           "RAD":"radiation component of an atmospheric model run 'offline'",
#           "SLAB":"slab-ocean used with an AGCM in representing the atmosphere-ocean coupled system"
#       },
#       "frequency":{
#           "1hr":"sampled hourly",
#           "1hrCM":"monthly-mean diurnal cycle resolving each day into 1-hour means",
#           "1hrPt":"sampled hourly, at specified time point within an hour",
#           "3hr":"sampled every 3 hours",
#           "3hrPt":"sampled 3 hourly, at specified time point within the time period",
#           "6hr":"sampled every 6 hours",
#           "6hrPt":"sampled 6 hourly, at specified time point within the time period",
#           "day":"daily mean samples",
#           "dec":"decadal mean samples",
#           "fx":"fixed (time invariant) field",
#           "mon":"monthly mean samples",
#           "monC":"monthly climatology computed from monthly mean samples",
#           "monPt":"sampled monthly, at specified time point within the time period",
#           "subhrPt":"sampled sub-hourly, at specified time point within an hour",
#           "yr":"annual mean samples",
#           "yrPt":"sampled yearly, at specified time point within the time period"
#       },
#       "grid_label":{
#           "gm":"global mean data",
#           "gn":"data reported on a model's native grid",
#           "gna":"data reported on a native grid in the region of Antarctica",
#           "gng":"data reported on a native grid in the region of Greenland",
#           "gnz":"zonal mean data reported on a model's native latitude grid",
#           "gr":"regridded data reported on the data provider's preferred target grid",
#           "gr1":"regridded data reported on a grid other than the native grid and other than the preferred target grid",
#           "gr1a":"regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid",
#           "gr1g":"regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid",
#           "gr1z":"regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid",
#           "gr2":"regridded data reported on a grid other than the native grid and other than the preferred target grid",
#           "gr2a":"regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid",
#           "gr2g":"regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid",
#           "gr2z":"regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid",
#           "gr3":"regridded data reported on a grid other than the native grid and other than the preferred target grid",
#           "gr3a":"regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid",
#           "gr3g":"regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid",
#           "gr3z":"regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid",
#           "gr4":"regridded data reported on a grid other than the native grid and other than the preferred target grid",
#           "gr4a":"regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid",
#           "gr4g":"regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid",
#           "gr4z":"regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid",
#           "gr5":"regridded data reported on a grid other than the native grid and other than the preferred target grid",
#           "gr5a":"regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid",
#           "gr5g":"regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid",
#           "gr5z":"regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid",
#           "gr6":"regridded data reported on a grid other than the native grid and other than the preferred target grid",
#           "gr6a":"regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid",
#           "gr6g":"regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid",
#           "gr6z":"regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid",
#           "gr7":"regridded data reported on a grid other than the native grid and other than the preferred target grid",
#           "gr7a":"regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid",
#           "gr7g":"regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid",
#           "gr7z":"regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid",
#           "gr8":"regridded data reported on a grid other than the native grid and other than the preferred target grid",
#           "gr8a":"regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid",
#           "gr8g":"regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid",
#           "gr8z":"regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid",
#           "gr9":"regridded data reported on a grid other than the native grid and other than the preferred target grid",
#           "gr9a":"regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid",
#           "gr9g":"regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid",
#           "gr9z":"regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid",
#           "gra":"regridded data in the region of Antarctica reported on the data provider's preferred target grid",
#           "grg":"regridded data in the region of Greenland reported on the data provider's preferred target grid",
#           "grz":"regridded zonal mean data reported on the data provider's preferred latitude target grid"
#       },
#       "nominal_resolution":[
#           "0.5 km",
#           "1 km",
#           "10 km",
#           "100 km",
#           "1000 km",
#           "10000 km",
#           "1x1 degree",
#           "2.5 km",
#           "25 km",
#           "250 km",
#           "2500 km",
#           "5 km",
#           "50 km",
#           "500 km",
#           "5000 km"
