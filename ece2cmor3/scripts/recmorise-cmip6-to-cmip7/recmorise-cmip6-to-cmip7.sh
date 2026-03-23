#!/usr/bin/env bash
#
# This script creates the run-recmorise-cmip6-to-cmip7.sh script which calls the recmorise-cmip6-to-cmip7.py
# script for all CMIP6 variable combinations for a given CMIP6 top directory with CMIP6 cmorised data.
#
# This script requires no arguments.

# Adjust this path also in LOCAL_CMIP6_ROOT in recmorise-cmip6-to-cmip7.py:
 ece3_cmip6_data_dir_root=/scratch/nktr/test-data/CE42-test/
#ece3_cmip6_data_dir_root=~/cmorize/test-data-ece/CE37-test/

 for j in {3hr,6hrPlev,Amon,day,Efx,Emon,Eyr,fx,LImon,Lmon,Oday,Ofx,Omon,SIday,SImon,}; do
   for i in `/usr/bin/ls -1  ${ece3_cmip6_data_dir_root}/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-piControl/r1i1p1f1/$j`; do
     printf " ./recmorise-cmip6-to-cmip7.py  %-8s %-20s  &>> recmorise-cmip6-to-cmip7.log\n" $j ${i}
   done
   echo
 done > run-recmorise-cmip6-to-cmip7.sh

 chmod uog+x run-recmorise-cmip6-to-cmip7.sh

#./run-recmorise-cmip6-to-cmip7.sh


# day hur => CFday hur
