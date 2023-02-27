#!/usr/bin/env bash
# Thomas Reerink
#
# Run this script without arguments for examples how to call this script.
#
# With this script genecec can be run and the output is written to a log file.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.
#
# Note that this script calls genecec.py


if [ "$#" -eq 3 ]; then

  if ! type "ece2cmor" > /dev/null; then
   echo; tput setaf 1;
   echo ' The CMIP6 data request tool ece2cmor is not available because of one of the following reasons:'
   echo '  1. ece2cmor might be not installed'
   echo '  2. ece2cmor might be not active, check whether the ece2cmor3 environment is activated'
   echo ' Stop'
   tput sgr0; echo
   exit
  fi

  if ! type "drq" > /dev/null; then
   echo; tput setaf 1;
   echo ' The CMIP6 data request tool drq is not available because of one of the following reasons:'
   echo '  1. drq might be not installed'
   echo '  2. drq might be not active, check whether the ece2cmor3 environment is activated'
   echo ' Stop'
   tput sgr0; echo
   exit
  fi

  pextra_mode=$1
  version=$2
  python_case=$3

  config_genecec_run_file=config-genecec-run

  if [ "${pextra_mode}" == 'pextra' ]; then
   label=${version}-'pextra'
  else
   label=${version}
  fi

  sed -e 's/output-control-files/~\/cmorize\/control-output-files\/output-control-files-v'${version}'/' config-genecec > ${config_genecec_run_file}
  if [ "${pextra_mode}" == 'pextra' ]; then
   sed -i -e 's/activate_pextra_mode           = False/activate_pextra_mode           = True /' ${config_genecec_run_file}
   sed -i -e 's/default/pextra/' ${config_genecec_run_file}                                                                # Adjust just example in header
  fi
  sed -i -e "s/001/${version}/" ${config_genecec_run_file}                                                                 # Adjust just example in header

  if [ "${python_case}" == 'in-ece2cmor3-python-2-dir' ]; then
   sed -i -e "s/ece2cmor3/ece2cmor3-python-2/" ${config_genecec_run_file}
   sed -i -e "s/in-ece2cmor3-dir/in-ece2cmor3-python-2-dir/" ${config_genecec_run_file}                                    # Adjust just example in header
  elif [ "${python_case}" == 'in-ece2cmor3-python-3-dir' ]; then
   sed -i -e "s/ece2cmor3/ece2cmor3-python-3/" ${config_genecec_run_file}
   sed -i -e "s/in-ece2cmor3-dir/in-ece2cmor3-python-3-dir/" ${config_genecec_run_file}                                    # Adjust just example in header
  fi

  log_dir=~/cmorize/control-output-files/log-genecec
  log_file=${log_dir}/log-genecec-v${label}
  mkdir -p ${log_dir}
  ./genecec.py ${config_genecec_run_file} >& ${log_file} &
 #./genecec.py ${config_genecec_run_file} >  ${log_file/genecec/-stdout} 2> ${log_file/genecec/-stderr} &

else
  echo
  echo '  This scripts requires three arguments, e.g.:'
  echo '  ' $0 'default 228 in-ece2cmor3-python-2-dir'
  echo '  ' $0 'pextra  228 in-ece2cmor3-python-2-dir'
  echo '  ' $0 'default 228 in-ece2cmor3-python-3-dir'
  echo '  ' $0 'pextra  228 in-ece2cmor3-python-3-dir'
  echo '  ' $0 'default 228 in-ece2cmor3-dir'
  echo '  ' $0 'pextra  228 in-ece2cmor3-dir'
  echo
fi
