import cmor
import logging
import netCDF4
import numpy
import os

import cmor_target
import cmor_task
import cmor_utils

# Logger object
log = logging.getLogger(__name__)

extra_axes = {"basin": {"ncdim": "3basin",
                        "ncvals": ["global_ocean", "atlantic_arctic_ocean", "indian_pacific_ocean"]},
              "typesi": {"ncdim": "ncatice"},
              "iceband": {"ncdim": "ncatice",
                          "ncunits": "m",
                          "ncvals": [0.277, 0.7915, 1.635, 2.906, 3.671],
                          "ncbnds": [0., 0.454, 1.129, 2.141, 3.671, 99.0]}}

# Experiment name
exp_name_ = None

# Reference date
ref_date_ = None

# Table root
table_root_ = None

# Files that are being processed in the current execution loop.
nemo_files_ = []

# Dictionary of NEMO grid type with cmor grid id.
grid_ids_ = {}

# List of depth axis ids with cmor grid id.
depth_axes_ = {}

# Dictionary of output frequencies with cmor time axis id.
time_axes_ = {}

# Dictionary of sea-ice output types, 1 by default...
type_axes_ = {}


# Initializes the processing loop.
def initialize(path, expname, tableroot, refdate):
    global log, nemo_files_, exp_name_, table_root_, ref_date_
    exp_name_ = expname
    table_root_ = tableroot
    ref_date_ = refdate
    nemo_files_ = cmor_utils.find_nemo_output(path, expname)
    cal = None
    for f in nemo_files_:
        cal = read_calendar(f)
        if cal:
            break
    if cal:
        cmor.set_cur_dataset_attribute("calendar", cal)
    return True


# Resets the module globals.
def finalize():
    global nemo_files_, grid_ids_, depth_axes_, time_axes_
    nemo_files_ = []
    grid_ids_ = {}
    depth_axes_ = {}
    time_axes_ = {}


# Executes the processing loop.
def execute(tasks):
    global log, time_axes_, depth_axes_, table_root_
    log.info("Looking up variables in files...")
    tasks = lookup_variables(tasks)
    log.info("Creating NEMO grids in CMOR...")
    create_grids(tasks)
    log.info("Executing %d NEMO tasks..." % len(tasks))
    log.info("Cmorizing NEMO tasks...")
    task_groups = cmor_utils.group(tasks, lambda tsk: getattr(tsk, cmor_task.output_path_key, None))
    for filename, task_group in task_groups.iteritems():
        dataset = netCDF4.Dataset(filename, 'r')
        task_sub_groups = cmor_utils.group(task_group, lambda tsk: tsk.target.table)
        for table, task_list in task_sub_groups.iteritems():
            try:
                tab_id = cmor.load_table("_".join([table_root_, table]) + ".json")
                cmor.set_table(tab_id)
            except Exception as e:
                log.error("CMOR failed to load table %s, skipping variables %s. Reason: %s"
                          % (table, ','.join([tsk.target.variable for tsk in task_list]), e.message))
                continue
            if table not in time_axes_:
                log.info("Creating time axes for table %s from data in %s..." % (table, filename))
            create_time_axes(dataset, task_list, table)
            if table not in depth_axes_:
                log.info("Creating depth axes for table %s from data in %s ..." % (table, filename))
            create_depth_axes(dataset, task_list, table)
            if table not in type_axes_:
                log.info("Creating extra axes for table %s from data in %s ..." % (table, filename))
            create_type_axes(dataset, task_list, table)
            for task in task_list:
                execute_netcdf_task(dataset, task)
        dataset.close()


def lookup_variables(tasks):
    valid_tasks = []
    for task in tasks:
        file_candidates = select_freq_files(task.target.frequency)
        results = []
        for ncfile in file_candidates:
            ds = netCDF4.Dataset(ncfile)
            if task.source.variable() in ds.variables:
                results.append(ncfile)
            ds.close()
        if len(results) == 0:
            log.error("Variable %s needed for %s in table %s was not found in NEMO output files... skipping task" %
                      (task.source.variable(), task.target.variable, task.target.table))
            task.set_failed()
            continue
        if len(results) > 1:
            log.warning("Variable %s needed for %s in table %s was found in multiple NEMO output files %s... choosing "
                        "the first match %s " % (task.source.variable(), task.target.table, task.target.variable,
                                                 task.target.table, ','.join(results)))
        setattr(task, cmor_task.output_path_key, results[0])
        valid_tasks.append(task)
    return valid_tasks


# Performs a single task.
def execute_netcdf_task(dataset, task):
    global log, grid_ids_, depth_axes_, time_axes_
    task.status = cmor_task.status_cmorizing
    grid_axes = [] if not hasattr(task, "grid_id") else [getattr(task, "grid_id")]
    z_axes = getattr(task, "z_axes", [])
    t_axes = [] if not hasattr(task, "time_axis") else [getattr(task, "time_axis")]
    type_axes = [getattr(task, dim + "_axis") for dim in type_axes_.get(task.target.table, {}).keys() if
                 hasattr(task, dim + "_axis")]
    #TODO: Read axes order from netcdf file!
    axes = grid_axes + z_axes + type_axes + t_axes
    varid = create_cmor_variable(task, dataset, axes)
    ncvar = dataset.variables[task.source.variable()]
    missval = getattr(ncvar, "missing_value", getattr(ncvar, "_FillValue", numpy.nan))
    time_dim, index, time_sel = -1, 0, None
    for d in ncvar.dimensions:
        if d.startswith("time"):
            time_dim = index
            break
        index += 1
    time_sel = None
    if len(t_axes) > 0 > time_dim:
        for d in dataset.dimensions:
            if d.startswith("time"):
                time_sel = range(len(d)) # ensure copying of constant fields
                break
    if len(grid_axes) == 0:  # Fix for global averages/sums
        vals = numpy.ma.masked_equal(ncvar[...], missval)
        ncvar = numpy.mean(vals, axis=(1, 2))
    factor, term = get_conversion_constants(getattr(task, cmor_task.conversion_key, None))
    log.info("CMORizing variable %s in table %s from %s in "
             "file %s..." % (task.target.variable, task.target.table, task.source.variable(),
                             getattr(task, cmor_task.output_path_key)))
    cmor_utils.netcdf2cmor(varid, ncvar, time_dim, factor, term,
                           missval=getattr(task.target, cmor_target.missval_key, missval),
                           time_selection=time_sel)
    closed_file = cmor.close(varid, file_name=True)
    log.info("CMOR closed file %s" % closed_file)
    task.status = cmor_task.status_cmorized


# Returns the constants A,B for unit conversions of type y = A*x + B
def get_conversion_constants(conversion):
    global log
    if not conversion:
        return 1.0, 0.0
    if conversion == "tossqfix":
        return 1.0, 0.0
    if conversion == "frac2percent":
        return 100.0, 0.0
    if conversion == "percent2frac":
        return 0.01, 0.0
    if conversion == "K2degC":
        return 1.0, -273.15
    if conversion == "degC2K":
        return 1.0, 273.15
    if conversion == "sv2kgps":
        return 1.e+9, 0.
    log.error("Unknown explicit unit conversion %s will be ignored" % conversion)
    return 1.0, 0.0


# Creates a variable in the cmor package
def create_cmor_variable(task, dataset, axes):
    srcvar = task.source.variable()
    ncvar = dataset.variables[srcvar]
    unit = getattr(ncvar, "units", None)
    if (not unit) or hasattr(task, cmor_task.conversion_key):  # Explicit unit conversion
        unit = getattr(task.target, "units")
    if hasattr(task.target, "positive") and len(task.target.positive) != 0:
        return cmor.variable(table_entry=str(task.target.variable), units=str(unit), axis_ids=axes,
                             original_name=str(srcvar), positive=getattr(task.target, "positive"))
    else:
        return cmor.variable(table_entry=str(task.target.variable), units=str(unit), axis_ids=axes,
                             original_name=str(srcvar))


# Creates all depth axes for the given table from the given files
def create_depth_axes(ds, tasks, table):
    global depth_axes_
    if table not in depth_axes_:
        depth_axes_[table] = {}
    table_depth_axes = depth_axes_[table]
    other_nc_axes = ["time_counter", "x", "y"] + [extra_axes[k]["ncdim"] for k in extra_axes.keys()]
    for task in tasks:
        z_axes = [d for d in ds.variables[task.source.variable()].dimensions if d not in other_nc_axes]
        z_axis_ids = []
        for z_axis in z_axes:
            if z_axis in table_depth_axes:
                z_axis_ids.append(table_depth_axes[z_axis])
            else:
                depth_coordinates = ds.variables[z_axis]
                depth_bounds = ds.variables[getattr(depth_coordinates, "bounds", None)]
                if depth_bounds is None:
                    log.warning("No depth bounds found in file %s, taking midpoints" % (ds.filepath()))
                    depth_bounds = numpy.zeros((len(depth_coordinates[:]), 2), dtype=numpy.float64)
                    depth_bounds[1:, 0] = 0.5 * (depth_coordinates[0:-1] + depth_coordinates[1:])
                    depth_bounds[0:-1, 1] = depth_bounds[1:, 0]
                    depth_bounds[0, 0] = depth_coordinates[0]
                    depth_bounds[-1, 1] = depth_coordinates[-1]
                units = getattr(depth_coordinates, "units", "1")
                b = depth_bounds[:, :]
                b[b < 0] = 0
                z_axis_id = cmor.axis(table_entry="depth_coord", units=units, coord_vals=depth_coordinates[:],
                                      cell_bounds=b)
                z_axis_ids.append(z_axis_id)
                table_depth_axes[z_axis] = z_axis_id
        setattr(task, "z_axes", z_axis_ids)


# Creates a time axis for the currently loaded table
def create_time_axes(ds, tasks, table):
    global time_axes_
    if table not in time_axes_:
        time_axes_[table] = {}
    table_time_axes = time_axes_[table]
    times, time_bounds, time_units = None, None, None
    for varname, ncvar in ds.variables.items():
        if getattr(ncvar, "standard_name", None) == "time" or varname == "time_counter":
            time_bnds = ds.variables.get(getattr(ncvar, "bounds", None), None)
            if time_bnds is None:
                time_bnds = numpy.empty([len(ncvar[:]), 2])
                time_bnds[1:, 0] = 0.5 * (ncvar[0:-1] + ncvar[1:])
                time_bnds[:-1, 1] = time_bnds[1:, 0]
                time_bnds[0, 0] = 1.5 * ncvar[0] - 0.5 * ncvar[1]
                time_bnds[-1, 1] = 1.5 * ncvar[-1] - 0.5 * ncvar[-2]
            dt_array = netCDF4.num2date(ncvar[:], units=getattr(ncvar, "units", None),
                                        calendar=getattr(ds, "calendar", "gregorian"))
            times, time_units = cmor_utils.date2num(dt_array, ref_date_)
            dtb_array = netCDF4.num2date(time_bnds[:, :], units=getattr(ncvar, "units", None),
                                         calendar=getattr(ds, "calendar", "gregorian"))
            time_bounds, time_bounds_units = cmor_utils.date2num(dtb_array, ref_date_)
            break
    for task in tasks:
        tgtdims = getattr(task.target, cmor_target.dims_key)
        for time_dim in [d for d in list(set(tgtdims.split())) if d.startswith("time")]:
            if time_dim in table_time_axes:
                tid = table_time_axes[time_dim]
            else:
                if times is None:
                    log.error("Failed to read time axis information from file %s, skipping variable %s in table %s" %
                              (ds.filepath(), task.target.variable, task.target.table))
                    task.set_failed()
                    continue
                time_operator = getattr(task.target, "time_operator", ["point"])
                if time_operator == ["point"]:
                    tid = cmor.axis(table_entry=str(time_dim), units=time_units, coord_vals=times)
                else:
                    tid = cmor.axis(table_entry=str(time_dim), units=time_units, coord_vals=times,
                                    cell_bounds=time_bounds)
                table_time_axes[time_dim] = tid
            setattr(task, "time_axis", tid)
    return table_time_axes


def create_type_axes(ds, tasks, table):
    global type_axes_
    if table not in type_axes_:
        type_axes_[table] = {}
    table_type_axes = type_axes_[table]
    for task in tasks:
        tgtdims = set(getattr(task.target, cmor_target.dims_key).split()).intersection(extra_axes.keys())
        for dim in tgtdims:
            if dim in table_type_axes:
                axis_id = table_type_axes[dim]
            else:
                axisinfo = extra_axes[dim]
                nc_dim_name = axisinfo["ncdim"]
                if nc_dim_name in ds.dimensions:
                    ncdim, ncvals = ds.dimensions[nc_dim_name], axisinfo.get("ncvals", [])
                    if len(ncdim) == len(ncvals):
                        axis_values, axis_unit = ncvals, axisinfo.get("ncunits", "1")
                    else:
                        if any(ncvals):
                            log.error("Ece2cmor values for extra axis %s, %s, do not match dimension %s length %d found"
                                      " in file %s, taking values found in file" % (dim, str(ncvals), nc_dim_name,
                                                                                   len(ncdim), ds.filepath()))
                        ncvars = [v for v in ds.variables if list(ds.variables[v].dimensions) == [ncdim]]
                        axis_values, axis_unit = list(range(len(ncdim))), "1"
                        if any(ncvars):
                            if len(ncvars) > 1:
                                log.warning("Multiple axis variables found for dimension %s in file %s, choosing %s" %
                                            (nc_dim_name, ds.filepath(), ncvars[0]))
                            axis_values, axis_unit = list(ncvars[0][:]), getattr(ncvars[0], "units", None)
                else:
                    log.error("Dimension %s could not be found in file %s, inserting using length-one dimension "
                              "instead" % (nc_dim_name, ds.filepath()))
                    axis_values, axis_unit = [1], "1"
                if "ncbnds" in axisinfo:
                    bndlist = axisinfo["ncbnds"]
                    if len(bndlist) - 1 != len(axis_values):
                        log.error("Length of axis bounds %d does not correspond to axis coordinates %s" %
                                  (len(bndlist) - 1, str(axis_values)))
                    bnds = numpy.zeros((len(axis_values), 2))
                    bnds[:, 0] = bndlist[:-1]
                    bnds[:, 1] = bndlist[1:]
                    axis_id = cmor.axis(table_entry=dim, coord_vals=axis_values, units=axis_unit, cell_bounds=bnds)
                else:
                    axis_id = cmor.axis(table_entry=dim, coord_vals=axis_values, units=axis_unit)
                table_type_axes[dim] = axis_id
            setattr(task, dim + "_axis", axis_id)
    return table_type_axes


# Selects files with data with the given frequency
def select_freq_files(freq):
    global exp_name_, nemo_files_
    nemo_freq = None
    if freq == "monClim":
        nemo_freq = "1m"
    elif freq.endswith("mon"):
        n = 1 if freq == "mon" else int(freq[:-3])
        nemo_freq = str(n) + "m"
    elif freq.endswith("day"):
        n = 1 if freq == "day" else int(freq[:-3])
        nemo_freq = str(n) + "d"
    elif freq.endswith("hr"):
        n = 1 if freq == "hr" else int(freq[:-2])
        nemo_freq = str(n) + "h"
    return [f for f in nemo_files_ if cmor_utils.get_nemo_frequency(f, exp_name_) == nemo_freq]


# Reads the calendar attribute from the time dimension.
def read_calendar(ncfile):
    ds = None
    try:
        ds = netCDF4.Dataset(ncfile, 'r')
        if not ds:
            return None
        timvar = ds.variables["time_centered"]
        if timvar:
            result = getattr(timvar, "calendar")
            return result
        else:
            return None
    finally:
        if ds is not None:
            ds.close()


# Reads all the NEMO grid data from the input files.
def create_grids(tasks):
    global grid_ids_
    task_groups = cmor_utils.group(tasks, lambda t: getattr(t, cmor_task.output_path_key, None))
    for filename, task_list in task_groups.iteritems():
        if filename is not None:
            grid = read_grid(filename)
            if grid is not None:
                grid_id = write_grid(grid, task_list[0])
                if grid_id != 0:
                    grid_ids_[grid.name] = grid_id
                    for task in task_list:
                        setattr(task, "grid_id", grid_id)


# Reads a particular NEMO grid from the given input file.
def read_grid(ncfile):
    ds = None
    try:
        ds = netCDF4.Dataset(ncfile, 'r')
        name = getattr(ds.variables["nav_lon"], "nav_model", cmor_utils.get_nemo_grid(ncfile, exp_name_))
        if name == "scalar":
            return None
        lons = ds.variables["nav_lon"][:, :] if "nav_lon" in ds.variables else []
        lats = ds.variables["nav_lat"][:, :] if "nav_lat" in ds.variables else []
        if len(lons) == 0 and len(lats) == 0:
            return None
        return nemo_grid(name, lons, lats)
    finally:
        if ds is not None:
            ds.close()


# Transfers the grid to cmor.
def write_grid(grid, task):
    nx = grid.lons.shape[0]
    ny = grid.lons.shape[1]
    if ny == 1:
        if nx == 1:
            return 0
        cmor.load_table(table_root_ + "_" + task.target.table + ".json")
        return cmor.axis(table_entry="gridlatitude", coord_vals=grid.lats[:, 0], units="degrees_north",
                         cell_bounds=grid.vertex_lats)
    cmor.load_table(table_root_ + "_grids.json")
    i_index_id = cmor.axis(table_entry="j_index", units="1", coord_vals=numpy.array(range(1, nx + 1)))
    j_index_id = cmor.axis(table_entry="i_index", units="1", coord_vals=numpy.array(range(1, ny + 1)))
    return cmor.grid(axis_ids=[i_index_id, j_index_id],
                     latitude=grid.lats,
                     longitude=grid.lons,
                     latitude_vertices=grid.vertex_lats,
                     longitude_vertices=grid.vertex_lons)


# Class holding a NEMO grid, including bounds arrays
class nemo_grid(object):

    def __init__(self, name_, lons_, lats_):
        self.name = name_
        flon = numpy.vectorize(lambda x: x % 360)
        flat = numpy.vectorize(lambda x: (x + 90) % 180 - 90)
        self.lons = flon(nemo_grid.smoothen(lons_))
        input_lats = lats_
        # Dirty hack for lost precision in zonal grids:
        if input_lats.shape[1] == 1:
            if input_lats.shape[0] > 2 and input_lats[-1, 0] == input_lats[-2, 0]:
                input_lats[-1, 0] = input_lats[-1, 0] + (input_lats[-2, 0] - input_lats[-3, 0])
        self.lats = flat(input_lats)
        self.vertex_lons = nemo_grid.create_vertex_lons(lons_)
        self.vertex_lats = nemo_grid.create_vertex_lats(input_lats)

    @staticmethod
    def create_vertex_lons(a):
        ny = a.shape[0]
        nx = a.shape[1]
        f = numpy.vectorize(lambda x: x % 360)
        if nx == 1:  # Longitudes were integrated out
            if ny == 1:
                return f(numpy.array([a[0, 0]]))
            return numpy.zeros([ny, 2])
        b = numpy.zeros([ny, nx, 4])
        b[:, 1:nx, 0] = f(0.5 * (a[:, 0:nx - 1] + a[:, 1:nx]))
        b[:, 0, 0] = f(1.5 * a[:, 0] - 0.5 * a[:, 1])
        b[:, 0:nx - 1, 1] = b[:, 1:nx, 0]
        b[:, nx - 1, 1] = f(1.5 * a[:, nx - 1] - 0.5 * a[:, nx - 2])
        b[:, :, 2] = b[:, :, 1]
        b[:, :, 3] = b[:, :, 0]
        return b

    @staticmethod
    def create_vertex_lats(a):
        ny = a.shape[0]
        nx = a.shape[1]
        f = numpy.vectorize(lambda x: (x + 90) % 180 - 90)
        if nx == 1:  # Longitudes were integrated out
            if ny == 1:
                return f(numpy.array([a[0, 0]]))
            b = numpy.zeros([ny, 2])
            b[1:ny, 0] = f(0.5 * (a[0:ny - 1, 0] + a[1:ny, 0]))
            b[0, 0] = f(2 * a[0, 0] - b[1, 0])
            b[0:ny - 1, 1] = b[1:ny, 0]
            b[ny - 1, 1] = f(1.5 * a[ny - 1, 0] - 0.5 * a[ny - 2, 0])
            return b
        b = numpy.zeros([ny, nx, 4])
        b[1:ny, :, 0] = f(0.5 * (a[0:ny - 1, :] + a[1:ny, :]))
        b[0, :, 0] = f(2 * a[0, :] - b[1, :, 0])
        b[:, :, 1] = b[:, :, 0]
        b[0:ny - 1, :, 2] = b[1:ny, :, 0]
        b[ny - 1, :, 2] = f(1.5 * a[ny - 1, :] - 0.5 * a[ny - 2, :])
        b[:, :, 3] = b[:, :, 2]
        return b

    @staticmethod
    def modlon2(x, a):
        if x < a:
            return x + 360.0
        else:
            return x

    @staticmethod
    def smoothen(a):
        nx = a.shape[0]
        ny = a.shape[1]
        if ny == 1:
            return a
        mod = numpy.vectorize(nemo_grid.modlon2)
        b = numpy.empty([nx, ny])
        for i in range(0, nx):
            x = a[i, 1]
            b[i, 0] = a[i, 0]
            b[i, 1] = x
            b[i, 2:] = mod(a[i, 2:], x)
        return b
