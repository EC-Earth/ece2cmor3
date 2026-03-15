#!/usr/bin/env bash
#
# Recmorise CMIP6 cmorised data to CMIP7 cmorised data for ECE3-ESM-1.
#
# This scripts requires one argument: The path to the ripf directory of the CMIP6 cmorised data.
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

 if [ "$#" = 1 ]; then

   CMIP6DIR=$1

   if [ ! -d ${CMIP6DIR} ]; then echo -e "\e[1;31m Error:\e[0m"" Directory: ${CMIP6DIR}, does not exist. Abort $0"            >&2; exit 1; fi
   if [   -z ${CMIP6DIR} ]; then echo -e "\e[1;31m Error:\e[0m"" Empty directory, no cmorised data in: ${CMIP6DIR}. Abort $0" >&2; exit 1; fi

   module load gnuparallel

   source ${PERM}/mamba/etc/profile.d/conda.sh
   conda activate ece2cmor3

   export HDF5_USE_FILE_LOCKING=FALSE


   alias ls='/usr/bin/ls'
   tmpdir=.tmpdir-recmorise
   rm -f varlist
   for t in $(ls ${CMIP6DIR}); do for v in $(ls ${CMIP6DIR}/$t); do echo $t $v >> varlist; done; done
   sort varlist | uniq > varlist_sorted

   wc_varlist_1=`wc -l varlist        | sed 's/ .*//'`
   wc_varlist_2=`wc -l varlist_sorted | sed 's/ .*//'`

   if [ "${wc_varlist_1}" = "${wc_varlist_2}" ]; then
    echo " The number of CMIP6 cmorised variables is: ${wc_varlist_2}"
   else
    echo " The number of CMIP6 cmorised variables is: ${wc_varlist_2} but was reduced for duplicates from ${wc_varlist_1}"
   fi


   # Run the recmorise-cmip6-to-cmip7.py script via parallel calls on all variables in the CMIP6DIR:
   time cat varlist_sorted | parallel --colsep ' ' ./recmorise-cmip6-to-cmip7.py  -t ${tmpdir} {1} {2}

   mv varlist varlist_sorted ${tmpdir}/

 else
  account_info=`account -l $USER`
  echo
  echo " Illegal number of arguments: This submit script requires one argument: the path of the CMIP6 cmorised data, e.g.:"
  echo "  sbatch --qos=nf --cpus-per-task=4   --account=nlchekli $0 ~/cmorize/test-data-ece/CE37-test/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-piControl/r1i1p1f1/"
  echo "  sbatch --qos=nf --cpus-per-task=64  --account=nlchekli $0 /scratch/nktr/test-data/CE42-test/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-piControl/r1i1p1f1/"
  echo "  sbatch --qos=np --cpus-per-task=128 --account=nlchekli $0 /scratch/nktr/test-data/CE42-test/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-piControl/r1i1p1f1/"
  echo
  echo " Available accounts for ${USER} on hpc2020: ${account_info}"
  echo
 fi
