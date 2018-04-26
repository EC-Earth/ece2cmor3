import logging

import numexpr
import numpy
import cmor
from ece2cmor3 import cmor_target, cmor_task, cmor_source
from ece2cmor3.postproc import message, operator, zlevels

# Logger construction
log = logging.getLogger(__name__)

# Dictionary of grids, keys are horizontal sizes of incoming variables
grid_ids = {}

# Dictionary of time axes, keys are target variable frequencies and table
time_axis_ids = {}

# Dictionary of vertical axes, keys are target vertical dimension name and table
z_axis_ids = {}

# Dictionary of variable ids, keys are pairs of cmor variable name and table
var_ids = {}

# Dictionary of table ids
tab_ids = {}

ref_date = None
time_unit = "hour"

table_root = None


# Leaf operator: transfers data to the cmor library
class cmor_operator(operator.operator_base):
    missval = 1.e+20

    def __init__(self, task, chunk_size=10, store_var_key=None, mask_key=None):
        super(cmor_operator, self).__init__()
        self.task = task
        self.chunk_size = chunk_size
        self.variable = task.source
        self.store_var_key = store_var_key
        self.store_var_values = []
        self.mask_key = mask_key
        self.mask_expression = None
        self.mask_values = []
        self.var_id = None
        self.store_var_id = None
        self.cached_properties = [message.variable_key,
                                  message.leveltype_key,
                                  message.levellist_key,
                                  message.resolution_key]
        self.timestamps = []
        self.timebounds = []

    def apply_mask(self, array):
        if self.mask_key is None or self.mask_expression is None:
            return array
        src = cmor_source.grib_code(self.mask_key[0], self.mask_key[1])
        local_dict = {src.to_var_string(): self.mask_values}
        mask_array = numexpr.evaluate(self.mask_expression, local_dict=local_dict)
        numpy.putmask(array, numpy.broadcast_to(numpy.logical_not(mask_array), array.shape), self.missval)
        return array

    def fill_cache(self, msg):
        if self.var_id is None:
            self.var_id, self.store_var_id = create_cmor_variable(self.task, msg, self.store_var_key)
        if msg.get_variable() == self.task.source:
            conversion_factor = get_conversion_factor(getattr(self.task, cmor_task.conversion_key, None),
                                                      getattr(self.task, cmor_task.output_frequency_key))
            self.values.append(msg.get_values() * conversion_factor)
            self.timestamps.append(convert_time(msg.get_timestamp()))
            self.timebounds.append([convert_time(t) for t in msg.get_time_bounds()])

    def receive_extra_var(self, msg, values):
        if self.cache_is_full():
            self.clear_cache()
        if len(self.timestamps) < len(values):
            log.error("This should never happen")
        elif len(self.timestamps) == len(values):
            values.append(msg.get_values())
        else:
            prev_time, prev_bounds = self.timestamps[-1], self.timebounds[-1]
            if msg.get_timestamp() == prev_time:
                values.append(msg.get_values())
            elif prev_bounds[0] <= msg.get_timestamp() <= prev_bounds[1]:
                values.append(msg.get_values())
            else:
                log.warning("Skipping store/mask variable outside time bounds")
        if self.cache_is_full():
            self.send_msg()

    def receive_store_var(self, msg):
        self.receive_extra_var(msg, self.store_var_values)

    def receive_mask_var(self, msg):
        self.receive_extra_var(msg, self.mask_values)

    def cache_is_full(self):
        vals_complete = sum([num_slices(a) for a in self.values]) >= self.chunk_size
        store_complete = self.store_var_key is None or len(self.store_var_values) >= len(self.values)
        mask_complete = self.mask_key is None or len(self.mask_values) >= len(self.values)
        return super(cmor_operator, self).cache_is_full() and vals_complete and store_complete and mask_complete

    def cache_is_empty(self):
        return super(cmor_operator, self).cache_is_empty() or self.values == []

    def clear_cache(self):
        self.values, self.timestamps, self.timebounds = [], [], []

    def send_msg(self):
        load_table(self.task.target.table)
        log.info("Writing variable %s in table %s at times %s" % (self.task.target.variable, self.task.target.table,
                                                                  str(self.timestamps)))
        cmor.set_cur_dataset_attribute("frequency", str(getattr(self.task, cmor_task.output_frequency_key)) + "hrPt")
        if any(self.timebounds[0]):
            cmor.write(self.var_id, self.apply_mask(numpy.stack(self.values)), ntimes_passed=len(self.timestamps),
                       time_vals=self.timestamps, time_bnds=self.timebounds)
            if self.store_var_key is not None:
                cmor.write(self.store_var_id, numpy.stack(self.store_var_values), ntimes_passed=len(self.timestamps),
                           store_with=self.var_id, time_vals=self.timestamps, time_bnds=self.timebounds)
                self.store_var_values = None
        else:
            cmor.write(self.var_id, self.apply_mask(numpy.stack(self.values)), ntimes_passed=len(self.timestamps),
                       time_vals=self.timestamps)
            if self.store_var_key is not None:
                cmor.write(self.store_var_id, numpy.stack(self.store_var_values), store_with=self.var_id,
                           time_vals=self.timestamps, time_bnds=self.timebounds)
                self.store_var_values = None


# Creates a variable for the given task, and creates grid, time and z axes if necessary
def create_cmor_variable(task, msg, store_var_key=None):
    global grid_ids, time_axis_ids, z_axis_ids, var_ids
    shape = msg.get_values().shape
    key = (shape[-2], shape[-1])
    if key in grid_ids:
        grid_id = grid_ids[key]
    else:
        load_table("grids")
        grid_id = create_gauss_grid(key[1], key[0])
        grid_ids[key] = grid_id
    load_table(task.target.table)
    freq = getattr(task.target, cmor_target.freq_key, None)
    time_axis_id, key = 0, (task.target.table, freq)
    if key in time_axis_ids:
        time_axis_id = time_axis_ids[key]
    elif freq is not None:
        if not any(time_axis_ids):
            cmor.set_cur_dataset_attribute("calendar", "proleptic_gregorian")
        time_axis_id = create_time_axis(task, msg)
        if time_axis_id != 0:
            time_axis_ids[key] = time_axis_id
    z_axis, axis_variable, levels = cmor_target.get_z_axis(task.target)
    z_axis_id, key = 0, (task.target.table, z_axis)
    if key in z_axis_ids:
        z_axis_id = z_axis_ids[key]
    elif z_axis:
        z_axis_id = create_z_axis(z_axis, [float(l) for l in levels], task.target.table)
        z_axis_ids[key] = z_axis_id
    axes = [a for a in [time_axis_id, z_axis_id, grid_id] if a != 0]
    orientation = getattr(task.target, "positive", "")
    if len(orientation) != 0:
        var_id = cmor.variable(table_entry=str(task.target.variable), units=str(getattr(task.target, "units", "")),
                               axis_ids=axes, positive="down")
    else:
        var_id = cmor.variable(table_entry=str(task.target.variable), units=str(getattr(task.target, "units", "")),
                               axis_ids=axes)
    if store_var_key:
        store_var_id = cmor.zfactor(zaxis_id=z_axis_id, zfactor_name=get_store_variable(store_var_key[0]),
                                    axis_ids=[time_axis_id, grid_id], units="Pa")
        return var_id, store_var_id
    else:
        return var_id, None


def get_store_variable(code):
    if code == 134:
        return "ps"
    else:
        raise NotImplementedError("Cannot create store variable name for %d" % code)


def load_table(table):
    global tab_ids
    tab_id = tab_ids.get(table, 0)
    if tab_id == 0:
        tab_id = cmor.load_table(table_root + "_" + table + ".json")
        tab_ids[table] = tab_id
    cmor.set_table(tab_id)
    return tab_id


# Creates the regular gaussian grid from its arguments.
def create_gauss_grid(nx, ny):
    i_index_id = cmor.axis(table_entry="i_index", units="1", coord_vals=numpy.arange(1, nx + 1))
    j_index_id = cmor.axis(table_entry="j_index", units="1", coord_vals=numpy.arange(1, ny + 1))
    x0, y0 = 0., -90.
    dx, dy = 360. / nx, 180. / ny
    x_vals = numpy.array([x0 + (i + 0.5) * dx for i in range(nx)])
    y_vals = numpy.array([y0 + (i + 0.5) * dy for i in range(ny)])
    lon_arr = numpy.tile(x_vals, (ny, 1))
    lat_arr = numpy.tile(y_vals, (nx, 1)).transpose()
    lon_mids = numpy.array([x0 + i * dx for i in range(nx + 1)])
    lat_mids = numpy.array([y0 + i * dy for i in range(ny + 1)])
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
    global ref_date
    target_dims = getattr(task.target, cmor_target.dims_key)
    time_dims = [d for d in list(set(target_dims.split())) if d.startswith("time")]
    if any(time_dims):
        if ref_date is None:
            ref_date = msg.get_timestamp()
        # TODO: use UTC formatting for refdate
        return cmor.axis(table_entry=str(time_dims[0]), units=time_unit + "s since " + str(ref_date))
    else:
        return 0


def convert_time(timestamp):
    # TODO: use seconds/minutes dependent upon unit
    return (timestamp - ref_date).total_seconds() / 3600


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
                log.error("Failed to retrieve bounds for vertical axis %s" % z_axis)
        return cmor.axis(table_entry=z_axis, coord_vals=levels, units=unit)
    log.error("Failed to retrieve information for vertical axis %s in table %s" % (z_axis, table))
    return 0


def create_bounds(a, minbnd=-float("inf"), maxbnd=float("inf")):
    n = len(a)
    bnds = numpy.empty([n, 2])
    bnds[0, 0] = max(minbnd, 0.5 * (a[0] - a[1]))
    bnds[1:n, 0] = 0.5 * (a[:-1] + a[1:])
    bnds[0:n - 1, 1] = bnds[1:n, 0]
    bnds[n - 1, 1] = min(maxbnd, 1.5 * a[-1] + 0.5 * a[-2])
    return bnds


# Creates the hybrid model vertical axis in cmor.
def create_hybrid_level_axis(name):
    pref = 101325
    a = zlevels.a_coefs
    b = zlevels.b_coefs
    hcm = a / pref + b
    axisid = cmor.axis(table_entry=name, coord_vals=hcm, cell_bounds=create_bounds(hcm, 0., 1.), units="1")
    cmor.zfactor(zaxis_id=axisid, zfactor_name="ap", units="Pa", axis_ids=[axisid], zfactor_values=a[:],
                 zfactor_bounds=create_bounds(a, 0.))
    cmor.zfactor(zaxis_id=axisid, zfactor_name="b", units="1", axis_ids=[axisid], zfactor_values=b[:],
                 zfactor_bounds=create_bounds(b, 0., 1.))
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


# Returns the conversion factor from the input string
def get_conversion_factor(conversion, output_frequency):
    global log
    if not conversion:
        return 1.0
    if conversion == "cum2inst":
        return 1.0 / (3600 * output_frequency)
    if conversion == "inst2cum":
        return 3600 * output_frequency
    if conversion == "pot2alt":
        return 1.0 / 9.81
    if conversion == "alt2pot":
        return 9.81
    if conversion == "vol2flux":
        return 1000.0 / (3600 * output_frequency)
    if conversion == "vol2massl":
        return 1000.0
    if conversion == "frac2percent":
        return 100.0
    if conversion == "percent2frac":
        return 0.01
    log.error("Unknown explicit unit conversion: %s" % conversion)
    return 1.0


def num_slices(arr):
    return arr.shape[2] if len(arr.shape) > 2 else 1
