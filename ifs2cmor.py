import os
import logging
import itertools
import numpy
import datetime
import dateutil.relativedelta
import netCDF4
import cdo
import cmor
import cmor_utils
import cmor_source
import cmor_target
import cmor_task
import postproc
import cdoapi
import threading
import Queue

# Logger construction
log = logging.getLogger(__name__)

# Experiment name
exp_name_ = None

# Table root
table_root_ = None

# Files that are being processed in the current execution loop.
ifs_gridpoint_file_ = None
ifs_spectral_file_ = None

# IFS grid description data
ifs_grid_descr_ = {}

# Start date of the processed data
start_date_ = None

# Output interval. Denotes the 0utput file periods.
output_interval_ = None

# Output frequency (hrs). Minimal interval between output variables.
output_frequency_ = 3

# Fast storage temporary path
temp_dir_ = None
tempdir_created_ = False
max_size_ = float("inf")

# Reference date, times will be converted to hours since refdate
# TODO: set in init
ref_date_ = None


# Initializes the processing loop.
def initialize(path,expname,tableroot,start,length,refdate,interval = dateutil.relativedelta.relativedelta(month = 1),outputfreq = 3,tempdir = None,maxsizegb = float("inf")):
    global log,exp_name_,table_root_,ifs_gridpoint_file_,ifs_spectral_file_,output_interval_,ifs_grid_descr_
    global temp_dir_,tempdir_created_,max_size_,ref_date_,start_date_,output_frequency_

    exp_name_ = expname
    table_root_ = tableroot
    start_date_ = start
    output_interval_ = interval
    output_frequency_ = outputfreq
    ref_date_ = refdate
    datafiles = select_files(path,exp_name_,start,length,output_interval_)
    gpfiles = [f for f in datafiles if os.path.basename(f).startswith("ICMGG")]
    shfiles = [f for f in datafiles if os.path.basename(f).startswith("ICMSH")]
    if(len(gpfiles) == 0 or len(shfiles) == 0):
        filetype = "Gridpoint" if len(gpfiles) == 0 else "Spectral"
        log.error("%s file not found in directory %s, aborting..." % (filetype,path))
        return False
    if(len(gpfiles) > 1 or len(shfiles) > 1):
        #TODO: Support postprocessing over multiple files
        log.warning("Expected a single grid point and spectral file in %s, found %s and %s; \
                     will take first file of each list." % (path,str(gpfiles),str(shfiles)))
    ifs_gridpoint_file_ = gpfiles[0]
    ifs_grid_descr_ = cdoapi.cdo_command().get_griddes(ifs_gridpoint_file_) if os.path.exists(ifs_gridpoint_file_) else {}
    ifs_spectral_file_ = shfiles[0]
    if(tempdir):
        temp_dir_ = os.path.abspath(tempdir)
        if(not os.path.exists(temp_dir_)):
            os.makedirs(temp_dir_)
            tempdir_created_ = True
    max_size_ = maxsizegb
    return True


# Execute the postprocessing+cmorization tasks
def execute(tasks):
    global log
    supportedtasks = filter_tasks(tasks)
    log.info("Executing %d IFS tasks..." % len(supportedtasks))
    taskstodo = supportedtasks
    oldsptasks,newsptasks = get_sp_tasks(supportedtasks)
    sptasks = oldsptasks + newsptasks
    taskstodo = list(set(taskstodo)-set(sptasks))
    log.info("Post-processing surface pressures...")
    proc_sptasks = postprocess(sptasks)
    for task in taskstodo:
        sptask = getattr(task,"sp_task",None)
        if(sptask):
            setattr(task,"sp_path",getattr(sptask,"path",None))
            delattr(task,"sp_task")
    cmorize(oldsptasks)
    while(any(taskstodo)):
        processedtasks = postprocess(taskstodo)
        cmorize([t for t in processedtasks if getattr(t,"path",None) != None])
        cleanup(processedtasks,False)
        taskstodo = [t for t in set(taskstodo)-set(processedtasks) if hasattr(t,"path")]
    cleanup(oldsptasks)
    cleanup(proc_sptasks)


# Deletes all temporary paths and removes temp directory
def cleanup(tasks,cleanupdir = True):
    global temp_dir_,ifs_gridpoint_file_,ifs_spectral_file_,tempdir_created_
    for task in tasks:
        ncpath = getattr(task,"path",None)
        if(ncpath != None and os.path.exists(ncpath) and ncpath not in [ifs_spectral_file_,ifs_gridpoint_file_]):
            os.remove(ncpath)
            delattr(task,"path")
    if(cleanupdir and tempdir_created_ and temp_dir_ and len(os.listdir(temp_dir_)) == 0):
        os.rmdir(temp_dir_)
        temp_dir_=None


# Creates a sub-list of tasks that we believe we can succesfully process
# TODO: Extend this to a full validation.
def filter_tasks(tasks):
    global log
    log.info("Inspecting %d tasks." % len(tasks))
    result = []
    for task in tasks:
        tgtdims = getattr(task.target,cmor_target.dims_key,[]).split()
        haslat = "latitude" in tgtdims
        haslon = "longitude" in tgtdims
        if((haslat and haslon) or (not haslat and not haslon)):
            result.append(task)
        else:
            # TODO: Support zonal variables
            log.error("Variable %s has unsupported combination of dimensions %s and will be skipped." % (task.target.variable,tgtdims))
    log.info("Validated %d tasks for processing." % len(result))
    return result


# Creates extra tasks for surface pressure
def get_sp_tasks(tasks):
    global ifs_spectral_file_
    tasksbyfreq = cmor_utils.group(tasks,lambda t:t.target.frequency)
    existing_tasks,extra_tasks = [],[]
    for freq,taskgroup in tasksbyfreq.iteritems():
        tasks3d = [t for t in taskgroup if "alevel" in getattr(t.target,cmor_target.dims_key).split()]
        if(not any(tasks3d)): continue
        sptasks = [t for t in taskgroup if t.source.get_grib_code().var_id == 134 and getattr(t,"time_operator","point") in ["mean","point"]]
        sptask = sptasks[0] if any(sptasks) else None
        if(sptask):
            existing_tasks.append(sptask)
        else:
            sptask = cmor_task.cmor_task(cmor_source.ifs_source.create(134),cmor_target.cmor_target("sp",freq))
            setattr(sptask.target,cmor_target.freq_key,freq)
            setattr(sptask,"time_operator",["mean"])
            # TODO: Make this more flexible, often sp is in gridpoint file...
            setattr(sptask,"path",ifs_gridpoint_file_)
            extra_tasks.append(sptask)
        for task in tasks3d:
            setattr(task,"sp_task",sptask)
    return existing_tasks,extra_tasks


# Postprocessing of IFS tasks
def postprocess(tasks):
    global log,output_frequency_,temp_dir_,max_size_,ifs_grid_descr_
    log.info("Post-processing %d IFS tasks..." % len(tasks))
    for task in tasks:
        ifiles = get_source_files(task.source.get_root_codes())
        if(len(ifiles)):
            setattr(task,"path",ifiles[0])
        else:
            log.error("Task %s -> %s requires a combination of spectral and gridpoint variables.\
                       This is not supported yet, task will be skipped" % (task.source.get_grib_code().var_id,task.target.variable))
    postproc.output_frequency_ = output_frequency_
    tasks_done = postproc.post_process([t for t in tasks if hasattr(t,"path")],temp_dir_,max_size_,ifs_grid_descr_)
    log.info("Post-processed batch of %d tasks." % len(tasks_done))
    return tasks_done


# Counts the (minimal) number of source files needed for the given list of codes
def get_source_files(gribcodes):
    global ifs_gridpoint_file_,ifs_spectral_file_
    if(set(gribcodes).issubset(cmor_source.ifs_source.grib_codes_gg)): return [ifs_gridpoint_file_]
    if(set(gribcodes).issubset(cmor_source.ifs_source.grib_codes_sh)): return [ifs_spectral_file_]
    return [ifs_gridpoint_file_,ifs_spectral_file_]


# Do the cmorization tasks
def cmorize(tasks):
    global log,table_root_
    log.info("Cmorizing %d IFS tasks..." % len(tasks))
    if(not any(tasks)): return
    cmor.set_cur_dataset_attribute("calendar","proleptic_gregorian")
    cmor.load_table(table_root_ + "_grids.json")
    gridid = create_grid_from_grib(getattr(tasks[0],"path"))
    for task in tasks:
        tgtdims = getattr(task.target,cmor_target.dims_key).split()
        if("latitude" in tgtdims and "longitude" in tgtdims):
            setattr(task,"grid_id",gridid)
    taskdict=cmor_utils.group(tasks,lambda t:t.target.table)
    for k,v in taskdict.iteritems():
        tab = k
        tskgroup = v
        log.info("Loading CMOR table %s..." % tab)
        tab_id = -1
        try:
            tab_id = cmor.load_table("_".join([table_root_,tab]) + ".json")
            cmor.set_table(tab_id)
        except:
            log.error("CMOR failed to load table %s, the following variables will be skipped: %s" % (tab,str([t.target.variable for t in tskgroup])))
            continue
        log.info("Creating time axes for table %s..." % tab)
        create_time_axes(tskgroup)
        log.info("Creating depth axes for table %s..." % tab)
        create_depth_axes(tskgroup)
        q = Queue.Queue()
        for i in range(postproc.task_threads):
            worker = threading.Thread(target = cmor_worker,args = [q])
            worker.setDaemon(True)
            worker.start()
        for task in tskgroup:
            q.put(task)
        q.join()


def cmor_worker(queue):
    while(True):
        task = queue.get()
        log.info("Cmorizing source variable %s to target variable %s..." % (task.source.get_grib_code().var_id,task.target.variable))
        execute_netcdf_task(task)
        queue.task_done()


# Executes a single task
def execute_netcdf_task(task):
    global log
    filepath = getattr(task,"path",None)
    if(not filepath):
        log.error("Could not find file containing data for variable %s in table" % (task.target.variable,task.target.table))
        return
    storevar = getattr(task,"store_with",None)
    sppath = getattr(task,"sp_path",None)
    if(storevar and not sppath):
        log.error("Could not find file containing surface pressure for model level variable...skipping variable %s in table %s" % (task.target.variable,task.target.table))
        return
    axes = []
    grid_id = getattr(task,"grid_id",0)
    if(grid_id != 0):
        axes.append(grid_id)
    if(hasattr(task,"z_axis_id")):
        axes.append(getattr(task,"z_axis_id"))
    time_id = getattr(task,"time_axis",0)
    if(time_id != 0):
        axes.append(time_id)
    ncvars = []
    try:
        dataset = netCDF4.Dataset(filepath,'r')
        ncvars = dataset.variables
    except Exception:
        log.error("Could not read netcdf file %s while cmorizing variable %s in table %s" % (filepath,task.target.variable,task.target.table))
        return
    codestr = str(task.source.get_grib_code().var_id)
    varlist = [v for v in ncvars if str(getattr(ncvars[v],"code",None)) == codestr]
    if(len(varlist) == 0):
        varlist = [v for v in ncvars if str(v) == "var" + codestr]
    if(len(varlist) > 1):
        log.warning("CDO variable retrieval resulted in multiple (%d) netcdf variables; will take first" % len(varlist))
    ncvar = ncvars[varlist[0]]
    unit = getattr(ncvar,"units",None)
    if((not unit) or hasattr(task,cmor_task.conversion_key)):
        unit = getattr(task.target,"units")
    varid = 0
    if(hasattr(task.target,"positive") and len(task.target.positive) != 0):
        varid = cmor.variable(table_entry = str(task.target.variable),units = str(unit),axis_ids = axes,positive = "down")
    else:
        varid = cmor.variable(table_entry = str(task.target.variable),units = str(unit),axis_ids = axes)
    factor = get_conversion_factor(getattr(task,cmor_task.conversion_key,None))
    timdim,index = -1,0
    for d in ncvar.dimensions:
        if(d.startswith("time")):
            timdim = index
            break
        index += 1
    cmor_utils.netcdf2cmor(varid,ncvar,timdim,factor,storevar,get_spvar(sppath))
    cmor.close(varid)
    if(storevar): cmor.close(storevar)


# Returns the conversion factor from the input string
def get_conversion_factor(conversion):
    global log,output_frequency_
    if(not conversion): return 1.0
    if(conversion == "cum2inst"): return 1.0 / (3600 * output_frequency_)
    if(conversion == "inst2cum"): return (3600 * output_frequency_)
    if(conversion == "pot2alt"): return 1.0 / 9.81
    if(conversion == "alt2pot"): return 9.81
    if(conversion == "vol2flux"): return 1000.0 / (3600 * output_frequency_)
    if(conversion == "vol2massl"): return 1000.0
    log.error("Unknown explicit unit conversion: %s" % conversion)
    return 1.0


# Creates time axes in cmor and attach the id's as attributes to the tasks
def create_time_axes(tasks):
    global log
    time_axes = {}
    for task in tasks:
        tgtdims = getattr(task.target,cmor_target.dims_key)
        # TODO: better to check in the table axes if the standard name of the dimension equals "time"
        for tdim in [d for d in list(set(tgtdims.split())) if d.startswith("time")]:
            tid = 0
            if(tdim in time_axes):
                tid = time_axes[tdim]
            else:
                timop = getattr(task.target,"time_operator",["mean"])
                log.info("Creating time axis using variable %s..." % task.target.variable)
                tid = create_time_axis(freq = task.target.frequency,path = getattr(task,"path"),name = tdim,hasbnds = (timop != ["point"]))
                time_axes[tdim] = tid
            setattr(task,"time_axis",tid)
            break


# Creates depth axes in cmor and attach the id's as attributes to the tasks
def create_depth_axes(tasks):
    global log
    depth_axes = {}
    for task in tasks:
        tgtdims = getattr(task.target,cmor_target.dims_key)
        #TODO: Use table axes information to extract vertical axes
        zdims = getattr(task.target,"z_dims",[])
        if(len(zdims) == 0): continue
        if(len(zdims) > 1):
            log.error("Skipping variable %s in table %s with dimensions %s with multiple directions." % (task.target.variable,task.target.table,tgtdims))
            continue
        zdim = str(zdims[0])
        if zdim in depth_axes:
            setattr(task,"z_axis_id",depth_axes[zdim])
            if(zdim == "alevel"):
                setattr(task,"z_axis_id",depth_axes[zdim][0])
                setattr(task,"store_with",depth_axes[zdim][1])
            continue
        elif zdim == "alevel":
            log.info("Creating model level axis using variable %s..." % task.target.variable)
            axisid,psid = create_hybrid_level_axis(task)
            depth_axes[zdim] = (axisid,psid)
            setattr(task,"z_axis_id",axisid)
            setattr(task,"store_with",psid)
            continue
        elif zdim in ["sdepth","sdepth1"]:
            axisid = create_soil_depth_axis(0,zdim)
            depth_axes[zdim] = axisid
            setattr(task,"z_axis_id",axisid)
        elif zdim in cmor_target.get_axis_info(task.target.table):
            axisid = 0
            axis = cmor_target.get_axis_info(task.target.table)[zdim]
            levels = axis.get("requested",[])
            if(levels == ""):
                levels = []
            value = axis.get("value",None)
            if(value):
                levels.append(value)
            unit = axis.get("units",None)
            if(len(levels) == 0):
                log.warning("Skipping axis %s in table %s with no levels" % (zdim,task.target.table))
                continue
            else:
                log.info("Creating vertical axis for %s..." % str(zdim))
                vals = [float(l) for l in levels]
                if(axis.get("must_have_bounds","no") == "yes"):
                    bndlist,n = axis.get("requested_bounds",[]),len(vals)
                    bndarr = numpy.empty([n,2])
                    for i in range(n):
                        bndarr[i,0],bndarr[i,1] = bndlist[2*i],bndlist[2*i+1]
                    axisid = cmor.axis(table_entry = str(zdim),coord_vals = vals,units = unit,cell_bounds = bndarr)
                else:
                    axisid = cmor.axis(table_entry = str(zdim),coord_vals = vals,units = unit)
            depth_axes[zdim] = axisid
            setattr(task,"z_axis_id",axisid)
        else:
            log.error("Vertical dimension %s for variable %s not found in header of table %s" % (zdim,task.target.variable,task.target.table))


# Creates the hybrid model vertical axis in cmor.
def create_hybrid_level_axis(task):
    pref = 80000 # TODO: Move reference pressure level to model config
    path = getattr(task,"path")
    ds = netCDF4.Dataset(path)
    am = ds.variables["hyam"]
    aunit = getattr(am,"units")
    bm = ds.variables["hybm"]
    bunit = getattr(bm,"units")
    hcm = am[:]/pref+bm[:]
    n = hcm.shape[0]
    ai = ds.variables["hyai"]
    abnds = numpy.empty([n,2])
    abnds[:,0] = ai[0:n]
    abnds[:,1] = ai[1:n+1]
    bi = ds.variables["hybi"]
    bbnds = numpy.empty([n,2])
    bbnds[:,0] = bi[0:n]
    bbnds[:,1] = bi[1:n+1]
    hcbnds = abnds/pref+bbnds
    axid = cmor.axis(table_entry = "alternate_hybrid_sigma",coord_vals = hcm,cell_bounds = hcbnds,units = "1")
    cmor.zfactor(zaxis_id = axid,zfactor_name = "ap",units = str(aunit),axis_ids = [axid],zfactor_values = am[:],zfactor_bounds = abnds)
    cmor.zfactor(zaxis_id = axid,zfactor_name = "b",units = str(bunit),axis_ids = [axid],zfactor_values = bm[:],zfactor_bounds = bbnds)
    storewith = cmor.zfactor(zaxis_id = axid,zfactor_name = "ps",axis_ids = [getattr(task,"grid_id"),getattr(task,"time_axis")],units = "Pa")
    return (axid,storewith)


# Creates a soil depth axis
# TODO: Read from file
soil_depth_bounds = [0.0,0.07,0.28,1.0,2.89]


# Creates a soil depth axis.
def create_soil_depth_axis(layer,name):
    vals = [0.5*(soil_depth_bounds[layer] + soil_depth_bounds[layer + 1])]
    bounds = numpy.empty([1,2])
    bounds[0,0] = soil_depth_bounds[layer]
    bounds[0,1] = soil_depth_bounds[layer + 1]
    return cmor.axis(table_entry = name,coord_vals = vals,cell_bounds = bounds,units = "m")


# Makes a time axis for the given table
def create_time_axis(freq,path,name,hasbnds):
    global log,start_date_,ref_date_
    command = cdo.Cdo()
    datetimes = []
    times = command.showtimestamp(input = path)[0].split()
    datetimes = sorted(set(map(lambda s:datetime.datetime.strptime(s,"%Y-%m-%dT%H:%M:%S"),times)))
    if(len(datetimes) == 0):
        log.error("Empty time step list encountered at time axis creation for files %s" % str(path))
        return;
    timhrs = [(d - cmor_utils.make_datetime(ref_date_)).total_seconds()/3600 for d in datetimes]
    n = len(timhrs)
    times = numpy.array(timhrs)
    if(hasbnds):
        bndvar = numpy.empty([n,2])
        if(n == 1):
            bndvar[0,0] = (cmor_utils.make_datetime(start_date_) - cmor_utils.make_datetime(ref_date_)).total_seconds()/3600
            bndvar[0,1] = 2*times[0] - bndvar[0,0]
        else:
            midtimes = 0.5*(times[0:n-1] + times[1:n])
            bndvar[0,0] = 1.5*times[0] - 0.5*times[1]
            bndvar[1:n,0] = midtimes[:]
            bndvar[0:n-1,1] = midtimes[:]
            bndvar[n-1,1] = 1.5*times[n-1] - 0.5*times[n-2]
        return cmor.axis(table_entry = str(name),units = "hours since " + str(ref_date_),coord_vals = times,cell_bounds = bndvar)
    return cmor.axis(table_entry = str(name),units = "hours since " + str(ref_date_),coord_vals = times)


# Surface pressure variable lookup utility
def get_spvar(ncpath):
    if(not ncpath):
        return None
    if(not os.path.exists(ncpath)):
        return None
    try:
        ds = netCDF4.Dataset(ncpath)
        if("var134" in ds.variables):
            return ds.variables["var134"]
        for v in ds.variables:
            if(getattr(v,"code",0) == 134):
                return v
        return None
    except:
        return None


# Retrieves all IFS output files in the input directory.
def select_files(path,expname,start,length,interval):
    allfiles = cmor_utils.find_ifs_output(path,expname)
    startdate = cmor_utils.make_datetime(start).date()
    enddate = cmor_utils.make_datetime(start + length).date()
    return [f for f in allfiles if cmor_utils.get_ifs_date(f) < enddate and cmor_utils.get_ifs_date(f) >= startdate]


# Creates the regular gaussian grids from the postprocessed file argument.
def create_grid_from_grib(filepath):
    global log
    command = cdoapi.cdo_command()
    griddescr = command.get_griddes(filepath)
    gridtype = griddescr.get("gridtype","unknown")
    if(gridtype != "gaussian"):
        log.error("Cannot read other grids then regular gaussian grids, current grid type read from file %s was % s" % (filepath,gridtype))
        return None
    xsize = griddescr.get("xsize",0)
    xfirst = griddescr.get("xfirst",0)
    yvals = griddescr.get("yvals",numpy.array([]))
    if(not (xsize > 0 and len(yvals) > 0)):
        log.error("Invalid grid detected in post-processed data: %s" % str(griddescr))
        return None
    return create_gauss_grid(xsize,xfirst,yvals)


# Creates the regular gaussian grid from its arguments.
def create_gauss_grid(nx,x0,yvals):
    ny = len(yvals)
    i_index_id = cmor.axis(table_entry = "i_index",units = "1",coord_vals = numpy.array(range(1,nx + 1)))
    j_index_id = cmor.axis(table_entry = "j_index",units = "1",coord_vals = numpy.array(range(ny,0,-1)))
    xincr = 360./nx
    xvals = numpy.array([x0 + i*xincr for i in range(nx)])
    lonarr = numpy.tile(xvals,(ny,1)).transpose()
    latarr = numpy.tile(yvals,(nx,1))
    lonmids = numpy.append(xvals - 0.5*xincr,360.-0.5*xincr)
    lonmids[0] = lonmids[nx]
    latmids = numpy.empty([ny + 1])
    latmids[0] = 90.
    latmids[1:ny] = 0.5*(yvals[0:ny - 1]+yvals[1:ny])
    latmids[ny] = -90.
    numpy.append(latmids,-90.)
    vertlats = numpy.empty([nx,ny,4])
    vertlats[:,:,0] = numpy.tile(latmids[0:ny],(nx,1))
    vertlats[:,:,1] = vertlats[:,:,0]
    vertlats[:,:,2] = numpy.tile(latmids[1:ny+1],(nx,1))
    vertlats[:,:,3] = vertlats[:,:,2]
    vertlons = numpy.empty([nx,ny,4])
    vertlons[:,:,0] = numpy.tile(lonmids[0:nx],(ny,1)).transpose()
    vertlons[:,:,3] = vertlons[:,:,0]
    vertlons[:,:,1] = numpy.tile(lonmids[1:nx+1],(ny,1)).transpose()
    vertlons[:,:,2] = vertlons[:,:,1]
    return cmor.grid(axis_ids = [j_index_id,i_index_id],
                     latitude = latarr,
                     longitude = lonarr,
                     latitude_vertices = vertlats,
                     longitude_vertices = vertlons)
