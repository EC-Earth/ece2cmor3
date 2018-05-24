#!/bin/bash
# Thomas Reerink
#
# This scripts requires 1 argument:
#
# ${1} the first argument is the ouput file: the new nemopar.json file.
#
# Run example:
#  ./generate-nemopar.json.sh new-nemopar.json
#

# Declare an array variable with all the nemo cmor variable names:
declare -a arr=(
 "vmo"
 "thkcello"
 "umo"
 "volo"
 "hfds"
 "vo"
 "ficeberg2d"
 "sos"
 "tossq"
 "siv"
 "zossq"
 "sithick"
 "tos"
 "soga"
 "siu"
 "thetao"
 "siconc"
 "friver"
 "zos"
 "wmo"
 "masso"
 "sisnthick"
 "sfdsi"
 "wo"
 "rsdo"
 "thetaoga"
 "vsfsit"
 "tauvo"
 "wfo"
 "zfullo"
 "mlotst"
 "uo"
 "tauuo"
 "so"
 "rsntds"
 "pbo"
 "zhalfo"
 "sipr"
)

# The default example list for this moment is produced by running:
#  more nemopar.json |grep -e target | sed -e 's/.*://'
# And pasting the result here.





function add_item {
 echo '    {'                     >> ${output_file}
 echo '        "source": "'$1'"'  >> ${output_file}
 echo '        "target": "'$1'"'  >> ${output_file}
 echo '    },'                    >> ${output_file}
}

function add_last_item {
 echo '    {'                     >> ${output_file}
 echo '        "source": "'$1'"'  >> ${output_file}
 echo '        "target": "'$1'"'  >> ${output_file}
 echo '    }'                     >> ${output_file}
}


if [ "$#" -eq 1 ]; then
 output_file=$1


 echo '['                         > ${output_file}

 # Loop through the array with all the nemo cmor variable names:
 # (Note individual array elements can be accessed by using "${arr[0]}", "${arr[1]}")
 
 N=${#arr[@]} # array length
 last_item="${arr[N-1]}"
#echo ${N} ${last_item}
 for i in "${arr[@]}"
 do
    if [ "$i" == ${last_item} ]; then
     add_last_item "$i"
    else
     add_item "$i"
    fi
 done

 echo ']'                         >> ${output_file}


 echo ' The file ' ${output_file} ' is created.'

else
    echo '  '
    echo '  This scripts requires one argument, e.g.:'
    echo '  ' $0 new-nemopar.json
    echo '  '
fi
