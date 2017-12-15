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
import math
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
ifs_init_gridpoint_file_ = None

# IFS surface pressure grib codes
surface_pressure = cmor_source.grib_code(134)
ln_surface_pressure = cmor_source.grib_code(152)

# IFS grid description data
ifs_grid_descr_ = {}

# Start date of the processed data
start_date_ = None

# Output interval. Denotes the 0utput file periods.
output_interval_ = None

# Output frequency (hrs). Minimal interval between output variables.
# TODO: Read from input
output_frequency_ = 3

# Fast storage temporary path
temp_dir_ = None
tempdir_created_ = False
max_size_ = float("inf")

# Reference date, times will be converted to hours since refdate
ref_date_ = None

# Available geospatial masks, assigned by ece2cmorlib
masks = {}


# Initializes the processing loop.
def initialize(path,expname,tableroot,start,length,refdate,interval = dateutil.relativedelta.relativedelta(month = 1),
               outputfreq = 3,tempdir = None,maxsizegb = float("inf")):
    global log,exp_name_,table_root_,ifs_gridpoint_file_,ifs_spectral_file_,ifs_init_gridpoint_file_,output_interval_
    global ifs_grid_descr_,temp_dir_,tempdir_created_,max_size_,ref_date_,start_date_,output_frequency_

    exp_name_ = expname
    table_root_ = tableroot
    start_date_ = start
    output_interval_ = interval
    output_frequency_ = outputfreq
    ref_date_ = refdate
    datafiles = select_files(path,exp_name_,start,length,output_interval_)
    inifiles = [f for f in datafiles if os.path.basename(f) == "ICMGG" + exp_name_ + "+000000"]
    gpfiles  = [f for f in datafiles if os.path.basename(f).startswith("ICMGG")]
    shfiles  = [f for f in datafiles if os.path.basename(f).startswith("ICMSH")]
    if(not any(gpfiles) or not any(shfiles)):
        filetype = "Gridpoint" if not any(gpfiles) else "Spectral"
        log.warning("%s file not found in directory %s, aborting..." % (filetype,path))
    if(len(gpfiles) > 1 or len(shfiles) > 1):
        #TODO: Support postprocessing over multiple files
        log.warning("Expected a single grid point and spectral file in %s, found %s and %s; \
                     will take first file of each list." % (path,str(gpfiles),str(shfiles)))
    ifs_gridpoint_file_ = gpfiles[0] if any(gpfiles) else ""
    ifs_grid_descr_ = cdoapi.cdo_command().get_griddes(ifs_gridpoint_file_) if os.path.exists(ifs_gridpoint_file_) else {}
    ifs_spectral_file_ = shfiles[0] if any(shfiles) else ""
    if(any(inifiles)):
        ifs_init_gridpoint_file_ = inifiles[0]
        if(len(inifiles) > 1):
            log.warning("Multiple initial gridpoint files found, will proceed with %s" % ifs_init_gridpoint_file_)
    else:
        ifs_init_gridpoint_file_ = ifs_gridpoint_file_
    if(tempdir):
        temp_dir_ = os.path.abspath(tempdir)
        if(not os.path.exists(temp_dir_)):
            os.makedirs(temp_dir_)
            tempdir_created_ = True
    max_size_ = maxsizegb
    return True


# Execute the postprocessing+cmorization tasks
def execute(tasks,cleanup = True):
    global log,tempdir_created_
    supportedtasks = filter_tasks(tasks)
    log.info("Executing %d IFS tasks..." % len(supportedtasks))
    taskstodo = supportedtasks
    masktasks = get_mask_tasks(supportedtasks)
    processedtasks = []
    try:
        processedtasks = postprocess(masktasks)
        for task in processedtasks:
            read_mask(task.target.variable,getattr(task,"path"))
    except:
        if(cleanup):
            clean_tmp_data(processedtasks,True)
            processedtasks = []
        raise
    finally:
        if(cleanup): clean_tmp_data(processedtasks,False)
    oldsptasks,newsptasks = get_sp_tasks(supportedtasks)
    sptasks = oldsptasks + newsptasks
    taskstodo = list(set(taskstodo)-set(sptasks))
    log.info("Post-processing surface pressures...")
    proc_sptasks = []
    try:
        proc_sptasks = postprocess(sptasks)
        for task in taskstodo:
            sptask = getattr(task,"sp_task",None)
            if(sptask):
                setattr(task,"sp_path",getattr(sptask,"path",None))
                delattr(task,"sp_task")
        cmorize(oldsptasks)
        while(any(taskstodo)):
            try:
                processedtasks = postprocess(taskstodo)
                cmorize([t for t in processedtasks if getattr(t,"path",None) != None])
            finally:
                if(cleanup): clean_tmp_data(processedtasks,False)
            taskstodo = [t for t in set(taskstodo)-set(processedtasks) if hasattr(t,"path")]
    finally:
        if(cleanup): clean_tmp_data(oldsptasks + proc_sptasks,True)


# Converts the masks that are needed into a set of tasks
def get_mask_tasks(tasks):
    global log,masks
    selected_masks = []
    for task in tasks:
        msk = getattr(task.target,cmor_target.mask_key,None)
        if(msk):
            if(msk not in masks):
                log.warning("Mask %s is not supported as an IFS mask, skipping masking" % msk)
                delattr(task.target,cmor_target.mask_key)
            else:
                selected_masks.append(msk)
            continue
        for area_operator in getattr(task.target,"area_operator",[]):
            words = area_operator.split()
            if(len(words) == 3 and words[1] == "where"):
                maskname = words[2]
                if(maskname not in masks):
                    log.warning("Mask %s is not supported as an IFS mask, skipping masking" % maskname)
                else:
                    selected_masks.append(maskname)
                    setattr(task.target,cmor_target.mask_key,maskname)
    result = []
    for m in set(selected_masks):
        target = cmor_target.cmor_target(m,"fx")
        setattr(target,cmor_target.freq_key,0)
        setattr(target,"time_operator",["point"])
        result.append(cmor_task.cmor_task(masks[m]["source"],target))
    return result


# Reads the post-processed mask variable and converts it into a boolean array
def read_mask(name,filepath):
    global masks
    try:
        dataset = netCDF4.Dataset(filepath,'r')
    except Exception:
        log.error("Could not read netcdf file %s while reading mask %s" % (filepath,name))
        return
    try:
        ncvars = dataset.variables
        codestr = str(masks[name]["source"].get_grib_code().var_id)
        varlist = [v for v in ncvars if str(getattr(ncvars[v],"code",None)) == codestr]
        if(len(varlist) == 0):
            varlist = [v for v in ncvars if str(v) == "var" + codestr]
        if(len(varlist) > 1):
            log.warning("CDO variable retrieval resulted in multiple (%d) netcdf variables; will take first" % len(varlist))
        ncvar = ncvars[varlist[0]]
        var = None
        if(len(ncvar.shape) == 2):
            var = ncvar[:,:]
        elif(len(ncvar.shape) == 3 and ncvar.shape[0] == 1):
            var = ncvar[0,:,:]
        elif(len(ncvar.shape) == 4 and ncvar.shape[0] == 1 and ncvar.shape[1] == 1):
            var = ncvar[0,0,:,:]
        else:
            log.error("After processing, the shape of the mask variable is %s which cannot be applied to time slices" % str(ncvar.shape))
            return
        f,v = masks[name]["operator"],masks[name]["rhs"]
        func = numpy.vectorize(lambda x:f(x,v))
        masks[name]["array"] = func(var[:,:])
    finally:
        dataset.close()


# Deletes all temporary paths and removes temp directory
def clean_tmp_data(tasks,cleanupdir = True):
    global temp_dir_,ifs_gridpoint_file_,ifs_spectral_file_,tempdir_created_
    for task in tasks:
        ncpath = getattr(task,"path",None)
        if(ncpath != None and os.path.exists(ncpath) and ncpath not in [ifs_spectral_file_,ifs_gridpoint_file_]):
            os.remove(ncpath)
            delattr(task,"path")
    if(cleanupdir and tempdir_created_ and temp_dir_ and len(os.listdir(temp_dir_)) == 0):
        os.rmdir(temp_dir_)
        temp_dir_ =  None


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
        sptasks = [t for t in taskgroup if t.source.get_grib_code() == surface_pressure and
                                           getattr(t,"time_operator","point") in ["mean","point"]]
        sptask = sptasks[0] if any(sptasks) else None
        if(sptask):
            existing_tasks.append(sptask)
        else:
            source = cmor_source.ifs_source(surface_pressure)
            sptask = cmor_task.cmor_task(source,cmor_target.cmor_target("sp",freq))
            setattr(sptask.target,cmor_target.freq_key,freq)
            setattr(sptask.target,"time_operator",["mean"])
            find_sp_variable(sptask)
            extra_tasks.append(sptask)
        for task in tasks3d:
            setattr(task,"sp_task",sptask)
    return existing_tasks,extra_tasks


# Postprocessing of IFS tasks
def postprocess(tasks):
    global log,output_frequency_,temp_dir_,max_size_,ifs_grid_descr_,surface_pressure
    log.info("Post-processing %d IFS tasks..." % len(tasks))
    for task in tasks:
        rootcodes = task.source.get_root_codes()
        if(rootcodes == [surface_pressure]):
            find_sp_variable(task)
        else:
            ifiles = get_source_files(rootcodes)
            if(len(ifiles) == 1):
                if(ifiles[0] == ifs_gridpoint_file_ and getattr(task.target,cmor_target.freq_key) == 0):
                    setattr(task,"path",ifs_init_gridpoint_file_)
                else:
                    setattr(task,"path",ifiles[0])
            else:
                log.error("Task %s -> %s requires a combination of spectral and gridpoint variables.\
                           This is not supported yet, task will be skipped" % (task.source.get_grib_code().var_id,task.target.variable))
    postproc.output_frequency_ = output_frequency_
    tasks_done = postproc.post_process([t for t in tasks if hasattr(t,"path")],temp_dir_,max_size_,ifs_grid_descr_)
    log.info("Post-processed batch of %d tasks." % len(tasks_done))
    return tasks_done


# Finds the surface pressure data source: gives priority to SH file.
def find_sp_variable(task):
    global ifs_gridpoint_file_,ifs_spectral_file_,surface_pressure,ln_surface_pressure
    log.info("Looking for surface pressure variable in input files...")
    command = cdo.Cdo()
    shcodestr = command.showcode(input = ifs_spectral_file_)
    shcodes = [cmor_source.grib_code(int(c)) for c in shcodestr[0].split()]
    if(surface_pressure in shcodes):
        log.info("Found surface pressure in spectral file")
        setattr(task,"path",ifs_spectral_file_)
        task.source.grid_ = 1
        return
    if(ln_surface_pressure in shcodes):
        log.info("Found lnsp in spectral file")
        setattr(task,"path",ifs_spectral_file_)
        task.source = cmor_source.ifs_source.read("var134=exp(var152)")
        return
    log.info("Did not find sp or lnsp in spectral file: assuming gridpoint file contains sp")
    setattr(task,"path",ifs_gridpoint_file_)
    task.source.grid_ = 0


# Counts the (minimal) number of source files needed for the given list of codes
def get_source_files(gribcodes):
    global ifs_gridpoint_file_,ifs_spectral_file_
    files = []
    for gc in gribcodes:
        if(gc in cmor_source.ifs_source.grib_codes_sh):
            files.append(ifs_spectral_file_)
        else:
            files.append(ifs_gridpoint_file_)
    return list(set(files))


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


# Worker function for parallel cmorization (not working at the present...)
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
    except Exception:
        log.error("Could not read netcdf file %s while cmorizing variable %s in table %s" % (filepath,task.target.variable,task.target.table))
        return
    try:
        ncvars = dataset.variables
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
        flipsign = False
        if(hasattr(task.target,"positive") and len(task.target.positive) != 0):
            flipsign = (getattr(task.target,"positive") == "up")
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
        mask = getattr(task.target,cmor_target.mask_key,None)
        maskarr = masks[mask].get("array",None) if mask in masks else None
        missval = getattr(task.target,cmor_target.missval_key,1.e+20)
        if(flipsign): missval = -missval
        cmor_utils.netcdf2cmor(varid,ncvar,timdim,factor,storevar,get_spvar(sppath),swaplatlon = False,fliplat = True,mask = maskarr,missval = missval)
        cmor.close(varid)
        if(storevar): cmor.close(storevar)
    finally:
        dataset.close()


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
    if(conversion == "frac2percent"): return 100.0
    if(conversion == "percent2frac"): return 0.01
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
                timop = getattr(task.target,"time_operator",["point"])
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
        elif zdim in ["sdepth"]:
            axisid = create_soil_depth_axis(zdim,getattr(task,"path"))
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
                    if(not bndlist):
                        bndlist = [float(x) for x in axis.get("bounds_values",[]).split()]
                    if(len(bndlist)==2*n):
                        bndarr = numpy.empty([n,2])
                        for i in range(n):
                            bndarr[i,0],bndarr[i,1] = bndlist[2*i],bndlist[2*i+1]
                        axisid = cmor.axis(table_entry = str(zdim),coord_vals = vals,units = unit,cell_bounds = bndarr)
                    else:
                        log.error("Failed to retrieve bounds for vertical axis %s" % str(zdim))
                        axisid = cmor.axis(table_entry = str(zdim),coord_vals = vals,units = unit)
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
    try:
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
    finally:
        ds.close()


# Creates a soil depth axis.
def create_soil_depth_axis(name,filepath):
    global log
    try:
        dataset = netCDF4.Dataset(filepath,'r')
        ncvar = dataset.variables.get("depth",None)
        if(not ncvar):
            log.error("Could retrieve depth coordinate from file %s" % filepath)
            return 0
        units = getattr(ncvar,"units","cm")
        factor = 0
        if(units == "mm"):
            factor = 0.001
        elif(units == "cm"):
            factor = 0.01
        elif(units == "m"):
            factor = 1
        else:
            log.error("Unknown units for depth axis in file %s" % filepath)
            return 0
        vals = factor*ncvar[:]
        ncvar = dataset.variables.get("depth_bnds",None)
        bndvals = None
        if(not ncvar):
            n = len(vals)
            bndvals = numpy.empty([n,2])
            bndvals[0,0] = 0.
            if(n > 1):
                bndvals[1:,0] = (vals[0:n - 1] + vals[1:])/2
                bndvals[0:n - 1,1] = bndvals[1:n,0]
                bndvals[n - 1,1] = (3*vals[n - 1] - bndvals[n - 1,0])/2
            else:
                bndvals[0,1] = 2*vals[0]
        else:
            bndvals = factor*ncvar[:,:]
        return cmor.axis(table_entry = name,coord_vals = vals,cell_bounds = bndvals,units = "m")
    except Exception:
        log.error("Could not read netcdf file %s while creating soil depth axis" % filepath)
    finally:
        dataset.close()
    return 0


# Makes a time axis for the given table
def create_time_axis(freq,path,name,hasbnds):
    global log,start_date_,ref_date_
    command = cdo.Cdo()
    times = command.showtimestamp(input = path)[0].split()
    datetimes = sorted(set(map(lambda s:datetime.datetime.strptime(s,"%Y-%m-%dT%H:%M:%S"),times)))
    if(len(datetimes) == 0):
        log.error("Empty time step list encountered at time axis creation for files %s" % str(path))
        return;
    refdt = cmor_utils.make_datetime(ref_date_)
    timconv = lambda d:(cmor_utils.get_rounded_time(freq,d) - refdt).total_seconds()/3600.
    if(hasbnds):
        n = len(datetimes)
        bndvar = numpy.empty([n,2])
        roundedtimes = map(timconv,datetimes)
        bndvar[:,0] = roundedtimes[:]
        bndvar[0:n-1,1] = roundedtimes[1:n]
        bndvar[n-1,1] = (cmor_utils.get_rounded_time(freq,datetimes[n-1],1) - refdt).total_seconds()/3600.
        times[:] = bndvar[:,0] + (bndvar[:,1] - bndvar[:,0])/2
        return cmor.axis(table_entry = str(name),units = "hours since " + str(ref_date_),coord_vals = times,cell_bounds = bndvar)
    times = numpy.array([(d - refdt).total_seconds()/3600 for d in datetimes])
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
    finally:
        dataset.close()


# Retrieves all IFS output files in the input directory.
def select_files(path,expname,start,length,interval):
    allfiles = cmor_utils.find_ifs_output(path,expname)
    startdate = cmor_utils.make_datetime(start).date()
    enddate = cmor_utils.make_datetime(start + length).date()
    return [f for f in allfiles if f.endswith("ICMGG" + expname + "+000000") or
            (cmor_utils.get_ifs_date(f) < enddate and cmor_utils.get_ifs_date(f) >= startdate)]


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
    j_index_id = cmor.axis(table_entry = "j_index",units = "1",coord_vals = numpy.array(range(1,ny + 1)))
    dx = 360./nx
    xvals = numpy.array([x0 + (i + 0.5)*dx for i in range(nx)])
    lonarr = numpy.tile(xvals,(ny,1))
    latarr = numpy.tile(yvals[::-1],(nx,1)).transpose()
    lonmids = numpy.array([x0 + i*dx for i in range(nx + 1)])
    latmids = numpy.empty([ny + 1])
    latmids[0] = 90.
    latmids[1:ny] = 0.5*(yvals[0:ny - 1] + yvals[1:ny])
    latmids[ny] = -90.
    vertlats = numpy.empty([ny,nx,4])
    vertlats[:,:,0] = numpy.tile(latmids[0:ny],(nx,1)).transpose()
    vertlats[:,:,1] = vertlats[:,:,0]
    vertlats[:,:,2] = numpy.tile(latmids[1:ny+1],(nx,1)).transpose()
    vertlats[:,:,3] = vertlats[:,:,2]
    vertlons = numpy.empty([ny,nx,4])
    vertlons[:,:,0] = numpy.tile(lonmids[0:nx],(ny,1))
    vertlons[:,:,3] = vertlons[:,:,0]
    vertlons[:,:,1] = numpy.tile(lonmids[1:nx+1],(ny,1))
    vertlons[:,:,2] = vertlons[:,:,1]
    return cmor.grid(axis_ids = [j_index_id,i_index_id],latitude = latarr,longitude = lonarr,
                     latitude_vertices = vertlats,longitude_vertices = vertlons)
