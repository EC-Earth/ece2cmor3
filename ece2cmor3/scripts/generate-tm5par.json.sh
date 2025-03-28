#!/bin/bash
# Thomas Reerink
#
# This scripts requires 1 argument:
#
# ${1} the first argument is the ouput file: the new tm5.json file.
#
# Run this script without arguments for examples how to call this script.
#

# The current list is in the arr array is compiled by considering all variables
# which are marked as: "Available in TM5" in the file
#  resources/pre-list-of-identified-missing-cmip6-requested-variables.xlsx

# Declare an array variable with all the nemo cmor variable names:
declare -a arr=(
"abs550aer"
"airmass"
"ald2"
"bldep"
"c2h4"
"c2h5oh"
"c2h6"
"c3h6"
"c3h8"
"ch3coch3"
"ch3cocho"
"ch3o2h"
"ch3o2no2"
"ch3oh"
"ch4"
"ch4Clim"
"ch4global"
"ch4globalClim"
"cheaqpso4"
"chegpso4"
"chepsoa"
"co"
"co2"
"co2mass"
"conccnmode01"
"conccnmode02"
"conccnmode03"
"conccnmode04"
"conccnmode05"
"conccnmode06"
"conccnmode07"
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
"h2o2"
"h2so4"
"hcho"
"hcooh"
"hno3"
"hno4"
"ho2"
"hono"
"hus"
"isop"
"ispd"
"jno2"
"loaddust"
"lossch4"
"lossco"
"maxpblz"
"mcooh"
"md"
"minpblz"
"mmraerh2o"
"mmraerh2omode01"
"mmraerh2omode02"
"mmraerh2omode03"
"mmraerh2omode04"
"mmrbc"
"mmrbcmode02"
"mmrbcmode03"
"mmrbcmode04"
"mmrbcmode05"
"mmrdust"
"mmrdustmode03"
"mmrdustmode04"
"mmrdustmode06"
"mmrdustmode07"
"mmrnh4"
"mmrno3"
"mmroa"
"mmroamode02"
"mmroamode03"
"mmroamode04"
"mmroamode05"
"mmrpm1"
"mmrpm10"
"mmrpm2p5"
"mmrso4"
"mmrso4mode01"
"mmrso4mode02"
"mmrso4mode03"
"mmrso4mode04"
"mmrsoa"
"mmrsoamode01"
"mmrsoamode02"
"mmrsoamode03"
"mmrsoamode04"
"mmrsoamode05"
"mmrss"
"mmrssmode03"
"mmrssmode04"
"msa"
"n2o5"
"nh3"
"no"
"no2"
"no3"
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
"ole"
"orgntr"
"pan"
"par"
"phalf"
"ps"
"ptp"
"rooh"
"sedustCI"
"sfno2"
"sfo3"
"sfo3max"
"sfpm25"
"so2"
"ta"
"tatp"
"terp"
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
"zg"
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

 # Loop through the array with all the TM5 cmor variable names:
 # (Note individual array elements can be accessed by using "${arr[0]}", "${arr[1]}")
 
 N=${#arr[@]} # array length
 last_item="${arr[N-1]}"
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
 echo
 echo "  This scripts requires one argument, e.g.:"
 echo "  $0 new-tm5par.json"
 echo
fi
