#!/bin/bash
#
# Note that manual update of the nemo-only-pre-list-of-identified-missing-cmpi6-requested-variables.xlsx might be necessary.
# The script produces:
#  nemo-only-list-cmpi6-requested-variables.xlsx
#  nemo-miss-list-cmpi6-requested-variables.xlsx
#
# Run example:
#  ./create-nemo-only-list.sh
#


if [ "$#" -eq 0 ]; then

# Procedure to produce the list-of-identified-missing-cmpi6-requested-variables.xlsx based on the most updated shaconemo ping files.
# In this way the variable and table can be provided in the list-of-identified-missing-cmpi6-requested-variables.xlsx while at the
# other hand shaconemo updates can be relatively easy followed by copying the entire variable column. In order to catch all provided
# (non dummy) variables from the shaconemo ping files, we use the total CMIP6 request for all CMIP6 MIPs with highest tier and priority.

# Step 1: request all CMIP6 MIPs for most extended tier and priority:
  cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/; 
  drq -m CMIP,AerChemMIP,C4MIP,CFMIP,DAMIP,DCPP,FAFMIP,GeoMIP,GMMIP,HighResMIP,ISMIP6,LS3MIP,LUMIP,OMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB -t 3 -p 3 -e CMIP  --xls --xlsDir xls-all-cmip6-t=3-p=3

# Step 2: update the Shaconemo repository and thus the ping files:
  cd ${HOME}/cmorize/shaconemo/ping-files/
  ./extract-info-from-ping-files.csh

# Step 3: Manually select the total column of variables in this file:
##  nedit ${HOME}/cmorize/shaconemo/ping-files/r255/cmor-varlist-based-on-ping-r255-without-dummy-lines.txt
# and copy them manually into the variable column in the file (also update the comment column):
##  xdg-open ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/pre-list-of-identified-missing-cmpi6-requested-variables.xlsx
# After updating the pre* files it is most convenient to commit them first.

# Step 4: Temporary overwrite the basic identifiedmissing and basic ignored files:
  cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/; 
  /bin/cp -f create-nemo-only-list/empty-nemopar.json                                                      ../resources/nemopar.json
  /bin/cp -f create-nemo-only-list/empty-list-of-cmpi6-requested-variables.xlsx                            ../resources/list-of-ignored-cmpi6-requested-variables.xlsx
  /bin/cp -f create-nemo-only-list/nemo-only-pre-list-of-identified-missing-cmpi6-requested-variables.xlsx ../resources/list-of-identified-missing-cmpi6-requested-variables.xlsx

# Step 5: Run with the --withouttablescheck option checkvars.py based on the largest data request (and the pre-list-*.xlsx):
   cd ${HOME}/cmorize/ece2cmor3/; python setup.py install; cd -;
   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts;
   ./checkvars.py --withouttablescheck --oce -v --vars  xls-all-cmip6-t=3-p=3/cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.vo_TOTAL_3_3.xlsx  --output cmvmm-all-mips-t=3-p=3
#  xdg-open cmvmm-all-mips-t=3-p=3.identifiedmissing.xlsx
#  xdg-open cmvmm-all-mips-t=3-p=3.ignored.xlsx

# Step 6: Copy the resulting identifiedmissing and ignored produced by the checkvars.py to the basic identifiedmissing and the basic ignored:
   /bin/cp -f cmvmm-all-mips-t=3-p=3.identifiedmissing.xlsx create-nemo-only-list/nemo-only-list-cmpi6-requested-variables.xlsx
   /bin/cp -f cmvmm-all-mips-t=3-p=3.missing.xlsx           create-nemo-only-list/nemo-miss-list-cmpi6-requested-variables.xlsx
   /bin/cp -f cmvmm-all-mips-t=3-p=3.identifiedmissing.txt  create-nemo-only-list/nemo-only-list-cmpi6-requested-variables.txt
   /bin/cp -f cmvmm-all-mips-t=3-p=3.missing.txt            create-nemo-only-list/nemo-miss-list-cmpi6-requested-variables.txt

   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/;
   git checkout nemopar.json
   git checkout list-of-ignored-cmpi6-requested-variables.xlsx
   git checkout list-of-identified-missing-cmpi6-requested-variables.xlsx
   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/; 
   git status 

# Note that in order to create the basic lists from the pre basic fields, the variables in the pre basic lists are matched against the data request by drq in 
# step 1 here, which includes all EC-Earth MIPs for the Core MIP experiments, however this does not include the endorsed MIP experiments (e.g drq -m LS3MIP -e LS3MIP ).
# Therefore the identified missing and ignored vraiables coming from the endorsed MIP experiments have to be added manually to the basic lists.

   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/; 
   /bin/cp -f create-nemo-only-list/empty-nemopar.json                            ../resources/nemopar.json
   /bin/cp -f create-nemo-only-list/empty-list-of-cmpi6-requested-variables.xlsx  ../resources/list-of-ignored-cmpi6-requested-variables.xlsx
   /bin/cp -f create-nemo-only-list/empty-list-of-cmpi6-requested-variables.xlsx  ../resources/list-of-identified-missing-cmpi6-requested-variables.xlsx
   /bin/cp create-nemo-only-list/nemo-only-list-cmpi6-requested-variables.xlsx    ../resources/lists-of-omitted-variables/list-of-omitted-variables-01.xlsx
   /bin/cp create-nemo-only-list/nemo-miss-list-cmpi6-requested-variables.xlsx    ../resources/lists-of-omitted-variables/list-of-omitted-variables-02.xlsx
   rm -f cmvmm-all-mips-t=3-p=3.*
   git status 

# Step 7: :
#  From here on one can uncomment one or more of the data requests below.

# Request for all EC-EARTH3-AOGCM MIPs (+ DAMIP) of the CMIP experiments for tier=1 and priority=1:
# ./determine-missing-variables.sh DCPP,LS3MIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB,DAMIP CMIP 1 1 --oce

# Request for all EC-EARTH3 MIPs (+ DAMIP) of the CMIP experiments for tier=1 and priority=1:
# ./determine-missing-variables.sh CMIP,AerChemMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB,DAMIP CMIP 1 1 --oce

# ./determine-missing-variables.sh AerChemMIP  AerChemMIP   1 1 --oce
# ./determine-missing-variables.sh C4MIP       C4MIP        1 1 --oce
# ./determine-missing-variables.sh DCPP        DCPP         1 1 --oce
# ./determine-missing-variables.sh HighResMIP  HighResMIP   1 1 --oce
# ./determine-missing-variables.sh ISMIP6      ISMIP6       1 1 --oce
# ./determine-missing-variables.sh LS3MIP      LS3MIP       1 1 --oce
# ./determine-missing-variables.sh LUMIP       LUMIP        1 1 --oce
# ./determine-missing-variables.sh PMIP        PMIP         1 1 --oce
# ./determine-missing-variables.sh RFMIP       RFMIP        1 1 --oce
# ./determine-missing-variables.sh ScenarioMIP ScenarioMIP  1 1 --oce
# ./determine-missing-variables.sh VolMIP      VolMIP       1 1 --oce
# ./determine-missing-variables.sh CORDEX      CORDEX       1 1 --oce
# ./determine-missing-variables.sh DynVar      DynVar       1 1 --oce
# ./determine-missing-variables.sh SIMIP       SIMIP        1 1 --oce
# ./determine-missing-variables.sh VIACSAB     VIACSAB      1 1 --oce
# ./determine-missing-variables.sh DAMIP       DAMIP        1 1 --oce

# ll *.missing.xlsx|grep -v 5.5K
# ll *.missing.txt|grep -v 266B
# m *.missing.txt|grep r255

   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/;
   git checkout nemopar.json
   git checkout list-of-ignored-cmpi6-requested-variables.xlsx
   git checkout list-of-identified-missing-cmpi6-requested-variables.xlsx
   git checkout lists-of-omitted-variables/list-of-omitted-variables-01.xlsx
   git checkout lists-of-omitted-variables/list-of-omitted-variables-02.xlsx
   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/; 
   git status 

else
    echo '  '
    echo '  This script can not be executed, because a few manual editting steps are required.'
    echo '  This guidence servers to produce the basic identifiedmissing file and the basic ignored file.'
    echo '  '
fi
