#!/usr/bin/env bash
# Thomas Reerink
#
# This script adds / inserts some non-cmor variables and /or non (yet) approved CMIP endorsed experiments (which thus
# do not exit in the CMIP6 data request) to the end of the cmor table in question.
#
# This scripts requires no arguments.
#
# Run example:
#  ./add-lamaclima-experiments.sh
#

if [ "$#" -eq 0 ]; then

 add_the_lamaclima_experiments=True             # See #853
 

 if [ add_the_lamaclima_experiments ]; then
  # See #853
  #  LAMACLIMA ssp585-lamaclima

  cd ../resources/cmip6-cmor-tables
  git checkout Tables/CMIP6_CV.json
  cd -

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
  ' ../resources/tables/CMIP6_CV.json

  sed -i  '/"LS3MIP":/i \
            "LAMACLIMA":"LAnd MAnagement for CLImate Mitigation and Adaptation",
  ' ../resources/tables/CMIP6_CV.json

  # Remove the trailing spaces of the inserted block above:
  sed -i 's/\s*$//g' ../resources/tables/CMIP6_CV.json

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
