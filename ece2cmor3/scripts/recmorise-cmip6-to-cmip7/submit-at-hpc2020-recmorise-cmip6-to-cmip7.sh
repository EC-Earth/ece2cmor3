#!/usr/bin/env bash
#
# Recmorise CMIP6 cmorised data to CMIP7 cmorised data for ECE3-ESM-1-1.
#
# This scripts requires three arguments: 1. Initiate 2. A varlist 3. A config file.
#

#SBATCH --time=01:05:00
#SBATCH --job-name=recmorise-cmip6-to-cmip7
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --qos=nf
#SBATCH --output=stdout-recmorise-cmip6-to-cmip7.%j.out
#SBATCH --error=stderr-recmorise-cmip6-to-cmip7.%j.out
#SBATCH --mail-type=FAIL

# CMIP6DIR  is the directory with the cmorised data

 if [ "$#" = 3 ]; then

   initiate=$1
   selected_varlist=$2
   config_file=$3

   if [ "${initiate}" = "yes" ] || [ "${initiate}" = "no" ]; then
    echo
    echo " Running:"
    echo "  $0 $@"
    echo
   else
    echo
    echo " Error: The first argument of $0 has to have value 'yes' or 'no' but given was: ${initiate}"
    echo
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

   CMIP6DIR=${ece3_cmip6_data_dir_root}/CMIP6/CMIP/${institution_id}/${cmip6_source_id}/${experiment_id}/${ripf_r}${ripf_i}${ripf_p}${ripf_f}/

   if [ ! -d ${CMIP6DIR} ]; then echo -e "\e[1;31m Error:\e[0m"" Directory: ${CMIP6DIR}, does not exist. Abort $0"            >&2; exit 1; fi
   if [   -z ${CMIP6DIR} ]; then echo -e "\e[1;31m Error:\e[0m"" Empty directory, no cmorised data in: ${CMIP6DIR}. Abort $0" >&2; exit 1; fi

   if [ "$ECPLATFORM" = "hpc2020" ]; then
    module load gnuparallel

    source ${PERM}/mamba/etc/profile.d/conda.sh
   else
    source ${HOME}/mamba/etc/profile.d/conda.sh
   fi

   conda activate ece2cmor3
   esgvoc use cmip7@latest universe@latest
   echo

   # This option and thus the corresponding argument can be removed as soon as the tables don't need any adjustment anymore.
   if [ "${initiate}" = "yes" ]; then
    # As long as the EMD registration is not finished: dd EC-Earth3-ESM-1 & EC-Earth3-ESM-1-1 to the file: cmip7-cmor-tables/tables-cvs/cmor-cvs.json
    ./add-ECE3-ESM-1-1-to-cmip7-cmor-table.sh
   fi

   alias ls='/usr/bin/ls'
   rm -f varlist
   for t in $(ls ${CMIP6DIR}); do for v in $(ls ${CMIP6DIR}/$t); do echo $t $v >> varlist; done; done
   sort varlist | uniq > varlist_sorted

   wc_varlist_1=`wc -l varlist        | sed 's/ .*//'`
   wc_varlist_2=`wc -l varlist_sorted | sed 's/ .*//'`

   if [ "${wc_varlist_1}" = "${wc_varlist_2}" ]; then
    echo
    echo " The number of CMIP6 cmorised variables is: ${wc_varlist_2}"
    echo
   else
    echo
    echo " The number of CMIP6 cmorised variables is: ${wc_varlist_2} but was reduced for duplicates from ${wc_varlist_1}"
    echo
   fi

   grep -v -e 3hr -e 6hrPlev varlist_sorted > varlist_sorted_low_frequent
   grep    -e 3hr -e 6hrPlev varlist_sorted > varlist_sorted_high_frequent

   if [ -f ${selected_varlist} ]; then
    tmpdir=logs-recmorise

    # Run the recmorise-cmip6-to-cmip7.py script via parallel calls on all variables in the CMIP6DIR:
    time cat ${selected_varlist} | parallel --colsep ' ' ./recmorise-cmip6-to-cmip7.py -e -t ${tmpdir} -r -c ${config_file} {1} {2}

    mkdir -p ${tmpdir}/varlists
    mv varlist varlist_sorted varlist_sorted_low_frequent varlist_sorted_high_frequent ${tmpdir}/varlists
   else
     echo " The varlist ${selected_varlist} does not exist."
   fi

 else
  account_info=`account -l $USER`
  echo
  echo " Illegal number of arguments: This submit script requires two arguments:"
  echo "  1. Initiate: yes or no. If yes this applies the changes to the cmip7 tables."
  echo "  2. A varlist: The varlist_sorted, varlist_sorted_low_frequent & varlist_sorted_high_frequent are generated on the flow based on the data path (second argument)."
  echo "  3. The config file."
  echo
  echo " For instance:"
  echo
  echo "  On a desktop without sbatch this can be run like:"
  echo "   $0 yes varlist_sorted config-file-recmorisation-desktop"
  echo
  echo "  On hpc-2020 with sbatch this can be run like:"
  echo "   sbatch --qos=np --cpus-per-task=128 --account=nlchekli $0 yes varlist_sorted               config-file-recmorisation"
  echo "   sbatch --qos=nf --cpus-per-task=64  --account=nlchekli $0 yes varlist_sorted_low_frequent  config-file-recmorisation"
  echo "   sbatch --qos=nf --cpus-per-task=7   --account=nlchekli $0 no  varlist_sorted_high_frequent config-file-recmorisation"
  echo "  The recommended recmorisation approach on hpc2020 is to use one full node (for memory reasons):"
  echo "   sbatch --qos=np --cpus-per-task=128 --account=nlchekli $0 yes varlist_sorted  config-file-recmorisation"
  echo
  echo " Available accounts for ${USER} on hpc2020: ${account_info}"
  echo
 fi
