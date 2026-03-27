#!/bin/bash
# Thomas Reerink
#
# This script adds Oday zos for the OptimESM CMIP7-FT project.
#
# This script requires one argument.
#
# For examples how to call this script, run it without arguments.
#

if [ "$#" -eq 1 ]; then

 # See #863  https://github.com/EC-Earth/ece2cmor3/issues/863

 file_def_file=$1

 sed -i  '/id="id_1d_t20d"/i \
     <field enabled="True" field_ref="sshdyn" freq_op="1ts" grid_ref="grid_T_2D" id="id_1d_zos" name="zos" operation="average" unit="m">                                                                        </field>
 ' ${file_def_file}

 # Remove the trailing spaces of the inserted block above:
 sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${file_def_file}

 echo
 echo " Running:"
 echo "  $0 $@"
 echo " has adjusted the file:"
 echo "  ${file_def_file}"
 echo " which is part of the output-control-files which are based on the combined OptimESM & CMIP7 request."
 echo

else
 echo
 echo " This scripts requires one argument: The file_def_nemo-opa.xml which needs to be adjusted:"
 echo "  $0 cmip7/archive/optimesm-core-combined-v10/file_def_nemo-opa.xml"
 echo
fi
