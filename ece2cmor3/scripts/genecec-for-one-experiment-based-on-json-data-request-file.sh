#!/usr/bin/env bash
# Thomas Reerink
#
# Run examples:
#  ./genecec-for-one-experiment-based-on-json-data-request-file.sh ../resources/miscellaneous-data-requests/lamaclima/lamaclima-data-request-varlist-EC-EARTH-Veg.json LAMACLIMA lamaclima_ssp585 EC-EARTH-Veg
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
#
# The earlier approaches used:
#  cd ../resources/miscellaneous-data-requests
#  drq -m CMIP,DCPP,LS3MIP,ScenarioMIP,CORDEX,DynVarMIP,VIACSAB -e ssp245 -t 1 -p 1 --xls --xlsDir cmip6-data-request-CovidMIP-scenariomip-EC-EARTH-AOGCM
#  cd cmip6-data-request-CovidMIP-scenariomip-EC-EARTH-AOGCM/
#  cp cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr-no-6hrLev.xlsx
# Then manually remove the 3hr and 6hrLev variables from the cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr-no-6hrLev.xlsx.

#  drq -m CMIP,DCPP,LS3MIP,PAMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB -e ssp245 -t 1 -p 1 --xls --xlsDir cmip6-data-request-CovidMIP-cmip-EC-EARTH-AOGCM

if [ "$#" -eq 4 ]; then

  data_request_file=$1

  mip_name=$2
  experiment=$3
  ece_configuration=$4


  output_dir=${experiment}-${ece_configuration}-request-1

  if [ ${mip_name} = 'CovidMIP' ]; then
   output_dir=cmip6-experiment-CovidMIP-${experiment}
  fi

  # Distinguish between a json & xlsx file:
  if [ ${data_request_file:(-4)} = 'json' ]; then
   request_option='--vars'
  else
   request_option='--drq'
  fi

  rm -rf   ${output_dir}
  mkdir -p ${output_dir}

  if [ ${request_option} = '--vars' ]; then
   rsync -a ${data_request_file} ${output_dir}
  fi

  ./drq2file_def-nemo.py ${request_option} ${data_request_file}

  mv xios-nemo-file_def-files/cmip6-file_def_nemo.xml          ${output_dir}
  mv xios-nemo-file_def-files/file_def_nemo-opa.xml            ${output_dir}
  mv xios-nemo-file_def-files/file_def_nemo-lim3.xml           ${output_dir}
  mv xios-nemo-file_def-files/file_def_nemo-pisces.xml         ${output_dir}
  mv xios-nemo-file_def-files/file_def_nemo-opa-compact.xml    ${output_dir}
  mv xios-nemo-file_def-files/file_def_nemo-pisces-compact.xml ${output_dir}
  mv xios-nemo-file_def-files/file_def_nemo-lim3-compact.xml   ${output_dir}
  mv volume-estimate-nemo.txt                                  ${output_dir}

  cd ${output_dir}

  ../drq2ppt.py ${request_option} ../${data_request_file}
  ../drq2ins.py ${request_option} ../${data_request_file}
  if [ ${request_option} = '--drq' ]; then
   ../drq2varlist.py ${request_option} ../${data_request_file} --ececonf EC-EARTH-AOGCM --varlist cmip6-data-request-varlist-${mip_name}-${experiment}-${ece_configuration}.json
  fi

  # Remove the cmip6-file_def_nemo.xml file & the compact file_def files:
  rm -f cmip6-file_def_nemo.xml *-compact.xml

  # Remove the freq_op attribute for the variable msftbarot (uoce_e3u_vsum_e2u_cumul) from the file_def_nemo.xml file #327 & e.g. #518-165 on the ec-earth portal
  sed -i -e 's/uoce_e3u_vsum_e2u_cumul. freq_op=.1ts/uoce_e3u_vsum_e2u_cumul/' file_def_nemo-opa.xml

  # Remove deptho from the file_def_nemo-opa.xml #249
  sed -i -e '/deptho/d' file_def_nemo-opa.xml

  # Switching the 'transect' variables off (the transect grid definition seems to depend on the XIOS 2.5 upgrade)
  sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' file_def_nemo*

  # Estimating the Volume of the TM5 output:
  ../estimate-tm5-volume.py ${request_option} ../${data_request_file}

  cat volume-estimate-ifs.txt volume-estimate-nemo.txt volume-estimate-tm5.txt volume-estimate-lpj-guess.txt > volume-estimate-${mip_name}-${experiment}.txt
  rm -f volume-estimate-ifs.txt volume-estimate-nemo.txt volume-estimate-tm5.txt volume-estimate-lpj-guess.txt

  cd ../
  # Produce the metadata files for this MIP experiment.
  ./modify-metadata-template.sh ${mip_name} ${experiment} ${ece_configuration};

  if [ ${mip_name} = 'CovidMIP' ]; then
   if [ ${experiment} = 'ssp245-baseline' ]; then
    sed -i -e 's/"parent_activity_id":           ""/"parent_activity_id":           "CMIP"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"parent_experiment_id":         ""/"parent_experiment_id":         "historical"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"branch_time_in_child":         "0.0D"/"branch_time_in_child":         "60265.0D"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"branch_time_in_parent":        "0.0D"/"branch_time_in_parent":        "60265.0D"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   else
    sed -i -e 's/"parent_activity_id":           ""/"parent_activity_id":           "DAMIP"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"parent_experiment_id":         ""/"parent_experiment_id":         "ssp245-baseline"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"branch_time_in_child":         "0.0D"/"branch_time_in_child":         "62091.0D"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
    sed -i -e 's/"branch_time_in_parent":        "0.0D"/"branch_time_in_parent":        "62091.0D"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   fi

   sed -i -e 's/"activity_id":                  "CovidMIP"/"activity_id":                  "DAMIP"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   sed -i -e 's/"forcing_index":                "1"/"forcing_index":                "2"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
  #sed -i -e 's/"#variant_info".*/"variant_info":                 "The f2 forcing referes to an update forcing of the XX data set which has been used in all covid experiments.",/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   sed -i -e 's/"#variant_info".*/"variant_info":                 "This experiment belongs to the set of CovidMIP experiments for which updated forcing aerosols data (MACv2-SP) have been provided, see https://gmd.copernicus.org/articles/12/989/2019/",/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json
   sed -i -e 's/"parent_variant_label":         "r1i1p1f1"/"parent_variant_label":         "r1i1p1f2"/' metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json

   # Prevent any 3 hourly raw output:
   rm -f ${output_dir}/pptdddddd0300
  fi

  mv -f metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json ${output_dir}

  if [ ${mip_name} = 'CovidMIP' ]; then
   mkdir -p CovidMIP
   mv -f ${output_dir} CovidMIP
  fi

  echo ' Finished:'
  echo '  '$0 $1 $2 $3 $4
  echo

else
    echo
    echo '  This scripts requires four arguments: MIP, MIP experiment, experiment tier, priority of variable, e.g.:'
    echo '  ' $0 ../resources/miscellaneous-data-requests/lamaclima/lamaclima-data-request-varlist-EC-EARTH-Veg.json LAMACLIMA lamaclima_ssp585 EC-EARTH-Veg
    echo
    echo '  ' $0 ../resources/miscellaneous-data-requests/CovidMIP/cmip6-data-request-varlist-ScenarioMIP-ssp245-EC-EARTH-AOGCM-covidmip.json CovidMIP ssp245-baseline     EC-EARTH-AOGCM
    echo '  ' $0 ../resources/miscellaneous-data-requests/CovidMIP/cmip6-data-request-varlist-ScenarioMIP-ssp245-EC-EARTH-AOGCM-covidmip.json CovidMIP ssp245-covid        EC-EARTH-AOGCM
    echo '  ' $0 ../resources/miscellaneous-data-requests/CovidMIP/cmip6-data-request-varlist-ScenarioMIP-ssp245-EC-EARTH-AOGCM-covidmip.json CovidMIP ssp245-cov-strgreen EC-EARTH-AOGCM
    echo '  ' $0 ../resources/miscellaneous-data-requests/CovidMIP/cmip6-data-request-varlist-ScenarioMIP-ssp245-EC-EARTH-AOGCM-covidmip.json CovidMIP ssp245-cov-modgreen EC-EARTH-AOGCM
    echo '  ' $0 ../resources/miscellaneous-data-requests/CovidMIP/cmip6-data-request-varlist-ScenarioMIP-ssp245-EC-EARTH-AOGCM-covidmip.json CovidMIP ssp245-cov-fossil   EC-EARTH-AOGCM
    echo '  ' $0 ../resources/miscellaneous-data-requests/CovidMIP/cmip6-data-request-varlist-ScenarioMIP-ssp245-EC-EARTH-AOGCM-covidmip.json CovidMIP ssp245-cov-aer      EC-EARTH-AOGCM
   #echo '  ' $0 ../resources/miscellaneous-data-requests/CovidMIP/cmip6-data-request-varlist-ScenarioMIP-ssp245-EC-EARTH-AOGCM-covidmip.json CovidMIP ssp245-cov-GHG      EC-EARTH-AOGCM
    echo
    echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP-scenariomip-EC-EARTH-AOGCM/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr-no-6hrLev.xlsx CovidMIP ssp245-baseline     EC-EARTH-AOGCM
    echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP-scenariomip-EC-EARTH-AOGCM/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr-no-6hrLev.xlsx CovidMIP ssp245-covid        EC-EARTH-AOGCM
    echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP-scenariomip-EC-EARTH-AOGCM/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr-no-6hrLev.xlsx CovidMIP ssp245-cov-strgreen EC-EARTH-AOGCM
    echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP-scenariomip-EC-EARTH-AOGCM/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr-no-6hrLev.xlsx CovidMIP ssp245-cov-modgreen EC-EARTH-AOGCM
    echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP-scenariomip-EC-EARTH-AOGCM/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr-no-6hrLev.xlsx CovidMIP ssp245-cov-fossil   EC-EARTH-AOGCM
    echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP-scenariomip-EC-EARTH-AOGCM/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr-no-6hrLev.xlsx CovidMIP ssp245-cov-aer      EC-EARTH-AOGCM
   #echo '  ' $0 ../resources/miscellaneous-data-requests/cmip6-data-request-CovidMIP-scenariomip-EC-EARTH-AOGCM/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr-no-6hrLev.xlsx CovidMIP ssp245-cov-GHG      EC-EARTH-AOGCM
    echo
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr.xlsx CovidMIP ssp245-baseline               EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr.xlsx CovidMIP ssp245-covid                  EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr.xlsx CovidMIP ssp245-cov-strgreen           EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr.xlsx CovidMIP ssp245-cov-modgreen           EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr.xlsx CovidMIP ssp245-cov-fossil             EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr.xlsx CovidMIP ssp245-cov-aer                EC-EARTH-AOGCM
   #echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-3hr.xlsx CovidMIP ssp245-cov-GHG                EC-EARTH-AOGCM
    echo
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-6hrLev.xlsx CovidMIP ssp245-baseline            EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-6hrLev.xlsx CovidMIP ssp245-covid               EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-6hrLev.xlsx CovidMIP ssp245-cov-strgreen        EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-6hrLev.xlsx CovidMIP ssp245-cov-modgreen        EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-6hrLev.xlsx CovidMIP ssp245-cov-fossil          EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-6hrLev.xlsx CovidMIP ssp245-cov-aer             EC-EARTH-AOGCM
   #echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1-no-6hrLev.xlsx CovidMIP ssp245-cov-GHG             EC-EARTH-AOGCM
    echo
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-baseline                      EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-covid                         EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-cov-strgreen                  EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-cov-modgreen                  EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-cov-fossil                    EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-cov-aer                       EC-EARTH-AOGCM
   #echo '  ' $0 cmip6-data-request-CovidMIP/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-cov-GHG                       EC-EARTH-AOGCM
    echo
    echo '  ' $0 cmip6-data-request/cmip6-data-request-m=CMIP.DCPP.LS3MIP.ScenarioMIP.CORDEX.DynVarMIP.VIACSAB-e=ssp245-t=1-p=1/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-baseline                      EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request/cmip6-data-request-m=CMIP.DCPP.LS3MIP.ScenarioMIP.CORDEX.DynVarMIP.VIACSAB-e=ssp245-t=1-p=1/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-covid                         EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request/cmip6-data-request-m=CMIP.DCPP.LS3MIP.ScenarioMIP.CORDEX.DynVarMIP.VIACSAB-e=ssp245-t=1-p=1/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-cov-strgreen                  EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request/cmip6-data-request-m=CMIP.DCPP.LS3MIP.ScenarioMIP.CORDEX.DynVarMIP.VIACSAB-e=ssp245-t=1-p=1/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-cov-modgreen                  EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request/cmip6-data-request-m=CMIP.DCPP.LS3MIP.ScenarioMIP.CORDEX.DynVarMIP.VIACSAB-e=ssp245-t=1-p=1/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-cov-fossil                    EC-EARTH-AOGCM
    echo '  ' $0 cmip6-data-request/cmip6-data-request-m=CMIP.DCPP.LS3MIP.ScenarioMIP.CORDEX.DynVarMIP.VIACSAB-e=ssp245-t=1-p=1/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-cov-aer                       EC-EARTH-AOGCM
   #echo '  ' $0 cmip6-data-request/cmip6-data-request-m=CMIP.DCPP.LS3MIP.ScenarioMIP.CORDEX.DynVarMIP.VIACSAB-e=ssp245-t=1-p=1/cmvme_cm.co.dc.dy.ls.sc.vi_ssp245_1_1.xlsx CovidMIP ssp245-cov-GHG                       EC-EARTH-AOGCM
    echo
fi
