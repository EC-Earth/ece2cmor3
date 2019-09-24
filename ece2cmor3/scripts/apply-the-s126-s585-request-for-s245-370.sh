#!/bin/bash
# Thomas Reerink
#
# This scripts needs one argument:
#
# ${1} the first   argument is the name of the control-output-files directory.
#
#
# Run example:
#  ./apply-the-s126-s585-request-for-s245-370.sh control-output-files
#
# With this script the ScenarioMIP requests for ScenarioMIP-ssp245 & ScenarioMIP-ssp370 are taken equal to the ones of ScenarioMIP-ssp585 & ScenarioMIP-ssp126.
# We consider it as a flaw in the data request that they differ, see also issue 517: https://github.com/EC-Earth/ece2cmor3/issues/517
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.
#
# Note that this script is called at the end of the script:
#  genecec.py


if [ "$#" -eq 1 ]; then

 # The name of the control output files directory:
 cofdir=$1

# Generating the lists has been done with help of:
#  ls ScenarioMIP/*/cmip6-experiment-ScenarioMIP-ssp[5]*/ppt0000000000 ScenarioMIP/*/cmip6-experiment-ScenarioMIP-ssp[5]*/pptdddddd0600 ScenarioMIP/*/cmip6-experiment-ScenarioMIP-ssp[5]*/cmip6-data-request-varlist-ScenarioMIP-ssp*-EC-EARTH-*.json
#  ls ScenarioMIP/*/cmip6-experiment-ScenarioMIP-ssp[2-3]*/ppt0000000000 ScenarioMIP/*/cmip6-experiment-ScenarioMIP-ssp[2-3]*/pptdddddd0600 ScenarioMIP/*/cmip6-experiment-ScenarioMIP-ssp[2-3]*/cmip6-data-request-varlist-ScenarioMIP-ssp*-EC-EARTH-*.json

# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-AerChem/cmip6-experiment-ScenarioMIP-ssp585/cmip6-data-request-varlist-ScenarioMIP-ssp585-EC-EARTH-AerChem.json   ${cofdir}/ScenarioMIP/EC-EARTH-AerChem/cmip6-experiment-ScenarioMIP-ssp245/cmip6-data-request-varlist-ScenarioMIP-ssp245-EC-EARTH-AerChem.json
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-AerChem/cmip6-experiment-ScenarioMIP-ssp585/ppt0000000000                                                         ${cofdir}/ScenarioMIP/EC-EARTH-AerChem/cmip6-experiment-ScenarioMIP-ssp245/ppt0000000000
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-AerChem/cmip6-experiment-ScenarioMIP-ssp585/pptdddddd0600                                                         ${cofdir}/ScenarioMIP/EC-EARTH-AerChem/cmip6-experiment-ScenarioMIP-ssp245/pptdddddd0600
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-AerChem/cmip6-experiment-ScenarioMIP-ssp585/cmip6-data-request-varlist-ScenarioMIP-ssp585-EC-EARTH-AerChem.json   ${cofdir}/ScenarioMIP/EC-EARTH-AerChem/cmip6-experiment-ScenarioMIP-ssp370/cmip6-data-request-varlist-ScenarioMIP-ssp370-EC-EARTH-AerChem.json
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-AerChem/cmip6-experiment-ScenarioMIP-ssp585/ppt0000000000                                                         ${cofdir}/ScenarioMIP/EC-EARTH-AerChem/cmip6-experiment-ScenarioMIP-ssp370/ppt0000000000
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-AerChem/cmip6-experiment-ScenarioMIP-ssp585/pptdddddd0600                                                         ${cofdir}/ScenarioMIP/EC-EARTH-AerChem/cmip6-experiment-ScenarioMIP-ssp370/pptdddddd0600
  cp -f ${cofdir}/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp585/cmip6-data-request-varlist-ScenarioMIP-ssp585-EC-EARTH-AOGCM.json       ${cofdir}/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp245/cmip6-data-request-varlist-ScenarioMIP-ssp245-EC-EARTH-AOGCM.json
  cp -f ${cofdir}/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp585/ppt0000000000                                                           ${cofdir}/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp245/ppt0000000000
  cp -f ${cofdir}/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp585/pptdddddd0600                                                           ${cofdir}/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp245/pptdddddd0600
  cp -f ${cofdir}/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp585/cmip6-data-request-varlist-ScenarioMIP-ssp585-EC-EARTH-AOGCM.json       ${cofdir}/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp370/cmip6-data-request-varlist-ScenarioMIP-ssp370-EC-EARTH-AOGCM.json
  cp -f ${cofdir}/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp585/ppt0000000000                                                           ${cofdir}/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp370/ppt0000000000
  cp -f ${cofdir}/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp585/pptdddddd0600                                                           ${cofdir}/ScenarioMIP/EC-EARTH-AOGCM/cmip6-experiment-ScenarioMIP-ssp370/pptdddddd0600
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp585/cmip6-data-request-varlist-ScenarioMIP-ssp585-EC-EARTH-Veg.json           ${cofdir}/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp245/cmip6-data-request-varlist-ScenarioMIP-ssp245-EC-EARTH-Veg.json
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp585/ppt0000000000                                                             ${cofdir}/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp245/ppt0000000000
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp585/pptdddddd0600                                                             ${cofdir}/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp245/pptdddddd0600
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp585/cmip6-data-request-varlist-ScenarioMIP-ssp585-EC-EARTH-Veg.json           ${cofdir}/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp370/cmip6-data-request-varlist-ScenarioMIP-ssp370-EC-EARTH-Veg.json
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp585/ppt0000000000                                                             ${cofdir}/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp370/ppt0000000000
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp585/pptdddddd0600                                                             ${cofdir}/ScenarioMIP/EC-EARTH-Veg/cmip6-experiment-ScenarioMIP-ssp370/pptdddddd0600
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-Veg-LR/cmip6-experiment-ScenarioMIP-ssp585/cmip6-data-request-varlist-ScenarioMIP-ssp585-EC-EARTH-Veg-LR.json     ${cofdir}/ScenarioMIP/EC-EARTH-Veg-LR/cmip6-experiment-ScenarioMIP-ssp245/cmip6-data-request-varlist-ScenarioMIP-ssp245-EC-EARTH-Veg-LR.json
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-Veg-LR/cmip6-experiment-ScenarioMIP-ssp585/ppt0000000000                                                          ${cofdir}/ScenarioMIP/EC-EARTH-Veg-LR/cmip6-experiment-ScenarioMIP-ssp245/ppt0000000000
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-Veg-LR/cmip6-experiment-ScenarioMIP-ssp585/pptdddddd0600                                                          ${cofdir}/ScenarioMIP/EC-EARTH-Veg-LR/cmip6-experiment-ScenarioMIP-ssp245/pptdddddd0600
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-Veg-LR/cmip6-experiment-ScenarioMIP-ssp585/cmip6-data-request-varlist-ScenarioMIP-ssp585-EC-EARTH-Veg-LR.json     ${cofdir}/ScenarioMIP/EC-EARTH-Veg-LR/cmip6-experiment-ScenarioMIP-ssp370/cmip6-data-request-varlist-ScenarioMIP-ssp370-EC-EARTH-Veg-LR.json
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-Veg-LR/cmip6-experiment-ScenarioMIP-ssp585/ppt0000000000                                                          ${cofdir}/ScenarioMIP/EC-EARTH-Veg-LR/cmip6-experiment-ScenarioMIP-ssp370/ppt0000000000
# cp -f ${cofdir}/ScenarioMIP/EC-EARTH-Veg-LR/cmip6-experiment-ScenarioMIP-ssp585/pptdddddd0600                                                          ${cofdir}/ScenarioMIP/EC-EARTH-Veg-LR/cmip6-experiment-ScenarioMIP-ssp370/pptdddddd0600

else
    echo '  '
    echo '  This scripts requires one argument, the control output directory:'
    echo '  ' $0 control-output-files
    echo '  '
fi
