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

  # LAMACLIMA ssp585-lamaclima

  table_path=../resources/cmip6-cmor-tables/Tables/
  table_file_cv=CMIP6_CV.json

  cd ${table_path}
  git checkout ${table_file_cv}

  sed -i  '/"ssp585-withism":{/i \
            "ssp585-lamaclima":{                                       \
                "activity_id":[                                        \
                    "LAMACLIMA"                                        \
                ],                                                     \
                "additional_allowed_model_components":[                \
                    "AER"                                              \
                ],                                                     \
                "experiment":"Lamaclima experiment based upon SSP585", \
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

  # Remove the trailing spaces of the inserted block above:
  sed -i 's/\s*$//g' ${table_file_cv}

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
