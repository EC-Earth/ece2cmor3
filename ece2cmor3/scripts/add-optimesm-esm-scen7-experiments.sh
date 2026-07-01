#!/bin/bash
# Thomas Reerink
#
# This script adds the OptimESM esm-scen7-vl and esm-scen7-h experiments to the CMIP6 CV
# because the will be recmorised to CMIP7 for the CMIP7-FT project.
#
# This script requires one argument.
#
# For examples how to call this script, run it without arguments.
#

if [ "$#" -eq 1 ]; then

 do_clean=$1

 add_optimesm_esm_scen7_experiments=True

 if [ add_optimesm_esm_scen7_experiments ]; then
  # See #888  https://github.com/EC-Earth/ece2cmor3/issues/888

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_CV=CMIP6_CV.json

  cd ${table_path}
  if [ ${do_clean} == 'clean-before' ]; then
   git checkout ${table_file_CV}
  fi

  sed -i  '/"esm-ssp534-over":{/i \
            "esm-scen7-h":{                                \
                "activity_id":[                            \
                    "ScenarioMIP"                          \
                ],                                         \
                "additional_allowed_model_components":[    \
                    "AER",                                 \
                    "CHEM"                                 \
                ],                                         \
                "experiment":"emission-driven scen7-h",    \
                "experiment_id":"esm-scen7-h",             \
                "parent_activity_id":[                     \
                    "CMIP"                                 \
                ],                                         \
                "parent_experiment_id":[                   \
                    "esm-hist"                             \
                ],                                         \
                "required_model_components":[              \
                    "AOGCM",                               \
                    "BGC"                                  \
                ],                                         \
                "sub_experiment_id":[                      \
                    "none"                                 \
                ]                                          \
            },                                             \
            "esm-scen7-vl":{                               \
                "activity_id":[                            \
                    "ScenarioMIP"                          \
                ],                                         \
                "additional_allowed_model_components":[    \
                    "AER",                                 \
                    "CHEM"                                 \
                ],                                         \
                "experiment":"emission-driven scen7-vl",   \
                "experiment_id":"esm-scen7-vl",            \
                "parent_activity_id":[                     \
                    "CMIP"                                 \
                ],                                         \
                "parent_experiment_id":[                   \
                    "esm-hist"                             \
                ],                                         \
                "required_model_components":[              \
                    "AOGCM",                               \
                    "BGC"                                  \
                ],                                         \
                "sub_experiment_id":[                      \
                    "none"                                 \
                ]                                          \
            },
  ' ${table_file_CV}

  # Remove the trailing spaces of the inserted block above:
 #sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_CV}
  sed -i -e 's/\s*$//g'                ${table_file_CV}

  cd -

  echo
  echo " Running:"
  echo "  $0 $@"
  echo " has adjusted the file:"
  echo "  ${table_path}/${table_file_CV}"
  echo " which is part of the nested CMOR Table repository. View the diff by running:"
  echo "  cd ${table_path}; git diff; cd -"
  echo " This changes can be reverted by running:"
  echo "  ./revert-nested-cmor-table-branch.sh"
  echo

 else
  echo
  echo " This scripts requires one argument: There are only two options:"
  echo "  $0 clean-before"
  echo "  $0 no-clean-before"
  echo
 fi

else
 echo
 echo " This scripts requires one argument: There are only two options:"
 echo "  $0 clean-before"
 echo "  $0 no-clean-before"
 echo
fi
