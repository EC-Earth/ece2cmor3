#!/bin/bash
# Thomas Reerink
#
# This script adds / inserts some non-cmor variables and /or non (yet) approved CMIP endorsed experiments (which thus
# do not exit in the CMIP6 data request) to the end of the cmor table in question.
#
# This scripts requires no arguments.
#
# Run example:
#  ./add-covidMIP-experiments.sh
#

if [ "$#" -eq 0 ]; then

 add_the_covidMIP_experiments=True             # See #847 & #895


 if [ add_the_covidMIP_experiments ]; then
  # See #847 & #895, the addition of five Covid experiments:
  #  CovidMIP ssp245-covid
  #  CovidMIP ssp245-cov-strgreen
  #  CovidMIP ssp245-cov-modgreen
  #  CovidMIP ssp245-cov-fossil
  #  CovidMIP ssp245-cov-aer

  table_path=../resources/cmip6-cmor-tables/Tables/
  table_file_cv=CMIP6_CV.json

  cd ${table_path}
  git checkout ${table_file_cv}

  sed -i  '/"ssp370":{/i \
            "ssp245-covid":{                                                                                                                          \
                "activity_id":[                                                                                                                       \
                    "DAMIP"                                                                                                                           \
                ],                                                                                                                                    \
                "additional_allowed_model_components":[                                                                                               \
                    "AER",                                                                                                                            \
                    "CHEM",                                                                                                                           \
                    "BGC"                                                                                                                             \
                ],                                                                                                                                    \
                "experiment":"2-year Covid-19 emissions blip based upon ssp245",                                                                      \
                "experiment_id":"ssp245-covid",                                                                                                       \
                "parent_activity_id":[                                                                                                                \
                    "ScenarioMIP"                                                                                                                     \
                ],                                                                                                                                    \
                "parent_experiment_id":[                                                                                                              \
                    "ssp245"                                                                                                                          \
                ],                                                                                                                                    \
                "required_model_components":[                                                                                                         \
                    "AOGCM"                                                                                                                           \
                ],                                                                                                                                    \
                "sub_experiment_id":[                                                                                                                 \
                    "none"                                                                                                                            \
                ]                                                                                                                                     \
            },                                                                                                                                        \
            "ssp245-cov-strgreen":{                                                                                                                   \
                "activity_id":[                                                                                                                       \
                    "DAMIP"                                                                                                                           \
                ],                                                                                                                                    \
                "additional_allowed_model_components":[                                                                                               \
                    "AER",                                                                                                                            \
                    "CHEM",                                                                                                                           \
                    "BGC"                                                                                                                             \
                ],                                                                                                                                    \
                "experiment":"2-year Covid-19 emissions blip followed by strong-green stimulus recovery, based upon ssp245",                          \
                "experiment_id":"ssp245-cov-strgreen",                                                                                                \
                "parent_activity_id":[                                                                                                                \
                    "ScenarioMIP"                                                                                                                     \
                ],                                                                                                                                    \
                "parent_experiment_id":[                                                                                                              \
                    "ssp245"                                                                                                                          \
                ],                                                                                                                                    \
                "required_model_components":[                                                                                                         \
                    "AOGCM"                                                                                                                           \
                ],                                                                                                                                    \
                "sub_experiment_id":[                                                                                                                 \
                    "none"                                                                                                                            \
                ]                                                                                                                                     \
            },                                                                                                                                        \
            "ssp245-cov-modgreen":{                                                                                                                   \
                "activity_id":[                                                                                                                       \
                    "DAMIP"                                                                                                                           \
                ],                                                                                                                                    \
                "additional_allowed_model_components":[                                                                                               \
                    "AER",                                                                                                                            \
                    "CHEM",                                                                                                                           \
                    "BGC"                                                                                                                             \
                ],                                                                                                                                    \
                "experiment":"2-year Covid-19 emissions blip followed by moderate-green stimulus recovery, based upon ssp245",                        \
                "experiment_id":"ssp245-cov-modgreen",                                                                                                \
                "parent_activity_id":[                                                                                                                \
                    "ScenarioMIP"                                                                                                                     \
                ],                                                                                                                                    \
                "parent_experiment_id":[                                                                                                              \
                    "ssp245"                                                                                                                          \
                ],                                                                                                                                    \
                "required_model_components":[                                                                                                         \
                    "AOGCM"                                                                                                                           \
                ],                                                                                                                                    \
                "sub_experiment_id":[                                                                                                                 \
                    "none"                                                                                                                            \
                ]                                                                                                                                     \
            },                                                                                                                                        \
            "ssp245-cov-fossil":{                                                                                                                     \
                "activity_id":[                                                                                                                       \
                    "DAMIP"                                                                                                                           \
                ],                                                                                                                                    \
                "additional_allowed_model_components":[                                                                                               \
                    "AER",                                                                                                                            \
                    "CHEM",                                                                                                                           \
                    "BGC"                                                                                                                             \
                ],                                                                                                                                    \
                "experiment":"2-year Covid-19 emissions blip followed by increased emissions due to a fossil-fuel based recovery, based upon ssp245", \
                "experiment_id":"ssp245-cov-fossil",                                                                                                  \
                "parent_activity_id":[                                                                                                                \
                    "ScenarioMIP"                                                                                                                     \
                ],                                                                                                                                    \
                "parent_experiment_id":[                                                                                                              \
                    "ssp245"                                                                                                                          \
                ],                                                                                                                                    \
                "required_model_components":[                                                                                                         \
                    "AOGCM"                                                                                                                           \
                ],                                                                                                                                    \
                "sub_experiment_id":[                                                                                                                 \
                    "none"                                                                                                                            \
                ]                                                                                                                                     \
            },                                                                                                                                        \
            "ssp245-cov-aer":{                                                                                                                        \
                "activity_id":[                                                                                                                       \
                    "DAMIP"                                                                                                                           \
                ],                                                                                                                                    \
                "additional_allowed_model_components":[                                                                                               \
                    "AER",                                                                                                                            \
                    "CHEM",                                                                                                                           \
                    "BGC"                                                                                                                             \
                ],                                                                                                                                    \
                "experiment":"2-year Covid-19 emissions blip including anthropogenic aerosols only, based upon ssp245",                               \
                "experiment_id":"ssp245-cov-aer",                                                                                                     \
                "parent_activity_id":[                                                                                                                \
                    "ScenarioMIP"                                                                                                                     \
                ],                                                                                                                                    \
                "parent_experiment_id":[                                                                                                              \
                    "ssp245"                                                                                                                          \
                ],                                                                                                                                    \
                "required_model_components":[                                                                                                         \
                    "AOGCM"                                                                                                                           \
                ],                                                                                                                                    \
                "sub_experiment_id":[                                                                                                                 \
                    "none"                                                                                                                            \
                ]                                                                                                                                     \
            },                                                                                                                                        
  ' ${table_file_cv}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' ${table_file_cv}

  cd -

  echo
  echo " $0 reports:"
  echo "  The adjusted file is:  ${table_path}/${table_file_cv}"
  echo "  Which is part of a nested repository, therefore to view the diff, run:"
  echo "  cd ${table_path}; git diff; cd -"
  echo

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
