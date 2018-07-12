#!/bin/bash
#
# This script can not be executed, because a few manual editting steps are required.
#
# Run example:
#  ./update-basic-identifiedmissing-ignored-files.sh
#

if [ "$#" -eq -2 ]; then

# Procedure to produce the list-of-identified-missing-cmpi6-requested-variables.xlsx based on the most updated shaconemo ping files.
# In this way the variable and table can be provided in the list-of-identified-missing-cmpi6-requested-variables.xlsx while at the
# other hand shaconemo updates can be relatively easy followed by copying the entire variable column. In order to catch all provided
# (non dummy) variables from the shaconemo ping files, we use the total CMIP6 request for all CMIP6 MIPs with highest tier and priority.

# Step 1: request all CMIP6 MIPs for most extended tier and priority:
  cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/; 
  drq -m CMIP,AerChemMIP,C4MIP,CFMIP,DAMIP,DCPP,FAFMIP,GeoMIP,GMMIP,HighResMIP,ISMIP6,LS3MIP,LUMIP,OMIP,PAMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB -t 3 -p 3 -e CMIP  --xls --xlsDir xls-all-cmip6-t=3-p=3

# Step 2: update the Shaconemo repository and thus the ping files:
  cd ${HOME}/cmorize/shaconemo/ping-files/
  ./extract-info-from-ping-files.csh

# Step 3: Manually select the total column of variables in this file:
  nedit r256/cmor-varlist-based-on-ping-r256-without-dummy-lines.txt
# and copy them manually into the variable column in the file (also update the comment column):
  xdg-open ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/pre-list-of-identified-missing-cmpi6-requested-variables.xlsx
# After updating the pre* files it is most convenient to commit them first.

# Step 4: Temporary overwrite the basic identifiedmissing and basic ignored files by their corresponding pre-* ones:
  cpf ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/pre-list-of-identified-missing-cmpi6-requested-variables.xlsx             ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/list-of-identified-missing-cmpi6-requested-variables.xlsx
  cpf ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/pre-list-of-ignored-cmpi6-requested-variables.xlsx                        ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/list-of-ignored-cmpi6-requested-variables.xlsx

# Step 5: Run with the --withouttablescheck option checkvars.py based on the largest data request (and the pre-list-*.xlsx):
   cd ${HOME}/cmorize/ece2cmor3/; python setup.py install; cd -;
   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts;
   ./checkvars.py --withouttablescheck -v --vars  xls-all-cmip6-t=3-p=3/cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pa.pm.rf.sc.si.vi.vo_TOTAL_3_3.xlsx  --output cmvmm-all-mips-t=3-p=3
#  xdg-open cmvmm-all-mips-t=3-p=3.identifiedmissing.xlsx
#  xdg-open cmvmm-all-mips-t=3-p=3.ignored.xlsx

# Step 6: Copy the resulting identifiedmissing and ignored produced by the checkvars.py to the basic identifiedmissing and the basic ignored:
   cpf cmvmm-all-mips-t=3-p=3.identifiedmissing.xlsx ../resources/list-of-identified-missing-cmpi6-requested-variables.xlsx
   cpf cmvmm-all-mips-t=3-p=3.ignored.xlsx           ../resources/list-of-ignored-cmpi6-requested-variables.xlsx

# Note that in order to create the basic lists from the pre basic fields, the variables in the pre basic lists are matched against the data request by drq in 
# step 1 here, which includes all EC-Earth MIPs for the Core MIP experiments, however this does not include the endorsed MIP experiments (e.g drq -m LS3MIP -e LS3MIP ).
# Therefore the identified missing and ignored variables coming from the endorsed MIP experiments have to be added manually to the basic lists:
#  -Note copying before saving in microsoft format allows correct copying of the links.
#  -Move Antarctic IfxAnt, (IyrAnt) and ImonAnt variables from list-of-identified-missing-cmpi6-requested-variables.xlsx
#   manually to the list-of-ignored-cmpi6-requested-variables.xlsx and adjust the comment.
#  -Move CFsubhr AerChemMIP variables (one block of variables) from list-of-identified-missing-cmpi6-requested-variables.xlsx 
#   manually to list-of-ignored-cmpi6-requested-variables.xlsx
#  -Adding manually the Eday LS3MIP (for step 3 LS3MIP) the variables prrc, ec, tran, evspsblpot, (et)
#   to the list-of-identified-missing-cmpi6-requested-variables.xlsx
#  -Manually adjust the Efx rlu, rsu, tld, rsd comments. [these are gone in data request 01.00.25]


# Test that this replace gives still the same results:
   mkdir -p ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/backup-cmvmm-all-mips-t=3-p=3; rm -f ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/backup-cmvmm-all-mips-t=3-p=3/cmvmm-all-mips-t=3-p=3.*;
   mv ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/cmvmm-all-mips-t=3-p=3.* ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/backup-cmvmm-all-mips-t=3-p=3/;
   cd ${HOME}/cmorize/ece2cmor3/; python setup.py install; cd -;
   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts;
   ./checkvars.py -v --vars  xls-all-cmip6-t=3-p=3/cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pa.pm.rf.sc.si.vi.vo_TOTAL_3_3.xlsx  --output cmvmm-all-mips-t=3-p=3
# The diff is not identical but the excel-diff gives no cel differences:
   diff       ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/cmvmm-all-mips-t=3-p=3.identifiedmissing.txt  ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/backup-cmvmm-all-mips-t=3-p=3/cmvmm-all-mips-t=3-p=3.identifiedmissing.txt
   diff       ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/cmvmm-all-mips-t=3-p=3.ignored.txt            ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/backup-cmvmm-all-mips-t=3-p=3/cmvmm-all-mips-t=3-p=3.ignored.txt
#  excel-diff ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/cmvmm-all-mips-t=3-p=3.identifiedmissing.xlsx ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/backup-cmvmm-all-mips-t=3-p=3/cmvmm-all-mips-t=3-p=3.identifiedmissing.xlsx
#  excel-diff ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/cmvmm-all-mips-t=3-p=3.ignored.xlsx           ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/backup-cmvmm-all-mips-t=3-p=3/cmvmm-all-mips-t=3-p=3.ignored.xlsx

# Note exel-diff is installed by following:
#   https://github.com/na-ka-na/ExcelCompare/blob/master/README.md
# Java is needed, on ubuntu this can be installed by: sudo apt-get update; sudo apt-get install -y default-jre
# Extract the zip and 
#  mv Downloads/ExcelCompare-0.6.1 ${HOME}/bin; cd ${HOME}/bin/; chmod uog+x ExcelCompare-0.6.1/bin/excel_cmp; ln -s ExcelCompare-0.6.1/bin/excel_cmp excel-diff;


else
    echo '  '
    echo '  This script can not be executed, because a few manual editting steps are required.'
    echo '  This guidence servers to produce the basic identifiedmissing file and the basic ignored file.'
    echo '  '
fi
