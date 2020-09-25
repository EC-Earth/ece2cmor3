#!/usr/bin/env bash
# Thomas Reerink
#
# Run examples:
#  ./genecec-for-one-experiment-based-on-json-data-request-file.sh ../resources/test-data-request/lamaclima-data-request-varlist-EC-EARTH-Veg.json LAMACLIMA lamaclima_ssp585 EC-EARTH-Veg

#
# With this script it is possible to generate the EC-Earth3 control output files, i.e.
# the IFS Fortran namelists (the ppt files), the NEMO xml files for XIOS (the
# file_def files for OPA, LIM and PISCES), the instruction file for LPJ_GUESS (the
# *.ins file) and the files required for the cmorisation for a certain MIP experiments.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.


if [ "$#" -eq 4 ]; then

  json_data_request_file=$1

  mip_name=$2
  experiment=$3
  ece_configuration=$4


  output_dir=${experiment}-${ece_configuration}-request-1
  rm -rf   ${output_dir}
  mkdir -p ${output_dir}

  rsync -a ${json_data_request_file} ${output_dir}

  ./drq2file_def-nemo.py  --vars    ${json_data_request_file}

  mv xios-nemo-file_def-files/cmip6-file_def_nemo.xml          ${output_dir}
  mv xios-nemo-file_def-files/file_def_nemo-opa.xml            ${output_dir}
  mv xios-nemo-file_def-files/file_def_nemo-lim3.xml           ${output_dir}
  mv xios-nemo-file_def-files/file_def_nemo-pisces.xml         ${output_dir}
  mv xios-nemo-file_def-files/file_def_nemo-opa-compact.xml    ${output_dir}
  mv xios-nemo-file_def-files/file_def_nemo-pisces-compact.xml ${output_dir}
  mv xios-nemo-file_def-files/file_def_nemo-lim3-compact.xml   ${output_dir}
  mv volume-estimate-nemo.txt                                  ${output_dir}

  cd ${output_dir}

  ../drq2ppt.py           --vars ../${json_data_request_file}
  ../drq2ins.py           --vars ../${json_data_request_file}

  # Remove the cmip6-file_def_nemo.xml file & the compact file_def files:
  rm -f cmip6-file_def_nemo.xml *-compact.xml

  # Remove the freq_op attribute for the variable msftbarot (uoce_e3u_vsum_e2u_cumul) from the file_def_nemo.xml file #327 & e.g. #518-165 on the ec-earth portal
  sed -i -e 's/uoce_e3u_vsum_e2u_cumul. freq_op=.1ts/uoce_e3u_vsum_e2u_cumul/' file_def_nemo-opa.xml

  # Remove deptho from the file_def_nemo-opa.xml #249
  sed -i -e '/deptho/d' file_def_nemo-opa.xml

  # Switching the 'transect' variables off (the transect grid definition seems to depend on the XIOS 2.5 upgrade)
  sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' file_def_nemo*

  # Estimating the Volume of the TM5 output:
  ../estimate-tm5-volume.py --vars ../${json_data_request_file}

  cat volume-estimate-ifs.txt volume-estimate-nemo.txt volume-estimate-tm5.txt volume-estimate-lpj-guess.txt > volume-estimate-${mip_name}-${experiment}.txt
  rm -f volume-estimate-ifs.txt volume-estimate-nemo.txt volume-estimate-tm5.txt volume-estimate-lpj-guess.txt

  cd ../
  # Produce the metadata files for this MIP experiment.
  ./modify-metadata-template.sh ${mip_name} ${experiment} ${ece_configuration};

  mv -f metadata-cmip6-${mip_name}-${experiment}-${ece_configuration}-*-template.json ${output_dir}

else
    echo '  '
    echo '  This scripts requires four arguments: MIP, MIP experiment, experiment tier, priority of variable, e.g.:'
    echo '  ' $0 ../resources/test-data-request/lamaclima-data-request-varlist-EC-EARTH-Veg.json LAMACLIMA lamaclima_ssp585 EC-EARTH-Veg
    echo '  '
fi
