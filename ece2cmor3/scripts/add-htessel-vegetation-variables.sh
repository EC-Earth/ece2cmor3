#!/bin/bash
# Thomas Reerink
#
# This script adds some non-cmor variables (which thus do not exit in
# the CMIP6 data request) to a new HTESEELmon CMOR table.
#
# This script requires one argument.
#
# For examples how to call this script, run it without arguments.
#

if [ "$#" -eq 1 ]; then

 do_clean=$1

 if [ ${do_clean} == 'clean-before' ] || [ ${do_clean} == 'no-clean-before' ]; then
  # See #802       https://github.com/EC-Earth/ece2cmor3/issues/#802
  # See #1312-106  https://dev.ec-earth.org/issues/1312#note-106

  # Overview of added variables:
  # https://codes.ecmwf.int/grib/param-db/27 27.128 Low  vegetation cover (cvl)                HTESSSELmon cvl     Lmon c3PftFrac is taken as basis
  # https://codes.ecmwf.int/grib/param-db/28 28.128 High vegetation cover (cvh)                HTESSSELmon cvh     Lmon c3PftFrac is taken as basis
  # https://codes.ecmwf.int/grib/param-db/29 29.128 Type of low vegetation (tvl)               HTESSSELmon tvl     Lmon c3PftFrac is taken as basis
  # https://codes.ecmwf.int/grib/param-db/30 30.128 Type of high vegetation (tvh)              HTESSSELmon tvh     Lmon c3PftFrac is taken as basis
  # https://codes.ecmwf.int/grib/param-db/66 66.128 Leaf area index, low vegetation (lai_lv)   HTESSSELmon lai_lv  Lmon lai       is taken as basis
  # https://codes.ecmwf.int/grib/param-db/67 67.128 Leaf area index, high vegetation (lai_hv)  HTESSSELmon lai_hv  Lmon lai       is taken as basis

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_cv=CMIP6_CV.json
  table_file_HTESSELmon=CMIP6_HTESSELmon.json

  cd ${table_path}
  if [ ${do_clean} == 'clean-before' ]; then
   rm -f ${table_file_HTESSELmon}
   git checkout ${table_file_cv}
  fi

  sed -i  '/"IfxAnt"/i \
            "HTESSELmon",
  ' ${table_file_cv}

  # Add CMIP6 HTESSELmon table header:
  echo '{                                              ' | sed 's/\s*$//g' >  ${table_file_HTESSELmon}
  echo '    "Header": {                                ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '        "data_specs_version": "01.00.33",      ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '        "cmor_version": "3.5",                 ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '        "table_id": "Table HTESSELmon",        ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '        "realm": "land",                       ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '        "table_date": "18 November 2020",      ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '        "missing_value": "1e20",               ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '        "int_missing_value": "-999",           ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '        "product": "model-output",             ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '        "approx_interval": "30.00000",         ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '        "generic_levels": "",                  ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '        "mip_era": "CMIP6",                    ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '        "Conventions": "CF-1.7 CMIP-6.2"       ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '    },                                         ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '    "variable_entry": {                        ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}

  grep -A 17 -e '"c3PftFrac":' CMIP6_Lmon.json | sed -e 's/c3PftFrac/cvl/g' -e 's/area_fraction/cvl/'                               -e 's/"long_name": ".*"/"long_name": "Low vegetation cover"/'              -e 's/"units": ".*"/"units": "0-1"/'    -e 's/"comment": ".*"/"comment": "This parameter is the fraction of the grid box (0-1) that is covered with vegetation that is classified as low (see https:\/\/codes.ecmwf.int\/grib\/param-db\/27)."/g'                  >> ${table_file_HTESSELmon}
  grep -A 17 -e '"c3PftFrac":' CMIP6_Lmon.json | sed -e 's/c3PftFrac/cvh/g' -e 's/area_fraction/cvh/'                               -e 's/"long_name": ".*"/"long_name": "High vegetation cover"/'             -e 's/"units": ".*"/"units": "0-1"/'    -e 's/"comment": ".*"/"comment": "This parameter is the fraction of the grid box (0-1) that is covered with vegetation that is classified as high (see https:\/\/codes.ecmwf.int\/grib\/param-db\/28)."/g'                 >> ${table_file_HTESSELmon}
  grep -A 17 -e '"c3PftFrac":' CMIP6_Lmon.json | sed -e 's/c3PftFrac/tvl/g' -e 's/area_fraction/tvl/'                               -e 's/"long_name": ".*"/"long_name": "Type of low vegetation"/'            -e 's/"units": ".*"/"units": "-"/'      -e 's/"comment": ".*"/"comment": "This parameter indicates the 10 types of low vegetation recognised by the ECMWF Integrated Forecasting System (see https:\/\/codes.ecmwf.int\/grib\/param-db\/29)."/g'                   >> ${table_file_HTESSELmon}
  grep -A 17 -e '"c3PftFrac":' CMIP6_Lmon.json | sed -e 's/c3PftFrac/tvh/g' -e 's/area_fraction/tvh/'                               -e 's/"long_name": ".*"/"long_name": "Type of high vegetation"/'           -e 's/"units": ".*"/"units": "-"/'      -e 's/"comment": ".*"/"comment": "This parameter indicates the 6 types of high vegetation recognised by the ECMWF Integrated Forecasting System (see https:\/\/codes.ecmwf.int\/grib\/param-db\/30)."/g'                   >> ${table_file_HTESSELmon}
  grep -A 17 -e '"lai":'       CMIP6_Lmon.json | sed -e 's/lai/lai_lv/g'    -e 's/leaf_area_index/leaf_area_index_low_vegetation/'  -e 's/"long_name": ".*"/"long_name": "Leaf area index, low vegetation"/'   -e 's/"units": ".*"/"units": "m2 m-2"/' -e 's/"comment": ".*"/"comment": "This parameter is the surface area of one side of all the leaves found over an area of land for vegetation classified as low (see https:\/\/codes.ecmwf.int\/grib\/param-db\/66)."/g'    >> ${table_file_HTESSELmon}
  grep -A 16 -e '"lai":'       CMIP6_Lmon.json | sed -e 's/lai/lai_hv/g'    -e 's/leaf_area_index/leaf_area_index_high_vegetation/' -e 's/"long_name": ".*"/"long_name": "Leaf area index, high vegetation"/'  -e 's/"units": ".*"/"units": "m2 m-2"/' -e 's/"comment": ".*"/"comment": "This parameter is the surface area of one side of all the leaves found over an area of land for vegetation classified as high (see https:\/\/codes.ecmwf.int\/grib\/param-db\/67)."/g'   >> ${table_file_HTESSELmon}

  sed -i -e 's/typec3pft/type/' ${table_file_HTESSELmon}

  # Add closing part of CMIP6 table json file:
  echo '        }                                      ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '    }                                          ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}
  echo '}                                              ' | sed 's/\s*$//g' >> ${table_file_HTESSELmon}


  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_HTESSELmon}
  sed -i -e 's/\s*$//g'                ${table_file_cv}

  cd -

  echo
  echo " Running:"
  echo "  $0 ${do_clean}"
  echo " has adjusted the file:"
  echo "  ${table_path}/${table_file_cv}"
  echo " and added the file:"
  echo "  ${table_path}/${table_file_HTESSELmon}"
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
