 # Name of this file needs to be changed. Though it is in bash form and possibly could be executed, it is for now more indtended to use
 # as an overview from which in th egiven sequence the scripts can be copied and run in the conmmandline manually.


 # The very compact guidelines in script / commandline form for running the new genecec for CMIP7 ECE3 & ECE4, which is heavily under development.
 # Based on the lessons learned from the ECE3 genecec CMIP6 approach and based on the possibilities for the CMIP7 DR framework: The genecec CMIP7
 # framework is fully based on XML data bases (following the XIOS approach) using XPATH. All scripts are in python and nearly everywhere (at least
 # everywhere were possible) the CMIP7 DR pythin API is used as interface with the CMIP7 DR (using the CMIP7 data request Software repository.
 
 # Currently the CMIP7 DR Software calls the actual CMIP7 DR Content (latest version), this will in its unchanged form try to connect to the internet
 # for the latest Content state, and therefore can be unexpectedly slow with a bad connection or lead to interruption on a platfrom without internet
 # access.

 # Just a script to play around with the CMIP7 DR, based on one of the basic examples provided by the 
  ./cmip7-request.py --all_opportunities --experiments piControl,historical --priority_cutoff high v1.2.2.3 cmip7-v1.2.2.3-request-piControl-historical.json > cmip7-v1.2.2.3-request-piControl-historical.log

 # Create the output-control-files for ECE3 based on the CMIP7 data request:
 ./genecec-cmip7-wrapper.sh high piControl,historical EC-Earth3-ESM-1
 echo " Produces the directory:"
 echo "  cmip7"

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

 ./convert-request-overview-to-xml.py request-overview-cmip6-pextra-all-ECE3-CC.txt
 echo " Produces:"
 echo "  ifspar-info.xml "
 echo "  request-overview-cmip6-pextra-all-ECE3-CC.xml "
 echo "  request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml "

 # From the request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml easily the file with the 238 ECE3 CMIP6 table-variable combinations can be extracted which are
 # not requested by the CMIP7 (prio=high) request. The file is sorted on ECE3 model component:
 echo '<cmip6_variables>'                                                                                                               > list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
 grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="ifs"'     >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
 grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="nemo"'    >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
 grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="lpjg"'    >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
 grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="tm5"'     >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
 grep -e 'no-cmip7-equivalent-var-' request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml | grep -e 'model_component="co2box"'  >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
 echo '</cmip6_variables>'                                                                                                             >> list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
 sed -i -e 's/region="None"     temporal_shape="None"                     //' -e 's/                     dimensions=/dimensions=/'        list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
 sed -i -e 's/cmip7_long_name="None"\s\{3,\}//'                                                                                           list_of_ece3_cmip6_identified_variables_not_in_cmip7.xml
 # Note that \s\{3,\} matches a pattern which will substitute every sequence of at least 3 whitespaces.
 # From the 238 CMIP6 table - variable combinations which are not in the CMIP7 request, 101 unique CMIP6 variables are requested in the CMIP7 request.


# With that we can run:
./cmip7-variable-identification-with-help-of-ECE3-CMIP6.py > cmip7-variable-identification-with-help-of-ECE3-CMIP6.log


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
          bup/cmip7-genecec-files/v03
