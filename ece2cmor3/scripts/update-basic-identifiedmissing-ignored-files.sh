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
   cd ${HOME}/cmorize/shaconemo/ping-files/
   ./extract-info-from-ping-files.csh
   nedit r200/cmor-varlist-based-on-ping-r200-without-dummy-lines.txt
# Manually select the total column of variables in this file and copy them manually into the variable column in the file:
   xdg-open ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/pre-list-of-identified-missing-cmpi6-requested-variables.xlsx
# Then temporary copy this into the list-of-identified-missing-cmpi6-requested-variables.xlsx:
   cp ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/pre-list-of-identified-missing-cmpi6-requested-variables.xlsx ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/list-of-identified-missing-cmpi6-requested-variables.xlsx
# Thereafter run the following steps:
# Step 1: request all CMIP6 MIPs for most extended tier and priority:
   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/scripts/; 
   drq -m CMIP,AerChemMIP,C4MIP,CFMIP,DAMIP,DCPP,FAFMIP,GeoMIP,GMMIP,HighResMIP,ISMIP6,LS3MIP,LUMIP,OMIP,PMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB -t 3 -p 3 -e CMIP  --xls --xlsDir xls-all-cmip6-t=3-p=3
# Copy the old version of taskloader.py without the table check:
   cp ${HOME}/cmorize/ece2cmor3/ece2cmor3/taskloader-without-table-check.py ${HOME}/cmorize/ece2cmor3/ece2cmor3/taskloader.py
   cd ${HOME}/cmorize/ece2cmor3/; python setup.py install; cd -;
   ./checkvars.py -v --vars  xls-all-cmip6-t=3-p=3/cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.vo_TOTAL_3_3.xlsx  --output cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.vo_TOTAL_3_3
   op cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.identifiedmissing.xlsx
   cp cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.identifiedmissing.xlsx ../resources/list-of-identified-missing-cmpi6-requested-variables.xlsx
   cp cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.ignored.xlsx           ../resources/list-of-ignored-cmpi6-requested-variables.xlsx
# Reset taskloader.py to the default version:
   git checkout ${HOME}/cmorize/ece2cmor3/ece2cmor3/taskloader.py

# Test that this replace gives still the same results:
   cp cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.identifiedmissing.xlsx bup-cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.identifiedmissing.xlsx
   cp cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.ignored.xlsx           bup-cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.ignored.xlsx
   cd ${HOME}/cmorize/ece2cmor3/; python setup.py install; cd -;
   ./checkvars.py -v --vars  xls-all-cmip6-t=3-p=3/cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.vo_TOTAL_3_3.xlsx  --output cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.vo_TOTAL_3_3
# The diff is not identical but the excel-diff gives no cel differences:
   excel-diff bup-cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.identifiedmissing.xlsx cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.identifiedmissing.xlsx
   excel-diff bup-cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.ignored.xlsx cmvmm_ae.c4.cf.cm.co.da.dc.dy.fa.ge.gm.hi.is.ls.lu.om.pm.rf.sc.si.vi.ignored.xlsx

# Note exel-diff is installed by following:
#   https://github.com/na-ka-na/ExcelCompare/blob/master/README.md
# Extract the zip and 
#  mv Downloads/ExcelCompare-0.6.1 ${HOME}/bin; cd ${HOME}/bin/; ln -s ExcelCompare-0.6.1/bin/excel_cmp excel-diff;


else
    echo '  '
    echo '  This script can not be executed, because a few manual editting steps are required.'
    echo '  This guidence servers to produce the basic identifiedmissing file and the basic ignored file.'
    echo '  '
fi
