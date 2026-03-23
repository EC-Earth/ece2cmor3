#!/bin/bash
#
# This script adds ols to the list of vertical_label's in the cmip7-cmor-tables/tables-cvs/cmor-cvs.json
#
# As long the EMD registration of EC-Earth3-ESM-1 & EC-Earth3-ESM-1-1 is not finished, they are inserted here in the table for now.
#
# This script requires no arguments.
#

if [ "$#" -eq 0 ]; then

 add_ols_to_vertical_labels=True

 if [ add_ols_to_vertical_labels ]; then
  # See #866  https://github.com/EC-Earth/ece2cmor3/issues/866

  table_path=../../resources/cmip7-cmor-tables/tables-cvs/
  table_file=cmor-cvs.json
  cd ${table_path}
  git checkout ${table_file}

  sed -i  '/"op4": /i \
            "ols": "Data is reported at sea surface.",' \
  ${table_file}

  sed -i  '/"IPSL": "/i \
            "EC-Earth-Consortium": "DMI, SMHI, KNMI, CNR, BSC, FMI, Met Eireann, AEMET, LU, Stockholm University, ENEA",' \
  ${table_file}
#            "EC-Earth-Consortium": "AEMET, Spain; BSC, Spain; CNR-ISAC, Italy; DMI, Denmark; ENEA, Italy; FMI, Finland; Geomar, Germany; ICHEC, Ireland; ICTP, Italy; IDL, Portugal; IMAU, The Netherlands; IPMA, Portugal; KIT, Karlsruhe, Germany; KNMI, The Netherlands; Lund University, Sweden; Met Eireann, Ireland; NLeSC, The Netherlands; NTNU, Norway; Oxford University, UK; surfSARA, The Netherlands; SMHI, Sweden; Stockholm University, Sweden; Unite ASTR, Belgium; University College Dublin, Ireland; University of Bergen, Norway; University of Copenhagen, Denmark; University of Helsinki, Finland; University of Santiago de Compostela, Spain; Uppsala University, Sweden; Utrecht University, The Netherlands; Vrije Universiteit Amsterdam, the Netherlands; Wageningen University, The Netherlands.",' \
#            "EC-Earth Consortium": "",' \

  sed -i  '/"DUMMY-MODEL": {/i \
            "EC-Earth3-ESM-1": {                 \
                "institution_id": [              \
                    "EC-Earth-Consortium"        \
                ],                               \
                "model_component": {},           \
                "source": "EC-Earth3-ESM-1:",    \
                "source_id": "EC-Earth3-ESM-1"   \
            },                                   \
            "EC-Earth3-ESM-1-1": {               \
                "institution_id": [              \
                    "EC-Earth-Consortium"        \
                ],                               \
                "model_component": {},           \
                "source": "EC-Earth3-ESM-1-1:",  \
                "source_id": "EC-Earth3-ESM-1-1" \
            },'                                  \
  ${table_file}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/,/g' ${table_file}


  cd -

  echo
  echo " Running:"
  echo "  $0"
  echo " has adjusted the file:"
  echo "  ${table_path}/${table_file}"
  echo " which is part of the nested CMIP7 CMOR Table repository. View the diff by running:"
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
