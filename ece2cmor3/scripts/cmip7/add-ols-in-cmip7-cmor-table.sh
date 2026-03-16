#!/bin/bash
#
# This script adds ols to the list of vertical_label's in the cmip7-cmor-tables/tables-cvs/cmor-cvs.json
#
# This script requires no arguments.
#

if [ "$#" -eq 0 ]; then

 add_ols_to_vertical_labels=True

 if [ add_ols_to_vertical_labels ]; then
  # See #866  https://github.com/EC-Earth/ece2cmor3/issues/866

 #table_path=../resources/cmip7-cmor-tables/tables-cvs/
  table_path=~/cmorize/cmip7-cmor-tables/tables-cvs/
  table_file=cmor-cvs.json
  cd ${table_path}
  git checkout ${table_file}

  sed -i  '/"op4": /i \
            "ols": "Data is reported at sea surface.",' ${table_file}

  cd -

  echo
  echo " Running:"
  echo "  $0"
  echo " has adjusted the file:"
  echo "  ${table_path}/${table_file}"
  echo " which is part of the nested CMOR Table repository. View the diff by running:"
  echo "  cd ${table_path}; git diff; cd -"
  echo " This changes can be reverted by running:"
  echo "  cd ${table_path}; git checkout ${table_file}; cd -"
  echo

 else
  echo
  echo " Nothing done, no set of variables and / or experiments has been selected to add to the tables."
  echo
 fi

else
 echo
 echo " This scripts requires no argument:"
 echo "  $0"
 echo
fi
