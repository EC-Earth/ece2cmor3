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

  cd ../resources/cmip6-cmor-tables
  git checkout Tables/CMIP6_CV.json
  cd -

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
  ' ../resources/tables/CMIP6_CV.json


 else
    echo '  '
    echo '  Noting done, no set of variables and / or experiments has been selected to add to the tables.'
    echo '  '
 fi

else
    echo '  '
    echo '  This scripts requires no argument:'
    echo '  ' $0
    echo '  '
fi
