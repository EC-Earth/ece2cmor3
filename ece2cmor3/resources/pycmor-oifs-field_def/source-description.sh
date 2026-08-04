# This field_def file for OIFS is taken from pycmor from its current (august 2026)
# feat/cmip7-awiesm3-veg-hr branch.

# The followed procedure has been:
   cd ${HOME}/cmorize/
   git clone   https://github.com/esm-tools/pycmor.git
   cd pycmor
   git checout feat/cmip7-awiesm3-veg-hr
   ls awi-esm3-veg-hr-variables/field_def_cmip7.xml.j2

   cd ${HOME}/cmorize/ece2cmor3/ece2cmor3/resources/pycmor-oifs-field_def/
   rsync -a ${HOME}/cmorize/pycmor/awi-esm3-veg-hr-variables/field_def_cmip7.xml.j2 field_def_oifs_cmip7_pycmor.xml.j2

# And at the head of this file, for highlight syntax pupose, the following line was added:
 <?xml version="1.0"?>

# So checking the files with:
   diff ${HOME}/cmorize/pycmor/awi-esm3-veg-hr-variables/field_def_cmip7.xml.j2 field_def_oifs_cmip7_pycmor.xml.j2
