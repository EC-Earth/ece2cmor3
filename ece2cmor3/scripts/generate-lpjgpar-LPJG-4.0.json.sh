#!/usr/bin/env bash
# Thomas Reerink
#
# This script adds the frac2percent unit conversion factor to the lpjgpar.json file for a number of LPJG variables
# for the case of cmorising older LPJG versions. See discussions on:
#  https://github.com/EC-Earth/ece2cmor3/pull/822
#  https://dev.ec-earth.org/issues/1312#note-219
#
# This script requires no arguments.
#

if [ "$#" -eq 0 ]; then

 lpjgpar_file=../resources/lpjgpar.json
 lpjgpar_file_for_previous_version=../resources/lpjgpar-LPJG-4.0.json

 git checkout ${lpjgpar_file}
 rsync -a ${lpjgpar_file} ${lpjgpar_file_for_previous_version}

 # The reverse case:
#sed -i '/frac2percent/d' ${lpjgpar_file}

 # Add the frac2percent unit conversion factor the following list of LPJG variables:
 for i in {baresoilFrac,cropFrac,cropFracC3,cropFracC4,grassFrac,grassFracC3,grassFracC4,landCoverFrac,nwdFracLut,pastureFrac,pastureFracC3,pastureFracC4,residualFrac,shrubFrac,treeFrac,treeFracBdlDcd,treeFracBdlEvg,treeFracNdlDcd,treeFracNdlEvg,vegFrac}; do
  sed -i '/"source": "'${i}'"/a \
        "convert": "frac2percent",
  ' ${lpjgpar_file_for_previous_version}
 done

else
 echo
 echo " This scripts requires no argument:"
 echo "  $0"
 echo
fi
