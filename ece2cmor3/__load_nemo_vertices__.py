import logging
import os

import netCDF4
import numpy

# Logger object
log = logging.getLogger(__name__)

orca1_grid_shape = (292, 362)
orca025_grid_shape = (1050, 1442)

cached_vertices = {}


def load_vertices_from_file(grid, shape):
    global cached_vertices
    if grid in ["T_2D", "T_3D", "W_2D", "W_3D"]:
        gridchar = 't'
    elif grid in ["U_2D", "U_3D"]:
        gridchar = 'u'
    elif grid in ["V_2D", "V_3D"]:
        gridchar = 'v'
    else:
        log.fatal("Unknown grid identifier for NEMO: %s" % str(grid))
        return None, None
    if shape == orca1_grid_shape:
        mesh = "ORCA1"
    elif shape == orca025_grid_shape:
        mesh = "ORCA025"
    else:
        log.fatal("Unsupported grid resolution for NEMO: %s" % str(shape))
        return None, None
    if (mesh, gridchar) in cached_vertices.keys():
        return cached_vertices[(mesh, gridchar)][0], cached_vertices[(mesh, gridchar)][1]
    file_name = '-'.join(["nemo", "vertices", mesh, gridchar, "grid"]) + ".nc"
    fullpath = os.path.join(os.path.dirname(__file__), "resources", "nemo-vertices", file_name)
    if not os.path.isfile(fullpath):
        log.fatal("The file %s does not exist, please update your repo and reinstall")
    nemo_vertices_file_name = os.path.join("ece2cmor3/resources/nemo-vertices/", fullpath)
    nemo_vertices_netcdf_file = netCDF4.Dataset(nemo_vertices_file_name, 'r')
    lon_vertices_raw = numpy.array(nemo_vertices_netcdf_file.variables["vertices_longitude"][...], copy=True)
    lat_vertices = numpy.array(nemo_vertices_netcdf_file.variables["vertices_latitude"][...], copy=True)
    nemo_vertices_netcdf_file.close()
    lon_vertices = numpy.where(lon_vertices_raw < 0, lon_vertices_raw + 360., lon_vertices_raw)
    cached_vertices[(mesh, gridchar)] = (lon_vertices, lat_vertices)
    return lon_vertices, lat_vertices
