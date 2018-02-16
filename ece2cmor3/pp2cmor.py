import logging
import numpy
import cmor
from ece2cmor3 import ppop, cmor_target

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


def create_time_axis(task, msg):
    target_dims = getattr(task.target, cmor_target.dims_key)
    time_dims = [d for d in list(set(target_dims.split())) if d.startswith("time")]
    if any(time_dims):
        refdate = msg.get_timestamp() if ref_date is None else ref_date
        return cmor.axis(table_entry=str(time_dims[0]), units=time_unit + "s since " + str(refdate))
    else:
        return 0


def create_z_axis(z_axis, levels):
    return 0


def create_cmor_variable(task, msg):
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
    if z_axis in z_axis_ids:
        z_axis_id = z_axis_ids[z_axis]
    elif z_axis:
        z_axis_id = create_z_axis(z_axis, levels)
        z_axis_ids[z_axis] = z_axis_ids
    axes = [time_axis_id, grid_id, z_axis_id]
    axes.remove(0)
    unit = msg.get_units()
    return cmor.variable(table_entry=str(task.target.variable), units=str(unit), axis_ids=axes, positive="down")


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


class msg_to_cmor(ppop.post_proc_operator):

    def __init__(self, task):
        super(msg_to_cmor, self).__init__()
        self.task = task
        self.var_id = None

    def fill_cache(self, msg):
        if self.var_id is None:
            self.var_id = create_cmor_variable(self.task, msg)
        else:
            timestamp = msg.get_timestamp()
            time_bnd_left = getattr(msg, "timebnd_left", timestamp)
            time_bnd_right = getattr(msg, "timebnd_right", timestamp)
            cmor.write(msg.get_values(), ntimes_passed=1, time_bnds=[time_bnd_left, time_bnd_right],
                       time_vals=[timestamp])
