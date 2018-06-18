#!/bin/bash
# Thomas Reerink
#
# This scripts requires 1 argument:
#
# ${1} the first argument is the ouput file: the new lpj-guess.json file.
#
# Run example:
#  ./generate-lpjguess.json.sh new-lpjguess.json
#

# The current list is in the arr array is compiled by considering all variables
# which are marked as: "Available in LPJ-GUESS" in the file
#  resources/pre-list-of-identified-missing-cmpi6-requested-variables.xlsx

# Declare an array variable with all the nemo cmor variable names:
declare -a arr=(
"evspsblpot"
"lai"
"mrsol"
"tsl"
"cSoil"
"mrsol"
"fCLandToOcean"
"fFireNat"
"fProductDecomp"
"fAnthDisturb"
"fDeforestToProduct"
"fHarvestToProduct"
"nLitter"
"nProduct"
"nLand"
"nMineral"
"fNloss"
"fNfert"
"fNdep"
"fBNF"
"fNup"
"fNnetmin"
"fNVegLitter"
"fNLandToOcean"
"fNLitterSoil"
"fNProduct"
"fNAnthDisturb"
"treeFracNdlDcd"
"treeFracBdlEvg"
"treeFracBdlDcd"
"grassFracC3"
"grassFracC4"
"pastureFracC3"
"pastureFracC4"
"cStem"
"cOther"
"cLitterCwd"
"cLitterSurf"
"cLitterSubSurf"
"fVegFire"
"fLitterFire"
"fFireAll"
"raRoot"
"raStem"
"raLeaf"
"raOther"
"rhLitter"
"rhSoil"
"gppTree"
"gppGrass"
"nppTree"
"nppGrass"
"raTree"
"raGrass"
"fHarvestToAtmos"
"fDeforestToAtmos"
"nLeaf"
"nStem"
"nRoot"
"nOther"
"nLitterCwd"
"nLitterSurf"
"nLitterSubSurf"
"nMineralNH4"
"nMineralNO3"
"fNleach"
"fNgasNonFire"
"fNgasFire"
"fLuc"
"cWood"
"gppLut"
"raLut"
"nppLut"
"cTotFireLut"
"rhLut"
"necbLut"
"nwdFracLut"
"laiLut"
"mrsosLut"
"mrroLut"
"mrsoLut"
"irrLut"
"fProductDecompLut"
"fLulccProductLut"
"fLulccResidueLut"
"fLulccAtmLut"
"fracLut"
"vegFrac"
"treeFracNdlEvg"
"cropFracC3"
"cropFracC4"
"cLand"
"vegHeightTree"
"nVeg"
"nSoil"
"fNgas"
"fracOutLut"
"fracInLut"
"fracLut"
"mrsos"
"mrso"
"mrros"
"mrro"
"prveg"
"evspsblveg"
"evspsblsoi"
"tran"
"tsl"
"treeFrac"
"grassFrac"
"shrubFrac"
"cropFrac"
"pastureFrac"
"baresoilFrac"
"residualFrac"
"cVeg"
"cLitter"
"cProduct"
"lai"
"gpp"
"ra"
"npp"
"rh"
"fGrazing"
"nbp"
"fVegLitter"
"fLitterSoil"
"cLeaf"
"cRoot"
"cLitterAbove"
"cLitterBelow"
"cSoilFast"
"cSoilMedium"
"cSoilSlow"
"landCoverFrac"
"cSoilLut"
"cVegLut"
"cLitterLut"
"cProductLut"
"mrsll"
"netAtmosLandCO2Flux"
"nep"
"fFire"
"fHarvest"
"cCwd"
"rGrowth"
"rMaint"
"prCrop"
"et"
"ec"
"tran"
"evspsblpot"
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
    echo '  ' $0 new-lpjguesspar.json
    echo '  '
fi
