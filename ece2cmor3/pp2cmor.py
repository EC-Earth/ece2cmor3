import logging
import numpy
import cmor
from ece2cmor3 import ppop, cmor_target, pplevels, ppmsg

# Logger construction
log = logging.getLogger(__name__)

# Dictionary of grids, keys are horizontal sizes of incoming variables
grid_ids = {}

# Dictionary of time axes, keys are target variable frequencies
time_axis_ids = {}

# Dictionary of vertical axes, keys are target vertical dimension names
z_axis_ids = {}

# Dictionary of variable id's, keys are pairs of cmor variable name and table
var_ids = {}

ref_date = None
time_unit = "hour"


# Creates a variable for the given task, and creates grid, time and z axes if necessary
def create_cmor_variable(task, msg, store_var=None):
    global grid_ids, time_axis_ids, z_axis_ids, var_ids
    shape = msg.get_values().shape
    hor_size = (shape[:-2], shape[:-1])
    if hor_size in grid_ids:
        grid_id = grid_ids[shape]
    else:
        grid_id = create_gauss_grid(hor_size[0], hor_size[1])
        grid_ids[shape] = grid_id
    freq = getattr(task.target, cmor_target.freq_key, None)
    time_axis_id = 0
    if freq in time_axis_ids:
        time_axis_id = time_axis_ids[freq]
    elif freq is not None:
        time_axis_id = create_time_axis(task, msg)
        if time_axis_id != 0:
            time_axis_ids[freq] = time_axis_id
    z_axis, levels = cmor_target.get_z_axis(task.target)
    z_axis_id = 0
    if z_axis in z_axis_ids:
        z_axis_id = z_axis_ids[z_axis]
    elif z_axis:
        z_axis_id = create_z_axis(z_axis, levels)
        z_axis_ids[z_axis] = z_axis_ids
    axes = [time_axis_id, grid_id, z_axis_id]
    axes.remove(0)
    var_id = cmor.variable(table_entry=str(task.target.variable), units=getattr(task.target, "units", None),
                           axis_ids=axes, positive="down")
    if store_var:
        store_var_id = cmor.zfactor(zaxis_id=z_axis_id, zfactor_name=store_var,
                                    axis_ids=[time_axis_id, grid_id], units="Pa")
        return var_id, store_var_id
    else:
        return var_id


# Creates the regular gaussian grid from its arguments.
def create_gauss_grid(nx, ny):
    i_index_id = cmor.axis(table_entry="i_index", units="1", coord_vals=numpy.array(range(1, nx + 1)))
    j_index_id = cmor.axis(table_entry="j_index", units="1", coord_vals=numpy.array(range(1, ny + 1)))
    x0, y0 = -180., -90.
    dx, dy = 360. / nx, 180. / ny
    x_vals = numpy.array([x0 + (i + 0.5) * dx for i in range(nx)])
    y_vals = numpy.array([y0 + (i + 0.5) * dy for i in range(ny)])
    lon_arr = numpy.tile(x_vals, (ny, 1))
    lat_arr = numpy.tile(y_vals, (nx, 1)).transpose()
    lon_mids = numpy.array([x0 + i * dx for i in range(nx + 1)])
    lat_mids = numpy.empty([y0 + i * dy for i in range(ny + 1)])
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


# Creates a time axis in the cmor library for this task
def create_time_axis(task, msg):
    target_dims = getattr(task.target, cmor_target.dims_key)
    time_dims = [d for d in list(set(target_dims.split())) if d.startswith("time")]
    if any(time_dims):
        refdate = msg.get_timestamp() if ref_date is None else ref_date
        return cmor.axis(table_entry=str(time_dims[0]), units=time_unit + "s since " + str(refdate))
    else:
        return 0


# Creates a vertical coordinate axis in the cmor library
def create_z_axis(z_axis, levels, table):
    if z_axis == "alevel":
        return create_hybrid_level_axis("alternate_hybrid_sigma")
    if z_axis == "sdepth":
        return create_soil_depth_axis(z_axis)
    if z_axis in cmor_target.get_axis_info(table):
        axis = cmor_target.get_axis_info(table)[z_axis]
        unit = axis.get("units", None)
        if axis.get("must_have_bounds", "no") == "yes":
            bounds_list = axis.get("requested_bounds", [])
            if not bounds_list:
                bounds_list = [float(x) for x in axis.get("bounds_values", []).split()]
            if len(bounds_list) == 2 * len(levels):
                bnds = numpy.array(bounds_list)
                bounds_array = numpy.stack([bnds[0::2], bnds[1::2]], axis=1)
                return cmor.axis(table_entry=z_axis, coord_vals=levels, units=unit, cell_bounds=bounds_array)
            else:
                log.error("Failed to retrieve bounds for vertical axis %s" % str(z_axis))
        return cmor.axis(table_entry=z_axis, coord_vals=levels, units=unit)
    return 0


# Creates the hybrid model vertical axis in cmor.
def create_hybrid_level_axis(name):
    pref = 101325
    a = pplevels.a_coefs
    abnds = 0.5 * (a[1:] + a[:-1])
    b = pplevels.b_coefs
    bbnds = 0.5 * (b[1:] + b[:-1])
    hcm = a / pref + b
    hcbnds = 0.5 * (hcm[1:] + hcm[:-1])
    axisid = cmor.axis(table_entry=name, coord_vals=hcm, cell_bounds=hcbnds, units="1")
    cmor.zfactor(zaxis_id=axisid, zfactor_name="ap", units="Pa", axis_ids=[axisid], zfactor_values=a[:],
                 zfactor_bounds=abnds)
    cmor.zfactor(zaxis_id=axisid, zfactor_name="b", units="1", axis_ids=[axisid], zfactor_values=b[:],
                 zfactor_bounds=bbnds)
    return axisid


# Creates a soil depth axis, assuming IFS soil scheme
def create_soil_depth_axis(name):
    global log
    # TODO: Read from grib...
    ifs_levels_mm = numpy.array([0, 7, 28, 100, 289])
    ifs_levels = 1e-2 * ifs_levels_mm
    values = (ifs_levels[:-1] + ifs_levels[1:]) / 2
    bounds = numpy.stack([ifs_levels[:-1], ifs_levels[1:]], axis=1)
    return cmor.axis(table_entry=name, coord_vals=values, cell_bounds=bounds, units="m")


# Leaf operator: transfers data to the cmor library
class msg_to_cmor(ppop.post_proc_operator):

    def __init__(self, task, conversion_factor=1.):
        super(msg_to_cmor, self).__init__()
        self.task = task
        self.variable = task.source
        self.var_id = None
        self.store_variable = None
        self.store_var_id = None
        self.store_values = None
        self.conversion_factor = conversion_factor
        self.time_bounds = [None, None]

    def set_store_var(self, store_variable, ps_operator):
        ps_operator.targets.append(self)
        self.store_variable = store_variable

    def fill_cache(self, msg):
        if self.var_id is None:
            if self.store_variable:
                self.var_id, self.store_var_id = create_cmor_variable(self.task, msg, "ps")
            else:
                self.var_id = create_cmor_variable(self.task, msg)
        if msg.get_variable() == self.store_variable:
            self.store_values = msg.get_values()
        if msg.get_variable() == self.task.source:
            self.values = msg.get_values() * self.conversion_factor
            self.time_bounds = [getattr(msg, "timebnd_left", msg.get_timestamp()),
                                getattr(msg, "timebnd_right", msg.get_timestamp())]

    def cache_is_full(self):
        if self.store_variable:
            return self.values is not None and self.store_values is not None
        else:
            return self.values is not None

    def clear_cache(self):
        self.values = None
        self.store_values = None

    def create_msg(self):
        timestamp = self.property_cache[ppmsg.message.datetime_key]
        cmor.write(self.var_id, self.values, ntimes_passed=1, time_bnds=self.time_bounds,
                   time_vals=[timestamp])
        if self.store_variable:
            cmor.write(self.store_var_id, self.store_values, ntimes_passed=1, time_vals=[timestamp])
