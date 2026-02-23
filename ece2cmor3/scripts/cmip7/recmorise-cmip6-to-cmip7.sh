#!/usr/bin/env bash

# Calling the recmorise-cmip6-to-cmip7.py script for (nearly) all CMIP6 variable combinations for a given CMIP6 top directory with CMIP6 cmorised data.

ece3_cmip6_data_dri_root=~/cmorize/test-data-ece3-ESM-1/CE37-test/
#ece3_cmip6_data_dri_root=/scratch/nktr/test-data/CE38-test/

#for j in {3hr,6hrPlev,Amon,day,Efx,Emon,Eyr,fx,LImon,Lmon,Oday,Ofx,Omon,SIday,SImon,}; do
for j in {3hr,6hrPlev,Amon,day,Emon,Eyr,LImon,Lmon,Oday,Omon,SIday,SImon,}; do
  for i in `/usr/bin/ls -1  ${ece3_cmip6_data_dri_root}/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-piControl/r1i1p1f1/$j`; do
    echo "./recmorise-cmip6-to-cmip7.py $j ${i} &>> recmorise-cmip6-to-cmip7.log";
  done
  echo
done | grep -v -e 'Omon msftyz' -e 'Omon sios' -e 'Omon soga' -e 'Omon thetaoga' -e 'Lmon landCoverFrac' -e '3hr pr' > run-recmorise-cmip6-to-cmip7.sh

# In th elatter pipe a few problematic cases are deselected from the list
# The 3hr pr is omiitted because of a corrupt netcdf in my test data

chmod uog+x run-recmorise-cmip6-to-cmip7.sh

#./run-recmorise-cmip6-to-cmip7.sh


# A log of the problematic encountered cases:

#    1. Difficulties: ['time', 'gridlatitude', 'olevel', 'basin']   olevel problematic
#     Omon         msftyz                      ==>  cmip7_compound_name="ocean.msfty.tavg-ol-ht-sea.mon.glb"               branded_variable_name="msfty_tavg-ol-ht-sea"                   units="kg s-1"            

#    2. Difficulties: ['time', 'osurf', 'latitude', 'longitude']
#     Omon         sios                        ==>  cmip7_compound_name="ocnBgchem.si.tavg-ols-hxy-sea.mon.glb"            branded_variable_name="si_tavg-ols-hxy-sea"                    units="mol m-3"           
#    Difficulties: standard_name            =""  EMPTY
#    osurf:
#      long_name                ="Ocean surface coordinate"
#      out_name                 ="seasurface"
#      standard_name            =""

#    3. Difficulties: ['time', 'olevel']
#     Omon         soga                        ==>  cmip7_compound_name="ocean.so.tavg-ol-hm-sea.mon.glb"                  branded_variable_name="so_tavg-ol-hm-sea"                      units="1E-03"             
#     Omon         thetaoga                    ==>  cmip7_compound_name="ocean.thetao.tavg-ol-hm-sea.mon.glb"              branded_variable_name="thetao_tavg-ol-hm-sea"                  units="degC"              

#    4. Lastig: ['time', 'vegtype', 'latitude', 'longitude']    problematic: vegtype
#     Lmon         landCoverFrac               ==>  cmip7_compound_name="land.landCoverFrac.tavg-u-hxy-u.mon.glb"          branded_variable_name="landCoverFrac_tavg-u-hxy-u"             units="%"                 


# Data dir wrong in my tets data (not so relevant):
#     day          tasmax                      ==>  cmip7_compound_name="atmos.tas.tmax-h2m-hxy-u.day.glb"                 branded_variable_name="tas_tmax-h2m-hxy-u"                     units="K"                 
#     day          tasmin                      ==>  cmip7_compound_name="atmos.tas.tmin-h2m-hxy-u.day.glb"                 branded_variable_name="tas_tmin-h2m-hxy-u"                     units="K"                 
#     ERROR: No files found for /home/reerink/cmorize/test-data-ece3-ESM-1/CE37-test/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-piControl/r1i1p1f1/day/tasmax/gr/v*/tasmax*.nc
#     ERROR: No files found for /home/reerink/cmorize/test-data-ece3-ESM-1/CE37-test/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-piControl/r1i1p1f1/day/tasmin/gr/v*/tasmin*.nc
