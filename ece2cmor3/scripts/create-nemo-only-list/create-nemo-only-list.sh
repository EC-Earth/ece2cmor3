#!/usr/bin/env bash
#
# Note that manual update of the nemo-only-pre-list-of-identified-missing-cmip6-requested-variables.xlsx might be necessary in advance of running this script.
# The script produces:
#  nemo-only-list-cmip6-requested-variables.xlsx
#  nemo-miss-list-cmip6-requested-variables.xlsx
#
# Run example:
#  ./create-nemo-only-list.sh
#


if [ "$#" -eq 0 ]; then

# Procedure to produce the list-of-identified-missing-cmip6-requested-variables.xlsx based on the most updated shaconemo ping files.
# In this way the variable and table can be provided in the list-of-identified-missing-cmip6-requested-variables.xlsx while at the
# other hand shaconemo updates can be relatively easy followed by copying the entire variable column. In order to catch all provided
# (non dummy) variables from the shaconemo ping files, we use the total CMIP6 request for all CMIP6 MIPs with highest tier and priority.

# Step 1: request all CMIP6 MIPs for most extended tier and priority:
  cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/; 
  drq -m CMIP,AerChemMIP,CDRMIP,C4MIP,CFMIP,DAMIP,DCPP,FAFMIP,GeoMIP,GMMIP,HighResMIP,ISMIP6,LS3MIP,LUMIP,OMIP,PAMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB -e CMIP -t 3 -p 3 --xls --xlsDir xls-m=all-cmip6-mips-e=CMIP-t=3-p=3

# Step 2: update the Shaconemo repository and thus the ping files:
# cd ${HOME}/cmorize/shaconemo/ping-files/
# ./extract-info-from-ping-files.csh

# Step 3: Open the following files:
#  cd ${HOME}/cmorize/shaconemo/ping-files/r274/; nedit cmor-*-without-dummy-lines.txt cmor-*-without-dummy-lines-only-model-name.txt cmor-*-without-dummy-lines-comment2.txt cmor-*-without-dummy-lines-only-model-name.txt cmor-*-without-dummy-lines-ping-file-unit.txt cmor-*-without-dummy-lines-ping-file-comment.txt; cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/create-nemo-only-list/;
#  xdg-open ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/create-nemo-only-list/nemo-only-pre-list-of-identified-missing-cmip6-requested-variables.xlsx
# And copy manually the content of the file:
#  cmor-varlist-based-on-ping-r274-without-dummy-lines.txt                   (the cmor variable names)              in the                     "variable"-column of the nemo-only-pre-list-*.xlsx file
#  cmor-varlist-based-on-ping-r274-without-dummy-lines-comment2.txt          (the identification comment)           in the                      "comment"-column of the nemo-only-pre-list-*.xlsx file
#  cmor-varlist-based-on-ping-r274-without-dummy-lines-only-model-name.txt   (the nemo model component)             in the "model component in ping file"-column of the nemo-only-pre-list-*.xlsx file
#  cmor-varlist-based-on-ping-r274-without-dummy-lines-ping-file-unit.txt    (the units from the ping file comment) in the        "units as in ping file"-column of the nemo-only-pre-list-*.xlsx file
#  cmor-varlist-based-on-ping-r274-without-dummy-lines-ping-file-comment.txt (the xml comment in the ping file)     in the            "ping file comment"-column of the nemo-only-pre-list-*.xlsx file
# After updating the pre* file it is most convenient to commit it first.

# Step 4: Temporary overwrite: Use an empty nemopar.json, use an empty list-of-ignored-cmip6-requested-variables.xlsx and use a
#         list-of-identified-missing-cmip6-requested-variables.xlsx which contains the non-dummy ping file variables.
  cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/; 
  /bin/cp -f create-nemo-only-list/empty-nemopar.json                                                      ../resources/nemopar.json
  /bin/cp -f create-nemo-only-list/empty-list-of-cmip6-requested-variables.xlsx                            ../resources/list-of-ignored-cmip6-requested-variables.xlsx
  /bin/cp -f create-nemo-only-list/nemo-only-pre-list-of-identified-missing-cmip6-requested-variables.xlsx ../resources/list-of-identified-missing-cmip6-requested-variables.xlsx
# Use the line below instead of the one above in order to create one list (without ping info, the resulting nemo-miss-list can be used to create a ping file template):
# /bin/cp -f create-nemo-only-list/empty-list-of-cmip6-requested-variables.xlsx                            ../resources/list-of-identified-missing-cmip6-requested-variables.xlsx

# Step 5: Run with the --withouttablescheck option checkvars based on the largest data request (and the pre-list-*.xlsx):
   cd ${HOME}/cmorize/ece2cmor3/; python setup.py develop; cd -;
   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts;
   checkvars --withouttablescheck --withping --nemo -v --drq xls-m=all-cmip6-mips-e=CMIP-t=3-p=3/cmvmm_ae.c4.cd.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pa.pm.rf.sc.si.vi.vo_TOTAL_3_3.xlsx  --output cmvmm-all-mips-t=3-p=3
#  xdg-open cmvmm-all-mips-t=3-p=3.identifiedmissing.xlsx
#  xdg-open cmvmm-all-mips-t=3-p=3.ignored.xlsx

# Step 6: Copy the resulting identifiedmissing and ignored produced by the checkvars to the basic identifiedmissing and the basic ignored:
   /bin/cp -f cmvmm-all-mips-t=3-p=3.identifiedmissing.xlsx create-nemo-only-list/nemo-only-list-cmip6-requested-variables.xlsx
   /bin/cp -f cmvmm-all-mips-t=3-p=3.missing.xlsx           create-nemo-only-list/nemo-miss-list-cmip6-requested-variables.xlsx
  #/bin/cp -f cmvmm-all-mips-t=3-p=3.identifiedmissing.txt  create-nemo-only-list/nemo-only-list-cmip6-requested-variables.txt
  #/bin/cp -f cmvmm-all-mips-t=3-p=3.missing.txt            create-nemo-only-list/nemo-miss-list-cmip6-requested-variables.txt

# Revert the temporary changed files:
   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/;
   git checkout nemopar.json
   git checkout list-of-ignored-cmip6-requested-variables.xlsx
   git checkout list-of-identified-missing-cmip6-requested-variables.xlsx
   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/; 
   git status 

# Note that in order to create the basic lists from the pre basic fields, the variables in the pre basic lists are matched against the data request by drq in 
# step 1 here, which includes all EC-Earth MIPs for the Core MIP experiments, however this does not include the endorsed MIP experiments (e.g drq -m LS3MIP -e LS3MIP ).
# Therefore the identified missing and ignored variables coming from the endorsed MIP experiments have to be added manually to the basic lists.


# Comment next two lines in order to continue with step 7 in this script.
   echo ' Omit step 7 (default) in this script.'
   exit
   echo ' Continue with step 7.'


# This prepares step 7 below:
#  Temporary overwrite: Use an empty nemopar.json, use an empty list-of-ignored-cmip6-requested-variables.xlsx and use an empty
#  list-of-identified-missing-cmip6-requested-variables.xlsx and copy the detected nemo-only and nemo-miss in two ignore files:
   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/; 
   /bin/cp -f create-nemo-only-list/empty-nemopar.json                            ../resources/nemopar.json
   /bin/cp -f create-nemo-only-list/empty-list-of-cmip6-requested-variables.xlsx  ../resources/list-of-ignored-cmip6-requested-variables.xlsx
   /bin/cp -f create-nemo-only-list/empty-list-of-cmip6-requested-variables.xlsx  ../resources/list-of-identified-missing-cmip6-requested-variables.xlsx
   /bin/cp create-nemo-only-list/nemo-only-list-cmip6-requested-variables.xlsx    ../resources/lists-of-omitted-variables/list-of-omitted-variables-01.xlsx
   /bin/cp create-nemo-only-list/nemo-miss-list-cmip6-requested-variables.xlsx    ../resources/lists-of-omitted-variables/list-of-omitted-variables-02.xlsx
   rm -f cmvmm-all-mips-t=3-p=3.*
   git status 

# Step 7: :
#  From here on one can uncomment one or more of the data requests below.

# Step 1: Request for CMIP experiments for tier=1 and priority=1:
# ./determine-missing-variables.sh CMIP       CMIP          1 1 --nemo

# Step 1+2: Request for all EC-EARTH3 MIPs of the CMIP experiments for tier=1 and priority=1:
# ./determine-missing-variables.sh CMIP,AerChemMIP,CDRMIP,C4MIP,DCPP,HighResMIP,ISMIP6,LS3MIP,LUMIP,OMIP,PAMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVarMIP,SIMIP,VIACSAB CMIP 1 1 --nemo

# Step 3:
# ./determine-missing-variables.sh AerChemMIP  AerChemMIP   1 1 --nemo
# ./determine-missing-variables.sh CDRMIP      CDRMIP       1 1 --nemo
# ./determine-missing-variables.sh C4MIP       C4MIP        1 1 --nemo
# ./determine-missing-variables.sh DCPP        DCPP         1 1 --nemo
# ./determine-missing-variables.sh HighResMIP  HighResMIP   1 1 --nemo
# ./determine-missing-variables.sh ISMIP6      ISMIP6       1 1 --nemo
# ./determine-missing-variables.sh LS3MIP      LS3MIP       1 1 --nemo
# ./determine-missing-variables.sh LUMIP       LUMIP        1 1 --nemo
# ./determine-missing-variables.sh OMIP        OMIP         1 1 --nemo
# ./determine-missing-variables.sh PAMIP       PAMIP        1 1 --nemo
# ./determine-missing-variables.sh PMIP        PMIP         1 1 --nemo
# ./determine-missing-variables.sh RFMIP       RFMIP        1 1 --nemo
# ./determine-missing-variables.sh ScenarioMIP ScenarioMIP  1 1 --nemo
# ./determine-missing-variables.sh VolMIP      VolMIP       1 1 --nemo
# ./determine-missing-variables.sh CORDEX      CORDEX       1 1 --nemo
# ./determine-missing-variables.sh DynVarMIP   DynVarMIP    1 1 --nemo
# ./determine-missing-variables.sh SIMIP       SIMIP        1 1 --nemo
# ./determine-missing-variables.sh VIACSAB     VIACSAB      1 1 --nemo

# ll *.missing.xlsx|grep -v 5.5K
# ll *.missing.txt|grep -v 266B
# m *.missing.txt|grep r274

# Revert the temporary changed files:
   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/;
   git checkout nemopar.json
   git checkout list-of-ignored-cmip6-requested-variables.xlsx
   git checkout list-of-identified-missing-cmip6-requested-variables.xlsx
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
