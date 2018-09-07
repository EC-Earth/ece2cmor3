import os
import re
import numpy
import datetime
import json
import logging
import netCDF4
import cmor
import cmor_utils
import cmor_source
import cmor_target
import cmor_task
import cdo
from ece2cmor3 import cdoapi
# Logger object
log = logging.getLogger(__name__)

# Experiment name
exp_name_ = None

# Table root
table_root_ = None

# Files that are being processed in the current execution loop.
tm5_files_ = []

# Dictionary of tm5 grid type with cmor grid id.
grid_ids_ = {}

# List of depth axis ids with cmor grid id.
depth_axes_ = {}

# Dictionary of output frequencies with cmor time axis id.
time_axes_ = {}

# Dictionary of sea-ice output types, 1 by default...
type_axes_ = {}

ps_tasks = {}

# Initializes the processing loop.
def initialize(path,expname,tabledir, prefix,start,length):
    global log,tm5_files_,exp_name_,table_root_
    exp_name_ = expname
    table_root_ =os.path.join(tabledir, prefix)
    print path,expname,start,length
    tm5_files_ = select_files(path,expname,start,length)
    cal = None
    for f in tm5_files_:
        cal = read_calendar(f)
        if(cal):
            break
    if(cal):
        cmor.set_cur_dataset_attribute("calendar",cal)
    
    cmor.load_table(table_root_ + "_grids.json")
    return True


# Resets the module globals.
def finalize():
    global tm5_files_,grid_ids_,depth_axes_,time_axes_
    tm5_files_ = []
    grid_ids_ = {}
    depth_axes_ = {}
    time_axes_ = {}


# Executes the processing loop.
def execute(tasks):
    global log,time_axes_,depth_axes_,table_root_,tm5_files_
    log.info("Executing %d tm5 tasks..." % len(tasks))
    log.info("Cmorizing tm5 tasks...")
    #Assign file to each task
    for task in tasks:
        setattr(task,cmor_task.output_path_key,None)
        for fstr in tm5_files_:
            print fstr
            if task.target.variable in fstr and task.target.frequency in fstr:
               
                fname=fstr
                #print fname
                setattr(task,cmor_task.output_path_key,fstr)
        #record the ps task for 3d-fields
        if task.target.variable=='ps':
            if task.target.frequency not in ps_tasks:
                ps_tasks[task.target.frequency]=task
    log.info('Creating TM5 3x2 deg lon-lat grid')
    grid = create_lonlat_grid()#xsize, xfirst, yvals)
    grid_ids_['lonlat']=grid

    cmor.set_cur_dataset_attribute("calendar", "proleptic_gregorian")
    cmor.load_table(table_root_ + "_grids.json")

    #group the taks according to table
    taskdict = cmor_utils.group(tasks,lambda t:t.target.table)
    for table,tasklist in taskdict.iteritems():
        try:
            log.info("Loading CMOR table %s to process %d variables..." % (table,len(tasklist)))
            tab_id = cmor.load_table("_".join([table_root_, table]) + ".json")
            cmor.set_table(tab_id)
        except Exception as e:
            log.error("CMOR failed to load table %s, skipping variables %s. Reason: %s"
                      % (table, ','.join([tsk.target.variable for tsk in tasklist]), e.message))
            continue
        log.info("Creating time axes for table %s..." % tab_id)
        create_time_axes(tasklist)
        for task in tasklist:
            #define task properties 
            #2D grid
            tgtdims = getattr(task.target, cmor_target.dims_key).split()
            if "latitude" in tgtdims and "longitude" in tgtdims:
                setattr(task, "grid_id", grid)
            #ZONAL
            if "latitude" in tgtdims and not "longitude" in tgtdims:
                setattr(task, "zonal", True)
            
            #Vertical
            if "alevel" in tgtdims:
                setattr(task,"ps_task",ps_tasks[task.target.frequency])
            freq = task.target.frequency.encode()
            #freq = tskgroup[0].target.frequency
            files = select_freq_files(freq)
            targetvars = task.target.variable
            if(len(files) == 0):
                log.error("No tm5 output files found for frequency %s in file list %s, skipping variables %s" % (freq,str(tm5_files_),str(targetvars)))
                continue
            #log.info("Loading CMOR table %s to process %d variables..." % (tab,len(targetvars)))
            #tab_id = -1
            #try:
            #    tab_id = cmor.load_table("_".join([table_root_,tab]) + ".json")
            #    cmor.set_table(tab_id)
            #except:
            #    log.error("CMOR failed to load table %s, skipping variables %s" % (tab,str(targetvars)))
            #    continue
            #log.info("Creating time axes for table %s..." % tab_id)
            #create_time_axes(tasklist)
            log.info("Creating vertical axis for table %s..." % tab_id)
            create_depth_axes(tasklist)  
            #taskmask = dict([t,False] for t in tskgroup)
            taskmask = dict([t,False] for t in tasklist)
            # Loop over files:

            # for ncf in files:
            #     try:
            #         ds = netCDF4.Dataset(ncf,'r')
            #for task in tskgroup:
                #if(task.source.var() in ds.variables):
            if(taskmask[task]):
                log.warning("Ignoring source variable in nc file %s, since it has already been cmorized." % ncf)
            else:
                log.info("Cmorizing source variable %s to target variable %s..." % (task.source.variable(),task.target.variable))
                execute_netcdf_task(task,tab_id)
                taskmask[task] = True
                # finally:
                #     ds.close()
            for task,executed in taskmask.iteritems():
                if(not executed):
                    log.error("The source variable %s could not be found in the input tm5 data" % task.source.variable())


# Performs a single task.
def execute_netcdf_task(task,tableid):
    global log,grid_ids_,depth_axes_,time_axes_
    #if not tableid in depth_axes_:
    #    depth_axes_[tableid]=create_hybrid_level_axis(task)

    task.status = cmor_task.status_cmorizing
    filepath = getattr(task, cmor_task.output_path_key, None)
    if not filepath:
        log.error(
            "Could not find file containing data for variable %s in table %s" % (task.target.variable,
                                                                                 task.target.table))
        return
    store_var = getattr(task, "store_with", None)
    dims = task.target.dims

    #if(not task.source.grid() in grid_ids_):
    #    log.error("Grid axis for %s has not been created; skipping variable." % task.source.grid())
    #    return
    #print task.grid_id
    axes = [grid_ids_['lonlat']]
    if( dims == 3):
        grid_index = axes#cmor_source.tm5_grid.index(task.grid_id)
        #print   grid_index, tableid,depth_axes_
        #if(not grid_index in cmor_source.tm5_depth_axes):
        #    log.error("Depth axis for grid %s has not been created; skipping variable." % task.source.grid())
        #    return
        #zaxid = depth_axes_[tableid][grid_index]
        if hasattr(task, "z_axis_id"):
            axes.append(getattr(task, "z_axis_id"))

        #axes.append(zaxid)
    time_id = getattr(task, "time_axis", 0)
    if time_id != 0:
        axes.append(time_id)
    #print axes
    #axes.append(time_axes_[tableid])
    for type in type_axes_:
        if type in getattr(task.target, cmor_target.dims_key):
            axes.append(type_axes_[type])
    try:
        dataset = netCDF4.Dataset(filepath, 'r')
    except Exception as e:
        log.error("Could not read netcdf file %s while cmorizing variable %s in table %s. Cause: %s" % (
            filepath, task.target.variable, task.target.table, e.message))
        return
    varid = create_cmor_variable(task,dataset,axes)
    ncvar = dataset.variables[task.source.variable()]
    vals=numpy.copy(ncvar[:])
    dims = numpy.shape(vals)
    nroll=dims[-1]/2
    ncvar = numpy.roll(vals,nroll,len(dims)-1)
    missval = getattr(ncvar,"missing_value",getattr(ncvar,"_FillValue",numpy.nan))
    vals=numpy.copy(ncvar[:,:,:])
    #factor 1. keep it for time being
    # Default values
    factor = 1.0#get_conversion_factor(getattr(task,cmor_task.conversion_key,None))
    term=0.0
    timdim=0
    cmor_utils.netcdf2cmor(varid, ncvar, timdim, factor, term, store_var, get_ps_var(getattr(ps_tasks[task.target.frequency],cmor_task.output_path_key,None)),
                               swaplatlon=False, fliplat=False, mask=None,missval=missval)
    cmor.close(varid)
    if store_var:
            cmor.close(store_var)
    task.status = cmor_task.status_cmorized
   
# Unit conversion utility method
# keep it for future
def get_conversion_factor(conversion):
    global log
    log.error("Unknown explicit unit conversion %s will be ignored" % conversion)
    return 1.0

# Creates a variable in the cmor package
def create_cmor_variable(task,dataset,axes):
    srcvar = task.source.variable()
    ncvar = dataset.variables[srcvar]
    unit = getattr(ncvar,"units",None)
    if((not unit) or hasattr(task,cmor_task.conversion_key)): # Explicit unit conversion
        unit = getattr(task.target,"units")
    if(hasattr(task.target,"positive") and len(task.target.positive) != 0):
        return cmor.variable(table_entry = str(task.target.variable),units = str(unit),axis_ids = axes,original_name = str(srcvar),positive = "down")
    else:
        return cmor.variable(table_entry = str(task.target.variable),units = str(unit),axis_ids = axes,original_name = str(srcvar))



# Creates a cmor depth axis
def create_depth_axis(ncfile):
    global log
    try:
        ds=netCDF4.Dataset(ncfile)
        varname="lev"
        #print varname
        if(not varname in ds.variables): # No 3D variables in this file... skip depth axis
            return 0
        depthvar = ds.variables[varname]
        #print depthvar
        #depthbnd = getattr(depthvar,"bounds")
        units = getattr(depthvar,"units")
        #bndvar = ds.variables[depthbnd]
        #b = bndvar[:,:]
        #b[b<0] = 0
        #return cmor.axis(table_entry = "depth_coord",units = units,coord_vals = depthvar[:],cell_bounds = b)
        return cmor.axis(table_entry = "depth_coord",units = units,coord_vals = depthvar[:])
    finally:
        ds.close()

# Creates time axes in cmor and attach the id's as attributes to the tasks
def create_time_axes(tasks):
    global log
    time_axes = {}
    for task in tasks:
        tgtdims = getattr(task.target, cmor_target.dims_key)
        if getattr(task, cmor_task.output_path_key)==None:
            continue
        # TODO: better to check in the table axes if the standard name of the dimension equals "time"
        for time_dim in [d for d in list(set(tgtdims.split())) if d.startswith("time")]:
            if time_dim in time_axes:
                tid = time_axes[time_dim]
            else:
                time_operator = getattr(task.target, "time_operator", ["point"])
                print task.target.variable
                print getattr(task, cmor_task.output_path_key)

                log.info("Creating time axis using variable %s..." % task.target.variable)
                tid = create_time_axis(freq=task.target.frequency, path=getattr(task, cmor_task.output_path_key),
                                       name=time_dim, has_bounds=(time_operator != ["point"]))
                time_axes[time_dim] = tid
            setattr(task, "time_axis", tid)
            break

# Creates a tie axis for the corresponding table (which is suppoed to be loaded)
def create_time_axis(freq,path,name,has_bounds):
    global log
    vals = None
    units = None
    ds = None
    #for ncfile in files:
    #has_bounds=False
    ncfile=path
    print path
    try:
        ds = netCDF4.Dataset(ncfile)
        timvar = ds.variables["time"]
        vals = timvar[:]
        #if 'bounds' in ds.variables:
        has_bounds=True
        bnds = getattr(timvar,"bounds")
        bndvar = ds.variables[bnds]
        units = getattr(timvar,"units")
        #break
    except:
        ds.close()
    if(len(vals) == 0 or units == None):
        log.error("No time values or units could be read from tm5 output files %s" % str(files))
        return 0
    print bndvar[:]
    if has_bounds:
        return cmor.axis(table_entry = str(name), units = units,coord_vals = vals,cell_bounds = bndvar[:,:])
    else:
        return cmor.axis(table_entry = str(name), units = units,coord_vals = vals)

# needed for wavelength ?
def create_type_axes():
    global type_axes_
    type_axes_["typesi"] = cmor.axis(table_entry="typesi", coord_vals=[1])

# Selects files with data with the given frequency
def select_freq_files(freq):
    global exp_name_,tm5_files_
    tm5freq = None
    if(freq == "monClim"):
        tm5freq = "1m"
    elif(freq.endswith("mon")):
        #n = 1 if freq == "mon" else int(freq[:-3])
        tm5freq = "AERmon"
    elif(freq.endswith("day")):
        #n = 1 if freq == "day" else int(freq[:-3])
        tm5freq = "AERday"
    elif(freq.endswith("hr")):
        n = 1 if freq == "hr" else int(freq[:-2])
        tm5freq = "AERhr"
    return [f for f in tm5_files_ if cmor_utils.get_tm5_frequency(f,exp_name_) == tm5freq]


# Retrieves all tm5 output files in the input directory.
def select_files(path,expname,start,length):
    allfiles = cmor_utils.find_tm5_output(path,expname)
    starttime = cmor_utils.make_datetime(start)
    stoptime = cmor_utils.make_datetime(start+length)
    return [f for f in allfiles if cmor_utils.get_tm5_interval(f)[0] <= stoptime and cmor_utils.get_tm5_interval(f)[1] >= starttime]


# Reads the calendar attribute from the time dimension.
def read_calendar(ncfile):
    try:
        ds = netCDF4.Dataset(ncfile,'r')
        if(not ds):
            return None
        timvar = ds.variables["time"]
        if(timvar):
            result = getattr(timvar,"calendar")
            return result
        else:
            return None
    finally:
        ds.close()


# Reads all the tm5 grid data from the input files.
# def create_grids():
#     global grid_ids_,tm5_files_
#     spatial_grids = [grd for grd in cmor_source.tm5_grid if grd != cmor_source.tm5_grid.scalar]
#     print spatial_grids

#     # for g in spatial_grids:

    #     gridfiles = [f for f in tm5_files_ if f.endswith(g + ".nc")]
    #     print gridfiles
    #     if(len(gridfiles) != 0):
    #         grid = read_grid(gridfiles[0])
    #         grid_ids_[g] = write_grid(grid)







# Creates the regular gaussian grids from the postprocessed file argument.
def create_grid_from_nc(filepath):
    global log
    command = cdoapi.cdo_command()
    grid_descr = command.get_grid_descr(filepath)
    gridtype = grid_descr.get("gridtype", "unknown")
    if gridtype != "gaussian":
        log.error("Cannot read other grids then regular gaussian grids, current grid type read from file %s was % s" % (
            filepath, gridtype))
        return None
    xsize = grid_descr.get("xsize", 0)
    xfirst = grid_descr.get("xfirst", 0)
    yvals = grid_descr.get("yvals", numpy.array([]))
    if not (xsize > 0 and len(yvals) > 0):
        log.error("Invalid grid detected in post-processed data: %s" % str(grid_descr))
        return None
    return create_gauss_grid(xsize, xfirst, yvals)


def create_depth_axes(tasks):
    global log
    depth_axes = {}
    for task in tasks:
        tgtdims = getattr(task.target, cmor_target.dims_key)
        zdims = getattr(task.target, "z_dims", [])
        if len(zdims) == 0:
            continue
        zdim=zdims[0]
        if zdim in depth_axes:
            setattr(task, "z_axis_id", depth_axes[zdim])
            if zdim == "alevel":
                setattr(task, "z_axis_id", depth_axes[zdim][0])
                setattr(task, "store_with", depth_axes[zdim][1])
            continue
        elif zdim == "alevel":
            log.info("Creating model level axis using variable %s..." % task.target.variable)
            axisid, psid = create_hybrid_level_axis(task)
            depth_axes[zdim] = (axisid, psid)
            setattr(task, "z_axis_id", axisid)
            setattr(task, "store_with", psid)
            continue

# Creates the hybrid model vertical axis in cmor.
def create_hybrid_level_axis(task):
    pref = 80000  # TODO: Move reference pressure level to model config
    path = getattr(task, cmor_task.output_path_key)
    #print path, task.target.variable
    ds = None
    try:
        ds = netCDF4.Dataset(path)
        am = ds.variables["a"]
        aunit = getattr(am, "units")
        bm = ds.variables["b"]
        bunit = getattr(bm, "units")
        hcm = am[:] / pref + bm[:]
        n = hcm.shape[0]
        #print n
        
        if "hyai" in ds.variables: 
            ai = ds.variables["hyai"]
            abnds = numpy.empty([n, 2])
            abnds[:, 0] = ai[0:n]
            abnds[:, 1] = ai[1:n + 1]
            bi = ds.variables["hybi"]
            bbnds = numpy.empty([n, 2])
            bbnds[:, 0] = bi[0:n]
            bbnds[:, 1] = bi[1:n + 1]
            hcbnds = abnds / pref + bbnds
        # temporary solution for current output
        else:
            ai=numpy.empty([n+1]    )
            bi=numpy.empty([n+1]    )
            ai[1:-1]=(am[1:]+am[0:-1])/2
            
            ai[0]=am[0]/2
            ai[-1]=am[-1]
            abnds = numpy.empty([n, 2])
            abnds[:, 0] = ai[0:n]
            abnds[:, 1] = ai[1:n + 1]

            bi[1:-1]=(bm[1:]+bm[0:-1])/2
            bi[0]=1.0
            bi[-1]=0.0
            bbnds = numpy.empty([n, 2])
            bbnds[:, 0] = bi[0:n]
            bbnds[:, 1] = bi[1:n + 1]
            hcbnds = abnds / pref + bbnds
            hcbnds[0,0]=1.0
        axisid = cmor.axis(table_entry="alternate_hybrid_sigma", coord_vals=hcm, cell_bounds=hcbnds, units="1")
        
        cmor.zfactor(zaxis_id=axisid, zfactor_name="ap", units=str(aunit), axis_ids=[axisid], zfactor_values=am[:],
                     zfactor_bounds=abnds)
        cmor.zfactor(zaxis_id=axisid, zfactor_name="b", units=str(bunit), axis_ids=[axisid], zfactor_values=bm[:],
                     zfactor_bounds=bbnds)
        axes=[]
        axes.append(getattr(task, "grid_id"))
        print axes
        axes.append( getattr(task, "time_axis"))
        print axes
        storewith = cmor.zfactor(zaxis_id=axisid, zfactor_name="ps",
                                axis_ids=axes, units="Pa")
        return axisid, storewith
    finally:
        if ds is not None:
            ds.close()

def create_lonlat_grid():#nx, x0, yvals):
   #print 'lonlat create',table_root_
    nx=120
    x0=0
    yvals=numpy.linspace(89,-89,90)
    ny = len(yvals)
    #print numpy.array(range(1, nx + 1))
    i_index_id = cmor.axis(table_entry="i_index", units="1", coord_vals=numpy.array(range(1, nx + 1)))
    j_index_id = cmor.axis(table_entry="j_index", units="1", coord_vals=numpy.array(range(1, ny + 1)))
    #print 'axisid',i_index_id,j_index_id
    dx = 360. / nx
    x_vals = numpy.array([x0 + (i + 0.5) * dx for i in range(nx)])
    lon_arr = numpy.tile(x_vals, (ny, 1))
    #lat_arr = numpy.tile(yvals[::-1], (nx, 1)).transpose()
    lat_arr = numpy.tile(yvals[:], (nx, 1)).transpose()
    lon_mids = numpy.array([x0 + i * dx for i in range(nx + 1)])
    lat_mids = numpy.empty([ny + 1])
    lat_mids[0] = 90.
    lat_mids[1:ny] = 0.5 * (yvals[0:ny-1] + yvals[1:ny])
    lat_mids[ny] = -90.
    vert_lats = numpy.empty([ny, nx, 4])
    vert_lats[:, :, 0] = numpy.tile(lat_mids[0:ny], (nx, 1)).transpose()
    vert_lats[:, :, 1] = vert_lats[:, :, 0]
    vert_lats[:, :, 2] = numpy.tile(lat_mids[1:ny + 1], (nx, 1)).transpose()
    vert_lats[:, :, 3] = vert_lats[:, :, 2]
    vert_lons = numpy.empty([ny, nx, 4])
    vert_lons[:, :, 0] = numpy.tile(lon_mids[0:nx], (ny, 1))
    vert_lons[:, :, 3] = vert_lons[:, :, 0]
    vert_lons[:, :, 1] = numpy.tile(lon_mids[1:nx + 1], (ny, 1))
    vert_lons[:, :, 2] = vert_lons[:, :, 1]

    lon_bnd=numpy.stack((lon_mids[:-1],lon_mids[1:]),axis=-1)
    lat_bnd=numpy.stack((lat_mids[:-1],lat_mids[1:]),axis=-1)
    #print lat_bnd
    lon_id=cmor.axis(table_entry="longitude", units="degrees_east",
                                    coord_vals=x_vals, cell_bounds=lon_bnd)
    lat_id=cmor.axis(table_entry="latitude", units="degrees_north",
                                    coord_vals=yvals, cell_bounds=lat_bnd)
    #return cmor.grid(axis_ids=[j_index_id, i_index_id], latitude=lat_arr, longitude=lon_arr,latitude_vertices=vert_lats, longitude_vertices=vert_lons)#,
    #return cmor.grid(axis_ids=[lat_id, lon_id], latitude=lat_arr, longitude=lon_arr,latitude_vertices=vert_lats, longitude_vertices=vert_lons)
    return cmor.grid(axis_ids=[lat_id, lon_id], latitude=lat_arr, longitude=lon_arr,latitude_vertices=vert_lats, longitude_vertices=vert_lons)
    #return [lon_id,lat_id]
    
# Surface pressure variable lookup utility
def get_ps_var(ncpath):
    if not ncpath:
        log.error("No path defined for surface pressure (ps).")
        return None
    if not os.path.exists(ncpath):
        log.error("Path does not exist for surface pressure (ps).")
        return None
    ds = None
    try:
        ds = netCDF4.Dataset(ncpath)
        if "ps" in ds.variables:
            return ds.variables["ps"]
        else:
            log.error("Variable ps not present in pressure file.")
            return None
    except Exception as e:
        log.error("Could not read netcdf file %s for surface pressure, reason: %s" % (ncpath, e.message))
        return None

# Creates extra tasks for surface pressure
# probably not needed
def get_sp_tasks(tasks, autofilter):
    global ifs_spectral_file_
    tasks_by_freq = cmor_utils.group(tasks, lambda task: task.target.frequency)
    result = []
    for freq, task_group in tasks_by_freq.iteritems():
        tasks3d = [t for t in task_group if "alevel" in getattr(t.target, cmor_target.dims_key).split()]
        if not any(tasks3d):
            continue
        surf_pressure_tasks = [t for t in task_group if t.source.get_grib_code() == surface_pressure and
                               getattr(t, "time_operator", "point") in ["mean", "point"]]
        surf_pressure_task = surf_pressure_tasks[0] if any(surf_pressure_tasks) else None
        if surf_pressure_task:
            result.append(surf_pressure_task)
        else:
            source = cmor_source.tm5_source(surface_pressure)
            surf_pressure_task = cmor_task.cmor_task(source, cmor_target.cmor_target("ps", freq))
            setattr(surf_pressure_task.target, cmor_target.freq_key, freq)
            setattr(surf_pressure_task.target, "time_operator", ["point"])
            find_sp_variable(surf_pressure_task, autofilter)
            result.append(surf_pressure_task)
        for task3d in tasks3d:
            setattr(task3d, "sp_task", surf_pressure_task)
    return result
