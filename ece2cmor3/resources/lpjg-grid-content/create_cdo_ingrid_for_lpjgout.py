#!/usr/bin/env python

# Note that at the time the script gave different precision results for different
# python versions,see https://github.com/EC-Earth/ece2cmor3/issues/633.

# Call the script like:
#  ./create_cdo_ingrid_for_lpjgout.py
#  python create_cdo_ingrid_for_lpjgout.py

import netCDF4 as nc
import numpy as np

"""
Create an input-grid ascii file (ingrid-file) to be used with CDO to convert from 
the output of out2nc into a regular gaussian
using in the produced ingrid.txt in cdo like
cdo remapycon,n128 -setgrid,<ingrid-filename> red_gaussian.nc gaussian.nc

The lon-lat-lpjg-auxiliary-T*-grid.nc files are obtained by:
ncks -v lon,lat LPJGtemp_T159.nc -o lon-lat-lpjg-auxiliary-T159-grid.nc
ncks -v lon,lat LPJGtemp_T255.nc -o lon-lat-lpjg-auxiliary-T255-grid.nc
The LPJGtemp_T*.nc files are provided by the LPJG community.
"""
################################################################################
# Start user modification
################################################################################

# Loop over the desired grids: T159 and T255:
for grid in ["T159", "T255"]:

 # set directory to read grid from (LPJG_temp_<grid>.nc) 
 inpath ="./"

 # chose output, i.e. ingrid-filename
 outpath = "./"

 # field separator
 fsep = " "

 # Lines may only be 64k characters long, so choose a save number of "values per line"
 # If there is a Warning from CDO about cell-weights vpl is probably to high
 vpl = 500

 ################################################################################
 # End user modification
 ################################################################################
#infile =inpath+"LPJGtemp_"+grid+".nc"
 infile =inpath+"lon-lat-lpjg-auxiliary-"+grid+"-grid.nc"
 ingridfile = outpath+"ingrid_"+grid+"_unstructured.txt"

 # open, read lat and lon, and close netcdf file 
 ds=nc.Dataset(infile,'r')
 lats=np.array(ds.variables['lat'][0,:])
 lons=np.array(ds.variables['lon'][0,:])
 ds.close()

 llo = len(lons)

 # open ascii file for writing
 f = open(ingridfile,'w')

 # set header parameters for ingrid-file
 f.write("gridtype = unstructured \n")
 f.write("gridsize = "+str(llo)+"\n")
 f.write("xsize = "+str(llo)+"\n")
 f.write("ysize = 1 \n")
 # 4 corner-points for each cell
 f.write("nvertex = 4 \n") 

 # write center coordinates read from netcdf-file
 f.write("xvals = ")
 for x in range(llo):
     f.write(str(lons[x])+fsep) 
     if  ( x+1 ) % vpl == 0:
         f.write(str('\n'))
 f.write(str('\n'))

 f.write("yvals = ")
 for x in range(llo):
     f.write(str(lats[x])+fsep) 
     if  ( x+1 ) % vpl == 0:
         f.write(str('\n'))
 f.write(str('\n'))

 # compute and write x and y boundaries, i.e. corner-coordinates

 # correction-factor for gridcell extension (1.0 leads to strange errors !!!only cdo v<1.6.x!!!)
 corfac = 1.0 #0.99999

 f.write("xbounds = ")
 for x in range(llo):
     # check how many identical lats there are
     nlat = len(lats[lats==lats[x]])
     # 1/2 zonal extension of cells at this latitude
     xnd = 0.5 * 360. / float(nlat) * corfac
     f.write(str(lons[x]-xnd)+fsep+str(lons[x]+xnd)+fsep+str(lons[x]+xnd)+fsep+str(lons[x]-xnd)+fsep) 
     if  ( x+1 ) % vpl == 0:
         f.write(str('\n'))
 f.write(str('\n'))

 # We start from 90 deg S northward. Since gaussian grids are not equidistant in N-S direction we need to 
 # take into account the different spacing north- and southward, respectively

 curr_lat = 90.
 prev_lat = 90.
 f.write("ybounds = ")
 for x in range(llo):
     # Check whether we moved south a step
     if  lats[x] != curr_lat:
         prev_lat = curr_lat
         curr_lat = lats[x]
         # search for next latitude 
         if (curr_lat < -89.4 and grid == "T255") or (curr_lat < -89.14 and grid == "T159"):
             next_lat = -90.0
         else:
             for xx in range(x+1,llo,1):
                 if lats[xx] < curr_lat:
                     next_lat = lats[xx]
                     break
     if prev_lat == 90.:
         dnorth = (prev_lat - curr_lat) * corfac
     else:
         dnorth = (prev_lat - curr_lat) / 2. * corfac
     if next_lat == -90.:
         dsouth = (curr_lat - next_lat) * corfac
     else:
         dsouth = (curr_lat - next_lat) / 2. * corfac

     f.write(str(lats[x]+dnorth)+fsep+str(lats[x]+dnorth)+fsep+str(lats[x]-dsouth)+fsep+str(lats[x]-dsouth)+fsep) 
     if  ( x+1 ) % vpl == 0:
         f.write(str('\n'))

 f.write(str('\n'))
 f.close()

 print(("Created file: "+ingridfile))
