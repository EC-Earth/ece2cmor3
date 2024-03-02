#!/bin/bash
# Thomas Reerink
#
# This script adds some non-cmor variables (which thus do not exit in
# the CMIP6 data request) to the new HTESEELday & HTESEELmon CMOR tables.
#
# This script requires one argument.
#
# For examples how to call this script, run it without arguments.
#

if [ "$#" -eq 1 ]; then

 do_clean=$1

 if [ ${do_clean} == 'clean-before' ] || [ ${do_clean} == 'no-clean-before' ]; then
  # See #802       https://github.com/EC-Earth/ece2cmor3/issues/#802
  # See #1312-146  https://dev.ec-earth.org/issues/1312#note-146

  # Overview of added seaIce variables:
  #  SIday sishevel   field_ref="ishear"   SImon sishevel   is taken as basis
  #  SIday sidconcdyn field_ref="afxdyn"   SImon sidconcdyn is taken as basis
  #  SIday sidconcth  field_ref="afxthd"   SImon sidconcth  is taken as basis
  #  SIday sidivvel   field_ref="idive"    SImon sidivvel   is taken as basis
  #  SIday sidmassdyn field_ref="dmidyn"   SImon sidmassdyn is taken as basis
  #  SIday sidmassth  field_ref="dmithd"   SImon sidmassth  is taken as basis

  table_path=../resources/cmip6-cmor-tables/Tables
  table_file_SIday=CMIP6_SIday.json
  tmp_file_SIday=CMIP6_SIday_tmp.json

  cd ${table_path}
  if [ ${do_clean} == 'clean-before' ]; then
   git checkout ${table_file_SIday}
  fi

  # Add all of the CMIP6_SIday.json except its last 3 lines to the tmp file:
  head -n -3 ${table_file_SIday}                                                                       >  ${tmp_file_SIday}
  echo '        }, '                                                                                   >> ${tmp_file_SIday}

  grep -A 17 '"sishevel":'   CMIP6_SImon.json  | sed -e 's/"frequency": "monPt"/"frequency": "day"/g'  >> ${tmp_file_SIday}
  grep -A 17 '"sidconcdyn":' CMIP6_SImon.json  | sed -e 's/"frequency": "mon"/"frequency": "day"/g'    >> ${tmp_file_SIday}
  grep -A 17 '"sidconcth":'  CMIP6_SImon.json  | sed -e 's/"frequency": "mon"/"frequency": "day"/g'    >> ${tmp_file_SIday}
  grep -A 17 '"sidivvel":'   CMIP6_SImon.json  | sed -e 's/"frequency": "monPt"/"frequency": "day"/g'  >> ${tmp_file_SIday}
  grep -A 17 '"sidmassdyn":' CMIP6_SImon.json  | sed -e 's/"frequency": "mon"/"frequency": "day"/g'    >> ${tmp_file_SIday}
  grep -A 16 '"sidmassth":'  CMIP6_SImon.json  | sed -e 's/"frequency": "mon"/"frequency": "day"/g'    >> ${tmp_file_SIday}

  # Add closing part of CMIP6 table json file:
  echo '        } '                                                                                    >> ${tmp_file_SIday}
  echo '    } '                                                                                        >> ${tmp_file_SIday}
  echo '} '                                                                                            >> ${tmp_file_SIday}

  mv -f ${tmp_file_SIday} ${table_file_SIday}

  # Remove the trailing spaces of the inserted block above:
  sed -i -e 's/\s*$//g' -e 's/,$/, /g' ${table_file_SIday}

  cd -

  echo
  echo " Running:"
  echo "  $0 ${do_clean}"
  echo " has adjusted the file:"
  echo "  ${table_path}/${table_file_SIday}"
 #echo " and added the files:"
 #echo "  ${table_path}/${table_file_SIday}"
  echo " which is part of the nested CMOR Table repository. View the diff by running:"
  echo "  cd ${table_path}; git diff; cd -"
  echo " This changes can be reverted by running:"
  echo "  ./revert-nested-cmor-table-branch.sh"
  echo

 else
  echo
  echo " This scripts requires one argument: There are only two options:"
  echo "  $0 clean-before"
  echo "  $0 no-clean-before"
  echo
 fi

else
 echo
 echo " This scripts requires one argument: There are only two options:"
 echo "  $0 clean-before"
 echo "  $0 no-clean-before"
 echo
fi
