#!/usr/bin/env bash
# Thomas Reerink
#
# This script adds / inserts a not (yet) approved CMIP endorsed MIP and experiment(s),
# which thus do not exist in the CMIP6 CMOR tables.
#
# This scripts requires no arguments.
#

if [ "$#" -eq 0 ]; then

 add_the_sofiamip_experiments=True

 if [ add_the_sofiamip_experiments ]; then
  # See #749  https://github.com/EC-Earth/ece2cmor3/issues/749

  # SOFIAMIP faf-antwater

  table_path=../resources/cmip6-cmor-tables/Tables/
  table_file_cv=CMIP6_CV.json

  cd ${table_path}
  git checkout ${table_file_cv}

  sed -i  '/"faf-antwater-stress":{/i \
            "faf-antwater":{                                                                                                                                  \
                "activity_id":[                                                                                                                               \
                    "SOFIAMIP"                                                                                                                                \
                ],                                                                                                                                            \
                "additional_allowed_model_components":[                                                                                                       \
                    "AER",                                                                                                                                    \
                    "CHEM",                                                                                                                                   \
                    "BGC"                                                                                                                                     \
                ],                                                                                                                                            \
                "experiment":"control plus perturbative surface fluxes of freshwater into ocean, the latter around the coast of Antarctica only",             \
                "experiment_id":"faf-antwater",                                                                                                               \
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
  ' ${table_file_cv}

  sed -i  '/"VIACSAB":/i \
            "SOFIAMIP":"Southern Ocean Freshwater release model experiments Initiative",
  ' ${table_file_cv}

  # Add KNMI as an institute with its own institution_id:
  sed -i  '/"KIOST":/i \
            "KNMI":"The Royal Netherlands Meteorological Institute (KNMI), De Bilt, The Netherlands",
  ' ${table_file_cv}

  # Adjust the license such that it matches with the production institute KNMI.
  sed -i -e 's/CMIP6 model data/The SOFIAMIP model data/' -e 's/Consult.*acknowledgment//' ${table_file_cv}

  # Allow KNMI on it self to be a institute which produces EC-Earth3 experiments:
  # This insert is vulnerable for upstream table changes within 20 lines after the match:
  sed -i -e '/"EC-Earth3":{/!b;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;n;a\                    "KNMI",' ${table_file_cv}

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
