#!/bin/bash
# Thomas Reerink
#
# This scripts requires 1 argument:
#
# ${1} the first argument is the ouput file: the new tm5.json file.
#
# Run example:
#  ./generate-tm5.json.sh new-tm5.json
#

# The current list is in the arr array is compiled by considering all variables
# which are marked as: "Available in TM5" in the file
#  resources/pre-list-of-identified-missing-cmpi6-requested-variables.xlsx

# Declare an array variable with all the nemo cmor variable names:
declare -a arr=(
"abs550aer"
"airmass"
"bldep"
"c2h6"
"c3h6"
"c3h8"
"ch3coch3"
"ch4"
"ch4Clim"
"ch4global"
"ch4globalClim"
"cheaqpso4"
"chegpso4"
"chepsoa"
"co"
"concdust"
"depdust"
"dms"
"drybc"
"drydust"
"drynh3"
"drynh4"
"drynoy"
"dryo3"
"dryoa"
"dryso2"
"dryso4"
"dryss"
"ec550aer"
"emibc"
"emibvoc"
"emico"
"emidms"
"emidust"
"emiisop"
"emilnox"
"eminh3"
"eminox"
"emioa"
"emiso2"
"emiso4"
"emiss"
"emivoc"
"flashrate"
"hcho"
"hno3"
"ho2"
"isop"
"jno2"
"loaddust"
"lossch4"
"lossco"
"maxpblz"
"md"
"minpblz"
"mmraerh2o"
"mmrbc"
"mmrdust"
"mmrnh4"
"mmrno3"
"mmroa"
"mmrpm1"
"mmrpm10"
"mmrpm2p5"
"mmrso4"
"mmrsoa"
"mmrss"
"no"
"no2"
"noy"
"o3"
"o3Clim"
"o3loss"
"o3prod"
"o3ste"
"od440aer"
"od550aer"
"od550aerh2o"
"od550bc"
"od550dust"
"od550lt1aer"
"od550no3"
"od550oa"
"od550so4"
"od550soa"
"od550ss"
"od870aer"
"oh"
"pan"
"phalf"
"ps"
"ptp"
"sedustCI"
"sfno2"
"sfo3"
"sfo3max"
"sfpm25"
"so2"
"tatp"
"toz"
"tropoz"
"wetbc"
"wetdust"
"wetnh3"
"wetnh4"
"wetnoy"
"wetoa"
"wetso2"
"wetso4"
"wetss"
"ztp"
)


function add_item {
 echo '    {'                     >> ${output_file}
 echo '        "source": "'$1'",' >> ${output_file}
 echo '        "target": "'$1'"'  >> ${output_file}
 echo '    },'                    >> ${output_file}
}

function add_last_item {
 echo '    {'                     >> ${output_file}
 echo '        "source": "'$1'",' >> ${output_file}
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

 # Adjust source for ch4Clim & ch4global & ch4globalClim:
 sed -i -e 's/"source": "ch4Clim"/"source": "ch4"/' ${output_file}
 sed -i -e 's/"source": "ch4global"/"source": "ch4"/' ${output_file}
 sed -i -e 's/"source": "ch4globalClim"/"source": "ch4"/' ${output_file}


 echo ' The file ' ${output_file} ' is created.'

else
    echo '  '
    echo '  This scripts requires one argument, e.g.:'
    echo '  ' $0 new-tm5par.json
    echo '  '
fi
