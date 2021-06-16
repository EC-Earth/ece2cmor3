import logging
import os

import netCDF4
import numpy

# Logger object
from ece2cmor3 import cmor_utils

log = logging.getLogger(__name__)

orca1_grid_shape = (292, 362)
orca025_grid_shape = (1050, 1442)

cached_vertices = {}


def load_vertices_from_file(gridtype, shape):
    global cached_vertices
    gridchar = gridtype
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
    fullpath = os.path.join(os.path.dirname(__file__), "resources", "b2share-data", file_name)
    if not os.path.isfile(fullpath):
        if not cmor_utils.get_from_b2share(file_name, fullpath):
            log.fatal("The file %s could not be downloaded, please install manually at %s" % (file_name, fullpath))
            return None, None
    nemo_vertices_file_name = os.path.join("ece2cmor3/resources/b2share-data/", fullpath)
    nemo_vertices_netcdf_file = netCDF4.Dataset(nemo_vertices_file_name, 'r')
    lon_vertices_raw = numpy.array(nemo_vertices_netcdf_file.variables["vertices_longitude"][...], copy=True)
    lat_vertices = numpy.array(nemo_vertices_netcdf_file.variables["vertices_latitude"][...], copy=True)
    nemo_vertices_netcdf_file.close()
    lon_vertices = numpy.where(lon_vertices_raw < 0, lon_vertices_raw + 360., lon_vertices_raw)
    cached_vertices[(mesh, gridchar)] = (lon_vertices, lat_vertices)
    return lon_vertices, lat_vertices
