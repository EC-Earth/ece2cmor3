#!/bin/bash
# Thomas Reerink
#
# This script applies the required changes to run ece2cmor3 & genecec in the PEXTRA mode or it resets these adjustments 
#
# This scripts requires one arguments:
#
# ${1} the first   argument is  activate-pextra-mode  or deactivate-pextra-mode 
#
# Run example:
#  ./switch-on-off-pextra-mode.sh activate-pextra-mode
#

if [ "$#" -eq 1 ]; then

 if [ $1 == 'activate-pextra-mode' ]; then
  sed -i -e 's/"NRFP3S"] = -1/"NRFP3S"] = -99/' drq2ppt.py
  cp -f ../resources/list-of-identified-missing-cmpi6-requested-variables-enable-pextra.xlsx ../resources/list-of-identified-missing-cmpi6-requested-variables.xlsx
  cd ../../; python setup.py develop; cd -;
  echo '  '
  git diff ../resources/list-of-identified-missing-cmpi6-requested-variables.xlsx
  echo '  '
  git diff drq2ppt.py
  echo '  '
 elif [ $1 == 'deactivate-pextra-mode' ]; then
  sed -i -e 's/"NRFP3S"] = -99/"NRFP3S"] = -1/' drq2ppt.py
  git checkout ../resources/list-of-identified-missing-cmpi6-requested-variables.xlsx
  cd ../../; python setup.py develop; cd -;
  echo '  '
  git diff ../resources/list-of-identified-missing-cmpi6-requested-variables.xlsx
  echo '  '
  git diff drq2ppt.py
  echo '  '
 else
    echo '  '
    echo '  Error: the value of the first argument is wrong.'
    echo '  '
    echo '  This scripts requires one argument: There are only two options:'
    echo '  ' $0 activate-pextra-mode
    echo '  ' $0 deactivate-pextra-mode
    echo '  '
 fi

else
    echo '  '
    echo '  This scripts requires one argument: There are only two options:'
    echo '  ' $0 activate-pextra-mode
    echo '  ' $0 deactivate-pextra-mode
    echo '  '
fi
