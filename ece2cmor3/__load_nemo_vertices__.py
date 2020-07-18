import logging
import sys
import os
import netCDF4
import numpy as np

# Logger object
log = logging.getLogger(__name__)

def load_vertices(vertices_file_name):
    # Loading once at the start the NEMO longitude and latitude vertices from a netcdf file:
    nemo_vertices_file_name=os.path.join("ece2cmor3/resources/nemo-vertices/", vertices_file_name)
    # Using log I get an error: No handlers could be found for logger "ece2cmor3.__load_nemo_vertices__"
   #if os.path.isfile(nemo_vertices_file_name) == False: log.error('The file {} does not exist. These vertices files are available in the cmor-fixer repository, follow the instructions from: ece2cmor3/resources/nemo-vertices/this-directory.txt\n'.format(vertices_file_name)); sys.exit(' Exiting ece2cmor.')
   #if os.path.isfile(nemo_vertices_file_name) == False: log.fatal('The file {} does not exist. These vertices files are available in the cmor-fixer repository, follow the instructions from: ece2cmor3/resources/nemo-vertices/this-directory.txt\n'.format(vertices_file_name)); sys.exit(' Exiting ece2cmor.')
    if os.path.isfile(nemo_vertices_file_name) == False: print('\nThe file {} does not exist. These vertices files are available in the cmor-fixer repository, follow the instructions from: ece2cmor3/resources/nemo-vertices/this-directory.txt\n'.format(vertices_file_name)); sys.exit(' Exiting ece2cmor.')
    nemo_vertices_netcdf_file = netCDF4.Dataset(nemo_vertices_file_name, 'r')
    lon_vertices_from_nemo_tmp = nemo_vertices_netcdf_file.variables["vertices_longitude"]
    lat_vertices_from_nemo_tmp = nemo_vertices_netcdf_file.variables["vertices_latitude"]
    lon_vertices_from_nemo = np.array(lon_vertices_from_nemo_tmp[...], copy=True)
    lat_vertices_from_nemo = np.array(lat_vertices_from_nemo_tmp[...], copy=True)
    nemo_vertices_netcdf_file.close()
    return lon_vertices_from_nemo, lat_vertices_from_nemo

# Load the vertices fields (Note these are global variables which otherwise have to be given as arguments via the function process_file to the function fix_file):
lon_vertices_from_nemo_orca1_t_grid, lat_vertices_from_nemo_orca1_t_grid = load_vertices("nemo-vertices-ORCA1-t-grid.nc")
lon_vertices_from_nemo_orca1_u_grid, lat_vertices_from_nemo_orca1_u_grid = load_vertices("nemo-vertices-ORCA1-u-grid.nc")
lon_vertices_from_nemo_orca1_v_grid, lat_vertices_from_nemo_orca1_v_grid = load_vertices("nemo-vertices-ORCA1-v-grid.nc")
# Convert the vertices_longitude to the 0-360 degree interval:
lon_vertices_from_nemo_orca1_t_grid = np.where(lon_vertices_from_nemo_orca1_t_grid < 0, lon_vertices_from_nemo_orca1_t_grid + 360.0, lon_vertices_from_nemo_orca1_t_grid)
lon_vertices_from_nemo_orca1_u_grid = np.where(lon_vertices_from_nemo_orca1_u_grid < 0, lon_vertices_from_nemo_orca1_u_grid + 360.0, lon_vertices_from_nemo_orca1_u_grid)
lon_vertices_from_nemo_orca1_v_grid = np.where(lon_vertices_from_nemo_orca1_v_grid < 0, lon_vertices_from_nemo_orca1_v_grid + 360.0, lon_vertices_from_nemo_orca1_v_grid)

# Load the vertices fields (Note these are global variables which otherwise have to be given as arguments via the function process_file to the function fix_file):
lon_vertices_from_nemo_orca025_t_grid, lat_vertices_from_nemo_orca025_t_grid = load_vertices("nemo-vertices-ORCA025-t-grid.nc")
lon_vertices_from_nemo_orca025_u_grid, lat_vertices_from_nemo_orca025_u_grid = load_vertices("nemo-vertices-ORCA025-u-grid.nc")
lon_vertices_from_nemo_orca025_v_grid, lat_vertices_from_nemo_orca025_v_grid = load_vertices("nemo-vertices-ORCA025-v-grid.nc")
# Convert the vertices_longitude to the 0-360 degree interval:
lon_vertices_from_nemo_orca025_t_grid = np.where(lon_vertices_from_nemo_orca025_t_grid < 0, lon_vertices_from_nemo_orca025_t_grid + 360.0, lon_vertices_from_nemo_orca025_t_grid)
lon_vertices_from_nemo_orca025_u_grid = np.where(lon_vertices_from_nemo_orca025_u_grid < 0, lon_vertices_from_nemo_orca025_u_grid + 360.0, lon_vertices_from_nemo_orca025_u_grid)
lon_vertices_from_nemo_orca025_v_grid = np.where(lon_vertices_from_nemo_orca025_v_grid < 0, lon_vertices_from_nemo_orca025_v_grid + 360.0, lon_vertices_from_nemo_orca025_v_grid)
