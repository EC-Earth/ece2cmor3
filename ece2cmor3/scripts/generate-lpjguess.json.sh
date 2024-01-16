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
#  resources/pre-list-of-identified-missing-cmip6-requested-variables.xlsx
# These variables are copied in an ascii file, e.g.: lpjg-list-new.txt
# Thereafter sorted and made unique (i.e. the duplicate once are removed) by:
#  sort lpjg-list-new.txt |uniq > lpjg-list-new-sorted-unique.txt
# And that list is pasted here in the arr variable.

# Declare an array variable with all the lpjg cmor variable names:
declare -a arr=(
"baresoilFrac"
"burntFractionAll"
"cCwd"
"cFluxYr"
"cLand"
"cLand1"
"cLandYr"
"cLeaf"
"cLitter"
"cLitterAbove"
"cLitterBelow"
"cLitterCwd"
"cLitterLut"
"cLitterSubSurf"
"cLitterSurf"
"cOther"
"cProduct"
"cProductLut"
"cRoot"
"cropFrac"
"cropFracC3"
"cropFracC4"
"cSoil"
"cSoilFast"
"cSoilLut"
"cSoilMedium"
"cSoilSlow"
"cStem"
"cTotFireLut"
"cVeg"
"cVegLut"
"cWood"
"evspsblpot"
"evspsblsoi"
"evspsblveg"
"fAnthDisturb"
"fBNF"
"fCLandToOcean"
"fco2antt"
"fco2nat"
"fDeforestToAtmos"
"fDeforestToProduct"
"fFire"
"fFireAll"
"fFireNat"
"fGrazing"
"fHarvest"
"fHarvestToAtmos"
"fLitterFire"
"fLitterSoil"
"fLuc"
"fLulccAtmLut"
"fLulccProductLut"
"fLulccResidueLut"
"fNAnthDisturb"
"fNdep"
"fNfert"
"fNgas"
"fNgasFire"
"fNgasNonFire"
"fNLandToOcean"
"fNleach"
"fNLitterSoil"
"fNloss"
"fNnetmin"
"fNProduct"
"fNup"
"fNVegLitter"
"fProductDecomp"
"fProductDecompLut"
"fracInLut"
"fracLut"
"fracOutLut"
"fVegFire"
"fVegLitter"
"gpp"
"gppGrass"
"gppLut"
"gppTree"
"grassFrac"
"grassFracC3"
"grassFracC4"
"irrLut"
"lai"
"laiLut"
"landCoverFrac"
"mrro"
"mrroLut"
"mrros"
"mrsll"
"mrso"
"mrsol"
"mrsoLut"
"mrsos"
"mrsosLut"
"nbp"
"necbLut"
"nep"
"netAtmosLandCO2Flux"
"nLand"
"nLeaf"
"nLitter"
"nLitterCwd"
"nLitterSubSurf"
"nLitterSurf"
"nMineral"
"nMineralNH4"
"nMineralNO3"
"nOther"
"npp"
"nppGrass"
"nppLut"
"nppTree"
"nProduct"
"nRoot"
"nSoil"
"nStem"
"nVeg"
"nwdFracLut"
"pastureFrac"
"pastureFracC3"
"pastureFracC4"
"prCrop"
"prveg"
"ra"
"raGrass"
"raLeaf"
"raLut"
"raOther"
"raRoot"
"raStem"
"raTree"
"residualFrac"
"rGrowth"
"rh"
"rhLitter"
"rhLut"
"rhSoil"
"rMaint"
"shrubFrac"
"tran"
"treeFrac"
"treeFracBdlDcd"
"treeFracBdlEvg"
"treeFracNdlDcd"
"treeFracNdlEvg"
"tsl"
"vegFrac"
"vegHeightTree"
)


function add_item {
 echo '    {'                     >> ${output_file}
 echo '        "source": "'$1'",' >> ${output_file}
 case $1 in
     burntFractionAll )                                              # In contrast to other fractions in LPJ-GIESS this one
      #echo '        "convert": "frac2percent",' >> ${output_file}   # is alreay in percentage, therefore omitting for the
	 ;;                                                          # variable burntFractionAll the conversion (see#546).
     *Frac* )
       echo '        "convert": "frac2percent",' >> ${output_file}
	 ;;
 esac
 echo '        "target": "'$1'"'  >> ${output_file}
 echo '    },'                    >> ${output_file}
}

function add_last_item {
 echo '    {'                     >> ${output_file}
 echo '        "source": "'$1'",' >> ${output_file}
 case $1 in
     *Frac* )
       echo '        "convert": "frac2percent",' >> ${output_file}
	 ;;
 esac
 echo '        "target": "'$1'"'  >> ${output_file}
 echo '    }'                     >> ${output_file}
}


if [ "$#" -eq 1 ]; then
 output_file=$1

 echo '['                         > ${output_file}

 # Loop through the array with all the LPJG cmor variable names:
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

 echo ' The file ' ${output_file} ' is created.'

else
 echo
 echo "  This scripts requires one argument, e.g.:"
 echo "  $0 new-lpjguesspar.json"
 echo
fi
