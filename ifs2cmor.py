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

# Logger construction
log = logging.getLogger(__name__)

# Experiment name
exp_name_ = None

# Table root
table_root_ = None

# Files that are being processed in the current execution loop.
ifs_gridpoint_file_ = None
ifs_spectral_file_ = None

# Start date of the processed data
start_date_ = None

# Output interval. Denotes the 0utput file periods.
output_interval_ = None

# Output frequency. Minimal interval between output variables.
output_freq_ = 3

# Fast storage temporary path
temp_dir_ = os.getcwd()
tempdir_created_ = False

# Reference date, times will be converted to hours since refdate
# TODO: set in init
ref_date_ = None

# Initializes the processing loop.
def initialize(path,expname,tableroot,start,length,refdate,interval=dateutil.relativedelta.relativedelta(month=1),tempdir=None):
    global exp_name_
    global table_root_
    global ifs_gridpoint_file_
    global ifs_spectral_file_
    global output_interval
    global temp_dir_
    global tempdir_created_
    global ref_date_
    global start_date_

    exp_name_ = expname
    table_root_ = tableroot
    start_date_ = start
    output_interval = interval
    ref_date_ = refdate
    datafiles = select_files(path,exp_name_,start,length,output_interval)
    gpfiles = [f for f in datafiles if os.path.basename(f).startswith("ICMGG")]
    shfiles = [f for f in datafiles if os.path.basename(f).startswith("ICMSH")]
    if(not (len(gpfiles) == 1 and len(shfiles) == 1)):
        #TODO: Support postprocessing over multiple files
        log.warning("Expected a single grid point and spectral file to process, found %s and %s; \
                     will take first file of each list." % (str(gpfiles),str(shfiles)))
    ifs_gridpoint_file_ = gpfiles[0]
    ifs_spectral_file_ = shfiles[0]
    if(tempdir):
        if(not os.path.exists(tempdir)):
            os.makedirs(tempdir)
            tempdir_created_ = True
        temp_dir_ = tempdir
    #TODO: set after conversion to netcdf
    cmor.set_cur_dataset_attribute("calendar","proleptic_gregorian")


# Execute the postprocessing+cmorization tasks
def execute(tasks):
    supportedtasks = filter_tasks(tasks)
    log.info("Executing %d IFS tasks..." % len(supportedtasks))
    postprocess(supportedtasks)
    log.info("Cmorizing IFS tasks...")
    cmorize(supportedtasks)


# Deletes all temporary paths and removes temp directory
def cleanup(tasks):
    for task in tasks:
        ncpath = getattr(task,"path",None)
        if(ncpath != None and os.path.exists(ncpath) and ncpath not in [ifs_spectral_file_,ifs_gridpoint_file_]):
            os.remove(ncpath)
        delattr(task,"path")
    if(tempdir_created_ and len(os.listdir(temp_dir_)) == 0):
        os.rmdir(temp_dir_)
        temp_dir_=None


# Creates a sub-list of tasks that we believe we can succesfully process
def filter_tasks(tasks):
    result = []
    for task in tasks:
        tgtdims=getattr(task.target,cmor_target.dims_key).split()
        haslat = "latitude" in tgtdims
        haslon = "longitude" in tgtdims
        if(haslat and haslon):
            result.append(task)
        elif(haslat or haslon):
            # TODO: Support meriodinal variables
            log.error("Variable %s has unsupported combination of dimensions %s and will be skipped." % (task.target.variable,tgtdims))
        else:
            result.append(task)
    return result


# Postprocessing of IFS tasks
def postprocess(tasks):
    log.info("Post-processing IFS tasks...")
    for task in tasks:
        setattr(task,"path",ifs_spectral_file_ if task.source.grid() == cmor_source.ifs_grid[cmor_source.ifs_grid.spec] else ifs_gridpoint_file_)
    postproc.post_process(tasks,temp_dir_)
    log.info("Post-processing surface pressures...")
    tasksbyfreq = cmor_utils.group(tasks,lambda t:t.target.frequency)
    for freq,taskgroup in tasksbyfreq.iteritems():
        tasks3d = [t for t in taskgroup if "alevel" in getattr(t.target,cmor_target.dims_key).split()]
        if(not any(tasks3d)): continue
        sptasks = [t for t in taskgroup if t.source.get_grib_code().var_id == 134 and getattr(t,"time_operator","point") in ["mean","point"]]
        sptask = sptasks[0] if any(sptasks) else None
        if(sptask == None or not getattr(sptask,"path","").endswith(".nc")):
            sptask = cmor_task.cmor_task(cmor_source.ifs_source.create(134),cmor_target.cmor_target("sp",freq))
            setattr(sptask.target,cmor_target.freq_key,freq)
            setattr(sptask,"time_operator",["mean"])
            setattr(sptask,"path",ifs_spectral_file_)
            postproc.post_process([sptask],temp_dir_)
        for task in tasks3d:
            setattr(task,"sp_path",getattr(sptask,"path"))


# Do the cmorization tasks
def cmorize(tasks):
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
        print "Loading CMOR table",tab,"..."
        tab_id = -1
        try:
            tab_id = cmor.load_table("_".join([table_root_,tab]) + ".json")
            cmor.set_table(tab_id)
        except:
            print "CMOR failed to load table",tab,", the following variables will be skipped: ",[t.target.variable for t in tskgroup]
            continue
        log.info("Creating time axes for table %s..." % tab)
        create_time_axes(tskgroup)
        log.info("Creating depth axes for table %s..." % tab)
        create_depth_axes(tskgroup)
        # TODO: parallelize
        for task in tskgroup:
            log.info("Cmorizing source variable %s to target variable %s..." % (task.source.get_grib_code().var_id,task.target.variable))
            execute_netcdf_task(task)


# Executes a single task
def execute_netcdf_task(task):
    storevar = getattr(task,"store_with",None)
    sppath = getattr(task,"sp_path",None)
    if(storevar and not sppath):
        log.error("Could not find file containing surface pressure for model level variable...skipping variable %s" % task.target.variable)
        return
    axes = []
    grid_id = getattr(task,"grid_id",0)
    if(grid_id != 0):
        axes.append(grid_id)
    z_axis = getattr(task,"z_axis",None)
    if(z_axis):
        axes.append(getattr(task,"z_axis_id"))
    time_id = getattr(task,"time_axis",0)
    if(time_id != 0):
        axes.append(time_id)
    filepath = getattr(task,"path")
    cdocmd = cdo.Cdo()
    ncvars = []
    try:
        ncvars = cdocmd.copy(input = filepath,returnCdf = True).variables
    except Exception:
        log.error("CDO command %s has failed...skipping variable" % (command,task.target.variable))
        return
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


# Returns the conversion factor from the input string
def get_conversion_factor(conversion):
    if(not conversion): return 1.0
    if(conversion == "cum2inst"): return 1.0 / (3600 * output_freq_)
    if(conversion == "inst2cum"): return (3600 * output_freq_)
    if(conversion == "pot2alt"): return 1.0 / 9.81
    if(conversion == "alt2pot"): return 9.81
    if(conversion == "vol2flux"): return 1000.0 / (3600 * output_freq_)
    log.error("Unknown explicit unit conversion: %s" % conversion)
    return 1.0


# Creates time axes in cmor and attach the id's as attributes to the tasks
def create_time_axes(tasks):
    time_axes = {}
    for task in tasks:
        tgtdims = getattr(task.target,cmor_target.dims_key)
        # TODO: better to check in the table axes if the standard name of the dimension equals "time"
        tdims = [d for d in list(set(tgtdims.split())) if d.startswith("time")]
        for tdim in tdims:
            tid = 0
            if(tdim in time_axes):
                tid = time_axes[tdim]
            else:
                tid = create_time_axis(freq = task.target.frequency,path = getattr(task,"path"),name = tdim)
            setattr(task,"time_axis",tid)


# Creates depth axes in cmor and attach the id's as attributes to the tasks
def create_depth_axes(tasks):
    depth_axes = {}
    for task in tasks:
        tgtdims = getattr(task.target,cmor_target.dims_key)
        #TODO: Use table axes information to extract vertical axes
        zdims = getattr(task.target,"z_dims")
        if(len(zdims) == 0): continue
        if(len(zdims) > 1):
            log.error("Skipping variable %s in table %s with dimensions %s with multiple directions." % (task.target.variable,task.target.table,tgtdims))
            continue
        zdim = str(zdims[0])
        if zdim in depth_axes:
            setattr(task,"z_axis_id",depth_axes[zdim])
            if(zdim == "alevel"):
                zfactor = cmor.zfactor(zaxis_id = depth_axes[zdim],zfactor_name = "ps",axis_ids = [getattr(task,"grid_id"),getattr(task,"time_axis")],units = "Pa")
                setattr(task,"store_with",zfactor)
            continue
        elif zdim == "alevel":
            axisid,psid = create_hybrid_level_axis(task)
            depth_axes[zdim] = axisid
            setattr(task,"z_axis_id",axisid)
            setattr(task,"store_with",psid)
            continue
	elif zdim in ["sdepth","sdepth1"]:
            axisid = create_soil_depth_axis(0,zdim)
            depth_axes[zdim] = axisid
            setattr(task,"z_axis_id",axisid)
        elif zdim in cmor_target.axes[task.target.table]:
            axisid = 0
            axis = cmor_target.axes[task.target.table][zdim]
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
                vals = [float(l) for l in levels]
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
# TODO: move to some IFS model class
soil_depth_bounds = [0.0,0.07,0.28,1.0,2.89]

def create_soil_depth_axis(layer,name):
    vals = [0.5*(soil_depth_bounds[layer] + soil_depth_bounds[layer + 1])]
    bounds = numpy.empty([1,2])
    bounds[0,0] = soil_depth_bounds[layer]
    bounds[0,1] = soil_depth_bounds[layer + 1]
    return cmor.axis(table_entry = name,coord_vals = vals,cell_bounds = bounds,units = "m")

# Makes a time axis for the given table
def create_time_axis(freq,path,name):
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
    ax_id = cmor.axis(table_entry = str(name),units = "hours since " + str(ref_date_),coord_vals = times,cell_bounds = bndvar)
    return ax_id


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
    command = cdo.Cdo()
    griddescr = command.griddes(input = filepath)
    xsize = 0
    ysize = 0
    yvals = []
    xstart = 0.0
    reading_ys = False
    for s in griddescr:
        sstr = str(s)
        if(reading_ys):
            yvals.extend([float(s) for s in sstr.split()])
            continue
        if(sstr.startswith("gridtype")):
            gtype = sstr.split("=")[1].strip()
            if(gtype != "gaussian"):
                raise Exception("Cannot read other grids then regular gaussian grids, current grid type was:",gtype)
        if(sstr.startswith("xsize")):
            xsize = int(sstr.split("=")[1].strip())
            continue
        if(sstr.startswith("xfirst")):
            xfirst = float(sstr.split("=")[1].strip())
            continue
        if(sstr.startswith("ysize")):
            ysize = int(sstr.split("=")[1].strip())
            continue
        if(sstr.startswith("yvals")):
            reading_ys = True
            ylist = sstr.split("=")[1].strip()
            yvals.extend([float(s) for s in ylist.split()])
            continue
    if(len(yvals) != ysize):
        log.error("Invalid number of y-values given in file %s" % filepath)
    return create_gauss_grid(xsize,xstart,ysize,numpy.array(yvals))


# Creates the regular gaussian grid from its arguments.
def create_gauss_grid(nx,x0,ny,yvals):
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
