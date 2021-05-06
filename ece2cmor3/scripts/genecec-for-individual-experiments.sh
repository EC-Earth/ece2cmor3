#!/usr/bin/env bash
# Thomas Reerink
#
# This scripts requires four arguments:
#  first  argument is the path/data-request-filename
#  second argument is the MIP/project name
#  third  argument is the experiment name
#  fourth argument is the EC-Earth3 configuration
#  fifth  argument is the output directory
#
# Run this script without arguments for examples how to call this script.
#
# With this script it is possible to generate the EC-Earth3 control output files, i.e.
# the IFS Fortran namelists (the ppt files), the NEMO xml files for XIOS (the
# file_def files for OPA, LIM and PISCES), the instruction file for LPJ_GUESS (the
# *.ins file) and the files required for the cmorisation for a certain MIP experiments.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.


# The xlsx data request file has been created as follows:
#  cd ../resources/miscellaneous-data-requests
#  drq -m CMIP -e ssp245 -t 1 -p 1 --xls --xlsDir cmip6-data-request-CovidMIP
# With this minimal request no 3hr & 6hr fields are in the request such that the file:
#   ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1.xlsx
# can be directly used.
# However, finally the ec-earth consortium decided to add the following variables on top of this CMIP request:
#  6hrPlevPt psl, ta, ua, va & zg500 and Omon msftyz & SImon sivol & day sfcWind
# Therefore:
#  cd cmip6-data-request-CovidMIP/
#  cp cmvme_CMIP_ssp245_1_1.xlsx cmvme_CMIP_ssp245_1_1-additional.xlsx
# And manually edit the cmvme_CMIP_ssp245_1_1-additional.xlsx file by adding these variables on their
# respectively tables. Note that the 6hrPlevPt sheet had to be manually added in this xlsx file.
#
# The earlier approaches used:
#  cd ../resources/miscellaneous-data-requests
#  drq -m CMIP,DCPP,LS3MIP,ScenarioMIP,CORDEX,DynVarMIP,VIACSAB -e ssp245 -t 1 -p 1 --xls --xlsDir cmip6-data-request-CovidMIP-scenariomip-EC-EARTH-AOGCM
#  cd cmip6-data-request-CovidMIP-scenariomip-EC-EARTH-AOGCM/
#  cp cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr-no-6hrLev.xlsx
# Then manually remove the 3hr and 6hrLev variables from the cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr-no-6hrLev.xlsx.

#  drq -m CMIP,DCPP,LS3MIP,PAMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB -e ssp245 -t 1 -p 1 --xls --xlsDir cmip6-data-request-CovidMIP-cmip-EC-EARTH-AOGCM

if [ "$#" -eq 5 ]; then

  data_request_file=$1
  mip_name=$2
  experiment=$3
  ece_configuration=$4
  output_dir=$5

  # If the data request file has a releative path a preceeding PWD is concatenated:
  if [[ "${data_request_file:0:1}" != / && "${data_request_file:0:2}" != ~[/a-z] ]]; then
   data_request_file=${PWD}/${data_request_file}
  fi

  if [ ${mip_name} = 'LAMACLIMA' ]; then
   ./add-lamaclima-experiments.sh
  fi

  rm -rf   ${output_dir}
  mkdir -p ${output_dir}

  if [ ${data_request_file##*/} = 'cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx' ] || [ ${data_request_file##*/} = 'cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx' ]; then
   ./add-variables-with-pressure-levels-for-rcm-forcing.sh
  fi

  # Distinguish between a json & xlsx file:
  if [ ${data_request_file:(-4)} = 'json' ]; then
   request_option='--vars'
  else
   request_option='--drq'
  fi

  if [ ${request_option} = '--vars' ]; then
   rsync -a ${data_request_file} ${output_dir}
  fi

  # Generating the available, ignored, identified missing and missing xlsx & txt files:
  xls_ece_dir=cmip6-data-request-ece/data-request-ece-${mip_name}-${experiment}
  mkdir -p ${xls_ece_dir};

  # Check whether the data request file is a json file, if so convert the json file for the checkvars application:
  if [ "${data_request_file##*.}" = 'json' ]; then
   convert_component_to_flat_json ${data_request_file}
   data_request_file_for_checkvars=${data_request_file##*/}
   data_request_file_for_checkvars=${data_request_file_for_checkvars/.json/-flat.json}
  else
   data_request_file_for_checkvars=${data_request_file##*/}
   rsync -a ${data_request_file} ${data_request_file##*/}
  fi

  echo
  echo ' Running checkvars with:'
  echo ' ' checkvars -v --drq ${data_request_file_for_checkvars} --output ${xls_ece_dir}/variable-list-${mip_name}-${experiment}
  echo
  checkvars -v --drq ${data_request_file_for_checkvars} --output ${xls_ece_dir}/variable-list-${mip_name}-${experiment}
  echo
  rm -f ${data_request_file_for_checkvars}

  drq2file_def ${request_option} ${data_request_file}

  rm -f cmip6-file_def_nemo.xml
  mv -f file_def_nemo-opa.xml    ${output_dir}
  mv -f file_def_nemo-lim3.xml   ${output_dir}
  mv -f file_def_nemo-pisces.xml ${output_dir}
  mv -f volume-estimate-nemo.txt ${output_dir}

  cd ${output_dir}

  drq2ppt ${request_option} ${data_request_file}
  drq2ins ${request_option} ${data_request_file}
  if [ ${request_option} = '--drq' ]; then
   drq2varlist ${request_option} ${data_request_file} --ececonf EC-EARTH-AOGCM --varlist cmip6-data-request-varlist-${mip_name}-${experiment}-${ece_configuration}.json
   convert_component_to_flat_json cmip6-data-request-varlist-${mip_name}-${experiment}-${ece_configuration}.json
   checkvars -v --asciionly --drq cmip6-data-request-varlist-${mip_name}-${experiment}-${ece_configuration}-flat.json --output request-overview-with-ece-preferences
   rm -f cmip6-data-request-varlist-${mip_name}-${experiment}-${ece_configuration}-flat.json
  else
   convert_component_to_flat_json ${data_request_file##*/}
   data_request_file_for_checkvars=${data_request_file##*/}
   data_request_file_for_checkvars=${data_request_file_for_checkvars/.json/-flat.json}
   checkvars -v --asciionly --drq ${data_request_file_for_checkvars} --output request-overview-with-ece-preferences
   rm -f ${data_request_file_for_checkvars}
  fi

  # Remove the freq_op attribute for the variable msftbarot (uoce_e3u_vsum_e2u_cumul) from the file_def_nemo.xml file #327 & e.g. #518-165 on the ec-earth portal
  sed -i -e 's/uoce_e3u_vsum_e2u_cumul. freq_op=.1ts/uoce_e3u_vsum_e2u_cumul/' file_def_nemo-opa.xml

  # Remove deptho from the file_def_nemo-opa.xml #249
  sed -i -e '/deptho/d' file_def_nemo-opa.xml

  # Switching the 'transect' variables off (the transect grid definition seems to depend on the XIOS 2.5 upgrade)
  sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' file_def_nemo*

  # Estimating the Volume of the TM5 output:
  estimate_tm5_volume ${request_option} ${data_request_file}

  cat volume-estimate-ifs.txt volume-estimate-nemo.txt volume-estimate-tm5.txt volume-estimate-lpj-guess.txt > volume-estimate-${mip_name}-${experiment}.txt
  rm -f volume-estimate-ifs.txt volume-estimate-nemo.txt volume-estimate-tm5.txt volume-estimate-lpj-guess.txt

  cd -
  # Produce the metadata files for this MIP experiment.
  ./modify-metadata-template.sh ${mip_name} ${experiment} ${ece_configuration};

  if [ ${mip_name} = 'CovidMIP' ]; then
   if [ ${experiment} = 'ssp245-baseline' ]; then
    sed -i -e 's/"activity_id":                  "CovidMIP"/"activity_id":                  "ScenarioMIP"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"experiment_id":                "ssp245-baseline"/"experiment_id":                "ssp245"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"parent_activity_id":           ""/"parent_activity_id":           "CMIP"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"parent_experiment_id":         ""/"parent_experiment_id":         "historical"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"branch_time_in_child":         "0.0D"/"branch_time_in_child":         "60265.0D"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"branch_time_in_parent":        "0.0D"/"branch_time_in_parent":        "60265.0D"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   else
    sed -i -e 's/"activity_id":                  "CovidMIP"/"activity_id":                  "DAMIP"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"parent_activity_id":           ""/"parent_activity_id":           "ScenarioMIP"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"parent_experiment_id":         ""/"parent_experiment_id":         "ssp245"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"branch_time_in_child":         "0.0D"/"branch_time_in_child":         "62091.0D"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"branch_time_in_parent":        "0.0D"/"branch_time_in_parent":        "62091.0D"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   fi

   sed -i -e 's/"forcing_index":                "1"/"forcing_index":                "2"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   sed -i -e 's/"#variant_info".*/"variant_info":                 "This experiment belongs to the set of CovidMIP experiments which use specific forcings for GHG, aerosols (MACv2-SP) and ozone, which are available at https:\/\/zenodo.org\/record\/3957826 and https:\/\/zenodo.org\/record\/4021333",/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   sed -i -e 's/"parent_variant_label":         "r1i1p1f1"/"parent_variant_label":         "r1i1p1f2"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json

   # Prevent any 3 hourly raw output:
   rm -f ${output_dir}/pptdddddd0300
  fi


  if [ ${mip_name} = 'LAMACLIMA' ]; then
    sed -i -e 's/"parent_activity_id":           ""/"parent_activity_id":           "CMIP"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"parent_experiment_id":         ""/"parent_experiment_id":         "historical"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"branch_time_in_child":         "0.0D"/"branch_time_in_child":         "60265.0D"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"branch_time_in_parent":        "0.0D"/"branch_time_in_parent":        "60265.0D"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
  fi


  mv -f metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json ${output_dir}

  if [ ${mip_name} = 'LAMACLIMA' ]; then
   ./revert-nested-cmor-table-branch.sh
  fi

  if [ ${data_request_file##*/} = 'cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx' ]; then
   rm -f ${output_dir}/pptdddddd0300    # Prevent any 3 hourly raw output
   sed -i -e 's/EC-Earth3/EC-Earth3-RT/' -e 's/(2019)/(2021)/' ${output_dir}/metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   if [ ${mip_name} = 'ScenarioMIP' ]; then
     sed -i -e 's/"branch_time_in_child":         "0.0D"/"branch_time_in_child":         "60265.0D"/' ${output_dir}/metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
     sed -i -e 's/"branch_time_in_parent":        "0.0D"/"branch_time_in_parent":        "60265.0D"/' ${output_dir}/metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   fi
   mv -f ${xls_ece_dir} ${xls_ece_dir}-plev23
  fi

  if [ ${data_request_file##*/} = 'cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx' ]; then
   rm -f ${output_dir}/pptdddddd0300    # Prevent any 3 hourly raw output
   sed -i -e 's/EC-Earth3/EC-Earth3-RT/' -e 's/(2019)/(2021)/' ${output_dir}/metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   if [ ${mip_name} = 'ScenarioMIP' ]; then
     sed -i -e 's/"branch_time_in_child":         "0.0D"/"branch_time_in_child":         "60265.0D"/' ${output_dir}/metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
     sed -i -e 's/"branch_time_in_parent":        "0.0D"/"branch_time_in_parent":        "60265.0D"/' ${output_dir}/metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   fi
   mv -f ${xls_ece_dir} ${xls_ece_dir}-plev36
  fi

  if [ ${data_request_file##*/} = 'cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx' ] || [ ${data_request_file##*/} = 'cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx' ]; then
   ./revert-nested-cmor-table-branch.sh
  fi

  if [ ${data_request_file##*/} = 'cmvme_CMIP_ssp245_1_1-additional.xlsx' ] && [ ${mip_name} != 'CovidMIP' ]; then
   rm -f ${output_dir}/pptdddddd0300    # Prevent any 3 hourly raw output
  #sed -i -e 's/EC-Earth3/EC-Earth3-RT/' -e 's/(2019)/(2020)/' ${output_dir}/metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   mv -f ${xls_ece_dir} ${xls_ece_dir}-compact
  fi

  echo
  echo ' Finished:'
  echo ' '$0 "$@"
  echo

else
    echo
    echo '  This scripts requires five arguments: path/data-request-filename, MIP name, MIP experiment, EC-Earth3 configuration, output directory, e.g.:'
    echo '  ' $0 ../resources/miscellaneous-data-requests/lamaclima/lamaclima-data-request-varlist-EC-EARTH-Veg.json        LAMACLIMA   ssp585-lamaclima    EC-EARTH-Veg   lamaclima-control-output-files/ssp585-lamaclima-EC-EARTH-Veg
    echo
    echo '  ' $0 ../resources/miscellaneous-data-requests/compact-request/cmvme_CMIP_ssp245_1_1-additional.xlsx             CMIP        piControl           EC-EARTH-AOGCM compact-request
    echo
    echo '  ' $0 ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx  CMIP        historical          EC-EARTH-AOGCM rcm-dynamic-plev-forcing/EC-EARTH-AOGCM/historical-plev23
    echo '  ' $0 ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx  ScenarioMIP ssp126              EC-EARTH-AOGCM rcm-dynamic-plev-forcing/EC-EARTH-AOGCM/ssp126-plev23
    echo '  ' $0 ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx  ScenarioMIP ssp245              EC-EARTH-AOGCM rcm-dynamic-plev-forcing/EC-EARTH-AOGCM/ssp245-plev23
    echo '  ' $0 ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev23r.xlsx  ScenarioMIP ssp585              EC-EARTH-AOGCM rcm-dynamic-plev-forcing/EC-EARTH-AOGCM/ssp585-plev23
    echo '  ' $0 ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx   CMIP        historical          EC-EARTH-AOGCM rcm-dynamic-plev-forcing/EC-EARTH-AOGCM/historical-plev36
    echo '  ' $0 ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx   ScenarioMIP ssp126              EC-EARTH-AOGCM rcm-dynamic-plev-forcing/EC-EARTH-AOGCM/ssp126-plev36
    echo '  ' $0 ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx   ScenarioMIP ssp245              EC-EARTH-AOGCM rcm-dynamic-plev-forcing/EC-EARTH-AOGCM/ssp245-plev36
    echo '  ' $0 ../resources/miscellaneous-data-requests/knmi23-dutch-scenarios/cmvme_CMIP_ssp245_1_1-knmi23-plev36.xlsx   ScenarioMIP ssp585              EC-EARTH-AOGCM rcm-dynamic-plev-forcing/EC-EARTH-AOGCM/ssp585-plev36
    echo
    echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-baseline     EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-ssp245-baseline
    echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-covid        EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-ssp245-covid
    echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-cov-strgreen EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-ssp245-cov-strgreen
    echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-cov-modgreen EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-ssp245-cov-modgreen
    echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-cov-fossil   EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-ssp245-cov-fossil
    echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-cov-aer      EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-ssp245-cov-aer
   #echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP/cmvme_CMIP_ssp245_1_1-additional.xlsx CovidMIP    ssp245-cov-GHG      EC-EARTH-AOGCM CovidMIP/cmip6-experiment-CovidMIP-sssp245-cov-GHG
    echo
fi
