#!/usr/bin/env bash

# ECE4 genecec-cmip7:

if [ "$#" -eq 1 ]; then

  version=$1

  data_request_version=v1.2.2.3

  # Requesting the variables for all experiments and for all priority levels (which creates an XML file which contains all CMIP7 variables including
  # the highest encountered priority for each variable):
  ./cmip7-request.py --all_opportunities --priority_cutoff low -r ${data_request_version} > cmip7-request.log
  mv -f cmip7-request.log cmip7-request-${data_request_version}-all/

  log_file=cmip7-request-${data_request_version}-all/cmip7-request-${data_request_version}-all.log
  xml_file=cmip7-request-${data_request_version}-all/cmip7-request-${data_request_version}-all-priority-ordered.xml

  grep '    adjusted'                  ${log_file}                                             | wc  # = 1816 occurences
  grep 'Different priorities detected' ${log_file}                                             | wc  # = 3517 occurences
  grep 'Different priorities detected' ${log_file} | tr -s ' ' | cut -d ' ' -f 9 | sort | uniq | wc  # =  224 occurences
  grep 'Priority adjusted from'        ${log_file} | tr -s ' ' | cut -d ' ' -f 9 | sort | uniq | wc  # =   52 occurences

  # The searches for establishing the iterate lists for the realm & cmip6_table ordering in the cmip7-request.py script code:
  grep -e 'cmip7_compound_name=' ${xml_file} | sed -e 's/.*cmip7_compound_name="//' -e 's/\..*physical_parameter_name.*//' | sort | uniq                                           | tr '\n' ',' | sed -e 's/,/", "/g' -e 's/, "$/\n/' -e 's/^/\n"/'
  grep -e 'cmip6_table='         ${xml_file} | sed -e 's/.*cmip6_table=//'          -e 's/ .*physical_parameter_name.*//'  | sort | uniq | grep fx                                 | tr '\n' ',' | sed -e 's/,/, /g'   -e 's/$/ \\\n/'
  grep -e 'cmip6_table='         ${xml_file} | sed -e 's/.*cmip6_table=//'          -e 's/ .*physical_parameter_name.*//'  | sort | uniq | grep hr                                 | tr '\n' ',' | sed -e 's/,/, /g'   -e 's/$/ \\\n/'
  grep -e 'cmip6_table='         ${xml_file} | sed -e 's/.*cmip6_table=//'          -e 's/ .*physical_parameter_name.*//'  | sort | uniq | grep day                                | tr '\n' ',' | sed -e 's/,/, /g'   -e 's/$/ \\\n/'
  grep -e 'cmip6_table='         ${xml_file} | sed -e 's/.*cmip6_table=//'          -e 's/ .*physical_parameter_name.*//'  | sort | uniq | grep mon                                | tr '\n' ',' | sed -e 's/,/, /g'   -e 's/$/ \\\n/'
  grep -e 'cmip6_table='         ${xml_file} | sed -e 's/.*cmip6_table=//'          -e 's/ .*physical_parameter_name.*//'  | sort | uniq | grep yr                                 | tr '\n' ',' | sed -e 's/,/, /g'   -e 's/$/ \\\n/'
  grep -e 'cmip6_table='         ${xml_file} | sed -e 's/.*cmip6_table=//'          -e 's/ .*physical_parameter_name.*//'  | sort | uniq | grep -v -e fx -e hr -e day -e mon -e yr | tr '\n' ',' | sed -e 's/,/, /g'   -e 's/$/ \\\n/'

  # Independent of other genecec-cmip7 generated files:
  ./convert-grib-table-to-xml.py xml-files/genecec-cmip7/grib-table.xml

  # Independent of other genecec-cmip7 generated files:
  ./create-basic-ecearth4-cmip7-xios-configuration-file.py config-create-basic-ecearth4-cmip7-xios-configuration-file

  # Independent of other genecec-cmip7 generated files:
  ./scan-xios-xml-elementtree-structure.py > scan.log
  mkdir -p archive/log-files/${version}/
  mv -f scan.log archive/log-files/${version}/

  # Independent of other genecec-cmip7 generated files:
  ./cmip6-cmip7-variable-mapping.py -r ${data_request_version}

  # Depending on the genecec-cmip7 input files:
  #  xml-files/genecec-cmip7/grib-table.xml
  #  xml-files/genecec-cmip7/cmip7-variables-and-metadata-all.xml
  #  request-overview-cmip6-pextra-all-ECE3-CC.txt  (in repository, actually a genecec cmip6 file)
  # The latter request-overview file equals:
  diff ~/cmorize/control-output-files/output-control-files-v462/cmip6-pextra/test-all-ece-mip-variables/request-overview-all-including-EC-EARTH-CC-preferences.txt request-overview-cmip6-pextra-all-ECE3-CC.txt
  ./convert-request-overview-to-xml.py request-overview-cmip6-pextra-all-ECE3-CC.txt

  # From the ${request_overview_xml_file} easily the file with the 238 ECE3 CMIP6 table-variable combinations can be extracted which are
  # not requested by the CMIP7 request:
  request_overview_xml_file=./xml-files/genecec-cmip7/request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml
  non_requested_cmip7_file=xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7.xml
  non_requested_cmip7_ordered_file=xml-files/ece3-cmip6-identified-variables-not-requested-by-cmip7-component-ordered.xml
  grep -e cmip6_variables -e no-cmip7-equivalent-var- ${request_overview_xml_file}                                                  >  ${non_requested_cmip7_file}
  sed -i -e 's/region="None"     temporal_shape="None"                     //' -e 's/                     dimensions=/dimensions=/'    ${non_requested_cmip7_file}
  sed -i -e 's/cmip7_long_name="None"\s\{3,\}//'                                                                                       ${non_requested_cmip7_file}
  # The same, but the file is sorted on ECE3 model component:
  echo '<cmip6_variables>'                                                                                                          >  ${non_requested_cmip7_ordered_file}
  grep -e 'no-cmip7-equivalent-var-' ${request_overview_xml_file} | grep -e 'model_component="ifs"'                                 >> ${non_requested_cmip7_ordered_file}
  grep -e 'no-cmip7-equivalent-var-' ${request_overview_xml_file} | grep -e 'model_component="nemo"'                                >> ${non_requested_cmip7_ordered_file}
  grep -e 'no-cmip7-equivalent-var-' ${request_overview_xml_file} | grep -e 'model_component="lpjg"'                                >> ${non_requested_cmip7_ordered_file}
  grep -e 'no-cmip7-equivalent-var-' ${request_overview_xml_file} | grep -e 'model_component="tm5"'                                 >> ${non_requested_cmip7_ordered_file}
  grep -e 'no-cmip7-equivalent-var-' ${request_overview_xml_file} | grep -e 'model_component="co2box"'                              >> ${non_requested_cmip7_ordered_file}
  echo '</cmip6_variables>'                                                                                                         >> ${non_requested_cmip7_ordered_file}
  sed -i -e 's/region="None"     temporal_shape="None"                     //' -e 's/                     dimensions=/dimensions=/'    ${non_requested_cmip7_ordered_file}
  sed -i -e 's/cmip7_long_name="None"\s\{3,\}//'                                                                                       ${non_requested_cmip7_ordered_file}
  # Note that \s\{3,\} matches a pattern which will substitute every sequence of at least 3 whitespaces.
  # From the 238 CMIP6 table - variable combinations which are not in the CMIP7 request, 101 unique CMIP6 variables are requested in the CMIP7 request.

  # Create the combined files with the CMIP7 requested variables for all priorities with the ECE3 - CMIP6 matched identification info where possible,
  # ordered in a way to allow convenient working on these lists:
  # Depending on the genecec-cmip7 input files:
  #  cmip7-request-v1.2.2.3-all/cmip7-request-v1.2.2.3-all-frequency-ordered.xml
  #  ./xml-files/genecec-cmip7/request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml
  ./identify-ece4-cmip7-request.py -a > identify-ece4-cmip7-request.log
  mv -f identify-ece4-cmip7-request.log archive/log-files/${version}/

  # With that we can run (actually this script is REPLACED BY the identify-ece4-cmip7-request.py script):
  # Depending on the genecec-cmip7 input files:
  #  cmip7-request-v1.2.2.3-all/cmip7-request-v1.2.2.3-all-frequency-ordered.xml
  #  ./xml-files/genecec-cmip7/request-overview-cmip6-pextra-all-ECE3-CC-neat-formatted.xml
 #./cmip7-variable-identification-with-help-of-ECE3-CMIP6.py > cmip7-variable-identification-with-help-of-ECE3-CMIP6.log


  # Archive the results from the cmip7-request.py call which creates the cmip7-request-v1.2.2.3-all:
  rsync -a --mkpath cmip7-request-${data_request_version}-all/ archive/cmip7-request-${data_request_version}-all/${version}

  # Create a backup reference of all identify-ece4-cmip7-request.py created files:
  rsync -a --mkpath xml-files/genecec-cmip7/ archive/genecec-cmip7/${version}


  # Check:
 #diff -r cmip7-request-${data_request_version}-all/ archive/cmip7-request-${data_request_version}-all/${version}
 #diff -r xml-files/genecec-cmip7/                   archive/genecec-cmip7/${version}

  # Archive the most important, best ordered XML files:
 #rsync -a cmip7-request-${data_request_version}-all-full-identified-freq-mc-prio.xml      xml-files/
 #rsync -a cmip7-request-${data_request_version}-all-full-var_identified-freq-mc-prio.xml  xml-files/
 #rsync -a cmip7-request-${data_request_version}-all-full-unidentified-freq-realm-prio.xml xml-files/

else
  echo
  echo " This scripts requires one argument:"
  echo "  - Argument 1: version of created directories"
  echo " For instance:"
  echo "  $0 v01"
  echo
fi
