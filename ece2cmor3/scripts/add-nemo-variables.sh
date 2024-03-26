#!/bin/bash
# Thomas Reerink
#
# This script adds some non-cmor variables (which thus do not exit in
# the CMIP6 data request) to a few CMOR tables. And add the dayPt frequency.
#
# This script requires one argument.
#
# For examples how to call this script, run it without arguments.
#

if [ "$#" -eq 1 ]; then

 do_clean=$1

 if [ ${do_clean} == 'clean-before' ] || [ ${do_clean} == 'no-clean-before' ]; then
  # See #811       https://github.com/EC-Earth/ece2cmor3/issues/811
  # See #814       https://github.com/EC-Earth/ece2cmor3/issues/814
  # See #1312-146  https://dev.ec-earth.org/issues/1312#note-146

  # Overview of added seaIce variables:
  #  SIday sishevel   field_ref="ishear"   SImon sishevel   is taken as basis
  #  SIday sidconcdyn field_ref="afxdyn"   SImon sidconcdyn is taken as basis
  #  SIday sidconcth  field_ref="afxthd"   SImon sidconcth  is taken as basis
  #  SIday sidivvel   field_ref="idive"    SImon sidivvel   is taken as basis
  #  SIday sidmassdyn field_ref="dmidyn"   SImon sidmassdyn is taken as basis
  #  SIday sidmassth  field_ref="dmithd"   SImon sidmassth  is taken as basis

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_cv=CMIP6_CV.json
  table_file_SIday=CMIP6_SIday.json
  table_file_SImon=CMIP6_SImon.json
  table_file_Omon=CMIP6_Omon.json
  tmp_file_SIday=CMIP6_SIday_tmp.json

  cd ${table_path}
  if [ ${do_clean} == 'clean-before' ]; then
   git checkout ${table_file_cv}
   git checkout ${table_file_SIday}
   git checkout ${table_file_SImon}
   git checkout ${table_file_Omon}
  fi

  sed -i  '/"dec":"decadal mean samples"/i \
            "dayPt":"sampled daily, at specified time point within the time period",
  ' ${table_file_cv}

  # Add all of the CMIP6_SIday.json except its last 3 lines to the tmp file:
  head -n -3 ${table_file_SIday}                                                                         >  ${tmp_file_SIday}
  echo '        }, '                                                                                     >> ${tmp_file_SIday}

  grep -A 17 '"sishevel":'   CMIP6_SImon.json  | sed -e 's/"frequency": "monPt"/"frequency": "dayPt"/g'  >> ${tmp_file_SIday}
  grep -A 17 '"sidconcdyn":' CMIP6_SImon.json  | sed -e 's/"frequency": "mon"/"frequency": "day"/g'      >> ${tmp_file_SIday}
  grep -A 17 '"sidconcth":'  CMIP6_SImon.json  | sed -e 's/"frequency": "mon"/"frequency": "day"/g'      >> ${tmp_file_SIday}
  grep -A 17 '"sidivvel":'   CMIP6_SImon.json  | sed -e 's/"frequency": "monPt"/"frequency": "dayPt"/g'  >> ${tmp_file_SIday}
  grep -A 17 '"sidmassdyn":' CMIP6_SImon.json  | sed -e 's/"frequency": "mon"/"frequency": "day"/g'      >> ${tmp_file_SIday}
  grep -A 16 '"sidmassth":'  CMIP6_SImon.json  | sed -e 's/"frequency": "mon"/"frequency": "day"/g'      >> ${tmp_file_SIday}

  # Add closing part of CMIP6 table json file:
  echo '        } '                                                                                      >> ${tmp_file_SIday}
  echo '    } '                                                                                          >> ${tmp_file_SIday}
  echo '} '                                                                                              >> ${tmp_file_SIday}

  mv -f ${tmp_file_SIday} ${table_file_SIday}


  # SImon sfdsi has been used as template:
  sed -i  '/"sidmassdyn": {/i \
        "siflsaltbot": {                                                                        \
            "frequency": "mon",                                                                 \
            "modeling_realm": "seaIce",                                                         \
            "standard_name": "total_flux_of_salt_from_water_into_sea_ice",                      \
            "units": "kg m-2 s-1",                                                              \
            "cell_methods": "area: time: mean where sea_ice (comment: mask=siconc)",            \
            "cell_measures": "area: areacello",                                                 \
            "long_name": "Total flux from water into sea ice",                                  \
            "comment": "Total flux of salt from water into sea ice divided by grid-cell area; salt flux is upward (negative) during ice growth when salt is embedded into the ice and downward (positive) during melt when salt from sea ice is again released to the ocean.",                                                               \
            "dimensions": "longitude latitude time",                                            \
            "out_name": "siflsaltbot",                                                          \
            "type": "real",                                                                     \
            "positive": "down",                                                                 \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        }, 
  ' ${table_file_SImon}


  # Add four ocean variables to the Omon table:
  sed -i  '/"umo": {/i \
        "ubar": {                                                                               \
            "frequency": "mon",                                                                 \
            "modeling_realm": "ocean",                                                          \
            "standard_name": "ocean_barotropic_current_along_i_axis",                           \
            "units": "m s-1",                                                                   \
            "cell_methods": "area: mean where sea time: mean",                                  \
            "cell_measures": "area: areacello",                                                 \
            "long_name": "Ocean Barotropic Current along i-axis",                               \
            "comment": "",                                                                      \
            "dimensions": "longitude latitude time",                                            \
            "out_name": "ubar",                                                                 \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },
  ' ${table_file_Omon}

  sed -i  '/"vmo": {/i \
        "vbar": {                                                                               \
            "frequency": "mon",                                                                 \
            "modeling_realm": "ocean",                                                          \
            "standard_name": "ocean_barotropic_current_along_j_axis",                           \
            "units": "m s-1",                                                                   \
            "cell_methods": "area: mean where sea time: mean",                                  \
            "cell_measures": "area: areacello",                                                 \
            "long_name": "Ocean Barotropic Current along j-axis",                               \
            "comment": "",                                                                      \
            "dimensions": "longitude latitude time",                                            \
            "out_name": "vbar",                                                                 \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },
  ' ${table_file_Omon}

  sed -i  '/"mlotst": {/i \
        "mlddzt": {                                                                             \
            "frequency": "mon",                                                                 \
            "modeling_realm": "ocean",                                                          \
            "standard_name": "thermocline_depth",                                               \
            "units": "m",                                                                       \
            "cell_methods": "area: mean where sea time: mean",                                  \
            "cell_measures": "area: areacello",                                                 \
            "long_name": "Thermocline Depth (depth of max dT/dz)",                              \
            "comment": "depth at maximum upward derivative of sea water potential temperature", \
            "dimensions": "longitude latitude time",                                            \
            "out_name": "mlddzt",                                                               \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },
  ' ${table_file_Omon}

  sed -i  '/"hfbasin": {/i \
        "hcont300": {                                                                           \
            "frequency": "mon",                                                                 \
            "modeling_realm": "ocean",                                                          \
            "standard_name": "heat_content_for_0_300m_top_layer",                               \
            "units": "J m-2",                                                                   \
            "cell_methods": "area: mean where sea time: mean",                                  \
            "cell_measures": "area: areacello",                                                 \
            "long_name": "Heat content 0-300m",                                                 \
            "comment": "",                                                                      \
            "dimensions": "longitude latitude time",                                            \
            "out_name": "hcont300",                                                             \
            "type": "real",                                                                     \
            "positive": "",                                                                     \
            "valid_min": "",                                                                    \
            "valid_max": "",                                                                    \
            "ok_min_mean_abs": "",                                                              \
            "ok_max_mean_abs": ""                                                               \
        },
  ' ${table_file_Omon}


  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g'                ${table_file_cv}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_SIday}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_SImon}
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_Omon}

  cd -

  echo
  echo " Running:"
  echo "  $0 ${do_clean}"
  echo " has adjusted the files:"
  echo "  ${table_path}/${table_file_cv}"
  echo "  ${table_path}/${table_file_SIday}"
  echo "  ${table_path}/${table_file_SImon}"
  echo "  ${table_path}/${table_file_Omon}"
  echo " which is part of the nested CMOR Table repository. View the diff by running:"
  echo "  cd ${table_path}; git diff; cd -"
  echo " This changes can be reverted by running:"
  echo "  ./revert-nested-cmor-table-branch.sh"
  echo

 else
  echo
  echo " This scripts requires one argument: There are only two options:"
  echo "  $0 clean-before"
  echo "  $0 no-clean-before"
  echo
 fi

else
 echo
 echo " This scripts requires one argument: There are only two options:"
 echo "  $0 clean-before"
 echo "  $0 no-clean-before"
 echo
fi
