#!/usr/bin/env bash
#
# This script creates a run script which calls the recmorise-cmip6-to-cmip7.py
# script for all CMIP6 variable combinations for a given CMIP6 top directory with CMIP6 cmorised data.
#
# This script requires one argument.

 if [ "$#" = 1 ]; then
   config_file=$1

   run_script=run-recmorise-cmip6-to-cmip7.sh

   if [ ! -e ${config_file} ]; then
    echo; echo " The file ${config_file} does not exist."; echo
    exit
   fi

   # Catch all the path variables from the config file:
   ece3_cmip6_data_dir_root=`grep -e cmip6_input_dir_name ${config_file} | sed -e "s/.*= //" -e "s/'//g" -e 's/ .*//'`
   cmip6_source_id=`         grep -e cmip6_source_id      ${config_file} | sed -e "s/.*= //" -e "s/'//g" -e 's/ .*//'`
   institution_id=`          grep -e institution_id       ${config_file} | sed -e "s/.*= //" -e "s/'//g" -e 's/ .*//'`
   experiment_id=`           grep -e '^experiment_id'     ${config_file} | sed -e "s/.*= //" -e "s/'//g" -e 's/ .*//'`
   ripf_r=`                  grep -e ripf_r               ${config_file} | sed -e "s/.*= //" -e "s/'//g" -e 's/ .*//'`
   ripf_i=`                  grep -e ripf_i               ${config_file} | sed -e "s/.*= //" -e "s/'//g" -e 's/ .*//'`
   ripf_p=`                  grep -e ripf_p               ${config_file} | sed -e "s/.*= //" -e "s/'//g" -e 's/ .*//'`
   ripf_f=`                  grep -e ripf_f               ${config_file} | sed -e "s/.*= //" -e "s/'//g" -e 's/ .*//'`
   # Replace the tilde:
   ece3_cmip6_data_dir_root="${ece3_cmip6_data_dir_root/#\~/$HOME}"

   base_path=${ece3_cmip6_data_dir_root}CMIP6/CMIP/${institution_id}/${cmip6_source_id}/${experiment_id}/${ripf_r}${ripf_i}${ripf_p}${ripf_f}

   for j in {3hr,6hrPlev,Amon,day,Efx,Emon,Eyr,fx,LImon,Lmon,Oday,Ofx,Omon,SIday,SImon,}; do
     for i in `/usr/bin/ls -1 ${base_path}/$j`; do
       printf " ./recmorise-cmip6-to-cmip7.py  -r -c ${config_file} %-8s %-20s  &>> recmorise-cmip6-to-cmip7.log\n" $j ${i}
     done
     echo
   done > ${run_script}

   chmod uog+x ${run_script}

   ./${run_script}

   rm -f ${run_script}

 else
  echo
  echo " Illegal number of arguments: This submit script requires one argument:"
  echo "  1. A config file"
  echo
  echo " For instance:"
  echo "  $0 config-file-recmorisation"
  echo
 fi
