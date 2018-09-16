import datetime

import cdo
import cmor
import glob
import logging
import multiprocessing
import netCDF4
import numpy
import os

from ece2cmor3 import grib_filter, cdoapi, cmor_source, cmor_target, cmor_task, cmor_utils, postproc

# Logger construction
log = logging.getLogger(__name__)

# Experiment name
exp_name_ = None

# Table root
table_root_ = None

# Files that are being processed in the current execution loop.
ifs_gridpoint_files_ = None
ifs_spectral_files_ = None
ifs_init_gridpoint_file_ = None

# IFS surface pressure grib codes
surface_pressure = cmor_source.grib_code(134)
ln_surface_pressure = cmor_source.grib_code(152)

# IFS grid description data
ifs_grid_descr_ = {}

# Start date of the processed data
start_date_ = None

# Output frequency (hrs). Minimal interval between output variables.
output_frequency_ = 6

# Fast storage temporary path
temp_dir_ = None
max_size_ = float("inf")

# Reference date, times will be converted to hours since refdate
ref_date_ = None

# Autofilter option
auto_filter_ = True

# Available geospatial masks, assigned by ece2cmorlib
masks = {}


# Initializes the processing loop.
def initialize(path, expname, tableroot, start, length, refdate, outputfreq=6, tempdir=None, maxsizegb=float("inf"),
               autofilter=True):
    global log, exp_name_, table_root_, ifs_gridpoint_files_, ifs_spectral_files_, ifs_init_gridpoint_file_, \
        ifs_grid_descr_, temp_dir_, max_size_, ref_date_, start_date_, output_frequency_, auto_filter_

    exp_name_ = expname
    table_root_ = tableroot
    start_date_ = start
    output_frequency_ = outputfreq
    ref_date_ = refdate
    auto_filter_ = autofilter

    inifiles = glob.glob1(path, "ICMGG" + exp_name_ + "+000000")
    if any(inifiles):
        ifs_init_gridpoint_file_ = inifiles[0]
        if len(inifiles) > 1:
            log.warning("Multiple initial gridpoint files found, will proceed with %s" % ifs_init_gridpoint_file_)

    file_pattern = expname + "+[0-9][0-9][0-9][0-9][0-9][0-9]"
    gpfiles = {cmor_utils.get_ifs_date(f): f for f in glob.glob1(path, "ICMGG" + file_pattern) if not f.endswith("+000000")}
    shfiles = {cmor_utils.get_ifs_date(f): f for f in glob.glob1(path, "ICMSH" + file_pattern) if not f.endswith("+000000")}
    gpfiles = {date: gpfiles[date] for date in gpfiles.keys() if start <= date < start + length}
    shfiles = {date: shfiles[date] for date in shfiles.keys() if start <= date < start + length}

    if set(gpfiles.keys()) != set(shfiles.keys()):
        intersection = set(gpfiles.keys()).intersection(set(shfiles.keys()))
        if not any(intersection):
            log.error("Gridpoint files %s and spectral files %s correspond to different months, no overlap found..." %
                      (str(gpfiles.values()), str(shfiles.values())))
            ifs_gridpoint_files_ = {}
            ifs_spectral_files_ = {}
            return False
        else:
            ifs_gridpoint_files_ = {date: gpfiles[date] for date in intersection}
            ifs_spectral_files_ = {date: shfiles[date] for date in intersection}
            log.warning("Gridpoint files %s and spectral files %s correspond to different months, found overlapping "
                        "dates %s" % (str(gpfiles.values()), str(shfiles.values()), str(intersection)))
    else:
        ifs_gridpoint_files_, ifs_spectral_files_ = gpfiles, shfiles

    tmpdir_parent = os.getcwd() if tempdir is None else tempdir
    dirname = exp_name_ + start_date_.strftime("-ifs-%Y")
    temp_dir_ = os.path.join(tmpdir_parent, dirname)
    os.makedirs(temp_dir_, exist_ok=True)
    max_size_ = maxsizegb
    if auto_filter_:
        grib_filter.initialize(ifs_gridpoint_files_, ifs_spectral_files_, temp_dir_)
    return True


# Execute the postprocessing+cmorization tasks. First masks, then surface pressures, then regular tasks.
def execute(tasks, cleanup=True, nthreads=1):
    global log, start_date_, ifs_grid_descr_, auto_filter_
    supported_tasks = [t for t in filter_tasks(tasks) if t.status == cmor_task.status_initialized]
    log.info("Executing %d IFS tasks..." % len(supported_tasks))
    mask_tasks = get_mask_tasks(supported_tasks)
    surf_pressure_tasks = get_sp_tasks(supported_tasks)
    regular_tasks = [t for t in supported_tasks if t not in surf_pressure_tasks]
    tasks_todo = mask_tasks + surf_pressure_tasks + regular_tasks
    grid_descr_file = None
    if auto_filter_:
        tasks_todo = grib_filter.execute(tasks_todo)
        for t in tasks_todo:
            if getattr(t.source, "grid_", None) == cmor_source.ifs_grid.point:
                filepaths = getattr(t, cmor_task.filter_output_key, [])
                if any(filepaths):
                    grid_descr_file = filepaths[0]
                    break
    else:
        for task in tasks_todo:
            if task.source.grid_id() == cmor_source.ifs_grid.point:
                setattr(task, cmor_task.filter_output_key, ifs_gridpoint_files_.values())
            elif task.source.grid_id() == cmor_source.ifs_grid.spec:
                setattr(task, cmor_task.filter_output_key, ifs_spectral_files_.values())
            else:
                log.error("Task ifs source has unknown grid for %s in table %s" % (task.target.variable,
                                                                                   task.target.table))
                task.set_failed()
            setattr(task, cmor_task.output_frequency_key, output_frequency_)
        grid_descr_file = ifs_gridpoint_files_.values()[0]
    log.info("Fetching grid description from %s ..." % grid_descr_file)
    ifs_grid_descr_ = cdoapi.cdo_command().get_grid_descr(grid_descr_file) if os.path.exists(grid_descr_file) else {}
    processed_tasks = []
    try:
        log.info("Post-processing tasks...")
        postproc.task_threads = nthreads
        processed_tasks = postprocess([t for t in tasks_todo if t.status == cmor_task.status_initialized])
        for task in [t for t in processed_tasks if t in mask_tasks]:
            read_mask(task.target.variable, getattr(task, cmor_task.output_path_key))
        cmorize([t for t in processed_tasks if t in supported_tasks], nthreads=nthreads)
    finally:
        if cleanup:
            clean_tmp_data(processed_tasks)


# Converts the masks that are needed into a set of tasks
def get_mask_tasks(tasks):
    global log, masks
    selected_masks = []
    for task in tasks:
        msk = getattr(task.target, cmor_target.mask_key, None)
        if msk:
            if msk not in masks:
                log.warning("Mask %s is not supported as an IFS mask, skipping masking" % msk)
                delattr(task.target, cmor_target.mask_key)
            else:
                selected_masks.append(msk)
            continue
        for area_operator in getattr(task.target, "area_operator", []):
            words = area_operator.split()
            if len(words) == 3 and words[1] == "where":
                mask_name = words[2]
                if mask_name not in masks:
                    log.warning("Mask %s is not supported as an IFS mask, skipping masking" % mask_name)
                else:
                    selected_masks.append(mask_name)
                    setattr(task.target, cmor_target.mask_key, mask_name)
    result = []
    for m in set(selected_masks):
        target = cmor_target.cmor_target(m, "fx")
        setattr(target, cmor_target.freq_key, 0)
        setattr(target, "time_operator", ["point"])
        result_task = cmor_task.cmor_task(masks[m]["source"], target)
        setattr(result_task, cmor_task.output_path_key, ifs_gridpoint_files_)
        result.append(result_task)
    return result


# Reads the post-processed mask variable and converts it into a boolean array
def read_mask(name, filepath):
    global masks
    try:
        dataset = netCDF4.Dataset(filepath, 'r')
    except Exception as e:
        log.error("Could not read netcdf file %s while reading mask %s, reason: %s" % (filepath, name, e.message))
        return
    try:
        ncvars = dataset.variables
        codestr = str(masks[name]["source"].get_grib_code().var_id)
        varlist = [v for v in ncvars if str(getattr(ncvars[v], "code", None)) == codestr]
        if len(varlist) == 0:
            varlist = [v for v in ncvars if str(v) == "var" + codestr]
        if len(varlist) > 1:
            log.warning(
                "CDO variable retrieval resulted in multiple (%d) netcdf variables; will take first" % len(varlist))
        ncvar = ncvars[varlist[0]]
        if len(ncvar.shape) == 2:
            var = ncvar[:, :]
        elif len(ncvar.shape) == 3 and ncvar.shape[0] == 1:
            var = ncvar[0, :, :]
        elif len(ncvar.shape) == 4 and ncvar.shape[0] == 1 and ncvar.shape[1] == 1:
            var = ncvar[0, 0, :, :]
        else:
            log.error(
                "After processing, the shape of the mask variable is %s which cannot be applied to time slices" % str(
                    ncvar.shape))
            return
        f, v = masks[name]["operator"], masks[name]["rhs"]
        func = numpy.vectorize(lambda x: f(x, v))
        masks[name]["array"] = func(var[:, :])
    finally:
        dataset.close()


# Deletes all temporary paths and removes temp directory
def clean_tmp_data(tasks):
    global temp_dir_, ifs_gridpoint_files_, ifs_spectral_files_
    for task in tasks:
        for key in [cmor_task.filter_output_key, cmor_task.output_path_key]:
            data_path = getattr(task, key, None)
            if data_path is not None and data_path not in ifs_spectral_files_.values() + ifs_gridpoint_files_.values() \
                    and data_path in [os.path.join(temp_dir_, f) for f in os.listdir(temp_dir_)]:
                os.remove(data_path)
                delattr(task, cmor_task.output_path_key)
    if not any(os.listdir(temp_dir_)):
        os.rmdir(temp_dir_)
        temp_dir_ = os.getcwd()
    else:
        log.warning("Skipped removal of nonempty work directory %s" % temp_dir_)


# Creates a sub-list of tasks that we believe we can successfully process
def filter_tasks(tasks):
    global log
    log.info("Inspecting %d tasks." % len(tasks))
    result = []
    for task in tasks:
        tgtdims = getattr(task.target, cmor_target.dims_key, []).split()
        haslat = "latitude" in tgtdims
        haslon = "longitude" in tgtdims
        if (haslat and haslon) or (not haslat and not haslon):
            result.append(task)
        else:
            # TODO: Support zonal variables
            log.error("Variable %s has unsupported combination of dimensions %s and will be skipped." % (
                task.target.variable, tgtdims))
    log.info("Validated %d tasks for processing." % len(result))
    return result


# Creates extra tasks for surface pressure
def get_sp_tasks(tasks):
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
            source = cmor_source.ifs_source(surface_pressure)
            surf_pressure_task = cmor_task.cmor_task(source, cmor_target.cmor_target("sp", freq))
            setattr(surf_pressure_task.target, cmor_target.freq_key, freq)
            setattr(surf_pressure_task.target, "time_operator", ["point"])
            find_sp_variable(surf_pressure_task)
            result.append(surf_pressure_task)
        for task3d in tasks3d:
            setattr(task3d, "sp_task", surf_pressure_task)
    return result


# Postprocessing of IFS tasks
def postprocess(tasks):
    global log, temp_dir_, max_size_, ifs_grid_descr_, surface_pressure
    log.info("Post-processing %d IFS tasks..." % len(tasks))
    tasks_done = postproc.post_process(tasks, temp_dir_, max_size_, ifs_grid_descr_)
    log.info("Post-processed batch of %d tasks." % len(tasks_done))
    return tasks_done


# Finds the surface pressure data source: gives priority to SH file.
def find_sp_variable(task):
    global ifs_gridpoint_files_, ifs_spectral_files_, surface_pressure, ln_surface_pressure, auto_filter_
    ifs_ps_source = cmor_source.ifs_source.create(134)
    setattr(ifs_ps_source, cmor_source.expression_key, "var134=exp(var152)")
    setattr(ifs_ps_source, "root_codes", [cmor_source.grib_code(134)])
    if auto_filter_:
        if grib_filter.spvar is None:
            log.error("Could not find surface pressure in model output...")
            return
        log.info("Found surface pressure in file %s" % grib_filter.spvar[2])
        setattr(task, cmor_task.filter_output_key, [grib_filter.spvar[2]])
        if grib_filter.spvar[0] == 152:
            task.source = ifs_ps_source
        task.source.grid_ = 1 if grib_filter.spvar[2] == ifs_spectral_files_ else 0
        return
    log.info("Looking for surface pressure variable in input files...")
    command = cdoapi.cdo_command()
    code_string = command.show_code(ifs_spectral_files_.values()[0])
    codes = [cmor_source.grib_code(int(c)) for c in code_string[0].split()]
    if surface_pressure in codes:
        log.info("Found surface pressure in spectral files")
        setattr(task, cmor_task.filter_output_key, ifs_spectral_files_.values())
        task.source.grid_ = 1
        return
    if ln_surface_pressure in codes:
        log.info("Found lnsp in spectral file")
        setattr(task, cmor_task.filter_output_key, ifs_spectral_files_.values())
        task.source = ifs_ps_source
        return
    log.info("Did not find sp or lnsp in spectral file: assuming gridpoint file contains sp")
    setattr(task, cmor_task.filter_output_key, ifs_gridpoint_files_.values())
    task.source.grid_ = 0


# Do the cmorization tasks
def cmorize(tasks, nthreads):
    global log, table_root_
    log.info("Cmorizing %d IFS tasks..." % len(tasks))
    if not any(tasks):
        return
    skip_status = [cmor_task.status_failed, cmor_task.status_cmorized, cmor_task.status_cmorizing]
    path = getattr([t for t in tasks if hasattr(t, "path")][0], "path")
    if nthreads < 1:
        log.error("Number of available threads %d for cmorization is non-positive: skipping cmor part" % nthreads)
        return
    if nthreads == 1:
        init_cmor(path)
        for task in tasks:
            if task.status not in skip_status:
                cmor_worker(task)
        return
    pool = multiprocessing.Pool(processes=nthreads, initializer=init_cmor, initargs=[path])
    pool.map(cmor_worker, [task for task in tasks if task.status not in skip_status])


grid_id = 0
time_axis_ids = {}
depth_axis_ids = {}


def init_cmor(filepath):
    global grid_id
    cmor.set_cur_dataset_attribute("calendar", "proleptic_gregorian")
    cmor.load_table(table_root_ + "_grids.json")
    if grid_id == 0:
        grid_id = create_grid_from_grib(filepath)


def define_cmor_axes(task):
    global grid_id
    tgtdims = getattr(task.target, cmor_target.dims_key).split()
    if "latitude" in tgtdims and "longitude" in tgtdims:
        setattr(task, "grid_id", grid_id)
    log.info("Loading CMOR table %s..." % task.target.table)
    try:
        tab_id = cmor.load_table("_".join([table_root_, task.target.table]) + ".json")
        cmor.set_table(tab_id)
    except Exception as e:
        log.error("CMOR failed to load table %s, the following variable will be skipped: %s. Reason: %s" % (
            task.target.table, task.target.variable, e.message))
        task.set_failed()
        return
    create_time_axes(task)
    if task.status == cmor_task.status_failed:
        return
    create_depth_axes(task)


# Worker function for parallel cmorization (not working at the present...)
def cmor_worker(task):
    log.info("Cmorizing source variable %s to target variable %s..." % (task.source.get_grib_code().var_id,
                                                                        task.target.variable))
    define_cmor_axes(task)
    if task.status == cmor_task.status_failed:
        return
    execute_netcdf_task(task)


# Executes a single task
def execute_netcdf_task(task):
    global log
    task.next_state()
    filepath = getattr(task, cmor_task.output_path_key, None)
    if not filepath:
        log.error(
            "Could not find file containing data for variable %s in table %s" % (task.target.variable,
                                                                                 task.target.table))
        return
    store_var = getattr(task, "store_with", None)
    surf_pressure_task = getattr(task, "sp_task", None)
    surf_pressure_path = getattr(surf_pressure_task, "path", None) if surf_pressure_task else None
    if store_var and not surf_pressure_path:
        log.error(
            "Could not find file containing surface pressure for model level variable...skipping variable %s in table "
            "%s" % (task.target.variable, task.target.table))
        return
    axes = []
    gid = getattr(task, "grid_id", 0)
    if gid != 0:
        axes.append(gid)
    if hasattr(task, "z_axis_id"):
        axes.append(getattr(task, "z_axis_id"))
    time_id = getattr(task, "t_axis_id", 0)
    if time_id != 0:
        axes.append(time_id)
    try:
        dataset = netCDF4.Dataset(filepath, 'r')
    except Exception as e:
        log.error("Could not read netcdf file %s while cmorizing variable %s in table %s. Cause: %s" % (
            filepath, task.target.variable, task.target.table, e.message))
        return
    try:
        ncvars = dataset.variables
        codestr = str(task.source.get_grib_code().var_id)
        varlist = [v for v in ncvars if str(getattr(ncvars[v], "code", None)) == codestr]
        if len(varlist) == 0:
            varlist = [v for v in ncvars if str(v) == "var" + codestr]
        if len(varlist) > 1:
            log.warning(
                "CDO variable retrieval resulted in multiple (%d) netcdf variables; will take first" % len(varlist))
        ncvar = ncvars[varlist[0]]
        unit = getattr(ncvar, "units", None)
        if (not unit) or hasattr(task, cmor_task.conversion_key):
            unit = getattr(task.target, "units")
        if len(getattr(task.target, "positive", "")) > 0:
            var_id = cmor.variable(table_entry=str(task.target.variable), units=str(unit), axis_ids=axes,
                                   positive="down")
        else:
            var_id = cmor.variable(table_entry=str(task.target.variable), units=str(unit), axis_ids=axes)
        flip_sign = (getattr(task.target, "positive", None) == "up")
        factor, term = get_conversion_constants(getattr(task, cmor_task.conversion_key, None),
                                                getattr(task, cmor_task.output_frequency_key))
        time_dim, index = -1, 0
        for d in ncvar.dimensions:
            if d.startswith("time"):
                time_dim = index
                break
            index += 1
        mask = getattr(task.target, cmor_target.mask_key, None)
        mask_array = masks[mask].get("array", None) if mask in masks else None
        missval = getattr(task.target, cmor_target.missval_key, 1.e+20)
        if flip_sign:
            missval = -missval
        cmor_utils.netcdf2cmor(var_id, ncvar, time_dim, factor, term, store_var, get_sp_var(surf_pressure_path),
                               swaplatlon=False, fliplat=True, mask=mask_array, missval=missval)
        cmor.close(var_id)
        task.next_state()
        if store_var:
            cmor.close(store_var)
    finally:
        dataset.close()


# Returns the constants A,B for unit conversions of type y = A*x + B
def get_conversion_constants(conversion, output_frequency):
    global log
    if not conversion:
        return 1.0, 0.0
    if conversion == "cum2inst":
        return 1.0 / (3600 * output_frequency), 0.0
    if conversion == "inst2cum":
        return 3600 * output_frequency, 0.0
    if conversion == "pot2alt":
        return 1.0 / 9.81, 0.0
    if conversion == "alt2pot":
        return 9.81, 0.0
    if conversion == "vol2flux":
        return 1000.0 / (3600 * output_frequency), 0.0
    if conversion == "vol2massl":
        return 1000.0, 0.0
    if conversion == "frac2percent":
        return 100.0, 0.0
    if conversion == "percent2frac":
        return 0.01, 0.0
    if conversion == "K2degC":
        return 1.0, -273.15
    if conversion == "degC2K":
        return 1.0, 273.15
    log.error("Unknown explicit unit conversion: %s" % conversion)
    return 1.0, 0.0


# Creates time axes in cmor and attach the id's as attributes to the tasks
def create_time_axes(task):
    global log, time_axis_ids
    tgtdims = getattr(task.target, cmor_target.dims_key)
    # TODO: better to check in the table axes if the standard name of the dimension equals "time"
    time_dims = [d for d in list(set(tgtdims.split())) if d.startswith("time")]
    if not any(time_dims):
        return
    if len(time_dims) > 1:
        log.error("Skipping variable %s in table %s with dimensions %s with multiple time dimensions." % (
            task.target.variable, task.target.table, tgtdims))
        task.set_failed()
        return
    time_dim = str(time_dims[0])
    key = (task.target.table, time_dim)
    if key in time_axis_ids:
        tid = time_axis_ids[key]
    else:
        time_operator = getattr(task.target, "time_operator", ["point"])
        log.info("Creating time axis using variable %s..." % task.target.variable)
        tid = create_time_axis(freq=task.target.frequency, path=getattr(task, cmor_task.output_path_key),
                               name=time_dim, has_bounds=(time_operator != ["point"]))
        time_axis_ids[key] = tid
    setattr(task, "t_axis_id", tid)


# Creates depth axes in cmor and attach the id's as attributes to the tasks
def create_depth_axes(task):
    global log, depth_axis_ids
    tgtdims = getattr(task.target, cmor_target.dims_key)
    z_dims = getattr(task.target, "z_dims", [])
    if not any(z_dims):
        return
    if len(z_dims) > 1:
        log.error("Skipping variable %s in table %s with dimensions %s with multiple z-directions." % (
            task.target.variable, task.target.table, tgtdims))
        task.set_failed()
        return
    z_dim = str(z_dims[0])
    key = (task.target.table, z_dim)
    if key in depth_axis_ids:
        if z_dim == "alevel":
            setattr(task, "z_axis_id", depth_axis_ids[key][0])
            setattr(task, "store_with", depth_axis_ids[key][1])
        else:
            setattr(task, "z_axis_id", depth_axis_ids[key])
        return
    elif z_dim == "alevel":
        log.info("Creating model level axis using variable %s..." % task.target.variable)
        axisid, psid = create_hybrid_level_axis(task)
        depth_axis_ids[key] = (axisid, psid)
        setattr(task, "z_axis_id", axisid)
        setattr(task, "store_with", psid)
        return
    elif z_dim == "sdepth":
        log.info("Creating soil depth axis using variable %s..." % task.target.variable)
        axisid = create_soil_depth_axis(z_dim, getattr(task, cmor_task.output_path_key))
        depth_axis_ids[key] = axisid
        setattr(task, "z_axis_id", axisid)
    elif z_dim in cmor_target.get_axis_info(task.target.table):
        axis = cmor_target.get_axis_info(task.target.table)[z_dim]
        levels = axis.get("requested", [])
        if levels == "":
            levels = []
        value = axis.get("value", None)
        if value:
            levels.append(value)
        unit = axis.get("units", None)
        if len(levels) == 0:
            log.warning("Skipping axis %s in table %s with no levels" % (z_dim, task.target.table))
            return
        else:
            values = [float(l) for l in levels]
            if axis.get("must_have_bounds", "no") == "yes":
                bounds_list, n = axis.get("requested_bounds", []), len(values)
                if not bounds_list:
                    bounds_list = [float(x) for x in axis.get("bounds_values", []).split()]
                if len(bounds_list) == 2 * n:
                    bounds_array = numpy.empty([n, 2])
                    for i in range(n):
                        bounds_array[i, 0], bounds_array[i, 1] = bounds_list[2 * i], bounds_list[2 * i + 1]
                    axisid = cmor.axis(table_entry=str(z_dim), coord_vals=values, units=unit,
                                       cell_bounds=bounds_array)
                else:
                    log.error("Failed to retrieve bounds for vertical axis %s" % str(z_dim))
                    axisid = cmor.axis(table_entry=str(z_dim), coord_vals=values, units=unit)
            else:
                axisid = cmor.axis(table_entry=str(z_dim), coord_vals=values, units=unit)
            depth_axis_ids[key] = axisid
            setattr(task, "z_axis_id", axisid)
    else:
        log.error("Vertical dimension %s for variable %s not found in header of table %s" % (
            z_dim, task.target.variable, task.target.table))


# Creates the hybrid model vertical axis in cmor.
def create_hybrid_level_axis(task):
    pref = 80000  # TODO: Move reference pressure level to model config
    path = getattr(task, cmor_task.output_path_key)
    ds = None
    try:
        ds = netCDF4.Dataset(path)
        am = ds.variables["hyam"]
        aunit = getattr(am, "units")
        bm = ds.variables["hybm"]
        bunit = getattr(bm, "units")
        hcm = am[:] / pref + bm[:]
        n = hcm.shape[0]
        ai = ds.variables["hyai"]
        abnds = numpy.empty([n, 2])
        abnds[:, 0] = ai[0:n]
        abnds[:, 1] = ai[1:n + 1]
        bi = ds.variables["hybi"]
        bbnds = numpy.empty([n, 2])
        bbnds[:, 0] = bi[0:n]
        bbnds[:, 1] = bi[1:n + 1]
        hcbnds = abnds / pref + bbnds
        axisid = cmor.axis(table_entry="alternate_hybrid_sigma", coord_vals=hcm, cell_bounds=hcbnds, units="1")
        cmor.zfactor(zaxis_id=axisid, zfactor_name="ap", units=str(aunit), axis_ids=[axisid], zfactor_values=am[:],
                     zfactor_bounds=abnds)
        cmor.zfactor(zaxis_id=axisid, zfactor_name="b", units=str(bunit), axis_ids=[axisid], zfactor_values=bm[:],
                     zfactor_bounds=bbnds)
        storewith = cmor.zfactor(zaxis_id=axisid, zfactor_name="ps",
                                 axis_ids=[grid_id, getattr(task, "t_axis_id")], units="Pa")
        return axisid, storewith
    finally:
        if ds is not None:
            ds.close()


# Creates a soil depth axis.
def create_soil_depth_axis(name, filepath):
    global log
    # New version of cdo fails to pass soil depths correctly:
    bndcm = numpy.array([0, 7, 28, 100, 289])
    values = 0.5 * (bndcm[:4] + bndcm[1:])
    bounds = numpy.transpose(numpy.stack([bndcm[:4], bndcm[1:]]))
    return cmor.axis(table_entry=name, coord_vals=values, cell_bounds=bounds, units="cm")
    # dataset = None
    # try:
    #     dataset = netCDF4.Dataset(filepath, 'r')
    #     ncvar = dataset.variables.get("depth", None)
    #     if not ncvar:
    #         log.error("Could retrieve depth coordinate from file %s" % filepath)
    #         return 0
    #     units = getattr(ncvar, "units", "cm")
    #     if units == "mm":
    #         factor = 0.001
    #     elif units == "cm":
    #         factor = 0.01
    #     elif units == "m":
    #         factor = 1
    #     else:
    #         log.error("Unknown units for depth axis in file %s" % filepath)
    #         return 0
    #     values = factor * ncvar[:]
    #     ncvar = dataset.variables.get("depth_bnds", None)
    #     if not ncvar:
    #         n = len(values)
    #         bounds = numpy.empty([n, 2])
    #         bounds[0, 0] = 0.
    #         if n > 1:
    #             bounds[1:, 0] = (values[0:n - 1] + values[1:]) / 2
    #             bounds[0:n - 1, 1] = bounds[1:n, 0]
    #             bounds[n - 1, 1] = (3 * values[n - 1] - bounds[n - 1, 0]) / 2
    #         else:
    #             bounds[0, 1] = 2 * values[0]
    #     else:
    #         bounds = factor * ncvar[:, :]
    #     return cmor.axis(table_entry=name, coord_vals=values, cell_bounds=bounds, units="m")
    # except Exception as e:
    #     log.error("Could not read netcdf file %s while creating soil depth axis, reason: %s" % (filepath, e.message))
    # finally:
    #     if dataset is not None:
    #         dataset.close()
    # return 0


# Makes a time axis for the given table
def create_time_axis(freq, path, name, has_bounds):
    global log, start_date_, ref_date_
    command = cdo.Cdo()
    times = command.showtimestamp(input=path)[0].split()
    datetimes = sorted(set(map(lambda s: datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S"), times)))
    if len(datetimes) == 0:
        log.error("Empty time step list encountered at time axis creation for files %s" % str(path))
        return
    refdate = cmor_utils.make_datetime(ref_date_)
    if has_bounds:
        n = len(datetimes)
        bounds = numpy.empty([n, 2])
        rounded_times = map(lambda time: (cmor_utils.get_rounded_time(freq, time) - refdate).total_seconds() / 3600.,
                            datetimes)
        bounds[:, 0] = rounded_times[:]
        bounds[0:n - 1, 1] = rounded_times[1:n]
        bounds[n - 1, 1] = (cmor_utils.get_rounded_time(freq, datetimes[n - 1], 1) - refdate).total_seconds() / 3600.
        times[:] = bounds[:, 0] + (bounds[:, 1] - bounds[:, 0]) / 2
        return cmor.axis(table_entry=str(name), units="hours since " + str(ref_date_), coord_vals=times,
                         cell_bounds=bounds)
    times = numpy.array([(d - refdate).total_seconds() / 3600 for d in datetimes])
    return cmor.axis(table_entry=str(name), units="hours since " + str(ref_date_), coord_vals=times)


# Surface pressure variable lookup utility
def get_sp_var(ncpath):
    if not ncpath:
        return None
    if not os.path.exists(ncpath):
        return None
    try:
        ds = netCDF4.Dataset(ncpath)
        if "var134" in ds.variables:
            return ds.variables["var134"]
        for v in ds.variables:
            if getattr(v, "code", 0) == 134:
                return v
        return None
    except Exception as e:
        log.error("Could not read netcdf file %s for surface pressure, reason: %s" % (ncpath, e.message))
        return None


# Retrieves all IFS output files in the input directory.
def select_files(path, expname, start, length):
    allfiles = cmor_utils.find_ifs_output(path, expname)
    start_date = cmor_utils.make_datetime(start).date()
    end_date = cmor_utils.make_datetime(start + length).date()
    return [f for f in allfiles if f.endswith(expname + "+000000") or
            (end_date > cmor_utils.get_ifs_date(f) >= start_date)]


# Creates the regular gaussian grids from the postprocessed file argument.
def create_grid_from_grib(filepath):
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


# Creates the regular gaussian grid from its arguments.
def create_gauss_grid(nx, x0, yvals):
    ny = len(yvals)
    i_index_id = cmor.axis(table_entry="i_index", units="1", coord_vals=numpy.array(range(1, nx + 1)))
    j_index_id = cmor.axis(table_entry="j_index", units="1", coord_vals=numpy.array(range(1, ny + 1)))
    dx = 360. / nx
    x_vals = numpy.array([x0 + (i + 0.5) * dx for i in range(nx)])
    lon_arr = numpy.tile(x_vals, (ny, 1))
    lat_arr = numpy.tile(yvals[::-1], (nx, 1)).transpose()
    lon_mids = numpy.array([x0 + i * dx for i in range(nx + 1)])
    lat_mids = numpy.empty([ny + 1])
    lat_mids[0] = 90.
    lat_mids[1:ny] = 0.5 * (yvals[0:ny - 1] + yvals[1:ny])
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
    return cmor.grid(axis_ids=[j_index_id, i_index_id], latitude=lat_arr, longitude=lon_arr,
                     latitude_vertices=vert_lats, longitude_vertices=vert_lons)
