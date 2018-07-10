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
"o3"
"co2"
"ch4"
"phalf"
"ec550aer"
"sfno2"
"sfo3"
"sfpm25"
"abs550aer"
"airmass"
"bldep"
"c2h6"
"c3h6"
"c3h8"
"ch3coch3"
"ch4"
"cheaqpso4"
"chegpso4"
"chepsoa"
"co"
"co2"
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
"emibc"
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
"h2o"
"hno3"
"isop"
"jno2"
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
"nh50"
"no"
"no2"
"o3"
"od440aer"
"od550aer"
"od550aerh2o"
"od550bc"
"od550csaer"
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
"hcho"
"o3ste"
"phalf"
"ptp"
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
"cdnc"
"maxpblz"
"minpblz"
"od550aer"
"sfo3max"
"toz"
"phalf"
"ch4"
"h2o"
"hno3"
"ho2"
"noy"
"o3"
"oh"
"emibvoc"
"emivoc"
"fco2antt"
"fco2fos"
"fco2nat"
"o3Clim"
"co2Clim"
"co2mass"
"co2massClim"
"ch4Clim"
"ch4global"
"ch4globalClim"
"lossch4"
"lossco"
"o3loss"
"o3prod"
"flashrate"
"depdust"
"sedustCI"
"md"
"loaddust"
"concdust"
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


 echo ' The file ' ${output_file} ' is created.'

else
    echo '  '
    echo '  This scripts requires one argument, e.g.:'
    echo '  ' $0 new-tm5par.json
    echo '  '
fi
