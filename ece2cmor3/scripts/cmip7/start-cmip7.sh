 # Name of this file needs to be changed. Though it is in bash form and possibly could be executed, it is for now more indtended to use
 # as an overview from which in th egiven sequence the scripts can be copied and run in the conmmandline manually.


 # The very compact guidelines in script / commandline form for running the new genecec for CMIP7 ECE3 & ECE4, which is heavily under development.
 # Based on the lessons learned from the ECE3 genecec CMIP6 approach and based on the possibilities for the CMIP7 DR framework: The genecec CMIP7
 # framework is fully based on XML data bases (following the XIOS approach) using XPATH. All scripts are in python and nearly everywhere (at least
 # everywhere were possible) the CMIP7 DR pythin API is used as interface with the CMIP7 DR (using the CMIP7 data request Software repository.
 
 # Currently the CMIP7 DR Software calls the actual CMIP7 DR Content (latest version), this will in its unchanged form try to connect to the internet
 # for the latest Content state, and therefore can be unexpectedly slow with a bad connection or lead to interruption on a platfrom without internet
 # access.

 # With this script one can obtain the CMIP7 requested variables of a specified set of CMIIP7 experiments (it is based on one of the CMIP7 API examples):
 ./cmip7-request.py --all_opportunities --experiments piControl,historical --priority_cutoff high v1.2.2.3
 # Producing the core variable set:
 ./cmip7-request.py --all_opportunities --experiments           historical --priority_cutoff core v1.2.2.3


 # Create the output-control-files for ECE3 based on the CMIP7 data request:
 ./genecec-cmip7-wrapper.sh high piControl,historical EC-Earth3-ESM-1
 ./genecec-cmip7-wrapper.sh core esm-hist             EC-Earth3-ESM-1
 ./genecec-cmip7-wrapper.sh high esm-hist             EC-Earth3-ESM-1
 echo " Produces the directory:"
 echo "  cmip7"


 # Produce component varlist request files (like above) and move them to a backup place:
 ./genecec-cmip7-wrapper.sh core esm-hist             EC-Earth3-ESM-1
 ./genecec-cmip7-wrapper.sh high esm-hist             EC-Earth3-ESM-1
 mv cmip7-requested-varlist-per-experiment.json genecec-cmip7.log summarize.log metadata-of-requested-cmip7-variables.json cmip7 bup/output-control-files-ECE3-ESM-1-CMIP7-esm-hist-core-v03/
 mv cmip7-requested-varlist-per-experiment.json genecec-cmip7.log summarize.log metadata-of-requested-cmip7-variables.json cmip7 bup/output-control-files-ECE3-ESM-1-CMIP7-esm-hist-high-v03/

 # This also produces the cmip6Plus varlists:
 # Actually the optimesm varlist can also direclty taken from: ../resources/miscellaneous-data-requests/optimesm-request/optimesm-request-EC-EARTH-ESM-1-varlist.json
 ./genecec-for-individual-experiments.sh ../resources/miscellaneous-data-requests/optimesm-request/optimesm-request-EC-EARTH-ESM-1-varlist.json CMIP        esm-hist                 EC-EARTH-ESM-1   optimesm  &> genecec-for-individual-experiments.log
 mv genecec-for-individual-experiments.log optimesm/
 mv optimesm bup/optimesm/optimesm-v03

 # Combine and merge the OptimESM data request files and the CMIP7 request files:
 ./combine-and-merge-json-request-files.py bup/optimesm/optimesm-v03/optimesm-request-EC-EARTH-ESM-1-varlist.json cmip7/bup/output-control-files-ECE3-ESM-1-CMIP7-esm-hist-core-v03/cmip7/esm-hist-core-EC-Earth3-ESM-1/component-request-cmip7-esm-hist-core-EC-Earth3-ESM-1.json combined-optimesm-cmip7-core-request-EC-EARTH-ESM-1-varlist.json
 ./combine-and-merge-json-request-files.py bup/optimesm/optimesm-v03/optimesm-request-EC-EARTH-ESM-1-varlist.json cmip7/bup/output-control-files-ECE3-ESM-1-CMIP7-esm-hist-high-v03/cmip7/esm-hist-high-EC-Earth3-ESM-1/component-request-cmip7-esm-hist-high-EC-Earth3-ESM-1.json combined-optimesm-cmip7-high-request-EC-EARTH-ESM-1-varlist.json

 # Create the output-control-files for the combined OptimESM - CMIP7-FT request:
 ./genecec-for-individual-experiments.sh combined-optimesm-cmip7-core-request-EC-EARTH-ESM-1-varlist.json                                       CMIP        esm-hist                 EC-EARTH-ESM-1   bup/optimesm/optimesm-cmip7-ft-core-v01  &> genecec-for-individual-experiments-optimesm-cmip7-ft-core.log
 ./genecec-for-individual-experiments.sh combined-optimesm-cmip7-high-request-EC-EARTH-ESM-1-varlist.json                                       CMIP        esm-hist                 EC-EARTH-ESM-1   bup/optimesm/optimesm-cmip7-ft-high-v01  &> genecec-for-individual-experiments-optimesm-cmip7-ft-high.log
 mv genecec-for-individual-experiments-optimesm-cmip7-ft-core.log bup/optimesm/optimesm-cmip7-ft-core-v01
 mv genecec-for-individual-experiments-optimesm-cmip7-ft-high.log bup/optimesm/optimesm-cmip7-ft-high-v01


 # Requesting the variables for all experiments and for all priority levels (which creates an XML file which contains all CMIP7 variables including
 # the highest encountered priority for each variable):
 ./cmip7-request.py --all_opportunities --priority_cutoff low -r v1.2.2.3 > cmip7-request-v1.2.2.3-all.log-more

 grep '    adjusted'                  cmip7-request-v1.2.2.3-all.log                                             | wc  # = 1816 occurences
 grep 'Different priorities detected' cmip7-request-v1.2.2.3-all.log                                             | wc  # = 3517 occurences
 grep 'Different priorities detected' cmip7-request-v1.2.2.3-all.log | tr -s ' ' | cut -d ' ' -f 9 | sort | uniq | wc  # =  224 occurences
 grep 'Priority adjusted from'        cmip7-request-v1.2.2.3-all.log | tr -s ' ' | cut -d ' ' -f 9 | sort | uniq | wc  # =   52 occurences

 # The searches for establishing the iterate lists for the realm & cmip6_table ordering in the cmip7-request.py script code:
 grep -e cmip7_compound_name cmip7-request-v1.2.2.3-all-priority-ordered.xml | sed -e 's/.*cmip7_compound_name="//' -e 's/\..*physical_parameter_name.*//' | sort | uniq
 grep -e 'cmip6_table=' cmip7-request-v1.2.2.3-all-priority-ordered.xml |sed -e 's/.*cmip6_table=//' -e 's/ .*region.*//' | sort | uniq | grep fx
 grep -e 'cmip6_table=' cmip7-request-v1.2.2.3-all-priority-ordered.xml |sed -e 's/.*cmip6_table=//' -e 's/ .*region.*//' | sort | uniq | grep hr
 grep -e 'cmip6_table=' cmip7-request-v1.2.2.3-all-priority-ordered.xml |sed -e 's/.*cmip6_table=//' -e 's/ .*region.*//' | sort | uniq | grep day
 grep -e 'cmip6_table=' cmip7-request-v1.2.2.3-all-priority-ordered.xml |sed -e 's/.*cmip6_table=//' -e 's/ .*region.*//' | sort | uniq | grep mon
 grep -e 'cmip6_table=' cmip7-request-v1.2.2.3-all-priority-ordered.xml |sed -e 's/.*cmip6_table=//' -e 's/ .*region.*//' | sort | uniq | grep yr
 grep -e 'cmip6_table=' cmip7-request-v1.2.2.3-all-priority-ordered.xml |sed -e 's/.*cmip6_table=//' -e 's/ .*region.*//' | sort | uniq | grep -v -e fx -e hr -e day -e mon -e yr



 ./convert-grib-table-to-xml.py grib-table.xml
 echo " Produces:"
 echo "  grib-table.xml"


 ./create-basic-ecearth4-cmip7-xios-configuration-file.py config-create-basic-ecearth4-cmip7-xios-configuration-file
 echo " Produces:"
 echo "  ping_ocean_DR1.00.27_comment_in_attribute.xml     "
 echo "  ping_seaIce_DR1.00.27_comment_in_attribute.xml    "
 echo "  ping_ocnBgChem_DR1.00.27_comment_in_attribute.xml "
 echo "  ec-earth-ping.xml                                 "
 echo "  ec-earth-ping-canonic.xml                         "
 echo "  ec-earth-ping-neat-formatted.xml                  "

 ./scan-xios-xml-elementtree-structure.py > scan.log
 echo " Produces:"
 echo "  ec-earth-definition.xml                          "
 echo "  ec-earth-definition-canonic.xml                  "
 echo "  ec-earth-definition-neat-formatted.xml           "
 echo "  ec-earth-definition-inherited.xml                "
 echo "  ec-earth-definition-inherited-neat-formatted.xml "

 ./cmip6-cmip7-variable-mapping.py -r v1.2.2.3
 echo " Produces:"
 echo "  cmip7-variables-and-metadata-all.xml "
#echo "  cmip7-variables-and-metadata-all.txt "

 # Generate (archived in repository) the possible input file for convert-request-overview-to-xml.py:
 #  grep -v -e cWood ~/cmorize/control-output-files/output-control-files-v460/cmip6-pextra/test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-CC-preferences.txt > request-overview-cmip6-pextra-all-ECE3-CC.txt
 # In the resulting file: request-overview-cmip6-pextra-all-ECE3-CC.txt additional spaces before the unit has been inserted for now, this has to be corrected in taskloader.
 ./convert-request-overview-to-xml.py request-overview-cmip6-pextra-all-ECE3-CC.txt
 echo " Produces:"
 echo "  ifspar-info.xml "
 echo "  request-overview-cmip6-pextra-all-ECE3-CC.xml "
 echo "  request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml "

 # From the request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml easily the file with the 238 ECE3 CMIP6 table-variable combinations can be extracted which are
 # not requested by the CMIP7 request:
 grep -e cmip6_variables -e no-cmip7-equivalent-var- request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml                       > xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7.xml
 sed -i -e 's/region="None"     temporal_shape="None"                     //' -e 's/                     dimensions=/dimensions=/'        xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7.xml
 sed -i -e 's/cmip7_long_name="None"\s\{3,\}//'                                                                                           xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7.xml
 # The same, but the file is sorted on ECE3 model component:
 echo '<cmip6_variables>'                                                                                                               > xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7-component-ordered.xml
 grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="ifs"'     >> xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7-component-ordered.xml
 grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="nemo"'    >> xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7-component-ordered.xml
 grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="lpjg"'    >> xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7-component-ordered.xml
 grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="tm5"'     >> xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7-component-ordered.xml
 grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="co2box"'  >> xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7-component-ordered.xml
 echo '</cmip6_variables>'                                                                                                             >> xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7-component-ordered.xml
 sed -i -e 's/region="None"     temporal_shape="None"                     //' -e 's/                     dimensions=/dimensions=/'        xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7-component-ordered.xml
 sed -i -e 's/cmip7_long_name="None"\s\{3,\}//'                                                                                           xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7-component-ordered.xml
 # Note that \s\{3,\} matches a pattern which will substitute every sequence of at least 3 whitespaces.
 # From the 238 CMIP6 table - variable combinations which are not in the CMIP7 request, 101 unique CMIP6 variables are requested in the CMIP7 request.


 # With that we can run (actually this script is replaced by the identify-ece4-cmip7-request.py script):
 ./cmip7-variable-identification-with-help-of-ECE3-CMIP6.py > cmip7-variable-identification-with-help-of-ECE3-CMIP6.log

 # Create the combined files with the CMIP7 requested variables for all priorities with the ECE3 - CMIP6 matched identification info where possible,
 # ordered in a way to allow convenient working on these lists:
 ./identify-ece4-cmip7-request.py -a > identify-ece4-cmip7-request.log

 # Archive the most important, best ordered XML files:
 rsync -a cmip7-request-v1.2.2.3-all-full-identified-freq-mc-prio.xml      xml-files/
 rsync -a cmip7-request-v1.2.2.3-all-full-var_identified-freq-mc-prio.xml  xml-files/
 rsync -a cmip7-request-v1.2.2.3-all-full-unidentified-freq-realm-prio.xml xml-files/


 # Create a backup reference of all identify-ece4-cmip7-request.py created files:
 rsync -a cmip7-request-v1.2.2.3-all-full*.xml identify-ece4-cmip7-request.log  bup/identification/v33


 # Create a backup reference of all produced files:
 rsync -a cmip7-requested-varlist-per-experiment.json                    \
          cmip7-v1.2.2.3-request-piControl-historical.json               \
          cmip7-variables-and-metadata-all.xml                           \
          ec-earth-definition-canonic.xml                                \
          ec-earth-definition-inherited-neat-formatted.xml               \
          ec-earth-definition-inherited.xml                              \
          ec-earth-definition-neat-formatted.xml                         \
          ec-earth-definition.xml                                        \
          ec-earth-ping-canonic.xml                                      \
          ec-earth-ping-neat-formatted.xml                               \
          ec-earth-ping.xml                                              \
          grib-table.xml                                                 \
          ifspar-info.xml                                                \
          metadata-of-requested-cmip7-variables.json                     \
          ping_ocean_DR1.00.27_comment_in_attribute.xml                  \
          ping_ocnBgChem_DR1.00.27_comment_in_attribute.xml              \
          ping_seaIce_DR1.00.27_comment_in_attribute.xml                 \
          request-overview-cmip6-pextra-all-ECE3-CC.xml                  \
          request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml   \
          bup/cmip7-genecec-files/v04


# Opening freqeuntly used files:
#  n *.py config-* *.sh
#  n create-basic-ec-earth-cmip6-nemo-namelist.py config-create-basic-ec-earth-cmip6-nemo-namelist create-basic-ec-earth-cmip6-nemo-namelist.log ../resources/xios-nemo-file_def-files/basic-* ~/ec-earth/ecearth3/trunk/runtime/classic/ctrl/ping_* ~/ec-earth/ecearth3/trunk/runtime/classic/ctrl/field_def_nemo-*
#  n ~/cmorize/control-output-files/output-control-files-v460/cmip6-pextra/test-all-ece-mip-variables/*
#  n cmip7-variables-and-metadata-all.xml ec-earth-ping-neat-formatted.xml ec-earth-definition-inherited-neat-formatted.xml request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml ifspar-info.xml cmip7-request-v1.2.2.3-all-full-*identified-freq*prio.xml


# To do:
# - Use request overview neat formatted file to loop over the identified variables and add / adjust / compare the ECE field_def file
# - lpjg variables via .ins files
# - The identified and var_identified variables need to be incorporated into the ECE4 field_def file.

# - DRS format and with help of CMIP7 attributes a cmor-metadata-fixer for CMIP6 => CMIP7 possible?
# The CMIP7 archive organizes files hierarchically using the following DRS pattern:
#  <drs_specs>/<mip_era>/<activity_id>/<institution_id>/<source_id>/<experiment_id>/<variant_label>/<region>/<frequency>/variable_d>/<branding_suffix>/<grid_label>/<directoryDateDD>
# Example: MIP-DRS7/CMIP7/CMIP/CCCma/CanESM6-MR/historical/r2i1p1f1/glb/mon/tas/tavg-h2m-hxy-u/g13s/v20250622
# Source: https://wcrp-cmip.github.io/cmip7-guidance/CMIP7/global_attributes/

# From the  894 identified      variables there are  553 unique variables
# From the  242 var_identified  variables there are  163 unique variables
# From the  838 unidentified    variables there are  587 unique variables
# From the  238 non-cmip7       variables there are  101 unique variables
# The latter are variables which were identified within the ECE3-CMIP6 framework but which are not requested by CMIP7.


#  The CMIP7 - CMIP6 units check (CMIP7 units are used), one cases shows up:
#   CMIP7 unit: kg m-2 s-1  not equal to CMIP6 unit: mol s-1  for aerosol.emilnox.tavg-u-hxy-u.mon.glb   https://clipc-services.ceda.ac.uk/dreq/u/534001c2fd879bfda1d9b66d0a61144c.html

# For data request version v1.2.2.3, number of requested variables found by experiment:
#   1pctCO2                                                 : Core=  131, High=  915, Medium=  135, Low=   95, TOTAL= 1276
#   1pctCO2-bgc                                             : Core=  131, High=  809, Medium=  186, Low=   79, TOTAL= 1205
#   1pctCO2-rad                                             : Core=  131, High=  809, Medium=  186, Low=   79, TOTAL= 1205
#   abrupt-0p5CO2                                           : Core=  131, High=  954, Medium=  154, Low=   88, TOTAL= 1327
#   abrupt-127k                                             : Core=  131, High=  873, Medium=  154, Low=   70, TOTAL= 1228
#   abrupt-2xCO2                                            : Core=  131, High=  954, Medium=  154, Low=   88, TOTAL= 1327
#   abrupt-4xCO2                                            : Core=  131, High=  915, Medium=  135, Low=   95, TOTAL= 1276
#   amip                                                    : Core=  131, High=  978, Medium=  206, Low=   96, TOTAL= 1411
#   amip-irr                                                : Core=  131, High=    6, Medium=   11, Low=   22, TOTAL=  170
#   amip-m4K                                                : Core=  131, High=  263, Medium=    0, Low=   52, TOTAL=  446
#   amip-noirr                                              : Core=  131, High=    6, Medium=   11, Low=   22, TOTAL=  170
#   amip-p4K-SST-rad                                        : Core=  131, High=  263, Medium=    0, Low=   52, TOTAL=  446
#   amip-p4K-SST-turb                                       : Core=  131, High=  263, Medium=    0, Low=   52, TOTAL=  446
#   amip-p4k                                                : Core=  131, High= 1051, Medium=  214, Low=   97, TOTAL= 1493
#   amip-piForcing                                          : Core=  131, High=  887, Medium=  184, Low=   97, TOTAL= 1299
#   dcppA-assim                                             : Core=  131, High=   26, Medium=   96, Low=    0, TOTAL=  253
#   dcppA-hindcast                                          : Core=  131, High=   26, Medium=   96, Low=    0, TOTAL=  253
#   dcppB-forecast                                          : Core=  131, High=   26, Medium=   96, Low=    0, TOTAL=  253
#   dcppB-forecast-cmip6                                    : Core=  131, High=  852, Medium=  270, Low=   87, TOTAL= 1340
#   esm-flat10                                              : Core=  131, High=  795, Medium=  173, Low=   70, TOTAL= 1169
#   esm-flat10-cdr                                          : Core=  131, High=  795, Medium=  173, Low=   70, TOTAL= 1169
#   esm-flat10-zec                                          : Core=  131, High=  795, Medium=  173, Low=   70, TOTAL= 1169
#   esm-hist                                                : Core=  131, High= 1130, Medium=  481, Low=  112, TOTAL= 1854
#   esm-piControl                                           : Core=  131, High= 1035, Medium=  351, Low=  101, TOTAL= 1618
#   esm-s7h-noFireChange                                    : Core=  131, High=   82, Medium=    0, Low=    0, TOTAL=  213
#   esm-scen7-h                                             : Core=  131, High= 1059, Medium=  460, Low=  102, TOTAL= 1752
#   esm-scen7-h-AQ                                          : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   esm-scen7-h-Aer                                         : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   esm-scen7-h-ext                                         : Core=  131, High=  372, Medium=  280, Low=   49, TOTAL=  832
#   esm-scen7-hl                                            : Core=  131, High= 1027, Medium=  438, Low=  102, TOTAL= 1698
#   esm-scen7-hl-ext                                        : Core=  131, High=  289, Medium=  209, Low=   47, TOTAL=  676
#   esm-scen7-l                                             : Core=  131, High= 1059, Medium=  460, Low=  102, TOTAL= 1752
#   esm-scen7-l-ext                                         : Core=  131, High=  362, Medium=  152, Low=   49, TOTAL=  694
#   esm-scen7-ln                                            : Core=  131, High= 1027, Medium=  438, Low=  102, TOTAL= 1698
#   esm-scen7-ln-ext                                        : Core=  131, High=  279, Medium=   81, Low=   47, TOTAL=  538
#   esm-scen7-m                                             : Core=  131, High= 1070, Medium=  483, Low=   99, TOTAL= 1783
#   esm-scen7-m-ext                                         : Core=  131, High=  372, Medium=  280, Low=   49, TOTAL=  832
#   esm-scen7-ml                                            : Core=  131, High= 1059, Medium=  460, Low=  102, TOTAL= 1752
#   esm-scen7-ml-ext                                        : Core=  131, High=  325, Medium=  231, Low=   47, TOTAL=  734
#   esm-scen7-vl                                            : Core=  131, High= 1027, Medium=  438, Low=  102, TOTAL= 1698
#   esm-scen7-vl-AQ                                         : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   esm-scen7-vl-Aer                                        : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   esm-scen7-vl-ext                                        : Core=  131, High=  289, Medium=  209, Low=   47, TOTAL=  676
#   g7-1p5K-sai                                             : Core=  131, High=  855, Medium=  212, Low=   71, TOTAL= 1269
#   highres-future-scen7-m                                  : Core=  131, High=   68, Medium=   94, Low=   24, TOTAL=  317
#   highresSST-p2k-pat                                      : Core=  131, High=   68, Medium=   94, Low=   24, TOTAL=  317
#   highresSST-p4k-pat                                      : Core=  131, High=   68, Medium=   94, Low=   24, TOTAL=  317
#   hist-1950                                               : Core=  131, High=   68, Medium=   94, Low=   24, TOTAL=  317
#   hist-GHG                                                : Core=  131, High=  864, Medium=  232, Low=   79, TOTAL= 1306
#   hist-aer                                                : Core=  131, High=  864, Medium=  232, Low=   79, TOTAL= 1306
#   hist-irr                                                : Core=  131, High=    6, Medium=   11, Low=   22, TOTAL=  170
#   hist-nat                                                : Core=  131, High=  864, Medium=  232, Low=   79, TOTAL= 1306
#   hist-noFire                                             : Core=  131, High=   82, Medium=    0, Low=    0, TOTAL=  213
#   hist-noirr                                              : Core=  131, High=    6, Medium=   11, Low=   22, TOTAL=  170
#   hist-piAQ                                               : Core=  131, High=  805, Medium=  184, Low=   79, TOTAL= 1199
#   hist-piAer                                              : Core=  131, High=  805, Medium=  184, Low=   79, TOTAL= 1199
#   historical                                              : Core=  131, High= 1130, Medium=  481, Low=  112, TOTAL= 1854
#   land-hist                                               : Core=  131, High=  834, Medium=  241, Low=   71, TOTAL= 1277
#   piClim-4xCO2                                            : Core=  131, High=  822, Medium=  117, Low=   90, TOTAL= 1160
#   piClim-CH4                                              : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   piClim-N2O                                              : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   piClim-NOX                                              : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   piClim-ODS                                              : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   piClim-SO2                                              : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   piClim-aer                                              : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   piClim-anthro                                           : Core=  131, High=  839, Medium=  122, Low=   90, TOTAL= 1182
#   piClim-control                                          : Core=  131, High=  822, Medium=  117, Low=   90, TOTAL= 1160
#   piClim-histaer                                          : Core=  131, High=  795, Medium=  173, Low=   70, TOTAL= 1169
#   piClim-histall                                          : Core=  131, High=  795, Medium=  173, Low=   70, TOTAL= 1169
#   piControl                                               : Core=  131, High= 1035, Medium=  351, Low=  101, TOTAL= 1618
#   scen7-h                                                 : Core=  131, High= 1059, Medium=  460, Low=  102, TOTAL= 1752
#   scen7-h-AQ                                              : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   scen7-h-Aer                                             : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   scen7-h-ext                                             : Core=  131, High=  389, Medium=  281, Low=   49, TOTAL=  850
#   scen7-hl                                                : Core=  131, High= 1027, Medium=  438, Low=  102, TOTAL= 1698
#   scen7-hl-ext                                            : Core=  131, High=  307, Medium=  211, Low=   47, TOTAL=  696
#   scen7-l                                                 : Core=  131, High= 1059, Medium=  460, Low=  102, TOTAL= 1752
#   scen7-l-ext                                             : Core=  131, High=  379, Medium=  153, Low=   49, TOTAL=  712
#   scen7-ln                                                : Core=  131, High= 1027, Medium=  438, Low=  102, TOTAL= 1698
#   scen7-ln-ext                                            : Core=  131, High=  297, Medium=   83, Low=   47, TOTAL=  558
#   scen7-m                                                 : Core=  131, High= 1070, Medium=  483, Low=   99, TOTAL= 1783
#   scen7-m-ext                                             : Core=  131, High=  389, Medium=  281, Low=   49, TOTAL=  850
#   scen7-ml                                                : Core=  131, High= 1059, Medium=  460, Low=  102, TOTAL= 1752
#   scen7-ml-ext                                            : Core=  131, High=  343, Medium=  233, Low=   47, TOTAL=  754
#   scen7-vl                                                : Core=  131, High= 1027, Medium=  438, Low=  102, TOTAL= 1698
#   scen7-vl-AQ                                             : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   scen7-vl-Aer                                            : Core=  131, High=  799, Medium=  177, Low=   73, TOTAL= 1180
#   scen7-vl-ext                                            : Core=  131, High=  307, Medium=  211, Low=   47, TOTAL=  696
#   tipmip-provisional-esm-up2p0                            : Core=  131, High=   16, Medium=   36, Low=    0, TOTAL=  183
#   tipmip-provisional-esm-up2p0-gwl1p5                     : Core=  131, High=   16, Medium=   36, Low=    0, TOTAL=  183
#   tipmip-provisional-esm-up2p0-gwl2p0                     : Core=  131, High=   16, Medium=   36, Low=    0, TOTAL=  183
#   tipmip-provisional-esm-up2p0-gwl2p0-50y-dn2p0           : Core=  131, High=   16, Medium=   36, Low=    0, TOTAL=  183
#   tipmip-provisional-esm-up2p0-gwl3p0                     : Core=  131, High=   16, Medium=   36, Low=    0, TOTAL=  183
#   tipmip-provisional-esm-up2p0-gwl4p0                     : Core=  131, High=   16, Medium=   36, Low=    0, TOTAL=  183
#   tipmip-provisional-esm-up2p0-gwl4p0-50y-dn2p0           : Core=  131, High=   16, Medium=   36, Low=    0, TOTAL=  183
#   tipmip-provisional-esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0    : Core=  131, High=   16, Medium=   36, Low=    0, TOTAL=  183
#   tipmip-provisional-esm-up2p0-gwl5p0                     : Core=  131, High=   16, Medium=   36, Low=    0, TOTAL=  183
