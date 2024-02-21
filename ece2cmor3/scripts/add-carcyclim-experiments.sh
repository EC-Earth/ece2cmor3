#!/usr/bin/env bash
# Thomas Reerink
#
# This script adds / inserts a not (yet) approved CMIP endorsed MIP and experiment(s),
# which thus do not exist in the CMIP6 CMOR tables.
#
# This scripts requires no arguments.
#

if [ "$#" -eq 0 ]; then

 add_the_carcyclim_experiments=True

 if [ add_the_carcyclim_experiments ]; then
  # See #793   https://github.com/EC-Earth/ece2cmor3/issues/793
  # See #1323  https://dev.ec-earth.org/issues/1323

  # Add the five abrupt-NxCO2 EC-Earth3-CC CARCYCLIM experiments

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_cv=CMIP6_CV.json

  cd ${table_path}
  git checkout ${table_file_cv}

  sed -i  '/"abrupt-4xCO2":{/i \
            "carcyclim-abrupt-0p5xCO2":{                                                 \
                "activity_id":[                                                          \
                    "CARCYCLIM"                                                          \
                ],                                                                       \
                "additional_allowed_model_components":[                                  \
                    "BGC"                                                                \
                ],                                                                       \
                "experiment":"CARCYCLIM abrupt halving of CO2 with 2022 conditions",     \
                "experiment_id":"carcyclim-abrupt-0p5xCO2",                              \
                "parent_activity_id":[                                                   \
                    "ScenarioMIP"                                                        \
                ],                                                                       \
                "parent_experiment_id":[                                                 \
                    "ssp245"                                                             \
                ],                                                                       \
                "required_model_components":[                                            \
                    "AOGCM",                                                             \
                    "BGC"                                                                \
                ],                                                                       \
                "sub_experiment_id":[                                                    \
                    "none"                                                               \
                ]                                                                        \
            },                                                                           \
            "carcyclim-abrupt-0p8xCO2":{                                                 \
                "activity_id":[                                                          \
                    "CARCYCLIM"                                                          \
                ],                                                                       \
                "additional_allowed_model_components":[                                  \
                    "BGC"                                                                \
                ],                                                                       \
                "experiment":"CARCYCLIM abrupt 0.8 times CO2 with 2022 conditions",      \
                "experiment_id":"carcyclim-abrupt-0p8xCO2",                              \
                "parent_activity_id":[                                                   \
                    "ScenarioMIP"                                                        \
                ],                                                                       \
                "parent_experiment_id":[                                                 \
                    "ssp245"                                                             \
                ],                                                                       \
                "required_model_components":[                                            \
                    "AOGCM",                                                             \
                    "BGC"                                                                \
                ],                                                                       \
                "sub_experiment_id":[                                                    \
                    "none"                                                               \
                ]                                                                        \
            },                                                                           \
            "carcyclim-abrupt-1xCO2":{                                                   \
                "activity_id":[                                                          \
                    "CARCYCLIM"                                                          \
                ],                                                                       \
                "additional_allowed_model_components":[                                  \
                    "BGC"                                                                \
                ],                                                                       \
                "experiment":"CARCYCLIM keeping the 1 times CO2 with 2022 conditions",   \
                "experiment_id":"carcyclim-abrupt-1xCO2",                                \
                "parent_activity_id":[                                                   \
                    "ScenarioMIP"                                                        \
                ],                                                                       \
                "parent_experiment_id":[                                                 \
                    "ssp245"                                                             \
                ],                                                                       \
                "required_model_components":[                                            \
                    "AOGCM",                                                             \
                    "BGC"                                                                \
                ],                                                                       \
                "sub_experiment_id":[                                                    \
                    "none"                                                               \
                ]                                                                        \
            },                                                                           \
            "carcyclim-abrupt-2xCO2":{                                                   \
                "activity_id":[                                                          \
                    "CARCYCLIM"                                                          \
                ],                                                                       \
                "additional_allowed_model_components":[                                  \
                    "BGC"                                                                \
                ],                                                                       \
                "experiment":"CARCYCLIM abrupt doubling of CO2 with 2022 conditions",    \
                "experiment_id":"carcyclim-abrupt-2xCO2",                                \
                "parent_activity_id":[                                                   \
                    "ScenarioMIP"                                                        \
                ],                                                                       \
                "parent_experiment_id":[                                                 \
                    "ssp245"                                                             \
                ],                                                                       \
                "required_model_components":[                                            \
                    "AOGCM",                                                             \
                    "BGC"                                                                \
                ],                                                                       \
                "sub_experiment_id":[                                                    \
                    "none"                                                               \
                ]                                                                        \
            },                                                                           \
            "carcyclim-abrupt-4xCO2":{                                                   \
                "activity_id":[                                                          \
                    "CARCYCLIM"                                                          \
                ],                                                                       \
                "additional_allowed_model_components":[                                  \
                    "BGC"                                                                \
                ],                                                                       \
                "experiment":"CARCYCLIM abrupt quadrupling of CO2 with 2022 conditions", \
                "experiment_id":"carcyclim-abrupt-4xCO2",                                \
                "parent_activity_id":[                                                   \
                    "ScenarioMIP"                                                        \
                ],                                                                       \
                "parent_experiment_id":[                                                 \
                    "ssp245"                                                             \
                ],                                                                       \
                "required_model_components":[                                            \
                    "AOGCM",                                                             \
                    "BGC"                                                                \
                ],                                                                       \
                "sub_experiment_id":[                                                    \
                    "none"                                                               \
                ]                                                                        \
            },                                                                           
  ' ${table_file_cv}

  sed -i  '/"C4MIP":/i \
            "CARCYCLIM":"CARbon CYCLe CLIMate project",
  ' ${table_file_cv}

  # Set the TM5 34 levels to 10 levels:
  sed -i -e 's/EC-Earth3-CC (2019): \\naerosol: none\\natmos: IFS cy36r4 (TL255, linearly reduced Gaussian grid equivalent to 512 x 256 longitude\/latitude; 91 levels; top level 0.01 hPa)\\natmosChem: TM5 (3 x 2 degrees; 120 x 90 longitude\/latitude; 34 levels/EC-Earth3-CC (2019): \\naerosol: none\\natmos: IFS cy36r4 (TL255, linearly reduced Gaussian grid equivalent to 512 x 256 longitude\/latitude; 91 levels; top level 0.01 hPa)\\natmosChem: TM5 (3 x 2 degrees; 120 x 90 longitude\/latitude; 10 levels/' ${table_file_cv}

  # Remove the trailing spaces of the inserted block above:
  sed -i 's/\s*$//g' ${table_file_cv}

  cd -

  echo
  echo " Running:"
  echo "  $0"
  echo " has adjusted the file:"
  echo "  ${table_path}/${table_file_cv}"
  echo " which is part of the nested CMOR Table repository. View the diff by running:"
  echo "  cd ${table_path}; git diff; cd -"
  echo " This changes can be reverted by running:"
  echo "  ./revert-nested-cmor-table-branch.sh"
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
