#!/usr/bin/env bash
# Thomas Reerink
#
# This script creates CMIP6plus tables from the two required repositories (before for CMIP6 only one repositpry was needed).
#
# This scripts requires one argument: the path of the dir in which the new tables are downloaded
#
# For examples how to call this script, run it without arguments.
#

if [ "$#" -eq 1 ]; then

 dir_for_tables=$1

 echo
 if [ ! -d ${dir_for_tables} ]; then
  echo "Create ${dir_for_tables}"
  echo
  mkdir -p ${dir_for_tables}
 fi

 cd ${dir_for_tables}

 # Download the CMIP6Plus CV repository:
 if [ -d ${dir_for_tables}/CMIP6Plus_CVs ]; then
  cd ${dir_for_tables}/CMIP6Plus_CVs
  git pull
  cd ${dir_for_tables}
 else
  git clone https://github.com/WCRP-CMIP/CMIP6Plus_CVs/
 fi

 # Download the MIP tables repository:
 if [ -d ${dir_for_tables}/mip-cmor-tables ]; then
  cd ${dir_for_tables}/mip-cmor-tables
  git pull
  cd ${dir_for_tables}
 else
  git clone https://github.com/PCMDI/mip-cmor-tables
 fi

 # Create a new directory which from structure resembles the CMIP6 tables repository
 # with links to the two repositories which contain for CMIP6Plus the required files:
 mkdir -p cmip6plus-tables

 # Populate this new directory with the links to the concerning files:
 cd cmip6plus-tables
 ln -sf ${dir_for_tables}/mip-cmor-tables/{Auxillary_files,Tables}/* .
 ln -sf ${dir_for_tables}/CMIP6Plus_CVs/CVs/CMIP6Plus_CV.json .

 echo
 echo "In order to make use of the CMI6Plus tables set the following optional ece2cmor arguments:"
 echo " --tabledir ${dir_for_tables}/cmip6plus-tables"
 echo " --tableprefix MIP"
 echo

else
  echo
  echo " This scripts requires one argument (the path of the dir of the new tables), e.g.:"
  echo "  $0 \${HOME}/cmorize/"
  echo "  $0 \${PERM}/cmorize/"
  echo
fi
