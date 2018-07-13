#!/bin/bash
# Thomas Reerink
#
# This script produces the "ready to copy" ec-earth-cmip6-nemo-namelists for the ctrl/ directory in ec-earth3 for
#  DECK+historical (=CMIP)
#
# First TO BE ADDED other EC-EARTH3-AOGCM-mips:
#  EC-EARTH3-AOGCM-mips    DCPP,LS3MIP,PAMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB
# Outside this subset other MIPs are among the other EC-EARTH3 model configurations:
#  EC-EARTH3-HR-mips       DCPP,HighResMIP
#  EC-EARTH3-LR-mips       PMIP
#  EC-EARTH3-CC-mips       C4MIP,LUMIP
#  EC-EARTH3-GrisIS-mips   ISMIP6,PMIP
#  EC-EARTH3-AerChem-mips  AerChemMIP
#  EC-EARTH3-Veg-mips      LUMIP,LS3MIP,ScenarioMIP
#  EC-EARTH3-Veg-LR-mips   PMIP,ScenarioMIP
#
# In the end all MIps EC-EARTH3 participates in have to be added:
#  AerChemMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,PAMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB,DAMIP CMIP 1 1
#
# This scripts requires no arguments
#
# Run example:
#  ./pack-for-test-branch.sh
#

if [ "$#" -eq 0 ]; then

 rm -rf ec-earth-cmip6-nemo-namelists


 # DECK+HISTORICAL
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

 mkdir -p DECK+historical
 mv -f cmip6-experiment-m=* DECK+historical/
 cd ../


 # DCPP
 ./generate-ec-earth-namelists.sh DCPP dcppC-pac-control          1 1
 ./generate-ec-earth-namelists.sh DCPP dcppC-ipv-pos              1 1
 ./generate-ec-earth-namelists.sh DCPP dcppC-ipv-neg              1 1
 ./generate-ec-earth-namelists.sh DCPP dcppC-hindcast-noPinatubo  1 1
 ./generate-ec-earth-namelists.sh DCPP dcppC-forecast-addPinatubo 1 1
 ./generate-ec-earth-namelists.sh DCPP dcppC-atl-control          1 1
 ./generate-ec-earth-namelists.sh DCPP dcppC-amv-pos              1 1
 ./generate-ec-earth-namelists.sh DCPP dcppC-amv-neg              1 1
 ./generate-ec-earth-namelists.sh DCPP dcppB-forecast             1 1
 ./generate-ec-earth-namelists.sh DCPP dcppA-hindcast             1 1

 cd ec-earth-cmip6-nemo-namelists
 rm -rf cmip6-experiment-m=*/file_def-compact
 rm -f  cmip6-experiment-m=*/cmip6-file_def_nemo.xml

 mkdir -p DCPP
 mv -f cmip6-experiment-m=* DCPP/
 cd ../


else
    echo '  '
    echo '  This scripts requires no arguments'
    echo '  ' $0
    echo '  '
fi
