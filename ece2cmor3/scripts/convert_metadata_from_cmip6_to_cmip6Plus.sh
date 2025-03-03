#!/bin/bash
# Thomas Reerink
#
# This script reverts all local changes in the CMIP6Plus CMOR table repositories.
#
# This scripts requires one argument.
#

if [ "$#" -eq 1 ]; then

 metadata_filename_cmip6=$1
 metadata_filename_cmip6plus=${metadata_filename_cmip6/cmip6/cmip6plus}

 if [ -f ${metadata_filename_cmip6plus} ]; then
  echo "Error, abort because ${metadata_filename_cmip6plus} already exists."
  exit 1
 fi

 license="CMIP6Plus model data produced by EC-Earth-Consortium is licensed under a Creative Commons 4.0 (CC BY 4.0) License (https:\/\/creativecommons.org\/). Consult https:\/\/pcmdi.llnl.gov\/CMIP6Plus\/TermsOfUse for terms of use governing CMIP6Plus output, including citation requirements and proper acknowledgment. The data producers and data providers make no warranty, either express or implied, including, but not limited to, warranties of merchantability and fitness for a particular purpose. All liabilities arising from the supply of the information (including any liability arising in negligence) are excluded to the fullest extent permitted by law."

 sed    -e 's/"_control_vocabulary_file":     "CMIP6_CV.json"/"_controlled_vocabulary_file":  "CMIP6Plus_CV.json"/' ${metadata_filename_cmip6} > ${metadata_filename_cmip6plus}
 sed -i -e 's/"_cmip6_option":                "CMIP6"/"_cmip6_option":                "CMIP6Plus"/'                                              ${metadata_filename_cmip6plus}
 sed -i -e 's/"mip_era":                      "CMIP6"/"mip_era":                      "CMIP6Plus"/'                                              ${metadata_filename_cmip6plus}
 sed -i -e 's/"parent_mip_era":               "CMIP6"/"parent_mip_era":               "CMIP6Plus"/'                                              ${metadata_filename_cmip6plus}
 sed -i -e "s/license.:.*/license\":                      \"${license}\",/"                                                                      ${metadata_filename_cmip6plus}

 sed -i  '/"_controlled_vocabulary_file"/i \
    "_AXIS_ENTRY_FILE":             "MIP_coordinate.json",\
    "_FORMULA_VAR_FILE":            "MIP_formula_terms.json",
 ' ${metadata_filename_cmip6plus}

else
 echo
 echo " This scripts requires one argument: a metadata file:"
 echo "  $0 ../resources/metadata-templates/metadata-cmip6-CMIP-esm-hist-EC-EARTH-ESM-1-nemo-template.json"
 echo "  $0 optimesm/metadata-cmip6-CMIP-esm-hist-EC-EARTH-ESM-1-nemo-template.json"
 echo
fi
