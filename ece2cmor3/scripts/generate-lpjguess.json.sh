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

# Declare an array variable with all the lpjg cmor variable names:
declare -a arr=(
"baresoilFrac, Lmon, baresoilFrac"
"abaresoilFrac, Eyr, baresoilFrac"
"cCwd, Lmon, cCwd"
"cLand, Emon, cLand"
"cLeaf, Lmon, cLeaf"
"cLitter, Lmon, cLitter"
"acLitter, Eyr, cLitter"
"cLitterAbove, Lmon, cLitterAbove"
"cLitterBelow, Lmon, cLitterBelow"
"cLitterCwd, Emon, cLitterCwd"
"cLitterLut, Eyr, cLitterLut"
"cLitterSubSurf, Emon, cLitterSubSurf"
"cLitterSurf, Emon, cLitterSurf"
"cOther, Emon, cOther"
"cProduct, Lmon, cProduct"
"acProduct, Eyr, cProduct"
"cProductLut, Eyr, cProductLut"
"cRoot, Lmon, cRoot"
"cropFrac, Lmon, cropFrac"
"acropFrac, Eyr, cropFrac"
"cropFracC3, Emon, cropFracC3"
"cropFracC4, Emon, cropFracC4"
"cSoil, Emon, cSoil"
"acSoil, Eyr, cSoil"
"cSoilFast, Lmon, cSoilFast"
"cSoilLut, Eyr, cSoilLut"
"cSoilMedium, Lmon, cSoilMedium"
"cSoilSlow, Lmon, cSoilSlow"
"cStem, Emon, cStem"
"cTotFireLut, Emon, cTotFireLut"
"cVeg, Lmon, cVeg"
"acVeg, Eyr, cVeg"
"cVegLut, Eyr, cVegLut"
"cWood, Emon, cWood"
"dec, Eday, ec"
"det, Eday, et"
"evspsblpot, Emon, evspsblpot"
"devspsblpot, Eday, evspsblpot"
"evspsblsoi, Lmon, evspsblsoi"
"evspsblveg, Lmon, evspsblveg"
"fAnthDisturb, Emon, fAnthDisturb"
"fBNF, Emon, fBNF"
"fCLandToOcean, Emon, fCLandToOcean"
"fco2antt, Amon, fco2antt"
"fco2nat, Amon, fco2nat"
"fDeforestToAtmos, Emon, fDeforestToAtmos"
"fDeforestToProduct, Emon, fDeforestToProduct"
"fFire, Lmon, fFire"
"fFireAll, Emon, fFireAll"
"fFireNat, Emon, fFireNat"
"fGrazing, Lmon, fGrazing"
"fHarvest, Lmon, fHarvest"
"fHarvestToAtmos, Emon, fHarvestToAtmos"
"fHarvestToProduct, Emon, fHarvestToProduct"
"fLitterFire, Emon, fLitterFire"
"fLitterSoil, Lmon, fLitterSoil"
"fLuc, Emon, fLuc"
"fLulccAtmLut, Emon, fLulccAtmLut"
"fLulccProductLut, Emon, fLulccProductLut"
"fLulccResidueLut, Emon, fLulccResidueLut"
"fNAnthDisturb, Emon, fNAnthDisturb"
"fNdep, Emon, fNdep"
"fNfert, Emon, fNfert"
"fNgas, Emon, fNgas"
"fNgasFire, Emon, fNgasFire"
"fNgasNonFire, Emon, fNgasNonFire"
"fNLandToOcean, Emon, fNLandToOcean"
"fNleach, Emon, fNleach"
"fNLitterSoil, Emon, fNLitterSoil"
"fNloss, Emon, fNloss"
"fNnetmin, Emon, fNnetmin"
"fNProduct, Emon, fNProduct"
"fNup, Emon, fNup"
"fNVegLitter, Emon, fNVegLitter"
"fProductDecomp, Emon, fProductDecomp"
"fProductDecompLut, Emon, fProductDecompLut"
"fracInLut, Eyr, fracInLut"
"fracLut, Eyr, fracLut"
"mfracLut, Emon, fracLut"
"fracOutLut, Eyr, fracOutLut"
"fVegFire, Emon, fVegFire"
"fVegLitter, Lmon, fVegLitter"
"gpp, Lmon, gpp"
"gppGrass, Emon, gppGrass"
"gppLut, Emon, gppLut"
"gppTree, Emon, gppTree"
"grassFrac, Lmon, grassFrac"
"agrassFrac, Eyr, grassFrac"
"grassFracC3, Emon, grassFracC3"
"grassFracC4, Emon, grassFracC4"
"irrLut, Emon, irrLut"
"lai, Lmon, lai"
"dlai, Eday, lai"
"laiLut, Emon, laiLut"
"landCoverFrac, Lmon, landCoverFrac"
"mrro, Lmon, mrro"
"mrroLut, Emon, mrroLut"
"mrros, Lmon, mrros"
"mrsll, Emon, mrsll"
"dmrsll, Eday, mrsll"
"mrso, Lmon, mrso"
"mrsol, Emon, mrsol"
"dmrsol, Eday, mrsol"
"mrsoLut, Emon, mrsoLut"
"mrsos, Lmon, mrsos"
"mrsosLut, Emon, mrsosLut"
"nbp, Lmon, nbp"
"necbLut, Emon, necbLut"
"nep, Emon, nep"
"netAtmosLandCO2Flux, Emon, netAtmosLandCO2Flux"
"nLand, Emon, nLand"
"nLeaf, Emon, nLeaf"
"nLitter, Emon, nLitter"
"nLitterCwd, Emon, nLitterCwd"
"nLitterSubSurf, Emon, nLitterSubSurf"
"nLitterSurf, Emon, nLitterSurf"
"nMineral, Emon, nMineral"
"nMineralNH4, Emon, nMineralNH4"
"nMineralNO3, Emon, nMineralNO3"
"nOther, Emon, nOther"
"npp, Lmon, npp"
"nppGrass, Emon, nppGrass"
"nppLut, Emon, nppLut"
"nppTree, Emon, nppTree"
"nProduct, Emon, nProduct"
"nRoot, Emon, nRoot"
"nSoil, Emon, nSoil"
"nStem, Emon, nStem"
"nwdFracLut, Emon, nwdFracLut"
"nVeg, Emon, nVeg"
"pastureFrac, Lmon, pastureFrac"
"pastureFracC3, Emon, pastureFracC3"
"pastureFracC4, Emon, pastureFracC4"
"prCrop, Emon, prCrop"
"dprCrop, Eday, prCrop"
"prveg, Lmon, prveg"
"ra, Lmon, ra"
"raGrass, Emon, raGrass"
"raLeaf, Emon, raLeaf"
"raLut, Emon, raLut"
"raOther, Emon, raOther"
"raRoot, Emon, raRoot"
"raStem, Emon, raStem"
"raTree, Emon, raTree"
"residualFrac, Lmon, residualFrac"
"rGrowth, Lmon, rGrowth"
"rh, Lmon, rh"
"rhLitter, Emon, rhLitter"
"rhLut, Emon, rhLut"
"rhSoil, Emon, rhSoil"
"rMaint, Lmon, rMaint"
"shrubFrac, Lmon, shrubFrac"
"ashrubFrac, Eyr, shrubFrac"
"tran, Lmon, tran"
"dtran, Eday, tran"
"treeFrac, Lmon, treeFrac"
"atreeFrac, Eyr, treeFrac"
"treeFracBdlDcd, Emon, treeFracBdlDcd"
"treeFracBdlEvg, Emon, treeFracBdlEvg"
"treeFracNdlDcd, Emon, treeFracNdlDcd"
"treeFracNdlEvg, Emon, treeFracNdlEvg"
"tsl, Lmon, tsl"
"dtsl, Eday, tsl"
"vegFrac, Emon, vegFrac"
"vegHeightTree, Emon, vegHeightTree"
)


function add_item {
 echo '    {'                     >> ${output_file}
 echo '        "source": "'$1'",' >> ${output_file}
#echo '        "filepath": "'$1'.out",'  >> ${output_file}
 echo '        "table": "'$2'",'  >> ${output_file}
 echo '        "target": "'$3'"'  >> ${output_file}
 echo '    },'                    >> ${output_file}
}

function add_last_item {
 echo '    {'                     >> ${output_file}
 echo '        "source": "'$1'",' >> ${output_file}
#echo '        "filepath": "'$1'.out",'  >> ${output_file}
 echo '        "table": "'$2'",'  >> ${output_file}
 echo '        "target": "'$3'"'  >> ${output_file}
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
    IFS=', ' read -ra arr_entry <<< "$i"
    if [ "$i" == "$last_item" ]; then
        add_last_item "${arr_entry[0]}" "${arr_entry[1]}" "${arr_entry[2]}" 
    else
        add_item "${arr_entry[0]}" "${arr_entry[1]}" "${arr_entry[2]}" 
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
