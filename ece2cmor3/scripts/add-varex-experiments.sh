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

  # Always first revert the CMOR table file in its repository:
  cd ../resources/cmip6-cmor-tables
  git checkout Tables/CMIP6_CV.json
  cd -


  # Add KNMI as an institute with its own institution_id:
  sed -i  '/"KIOST":/i \
            "KNMI":"The Royal Netherlands Meteorological Institute (KNMI), De Bilt, The Netherlands",
  ' ../resources/tables/CMIP6_CV.json

  # Adjust the license such that it matches with the production institute KNMI.
  sed -i -e 's/CMIP6 model data/The VAREX model data/' -e 's/Consult.*acknowledgment//' ../resources/tables/CMIP6_CV.json

  # Allow KNMI on it self to be a institute which produces EC-Earth3 experiments:
  # This insert is vulnerable for upstream table changes within 20 lines after the match:
  sed -i -e '/"EC-Earth3":{/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;a\                    "KNMI",' ../resources/tables/CMIP6_CV.json

  # Allow a historical experiment to have a parent_experiment_id which is an historical experiment as well:
  # This insert is vulnerable for upstream table changes within 15 lines after the match:
  sed -i -e '/            "historical":{/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;a\                    "historical",' ../resources/tables/CMIP6_CV.json

 else
    echo '  '
    echo '  Nothing done, no set of variables and / or experiments has been selected to add to the tables.'
    echo '  '
 fi

else
    echo '  '
    echo '  This scripts requires no argument:'
    echo '  ' $0
    echo '  '
fi
