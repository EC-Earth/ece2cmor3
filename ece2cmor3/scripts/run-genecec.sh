#!/usr/bin/env bash
# Thomas Reerink
#
# This scripts requires one argument:
#  first  argument is a version number.
#
# Run this script without arguments for examples how to call this script.
#
# With this script genecec can be run and the output is written to a log file.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.
#
# Note that this script calls genecec.py


if [ "$#" -eq 2 ]; then

  if ! type "ece2cmor" > /dev/null; then
   echo; tput setaf 1;
   echo ' The CMIP6 data request tool ece2cmor is not available because of one of the following reasons:'
   echo '  1. ece2cmor might be not installed'
   echo '  2. ece2cmor might be not active, as the miniconda environment is not activated'
   echo ' Stop'
   tput sgr0; echo
   exit
  fi

  if ! type "drq" > /dev/null; then
   echo; tput setaf 1;
   echo ' The CMIP6 data request tool drq is not available because of one of the following reasons:'
   echo '  1. drq might be not installed'
   echo '  2. drq might be not active, as the miniconda environment is not activated'
   echo ' Stop'
   tput sgr0; echo
   exit
  fi

  version=$1
  pextra_mode=$2

  sed -e 's/output-control-files/control-output-files\/output-control-files-v'${version}'/' config-genecec > config-genecec-run
  ./genecec.py config-genecec-run >& control-output-files/log-genecec/log-genecec-v${version} &

  if [ "${pextra_mode}" == 'pextra' ]; then
   sed -e 's/activate_pextra_mode           = False/activate_pextra_mode           = True /' config-genecec > config-genecec-run
  fi

else
  echo
  echo '  This scripts requires one argument, e.g.:'
  echo '  ' $0 '190 default'
  echo '  ' $0 '190 pextra'
  echo
fi
