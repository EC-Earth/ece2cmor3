#!/bin/bash
#
# This tiny script just prints the alias commands to check whether the content of the following files:
#  nemo-only-list-cmpi6-requested-variables.xlsx
#  nemo-miss-list-cmpi6-requested-variables.xlsx
# has changed compared to the git archived version.
#
# Note exel-diff is installed by following:
#   https://github.com/na-ka-na/ExcelCompare/blob/master/README.md
# Java is needed, on ubuntu this can be installed by: sudo apt update; sudo apt install -y default-jre
# Extract the zip and 
#  cd ${HOME}; mv Downloads/ExcelCompare-0.6.1 ${HOME}/bin; cd ${HOME}/bin/; chmod uog+x ExcelCompare-0.6.1/bin/excel_cmp; ln -s ExcelCompare-0.6.1/bin/excel_cmp excel-diff;
#
# Run example:
#  ./check-nemo-archived-xlsx-files.sh
#

 echo ' Run:'
 echo "  rm -f gitdiff-nemo*; gitexceldiff nemo-only-list-cmpi6-requested-variables.xlsx; mv -f gitdiff.txt gitdiff-nemo-only.txt; gitexceldiff nemo-miss-list-cmpi6-requested-variables.xlsx; mv -f gitdiff.txt gitdiff-nemo-miss.txt;"
 echo ' '
 echo ' View the differences by:'
 echo '  nedit gitdiff-nemo-* &'
 echo ' '
 echo ' Remove the git diff files by:'
 echo '  rm -f gitdiff-nemo-*'
 echo ' '
 echo ' Revert the git archived xlsx files by:'
 echo '  git checkout nemo-miss-list-cmpi6-requested-variables.xlsx nemo-only-list-cmpi6-requested-variables.xlsx'
 echo ' '
