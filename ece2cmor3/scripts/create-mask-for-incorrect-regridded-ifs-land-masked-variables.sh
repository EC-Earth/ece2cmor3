#!/usr/bin/env bash
# Thomas Reerink
#
# This scripts needs one argument: the EC-Earth3 resolution
#
# Run this script without arguments for examples how to call this script.
#
# This script creates the omit_mask for the EC-Earth IFS land masked variables which are created with ece2cmor3 version earlier than 1.7.0, see:
#  https://github.com/EC-Earth/ece2cmor3/issues/691
#  https://github.com/EC-Earth/ece2cmor3/issues/671
#  https://github.com/EC-Earth/ece2cmor3/issues/686
#  https://github.com/EC-Earth/ece2cmor3/wiki/EC-Earth3-ESGF-errata
#  https://dev.ec-earth.org/issues/922
#  https://b2share.eudat.eu/records/f674000ecf3e4510a25960a4b7d77ee3

if [ "$#" -eq 1 ]; then
 ec_earth_resolution=$1

 # The path and filenames in this first if-else block need to fit your situation and thus require adjustment (no further adjustemts required):
 if [ "${ec_earth_resolution}" = "LR" ]; then
  ec_earth_resolution='lr'
  tsl_Lmon_incorrect=omit-mask-for-ifs-land-masked-variables/lr/cmor-Lmon-tsl-v1.5.0/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-LR/historical/r1i1p1f1/Lmon/tsl/gr/v20210324/tsl_Lmon_EC-Earth3-LR_historical_r1i1p1f1_gr_663501-663512.nc
  tsl_Lmon_corrected=omit-mask-for-ifs-land-masked-variables/lr/cmor-Lmon-tsl-v1.7.0/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-LR/historical/r1i1p1f1/Lmon/tsl/gr/v20210324/tsl_Lmon_EC-Earth3-LR_historical_r1i1p1f1_gr_663501-663512.nc
  resolution_comment="This mask corresponds to the EC-Earth3 LR resolution, i.e. it corresponds with the IFS T159 atmosphere resolution"
  output_file=omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables-LR.nc
 elif [ "${ec_earth_resolution}" = "standard" ]; then
  ec_earth_resolution='standard'
  tsl_Lmon_incorrect=omit-mask-for-ifs-land-masked-variables/standard/original/tsl_Lmon_EC-Earth3_piControl_r1i1p1f1_gr_199101-199112-v1.5.0.nc
  tsl_Lmon_corrected=omit-mask-for-ifs-land-masked-variables/standard/original/tsl_Lmon_EC-Earth3_piControl_r1i1p1f1_gr_199101-199112-v1.7.0.nc
  resolution_comment="This mask corresponds to the EC-Earth3 standard resolution, i.e. it corresponds with the IFS T255 atmosphere resolution"
  output_file=omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables.nc
 elif [ "${ec_earth_resolution}" = "HR" ]; then
  ec_earth_resolution='hr'
  tsl_Lmon_incorrect=omit-mask-for-ifs-land-masked-variables/hr/original/tsl_Lmon_EC-Earth3-HR_dcppA-hindcast_s1990-r1i2p1f1_gr_199011-199012.ece2cmor3-v1-5-0.nc
  tsl_Lmon_corrected=omit-mask-for-ifs-land-masked-variables/hr/original/tsl_Lmon_EC-Earth3-HR_dcppA-hindcast_s1990-r1i2p1f1_gr_199011-199012.ece2cmor3-v1-7-0.nc
  resolution_comment="This mask corresponds to the EC-Earth3 HR resolution, i.e. it corresponds with the IFS T511 atmosphere resolution"
  output_file=omit-mask-for-regrid-bug-in-ec-earth-atmospheric-land-masked-variables-HR.nc
 else
  echo 'Invalid argument value. Vaild options: LR, standard, HR'
  exit
 fi

 if [ ! -f "${tsl_Lmon_incorrect}" ]; then echo; echo " Error: " ${tsl_Lmon_incorrect} " does not exist. " >&2; echo; exit 1; fi
 if [ ! -f "${tsl_Lmon_corrected}" ]; then echo; echo " Error: " ${tsl_Lmon_corrected} " does not exist. " >&2; echo; exit 1; fi

 copy_tsl_Lmon_incorrect=${tsl_Lmon_incorrect##*/}
 copy_tsl_Lmon_corrected=${tsl_Lmon_corrected##*/}
 copy_tsl_Lmon_incorrect=${copy_tsl_Lmon_incorrect/.nc/-v1.5.0-${ec_earth_resolution}.nc}
 copy_tsl_Lmon_corrected=${copy_tsl_Lmon_corrected/.nc/-v1.7.0-${ec_earth_resolution}.nc}

 # Create a local copy:
 rsync -a ${tsl_Lmon_incorrect} ${copy_tsl_Lmon_incorrect}
 rsync -a ${tsl_Lmon_corrected} ${copy_tsl_Lmon_corrected}

 # Check the ece2cmor3 version in the data files:
 ncdump -h ${copy_tsl_Lmon_incorrect} | grep 'ece2cmor v1....' | sed -e 's/$/    # tag v1.5.0: 0e9c8f0d4efe956627d5dee9cd3ae6d26a995191 /'
 ncdump -h ${copy_tsl_Lmon_corrected} | grep 'ece2cmor v1....' | sed -e 's/$/    # tag v1.7.0: c9063184d7c8314349d4a99a737ad290ef0e97ac /'



 # Set missing values to -9999.0 in order to make the differences clear if in a ncdiff one point is missing and in the other has a value:
 cdo -O setmisstoc,-9999.0 ${copy_tsl_Lmon_incorrect} tsl_sample-v1.5.0-missval-9999.nc
 cdo -O setmisstoc,-9999.0 ${copy_tsl_Lmon_corrected} tsl_sample-v1.7.0-missval-9999.nc

 # Take the differences:
 ncdiff -O tsl_sample-v1.5.0-missval-9999.nc tsl_sample-v1.7.0-missval-9999.nc diff-tsl_sample-v1.5.0-v1.7.0-missval-9999.nc

 # Set all zero values to missing values:
 cdo -O setctomiss,0 diff-tsl_sample-v1.5.0-v1.7.0-missval-9999.nc diff-tsl_sample-v1.5.0-v1.7.0.nc

 # Set all non-zero values to 1:
 ncap2 -s 'where(tsl!=0) tsl=1;' diff-tsl_sample-v1.5.0-v1.7.0.nc -O diff-tsl_sample-v1.5.0-v1.7.0-mask.nc

 # Select one time record:
 ncks -O -d time,0 diff-tsl_sample-v1.5.0-v1.7.0-mask.nc omit-mask-v1.5.0-v1.7.0-a.nc

 # Select one depth layer:
 ncks -O -F -d depth,1 omit-mask-v1.5.0-v1.7.0-a.nc omit-mask-v1.5.0-v1.7.0-b.nc

 # Remove depricated time dimension from tsl:
 ncwa -O -a time -d time,0,0 omit-mask-v1.5.0-v1.7.0-b.nc omit-mask-v1.5.0-v1.7.0-c.nc

 # Remove depricated depth dimension from tsl:
 ncwa -O -a depth -d depth,0,0 omit-mask-v1.5.0-v1.7.0-c.nc omit-mask-v1.5.0-v1.7.0-d.nc

 # Get rid of unused dimensions:
 ncks -O -v tsl omit-mask-v1.5.0-v1.7.0-d.nc omit-mask-v1.5.0-v1.7.0-e.nc

 # Rename tsl to omit_mask:
 ncrename -O -v tsl,omit_mask omit-mask-v1.5.0-v1.7.0-e.nc omit-mask-v1.5.0-v1.7.0-f.nc

 # Remove all global attributes:
 ncatted -Oh -a ,global,d,, omit-mask-v1.5.0-v1.7.0-f.nc omit-mask-v1.5.0-v1.7.0-g.nc

 # Adjust & remove attributes:
 ncatted -Oh -a units,omit_mask,m,c,"-" -a comment,omit_mask,m,c,"The IFS land masked variables in EC-Earth3 which have been cmorised with an ece2cmor3 version earlier than v1.7 have wrong \n values at certain nearby coast points due to a regridding issue (see https://github.com/EC-Earth/ece2cmor3/issues/691). The points in \n this mask with value 1 have to be omitted in any analysis for these land masked variables." -a standard_name,omit_mask,d,, -a long_name,omit_mask,m,c,"omit mask" -a cell_measures,omit_mask,d,, -a cell_methods,omit_mask,d,, -a history,omit_mask,d,, omit-mask-v1.5.0-v1.7.0-g.nc omit-mask-v1.5.0-v1.7.0-h.nc


 # Finally set missing values to 0:
 cdo -O --history setmisstoc,0 omit-mask-v1.5.0-v1.7.0-h.nc omit-mask-v1.5.0-v1.7.0-i.nc


 # Add global production attributes:
 ncatted -Oh -a resolution,global,a,c,"${resolution_comment}" omit-mask-v1.5.0-v1.7.0-i.nc omit-mask-v1.5.0-v1.7.0-j.nc
 ncatted -Oh -a production,global,a,c,"This dataset is produced by Thomas Reerink at KNMI on behalf of the EC-Earth consortium" omit-mask-v1.5.0-v1.7.0-j.nc omit-mask-v1.5.0-v1.7.0-k.nc

 # Give the final output file its filename:
 rsync -a omit-mask-v1.5.0-v1.7.0-k.nc ${output_file}

 # Remove all temporal files:
 rm -f omit-mask-v1.5.0-v1.7.0-* diff-tsl_sample-v1.5.0-v1.7.0* tsl_*

 echo
 echo ' The result can be viewed by:' 
 echo '  ' ncview -repl -no_auto_overlay ${output_file}
 echo

else
    echo
    echo '  This scripts requires one arguments: the EC-Earth3 resolution, e.g.:'
    echo '  ' $0 LR
    echo '  ' $0 standard
    echo '  ' $0 HR
    echo
fi
