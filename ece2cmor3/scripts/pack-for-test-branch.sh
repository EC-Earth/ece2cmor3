#!/bin/bash
# Thomas Reerink
#
# This script produces the "ready to copy" ec-earth-cmip6-nemo-namelists for the ctrl/ directory in ec-earth3.
#
# This scripts requires no arguments
#
# Run example:
#  ./pack-for-test-branch.sh
#

if [ "$#" -eq 0 ]; then

 rm -rf ec-earth-cmip6-nemo-namelists

 ./generate-ec-earth-namelists.sh CMIP 1pctCO2      1 1
 ./generate-ec-earth-namelists.sh CMIP abrupt-4xCO2 1 1
 ./generate-ec-earth-namelists.sh CMIP amip         1 1
 ./generate-ec-earth-namelists.sh CMIP historical   1 1
 ./generate-ec-earth-namelists.sh CMIP piControl    1 1

 cd ec-earth-cmip6-nemo-namelists
 rm -rf cmip6-experiment-m=*/file_def-compact
 rm -f  cmip6-experiment-m=*/cmip6-file_def_nemo.xml

 sed -i -e 's/True\" field_ref=\"toce_pot/False\" field_ref=\"toce_pot/' cmip6-experiment-m=CMIP-e=amip-t=1-p=1/file_def_nemo-opa.xml
 sed -i -e 's/True\" field_ref=\"toce_pot/False\" field_ref=\"toce_pot/' cmip6-experiment-m=CMIP-e=1pctCO2-t=1-p=1/file_def_nemo-opa.xml
 sed -i -e 's/True\" field_ref=\"toce_pot/False\" field_ref=\"toce_pot/' cmip6-experiment-m=CMIP-e=abrupt-4xCO2-t=1-p=1/file_def_nemo-opa.xml
 sed -i -e 's/True\" field_ref=\"toce_pot/False\" field_ref=\"toce_pot/' cmip6-experiment-m=CMIP-e=piControl-t=1-p=1/file_def_nemo-opa.xml
 sed -i -e 's/True\" field_ref=\"toce_pot/False\" field_ref=\"toce_pot/' cmip6-experiment-m=CMIP-e=historical-t=1-p=1/file_def_nemo-opa.xml

else
    echo '  '
    echo '  This scripts requires no arguments'
    echo '  ' $0
    echo '  '
fi
