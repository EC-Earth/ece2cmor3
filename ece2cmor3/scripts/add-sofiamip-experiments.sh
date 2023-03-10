#!/usr/bin/env bash
# Thomas Reerink
#
# This script adds / inserts a not (yet) approved CMIP endorsed MIP and experiment(s),
# which thus do not exist in the CMIP6 CMOR tables.
#
# This scripts requires no arguments.
#

if [ "$#" -eq 0 ]; then

 add_the_sofiamip_experiments=True             # See #749
 

 if [ add_the_sofiamip_experiments ]; then
  # See #749
  #  sofiamip antwater

  cd ../resources/cmip6-cmor-tables
  git checkout Tables/CMIP6_CV.json
  cd -

# sed -i  '/"faf-antwater-stress":{/i \
#           "faf-antwater":{                                                                                                                                  \
#               "experiment_id":"faf-antwater",                                                                                                               \
  sed -i  '/"a4SST":{/i \
            "antwater":{                                                                                                                                      \
                "activity_id":[                                                                                                                               \
                    "SOFIAMIP"                                                                                                                                \
                ],                                                                                                                                            \
                "additional_allowed_model_components":[                                                                                                       \
                    "AER",                                                                                                                                    \
                    "CHEM",                                                                                                                                   \
                    "BGC"                                                                                                                                     \
                ],                                                                                                                                            \
                "experiment":"control plus perturbative surface fluxes of momentum and freshwater into ocean, the latter around the coast of Antarctica only" \
                "experiment_id":"antwater",                                                                                                                   \
                "parent_activity_id":[                                                                                                                        \
                    "CMIP"                                                                                                                                    \
                ],                                                                                                                                            \
                "parent_experiment_id":[                                                                                                                      \
                    "piControl"                                                                                                                               \
                ],                                                                                                                                            \
                "required_model_components":[                                                                                                                 \
                    "AOGCM"                                                                                                                                   \
                ],                                                                                                                                            \
                "sub_experiment_id":[                                                                                                                         \
                    "none"                                                                                                                                    \
                ]                                                                                                                                             \
            },                                                                                                                                                
  ' ../resources/tables/CMIP6_CV.json

  sed -i  '/"VIACSAB":/i \
            "SOFIAMIP":"Southern Ocean Freshwater release model experiments Initiative",
  ' ../resources/tables/CMIP6_CV.json

  # Remove the trailing spaces of the inserted block above:
  sed -i 's/\s*$//g' ../resources/tables/CMIP6_CV.json

  echo
  echo " $0 reports:"
  echo "  The adjusted file is:  ../resources/tables/CMIP6_CV.json "
  echo "  Which is part of a nested repository, therefore to view the diff, run:"
  echo "  cd ../resources/tables; git diff; cd -"
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
