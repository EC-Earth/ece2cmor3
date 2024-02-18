#!/bin/bash
# Thomas Reerink
#
# This script adds / inserts some non-cmor metadata for the VAREX project which thus
# does not exit in the CMIP6 data request.
#
# This scripts requires no arguments.
#

if [ "$#" -eq 0 ]; then

 add_the_varex_experiments=True

 if [ add_the_varex_experiments ]; then
  # See #728   https://github.com/EC-Earth/ece2cmor3/issues/728
  # See #1062  https://dev.ec-earth.org/issues/1062

  # VAREX

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_cv=CMIP6_CV.json

  # Always first revert the CMOR table file in its repository:
  cd ${table_path}
  git checkout ${table_file_cv}

  # Add KNMI as an institute with its own institution_id:
  sed -i  '/"KIOST":/i \
            "KNMI":"The Royal Netherlands Meteorological Institute (KNMI), De Bilt, The Netherlands",
  ' ${table_file_cv}

  # Adjust the license such that it matches with the production institute KNMI.
  sed -i -e 's/CMIP6 model data/The VAREX model data/' -e 's/Consult.*acknowledgment//' ${table_file_cv}

  # Allow KNMI on it self to be a institute which produces EC-Earth3 experiments:
  # This insert is vulnerable for upstream table changes within 20 lines after the match:
  sed -i -e '/"EC-Earth3":{/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;a\                    "KNMI",' ${table_file_cv}

  # Allow a historical experiment to have a parent_experiment_id which is an historical experiment as well:
  # This insert is vulnerable for upstream table changes within 15 lines after the match:
  sed -i -e '/            "historical":{/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;a\                    "historical",' ${table_file_cv}

  cd -

  echo
  echo " Running:"
  echo "  $0"
  echo " has adjusted the file:"
  echo "  ${table_path}/${table_file_cv}"
  echo " which is part of the nested CMOR Table repository. View the diff by running:"
  echo "  cd ${table_path}; git diff; cd -"
  echo " This changes can be reverted by running:"
  echo "  ./revert-nested-cmor-table-branch.sh"
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
