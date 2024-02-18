#!/usr/bin/env bash
# Thomas Reerink
#
# This script adds / inserts a not (yet) approved CMIP endorsed MIP and experiment(s),
# which thus do not exist in the CMIP6 CMOR tables.
#
# This scripts requires no arguments.
#

if [ "$#" -eq 0 ]; then

 add_the_lamaclima_experiments=True

 if [ add_the_lamaclima_experiments ]; then
  # See #645  https://github.com/EC-Earth/ece2cmor3/issues/645
  # See #699  https://github.com/EC-Earth/ece2cmor3/issues/699
  # See #739  https://github.com/EC-Earth/ece2cmor3/issues/739
  # See #853  https://dev.ec-earth.org/issues/853

  # Add the four ssp119 BGC LAMACLIMA experiments and the ssp585 AOGCM LAMACLIMA experiment

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_cv=CMIP6_CV.json

  cd ${table_path}
  git checkout ${table_file_cv}

  sed -i  '/"histSST":{/i \
            "histctl":{                                                \
                "activity_id":[                                        \
                    "LAMACLIMA"                                        \
                ],                                                     \
                "additional_allowed_model_components":[                \
                    "BGC"                                              \
                ],                                                     \
                "experiment":"Lamaclima experiment based upon SSP119", \
                "experiment_id":"histctl",                             \
                "parent_activity_id":[                                 \
                    "CMIP"                                             \
                ],                                                     \
                "parent_experiment_id":[                               \
                    "historical"                                       \
                ],                                                     \
                "required_model_components":[                          \
                    "AOGCM"                                            \
                ],                                                     \
                "sub_experiment_id":[                                  \
                    "none"                                             \
                ]                                                      \
            },                                                         
  ' ${table_file_cv}

  sed -i  '/"ssp126":{/i \
            "ssp119-futctl":{                                          \
                "activity_id":[                                        \
                    "LAMACLIMA"                                        \
                ],                                                     \
                "additional_allowed_model_components":[                \
                    "BGC"                                              \
                ],                                                     \
                "experiment":"Lamaclima experiment based upon SSP119", \
                "experiment_id":"ssp119-futctl",                       \
                "parent_activity_id":[                                 \
                    "LAMACLIMA"                                        \
                ],                                                     \
                "parent_experiment_id":[                               \
                    "histctl"                                          \
                ],                                                     \
                "required_model_components":[                          \
                    "AOGCM"                                            \
                ],                                                     \
                "sub_experiment_id":[                                  \
                    "none"                                             \
                ]                                                      \
            },                                                         \
            "ssp119-futsust":{                                         \
                "activity_id":[                                        \
                    "LAMACLIMA"                                        \
                ],                                                     \
                "additional_allowed_model_components":[                \
                    "BGC"                                              \
                ],                                                     \
                "experiment":"LAMACLIMA experiment based upon SSP119", \
                "experiment_id":"ssp119-futsust",                      \
                "parent_activity_id":[                                 \
                    "LAMACLIMA"                                        \
                ],                                                     \
                "parent_experiment_id":[                               \
                    "histctl"                                          \
                ],                                                     \
                "required_model_components":[                          \
                    "AOGCM"                                            \
                ],                                                     \
                "sub_experiment_id":[                                  \
                    "none"                                             \
                ]                                                      \
            },                                                         \
            "ssp119-futineq":{                                         \
                "activity_id":[                                        \
                    "LAMACLIMA"                                        \
                ],                                                     \
                "additional_allowed_model_components":[                \
                    "BGC"                                              \
                ],                                                     \
                "experiment":"LAMACLIMA experiment based upon SSP119", \
                "experiment_id":"ssp119-futineq",                      \
                "parent_activity_id":[                                 \
                    "LAMACLIMA"                                        \
                ],                                                     \
                "parent_experiment_id":[                               \
                    "histctl"                                          \
                ],                                                     \
                "required_model_components":[                          \
                    "AOGCM"                                            \
                ],                                                     \
                "sub_experiment_id":[                                  \
                    "none"                                             \
                ]                                                      \
            },                                                         
  ' ${table_file_cv}

  sed -i  '/"ssp585-withism":{/i \
            "ssp585-lamaclima":{                                       \
                "activity_id":[                                        \
                    "LAMACLIMA"                                        \
                ],                                                     \
                "additional_allowed_model_components":[                \
                    "AER"                                              \
                ],                                                     \
                "experiment":"LAMACLIMA experiment based upon SSP585", \
                "experiment_id":"ssp585-lamaclima",                    \
                "parent_activity_id":[                                 \
                    "CMIP"                                             \
                ],                                                     \
                "parent_experiment_id":[                               \
                    "historical"                                       \
                ],                                                     \
                "required_model_components":[                          \
                    "AOGCM"                                            \
                ],                                                     \
                "sub_experiment_id":[                                  \
                    "none"                                             \
                ]                                                      \
            },                                                         
  ' ${table_file_cv}

  sed -i  '/"LS3MIP":/i \
            "LAMACLIMA":"LAnd MAnagement for CLImate Mitigation and Adaptation",
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
