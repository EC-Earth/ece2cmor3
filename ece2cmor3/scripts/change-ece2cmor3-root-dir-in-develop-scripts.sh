#!/usr/bin/env bash
# Thomas Reerink
#
# This script applies the required changes to run ece2cmor3 & genecec in the PEXTRA mode or it resets these adjustments
#
# This scripts requires one argument: the ece2cmor3 root dir name
#
# Run this script without arguments for examples how to call this script.
# For examples how to call this script, run it without arguments.
#

if [ "$#" -eq 1 ]; then

  default_root_dir=ece2cmor3
  adjusted_root_dir=$1

  # First revert the concerned files:
  git checkout ../../environment.yml
  git checkout config-create-basic-ec-earth-cmip6-nemo-namelist
  git checkout create-nemo-only-list/create-nemo-only-list.sh
  git checkout update-basic-identifiedmissing-ignored-files.sh
  git checkout determine-missing-variables.sh

  # Adjust files:
  sed -i -e "s/name: ${default_root_dir}/name: ${adjusted_root_dir}/"       ../../environment.yml
  sed -i -e "s/cmorize\/${default_root_dir}/cmorize\/${adjusted_root_dir}/" config-create-basic-ec-earth-cmip6-nemo-namelist
  sed -i -e "s/cmorize\/${default_root_dir}/cmorize\/${adjusted_root_dir}/" create-nemo-only-list/create-nemo-only-list.sh
  sed -i -e "s/cmorize\/${default_root_dir}/cmorize\/${adjusted_root_dir}/" update-basic-identifiedmissing-ignored-files.sh
  sed -i -e "s/cmorize\/${default_root_dir}/cmorize\/${adjusted_root_dir}/" determine-missing-variables.sh

  git diff ../../environment.yml
  git diff config-create-basic-ec-earth-cmip6-nemo-namelist
  git diff create-nemo-only-list/create-nemo-only-list.sh
  git diff update-basic-identifiedmissing-ignored-files.sh
  git diff determine-missing-variables.sh

else
  echo
  echo " This scripts requires one argument:"
  echo "  $0 ece2cmor3"
  echo "  $0 ece2cmor3-python-2"
  echo "  $0 ece2cmor3-python-3"
  echo
fi
