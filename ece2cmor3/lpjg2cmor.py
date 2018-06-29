import os

import re
import numpy as np
import pandas as pd
import datetime
import json
import logging
import netCDF4
from cdo import *
import cmor
from ece2cmor3 import cmor_utils, cmor_source, cmor_target, cmor_task

#from cmor.Test.test_python_open_close_cmor_multiple import path

# Logger object
log = logging.getLogger(__name__)

# Experiment name
exp_name_ = None

# Table root
table_root_ = None

# Dictionary of lpjg grid type with cmor grid id.
grid_ids_ = {}

# List of land use tyle ids with ??? cmor grid id ???.
landuse_ = {}

# Dictionary of output frequencies with cmor time axis id.
time_axes_ = {}

# Reference date, will be start date if not given as a command line parameter 
ref_date_ = None
cmor_calendar_ = None

lpjg_path_ = None

ncpath_ = None
ncpath_created_ = False

gridfile_ = "ece2cmor3/resources/ingrid_T255_unstructured.txt"

_months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

#various things extracted from Michael.Mischurow out2nc tool: ec_earth.py
grids = {
    80:  [18, 25, 36, 40, 45, 54, 60, 64, 72, 72, 80, 90, 96, 100, 108, 120, 120, 128, 135, 144, 144, 150, 160, 160, 180, 180, 180, 192, 192, 200, 200, 216, 216, 216, 225, 225, 240, 240, 240, 256, 256, 256, 256, 288, 288, 288, 288, 288, 288, 288, 288, 288, 300, 300, 300, 300, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320],
    128: [18, 25, 36, 40, 45, 50, 60, 64, 72, 72, 80, 90, 90, 100, 108, 120, 120, 125, 128, 144, 144, 150, 160, 160, 180, 180, 180, 192, 192, 200, 216, 216, 216, 225, 240, 240, 240, 250, 250, 256, 270, 270, 288, 288, 288, 300, 300, 320, 320, 320, 320, 324, 360, 360, 360, 360, 360, 360, 360, 375, 375, 375, 375, 384, 384, 400, 400, 400, 400, 405, 432, 432, 432, 432, 432, 432, 432, 450, 450, 450, 450, 450, 480, 480, 480, 480, 480, 480, 480, 480, 480, 480, 486, 486, 486, 500, 500, 500, 500, 500, 500, 500, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512, 512],
}
grids = {i: j+j[::-1] for i, j in grids.items()}

def rnd(x, digits=3):
    return round(x, digits)

def coords(df, root, meta):
    # deg is 128 in N128
    # common deg: 32, 48, 80, 128, 160, 200, 256, 320, 400, 512, 640
    # correspondence to spectral truncation:
    # t159 = n80; t255 = n128; t319 = n160; t639 = n320; t1279 = n640
    # i.e. t(2*X -1) = nX
    # number of longitudes in the regular grid: deg * 4
    # At deg >= 319 polar correction might have to be applied (see Courtier and Naughton, 1994)
    deg = 128
    lons = [lon for num in grids[deg] for lon in np.linspace(0, 360, num, False)]
    x, w = np.polynomial.legendre.leggauss(deg*2)
    lats = np.arcsin(x) * 180 / -np.pi
    lats = [lats[i] for i, n in enumerate(grids[deg]) for _ in range(n)]

    i = root.createDimension('i', len(lons))
    j = root.createDimension('j', 1)

    latitude = root.createVariable('lat', 'f4', ('j', 'i'))
    latitude.standard_name = 'latitude'
    latitude.long_name = 'latitude coordinate'
    latitude.units = 'degrees_north'
    # latitude.bounds = 'lat_vertices'
    latitude[:] = lats

    longitude = root.createVariable('lon', 'f4', ('j', 'i'))
    longitude.standard_name = 'longitude'
    longitude.long_name = 'longitude coordinate'
    longitude.units = 'degrees_east'
    # longitude.bounds = 'lon_vertices'
    longitude[:] = lons

    run_lons = [rnd(i) for i in (df.index.levels[0].values + 360.0) % 360.0]
    run_lats = [rnd(i) for i in df.index.levels[1]]

    df.index.set_levels([run_lons, run_lats], inplace=True)
    df = df.reindex([(rnd(i), rnd(j)) for i, j in zip(lons, lats)], fill_value=meta['missing'])

    return df, ('j', 'i')


# Initializes the processing loop.
def initialize(path,ncpath,expname,tableroot,start,length,refdate):
    global log,exp_name_,table_root_
    global lpjg_path_, ncpath_, ncpath_created_
    exp_name_ = expname
    table_root_ = tableroot
    lpjg_path_ = path
    ref_date_ = refdate
    if not ncpath.startswith("/"):
        ncpath_ = os.path.join(lpjg_path_,ncpath)
    else:
        ncpath_ = ncpath
    if not os.path.exists(ncpath_) and not ncpath_created_:
        os.makedirs(ncpath_)
        ncpath_created_ = True
    cmor.set_cur_dataset_attribute("calendar", "proleptic_gregorian")
    cmor.load_table(tableroot + "_grids.json")
    
    return True


# Resets the module globals.
def finalize():
    global grid_ids_,landuse_,time_axes_
    grid_ids_ = {}
    landuse_ = {}
    time_axes_ = {}


# Executes the processing loop.
# used the nemo2cmor.py execute as template
def execute(tasks):
    global log,time_axes_,landuse_,table_root_
    global lpjg_path_, ncpath_
    log.info("Executing %d lpjg tasks..." % len(tasks))
    log.info("Cmorizing lpjg tasks...")
    taskdict = cmor_utils.group(tasks,lambda t:t.target.table)

    lon_id = None
    lat_id = None
    for table, tasklist in taskdict.iteritems():
        try:
            tab_id = cmor.load_table("_".join([table_root_, table]) + ".json")
            cmor.set_table(tab_id)
        except Exception as e:
            log.error("CMOR failed to load table %s, skipping variables %s. Reason: %s"
                      % (table, ','.join([tsk.target.variable for tsk in task_list]), e.message))
            continue

        for task in tasklist:
            freq = task.target.frequency.encode()
            lpjgfiles = task.source.srcpath()
            setattr(task, cmor_task.output_path_key, lpjgfiles)
            colname = task.source.variable().encode()
            outname = task.target.out_name
            outdims = task.target.dimensions
            
            #Read data from the .out-file and generate and the netCDF file including remapping
            ncfile = create_lpjg_netcdf(freq, colname, lpjgfiles, outname, outdims)
            
            dataset = netCDF4.Dataset(ncfile, 'r')
            #Create the grid, need to do only once as all LPJG variables will be on same grid
            #Currently create_grid just creates latitude and longitude axis since that should be all that is needed
            if lon_id is None and lat_id is None:
                lon_id, lat_id = create_grid(dataset, task)
            setattr(task, "longitude_axis", lon_id)
            setattr(task, "latitude_axis", lat_id)

            #Create cmor time axis for current variable
            create_time_axis(dataset, task)

            #cmorize the current task (variable)
            execute_single_task(dataset, task)
            dataset.close()
            
            #remove the regular (non-cmorized) netCDF file
            os.remove(ncfile)
            
    return 

#this function builds upon a combination of _get and save_nc functions from the out2nc.py tool originally by Michael Mischurow
def create_lpjg_netcdf(freq, colname, lpjgfiles, outname, outdims):
    global lpjg_path_, ncpath_, ref_date_, gridfile_

    #should lpjg_path be inside the runleg or parent dir?
    lpjgfile = os.path.join(lpjg_path_, lpjgfiles)

    #assigns a flag to handle two different possible monthly LPJ-Guess formats
    months_as_cols = False
    if freq == "mon":
        with open(lpjgfile) as f:
            header = next(f).lower().split()
            months_as_cols = header[-12:] == _months

    if freq == "mon" and not months_as_cols:
        idx_col = [0, 1, 2, 3]
    elif freq == "day":
        idx_col = [0, 1]
    else:
        idx_col = [0, 1, 2]

    df = pd.read_csv(lpjgfile, delim_whitespace=True, index_col=idx_col, dtype=np.float64, compression='infer')
#    df.rename(columns=lambda x: x.lower(), inplace=True)
    
    if freq == "day":
        #create a single time column so that extra days won't be added to the time axis (if there are both leap and non-leap years) 
        df['timecolumn'] = df['year'] + 0.001*df['day']
        df.set_index('timecolumn',append=True, inplace=True)
        df.drop(columns=['year', 'day'],inplace=True)

        if df.shape[1] != 1:
            raise ValueError('Multiple columns in the daily file are not supported')
        df = df.unstack()
    elif freq == "yr":
        df = df.pop(colname) #assume that the variable name actually exists in the lpjgfile (this is checked at some point earlier right?)
        df = df.unstack()
    elif freq == "mon":
        if months_as_cols:
            df.rename(columns=lambda x: x.lower(), inplace=True)
            df = df.unstack()
            sortrule = lambda x: (x[1], _months.index(x[0]))
            df = df.reindex(sorted(df.columns, key=sortrule),
                            axis=1, copy=False)
        else:
            df = df.pop(colname)
            df = df.unstack().unstack()
            sortrule = lambda x: (x[1], x[0])
            df = df.reindex(sorted(df.columns, key=sortrule),
                            axis=1, copy=False)

    if freq == "yr":
        startdate = str(int(df.columns[0])) + "01"
        enddate = str(int(df.columns[-1])) + "12"
    else:
        startdate = str(int(df.columns[0][1])) + "01"
        enddate = str(int(df.columns[-1][1])) + "12"
    ncfile = os.path.join(ncpath_, outname + "_" + freq + "_" + startdate + "_" + enddate + ".nc") 
    #Note that ncfile could be named anything, it will be deleted later and the cmorization takes care of proper naming conventions for the final file 
    print("create_lpjg_netcdf " + colname + " into " + ncfile)

    #temporary netcdf file name (will be removed after remapping is done)
    temp_ncfile = os.path.join(ncpath_, 'LPJGtemp.nc')
    root = netCDF4.Dataset(temp_ncfile, 'w', format='NETCDF4_CLASSIC') #what is the desired format here? 
                   
    meta = { "missing" : 1.e+20 } #the missing/fill value could/should be taken from the target header info if available 
                                  #and does not need to be in a meta dict since coords only needs the fillvalue anyway, but do it like this (i.e. out2nc-style) for now
    df_normalised, dimensions = coords(df, root, meta)

    time = root.createDimension('time', None)
    timev = root.createVariable('time', 'f4', ('time',))
    timev[:] = np.arange(df.shape[1])
    if freq == "mon":
        fyear, tres = int(df.columns[0][1]), 'month'
    elif freq == "day":
        fyear, tres = int(df.columns[0][1]), 'day'
    else:
        fyear, tres = int(df.columns[0]), 'year'
    #TODO: add the option (if required) for the start year to be a reference year other than the first year in the data file 
    timev.units = '{}s since {}-01-01'.format(tres, fyear)
    timev.calendar = "proleptic_gregorian"
    dimensions = 'time', dimensions[0], dimensions[1]
        
    variable = root.createVariable(outname, 'f4', dimensions, zlib=True,
                                   shuffle=False, complevel=5, fill_value=meta['missing'])
    variable[:] = df_normalised.values.T

    root.sync()
    root.close()

    #do the remapping
    cdo = Cdo()
    #for some reason chaining the other commands to invertlat gives an error, the line below works fine in out2nc.py 
#    cdo.invertlat(input = "-remapycon,n128 -setgrid," + gridfile_ + " " + temp_ncfile, output=ncfile)
    interm_file = os.path.join(ncpath_, 'intermediate.nc')
    cdo.remapycon('n128', input = "-setgrid," + gridfile_ + " " + temp_ncfile, output=interm_file)
    cdo.invertlat(input = interm_file, output=ncfile)
    os.remove(interm_file)
    os.remove(temp_ncfile)

    return ncfile

# Performs a single task.
def execute_single_task(dataset, task):
    global log
    task.status = cmor_task.status_cmorizing
    lon_axis = [] if not hasattr(task, "longitude_axis") else [getattr(task, "longitude_axis")]
    lat_axis = [] if not hasattr(task, "latitude_axis") else [getattr(task, "latitude_axis")]
    t_axis = [] if not hasattr(task, "time_axis") else [getattr(task, "time_axis")]
    axes = lon_axis + lat_axis + t_axis
    varid = create_cmor_variable(task, dataset, axes)
#    ncvar = dataset.variables[task.source.variable()]
    ncvar = dataset.variables[task.target.out_name]
    missval = getattr(ncvar, "missing_value", getattr(ncvar, "fill_value", np.nan))
    
    factor = get_conversion_factor(getattr(task, cmor_task.conversion_key, None))
    log.info("CMORizing variable %s in table %s form %s in "
             "file %s..." % (task.target.out_name, task.target.table, task.source.variable(),
                             getattr(task, cmor_task.output_path_key)))
    cmor_utils.netcdf2cmor(varid, ncvar, 0, factor, missval=getattr(task.target, cmor_target.missval_key, missval),
                           swaplatlon = True)
    closed_file = cmor.close(varid, file_name=True)
    log.info("CMOR closed file %s" % closed_file)
    task.status = cmor_task.status_cmorized

#Creates cmor time axis for the variable (task)
#Unlike e.g. the corresponding nemo2cmor function, the axis will be created for each variable instead of a table 
#in case the LPJ-Guess tables will not be organised so that all the variables in a table have same time axis    
def create_time_axis(ds, task):
    #finding the time dimension name: adapted from nemo2cmor, presumably there is always only one time dimension and the length of the time_dim list will be 1
    tgtdims = getattr(task.target, cmor_target.dims_key)
    time_dim = [d for d in list(set(tgtdims.split())) if d.startswith("time")]

    timevals = ds.variables["time"][:] #time variable in the netcdf-file from create_lpjg_netcdf is "time"
    #time requires bounds as well, the following should simply set them to be from start to end of each year/month/day (as appropriate for current data) 
    f = np.vectorize(lambda x: x + 1)
    time_bnd = np.stack((timevals, f(timevals)), axis = -1)

    tid = cmor.axis(table_entry=str(time_dim[0]), units=getattr(ds.variables["time"], "units"),
                                    coord_vals=timevals, cell_bounds=time_bnd) 
    setattr(task, "time_axis", tid)

    return

#Creates longitude and latitude cmor-axes for LPJ-Guess variables
#Seems this is enough for cmor according to the cmor documentation since the grid would now just be a lat/lon grid?
def create_grid(ds, task):
    lons = ds.variables["lon"][:]
    lats = ds.variables["lat"][:]
    
    #create the cell bounds since they are required: we have a 512x256 grid with longitude from 0 to 360 and latitude from -90 to 90, i.e. resolution ~0.7
    #longitude values start from 0 so the cell lower bounds are the same as lons (have to be: cmor requires monononically increasing values so 359.X to 0.X is not allowed)
    lon_bnd_upper = np.append(lons[1:], 360.0)
    lon_bnd = np.stack((lons, lon_bnd_upper), axis = -1)

    #creating latitude bounds so that latitude values are the (approximate) mid-points of the cell lower and upper bounds
    lat_bnd_lower = np.array([-90.0, -89.12264116])
    for i in range(1, 255):
        lat_bnd_lower = np.append(lat_bnd_lower, lat_bnd_lower[i] + 0.70175308)
    lat_bnd_upper = np.append(lat_bnd_lower[1:], 90.0)
    lat_bnd = np.stack((lat_bnd_lower, lat_bnd_upper), axis = -1)

    lon_id = cmor.axis(table_entry="longitude", units=getattr(ds.variables["lon"], "units"),
                                    coord_vals=lons, cell_bounds=lon_bnd)
    lat_id = cmor.axis(table_entry="latitude", units=getattr(ds.variables["lat"], "units"),
                                    coord_vals=lats, cell_bounds=lat_bnd)
     
    return lon_id, lat_id

# Unit conversion utility method
def get_conversion_factor(conversion):
    global log
    if not conversion:
        return 1.0
 #   if conversion == "tossqfix":
 #       return 1.0
    if conversion == "frac2percent":
        return 100.0
    if conversion == "percent2frac":
        return 0.01
    log.error("Unknown explicit unit conversion %s will be ignored" % conversion)
    return 1.0

# Creates a variable in the cmor package
def create_cmor_variable(task, dataset, axes):
    srcvar = task.source.variable()
    unit = getattr(task.target, "units")
    return cmor.variable(table_entry = str(task.target.out_name), units = str(unit), axis_ids = axes,
                         original_name = str(srcvar))

# Creates all landUse for the given table from the given files
# used nemo2cmor create_depth_axes as template
# Note: The land use routines are not yet functional!
def create_landuse_data(tab_id,files):
    global log,exp_name_
    result = {}
    for f in files:        
        #TODO: has the tab_id or look into files lpjg ncfile f the landuse dimensions
        #if yes: need to also create the cmo2 landuse var 
        #FIXME: is the grid check needed?
        gridstr = get_lpjg_grid(f,exp_name_)
        if(not gridstr in cmor_source.lpjg_grid):
            log.error("Unknown lpjg grid %s encountered. Skipping landuse axis creation" % gridstr)
            continue
        index = cmor_source.lpjg_grid.index(gridstr)
        if(not index in cmor_source.lpjg_landuse):
            continue
        if(index in result):
            continue
        did = create_landuse_var(f,cmor_source.lpjg_landuse[index])
        if(did != 0): result[index] = did
    return result


# Creates a cmor landUse dimension/axis
# used nemo2cmor create_depth_axis as template
def create_landuse_var(ncfile,gridchar):
    global log
    ds=netCDF4.Dataset(ncfile)
    varname="landUse"
#    if(not varname in ds.variables):
#        log.error("Could not find landuse axis variable %s in lpjg output file %s; skipping landuse axis creation." % (varname,gridchar))
#        return 0
    landusevar = ds.variables[varname]
#    landusebnd = getattr(landusevar,"bounds")
    units = getattr(landusevar,"units")
#    bndvar = ds.variables[landusebnd]
#    b = bndvar[:,:]
#    b[b<0] = 0
    return cmor.axis(table_entry = "landUse",units = units,coord_vals = landusevar[:],cell_bounds = None)
