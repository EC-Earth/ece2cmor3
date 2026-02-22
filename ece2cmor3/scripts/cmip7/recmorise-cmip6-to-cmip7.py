#!/usr/bin/env python

# Call example:
#  for i in `/usr/bin/ls -1         /scratch/nktr/test-data/CE37-test/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-piControl/r1i1p1f1/Amon`; do echo "./recmorise-cmip6-to-cmip7.py Amon ${i} &>> recmorise-cmip6-to-cmip7.log"; done
#  for i in `/usr/bin/ls -1  ~/cmorize/test-data-ece3-ESM-1/CE37-test/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-piControl/r1i1p1f1/Amon`; do echo "./recmorise-cmip6-to-cmip7.py Amon ${i} &>> recmorise-cmip6-to-cmip7.log"; done

import cmor      # used for writing files
import iris      # used for reading files -- netCDF4 or xarray could be used here based on preference
import json
import os
import sys
import glob
import re
import argparse
import warnings
import xml.etree.ElementTree as ET
from importlib.metadata import version
from os.path import expanduser


LOCAL_CMIP6_ROOT             = expanduser('~/cmorize/test-data-ece3-ESM-1/CE37-test/')
#LOCAL_CMIP6_ROOT             = expanduser('/scratch/nktr/test-data/CE38-test/')        # On hpc2020

production_date_version      = 'v*'
#grid_label                   = 'gr'
experiment_id                = 'esm-hist'
parent_experiment_id         = 'esm-piControl'
branch_time_in_child         = 30.0
branch_time_in_parent        = 10800.0
institution_id               = 'EC-Earth-Consortium'                                   # Not registered yet
source_id                    = 'EC-Earth3-ESM-1'                                       # Not registered yet
parent_source_id             = 'EC-Earth3-ESM-1'                                       # Not registered yet
institution_id               = 'MOHC'                                                  # for now
source_id                    = 'UKESM1-0-LL'                                           # for now
parent_source_id             = 'UKESM1-0-LL'                                           # for now
ripf_r                       = 'r1'
ripf_i                       = 'i1'
ripf_p                       = 'p1'
ripf_f                       = 'f1'
ripf                         = ripf_r + ripf_i + ripf_p + ripf_f
activity_id                  = 'CMIP'
time_units                   = 'days since 1850-01-01'                                 # probably

cmip7_cmip6_mapping_filename = './cmip7-variables-and-metadata-all.xml'                # Created by:  ./cmip6-cmip7-variable-mapping.py -r v1.2.2.3
cmip7_cmor_tables_dir        = '../../../../../cmorize/cmip7-cmor-tables/tables/'      # The cmor API allows only relative paths
cmip7_cmor_tables_cvs_dir    = '../../../../../cmorize/cmip7-cmor-tables/tables-cvs/'

drs_expirement_member  = 'CMIP6' + '/' + activity_id + '/' + 'EC-Earth-Consortium' + '/' + 'EC-Earth3-ESM-1' + '/' + 'esm-piControl' + '/' + ripf       # for now
#drs_expirement_member = 'CMIP6' + '/' + activity_id + '/' + institution_id        + '/' + source_id         + '/' + experiment_id   + '/' + ripf



def parse_args():
    """
    Parse command-line arguments
    """
    parser = argparse.ArgumentParser(
        description='Recmorise ECE3 CMIP6 CMOR data towards ECE3 CMIP7 CMOR data.'
    )
    # Posisional arguments
    parser.add_argument('table', metavar='cmip6_table'   , type=str, default='tas', help='The CMIP6 table    of the variable to convert, for instance: Amon')
    parser.add_argument('var'  , metavar='cmip6_variable', type=str, default='tas', help='The CMIP6 variable of the variable to convert, for instance: tas.')
    # Optional input arguments
    parser.add_argument('-v', '--verbose', action='store_true'                    , help="Verbose messaging")
    return parser.parse_args()


def dimension_attribute(coordinates_file, selected_dimension, specified_attribute):
    if selected_dimension == 'time':
     return time_units                      # Using the global defined one
    else:
     for k, v in coordinates_file.items():
      for dim_name, dim_attribute_dict in v.items():
       if dim_name == selected_dimension:
        for dim_attribute_name, dim_attribute_value in dim_attribute_dict.items():
         if dim_attribute_name == specified_attribute:
          return dim_attribute_value
#       "alternate_hybrid_sigma": {
#           "formula": "p = ap + b*ps",
#           "generic_level_name": "alevel",


def print_dimension_attributes_with_values(coordinates_file, selected_dimension):
    for k, v in coordinates_file.items():
     for dim_name, dim_attribute_dict in v.items():
      if dim_name == selected_dimension:
       print('\n {}:'.format(dim_name))
       for dim_attribute_name, dim_attribute_value in dim_attribute_dict.items():
        print('  {:25}="{}"'.format(dim_attribute_name, dim_attribute_value))
       print()


def variable_attribute(variable_file, selected_variable, specified_attribute):
     for k, v in variable_file.items():
      for var_name, var_attribute_dict in v.items():
       if var_name == selected_variable:
        for var_attribute_name, var_attribute_value in var_attribute_dict.items():
         if var_attribute_name == specified_attribute:
          return var_attribute_value


def tweakedorder_dimensions(list_of_dimensions):
 if   list_of_dimensions in ["time", "time1", "time2", "time3", "time4"] : return  1  # Without time3 here it wordks as well for variables like Amon rsdt
 elif list_of_dimensions == 'latitude'                                   : return  3
 elif list_of_dimensions == 'longitude'                                  : return  4
 else:                                                                     return  2  # The vertical coordinate has to be before the latitude & longitude


def add_dimension(var_cube, coordinates_file, dim, dim_standard_name):
    # Construct time coordinate in a way that we can update with points and bounds later
    if dim in ["time"]:
     cmordim = cmor.axis(dim, \
                         units=dimension_attribute(coordinates_file, dim, 'units'))
    elif dim in ["time1", "time2", "time3", "time4"]:
     cmordim = cmor.axis(dim, \
                         units=dimension_attribute(coordinates_file, dim_standard_name, 'units'))
    elif dim in ["latitude", "longitude", "plev19", "landuse", "sdepth"]:
     if False:
      print('\nINFO 1 from add_dimension:\n{}'  .format(var_cube))
      print('\nINFO 2 from add_dimension:\n{}\n'.format(var_cube.coord(dim_standard_name)))
     cmordim = cmor.axis(dim,                                                           \
                         coord_vals =var_cube.coord(dim_standard_name).points,          \
                         cell_bounds=var_cube.coord(dim_standard_name).bounds,          \
                         units      =dimension_attribute(coordinates_file, dim, 'units'))
    else:
     cmordim = None
    return cmordim



def main():

    args = parse_args()

    cmip6_table    = args.table
    cmip6_variable = args.var
    verbose        = args.verbose

    if verbose:
     print(' The CMIP7 dreq python api version is: v{}'  .format(version('CMIP7_data_request_api')))
     print(' The CMOR       python api version is: v{}\n'.format(version('cmor'                  )))

    # Check if the file exists and is a file
    if not os.path.isfile(cmip7_cmip6_mapping_filename):
     sys.exit(' ERROR: The file {:} does not exist, therefore first run:\n  ./cmip6-cmip7-variable-mapping.py -r v1.2.2.3\n'.format(cmip7_cmip6_mapping_filename))

    # Initiate CMOR:
    cmor.setup(inpath=cmip7_cmor_tables_dir, netcdf_file_action=cmor.CMOR_REPLACE)

    # Load the XML file with the CMIP7 - CMIP7 mapping and all CMIP7 attributes:
    tree_cmip7_variables = ET.parse(cmip7_cmip6_mapping_filename)
    root_cmip7_variables = tree_cmip7_variables.getroot()

    match = False
    xpath_expression = './/variable[@cmip6_compound_name="' + cmip6_table + '.' + cmip6_variable + '"]'
    for element in root_cmip7_variables.findall(xpath_expression):
     match = True
     cmip7_compound_name   = element.get('cmip7_compound_name')
     branded_variable_name = element.get('branded_variable_name')
     cmip7_units           = element.get('units')
     cmip7_frequency       = element.get('frequency')
     cmip7_region          = element.get('region')
     cmip7_realm           = re.sub(r'\..*','', element.get('cmip7_compound_name'))
     cmip7_out_name        = element.get('out_name')
     cmip7_dimensions      = element.get('dimensions').split()
     print(' {:12} {:26}  ==>  cmip7_compound_name={:50} branded_variable_name={:40} units={:20} frequency={:10} region={:15} realm={}'.format( \
            cmip6_table                , \
            cmip6_variable             , \
            '"' + cmip7_compound_name   + '"', \
            '"' + branded_variable_name + '"', \
            '"' + cmip7_units           + '"', \
            '"' + cmip7_frequency       + '"', \
            '"' + cmip7_region          + '"', \
            '"' + cmip7_realm           + '"'))
    else: # The for-else:
     if not match: sys.exit(' Sorry no CMIP7 equivalent:\n')


    # Overwrite grid label when::

    if cmip6_variable in ['co2s', 'co2mass']:
     grid_label = 'gm'
    elif cmip7_realm in ['ocean', 'seaIce', 'ocnBgchem']:
     grid_label = 'gn'
    else:
     grid_label = 'gr'


    DATASET_INFO = {
        "_AXIS_ENTRY_FILE"           : cmip7_cmor_tables_dir + 'CMIP7_coordinate.json',
        "_FORMULA_VAR_FILE"          : cmip7_cmor_tables_dir + 'CMIP7_formula_terms.json',
        "_cmip7_option"              : 1,
        "_controlled_vocabulary_file": cmip7_cmor_tables_cvs_dir + 'cmor-cvs.json',
        "activity_id"                : activity_id,
        "branch_method"              : "standard",
        "branch_time_in_child"       : branch_time_in_child,
        "branch_time_in_parent"      : branch_time_in_parent,
        "calendar"                   : "360_day",                             # check
        "drs_specs"                  : "MIP-DRS7",
        "data_specs_version"         : "MIP-DS7.0.0.0",
        "experiment_id"              : experiment_id,
        "forcing_index"              : ripf_f,
        "grid"                       : "N96",                                 # check
        "grid_label"                 : "g99",                                 # check
        "initialization_index"       : ripf_i,
        "institution_id"             : institution_id,
        "license_id"                 : "CC-BY-4-0",
        "nominal_resolution"         : "100 km",
        "outpath"                    : ".",
        "parent_mip_era"             : "CMIP7",
        "parent_time_units"          : "days since 1850-01-01",
        "parent_activity_id"         : "CMIP",
        "parent_source_id"           : parent_source_id,
        "parent_experiment_id"       : parent_experiment_id,
        "parent_variant_label"       : ripf,
        "physics_index"              : ripf_p,
        "realization_index"          : ripf_r,
        "source_id"                  : source_id,
        "tracking_prefix"            : "hdl:21.14107",                        # check
        "host_collection"            : "CMIP7",
        "frequency"                  : cmip7_frequency,
        "region"                     : cmip7_region,
        "archive_id"                 : "WCRP",
        "mip_era"                    : "CMIP7",
    }

    cmor_table_of_selected_realm = 'CMIP7_{}.json'.format(cmip7_realm)

    # Load the file with the CMIP7 coordinates (with the coordinate units):
    with open(cmip7_cmor_tables_dir + cmor_table_of_selected_realm, 'r') as file:
        cmip7_cmor_table_with_var = json.load(file)

    # Load the file with the CMIP7 coordinates (with the coordinate units):
    with open(cmip7_cmor_tables_dir + 'CMIP7_coordinate.json', 'r') as file:
        cmip7_coordinates = json.load(file)

    sorted_cmip7_dimensions = sorted(cmip7_dimensions, key=tweakedorder_dimensions)

    # Looking around in the CMIP7 coordinates of the considered variable:
    if False:
     for var_dimension in sorted_cmip7_dimensions:
      print_dimension_attributes_with_values(cmip7_coordinates, var_dimension)


    with open('input.json', 'w') as fh:
        json.dump(DATASET_INFO, fh, indent=2)

    cmor.dataset_json('input.json')

    cmor.load_table(cmor_table_of_selected_realm)

    # Load all existing data of the considered variable as a single iris cube:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cmip6_file_path_and_name = LOCAL_CMIP6_ROOT + drs_expirement_member   + '/' \
                                                    + cmip6_table             + '/' \
                                                    + cmip6_variable          + '/' \
                                                    + grid_label              + '/' \
                                                    + production_date_version + '/' \
                                                    + cmip6_variable          + '*.nc'

        matched_cmip6_files = glob.glob(cmip6_file_path_and_name)
        number_of_matched_cmip6_files = len(matched_cmip6_files)
        if number_of_matched_cmip6_files == 0:
         sys.exit(' ERROR: No files found for {}\n'.format(cmip6_file_path_and_name))
        elif number_of_matched_cmip6_files == 1:
         cubelist = iris.load(matched_cmip6_files[0])
        else:
         cubelist = iris.load(matched_cmip6_files[0])
         print(' WARNING: {} matched CMIP6 files found, the first one has been taken.\n'.format(number_of_matched_cmip6_files))
         if verbose:
          print(' The different files detected are:')
          for matched_cmip6_file in matched_cmip6_files:
           print('  {}'.format(matched_cmip6_file))
          print()

    for i in cubelist:
        i.attributes = {}

    var_cube = cubelist.concatenate_cube()


    # Define the CMOR variable object

    if cmip7_realm in ['ocean', 'seaIce', 'ocnBgchem']:
     orca_grid_case = True
    else:
     orca_grid_case = False

    variable_attrib = variable_attribute(cmip7_cmor_table_with_var, branded_variable_name, 'positive')

    if orca_grid_case:
     dim_standard_name = dimension_attribute(cmip7_coordinates, 'time', 'standard_name')
     time_axis_id = add_dimension(var_cube, cmip7_coordinates, 'time', dim_standard_name)

     # Here load the grids table to set up x and y axes and the lat-long grid:
     cmor.load_table('CMIP7_grids.json')

     lon_std_name = 'first spatial index for variables stored on an unstructured grid'
     lat_std_name = 'second spatial index for variables stored on an unstructured grid'

     y_axis_id = cmor.axis(table_entry='grid_latitude',
                           units='degrees',
                           coord_vals=var_cube.coord(lat_std_name).points,
                           cell_bounds=var_cube.coord(lat_std_name).bounds)
     x_axis_id = cmor.axis(table_entry='grid_longitude',
                           units='degrees',
                           coord_vals=var_cube.coord(lon_std_name).points,
                           cell_bounds=var_cube.coord(lon_std_name).bounds)
     grid_id   = cmor.grid(axis_ids=[y_axis_id, x_axis_id],
                           latitude=var_cube.coord('latitude').points,
                           longitude=var_cube.coord('longitude').points,
                           latitude_vertices=var_cube.coord('latitude').bounds,
                           longitude_vertices=var_cube.coord('longitude').bounds)

     # Load again the realm table of the variable:
     cmor.load_table(cmor_table_of_selected_realm)
     cmorvar = cmor.variable(branded_variable_name, cmip7_units, axis_ids=[time_axis_id, grid_id], positive=variable_attrib)
    else:

     # Define the CMOR variable object

     cmoraxes = []
     for dimension in sorted_cmip7_dimensions:
      dim_standard_name = dimension_attribute(cmip7_coordinates, dimension, 'standard_name')
      if verbose:
       print('  {:15} dimension with standard_name="{}"'.format(dimension, dim_standard_name))
      cmordim = add_dimension(var_cube, cmip7_coordinates, dimension, dim_standard_name)
      if cmordim is not None:
       cmoraxes.append(cmordim)
     if verbose: print()

     cmorvar = cmor.variable(branded_variable_name, cmip7_units, cmoraxes, positive=variable_attrib)


    # Apply cell measures
    with open(cmip7_cmor_tables_dir + 'CMIP7_cell_measures.json') as fh:
        cell_measures = json.load(fh)
    value_cell_measures = cell_measures['cell_measures'][cmip7_compound_name]
    cmor.set_variable_attribute(cmorvar, "cell_measures", "c", value_cell_measures)

    # Override long names if necessary
    with open(cmip7_cmor_tables_dir + 'CMIP7_long_name_overrides.json') as fh:
        long_name_overrides = json.load(fh)
    if cmip7_compound_name in long_name_overrides['long_name_overrides']:
        new_value_long_name = long_name_overrides['long_name_overrides'][cmip7_compound_name]
        cmor.set_variable_attribute(cmorvar, "long_name", "c", new_value_long_name)


    # Slice up data into N time record chunks and push through CMOR.write
    N = 50
    N = 12
    for i in range(0, 12, N):
        s = slice(i, i+N)
        if verbose:
         print(' {}'.format(s))
        cube_slice = var_cube[s]
        cmor.write(cmorvar, cube_slice.data, time_vals=cube_slice.coord('time').points
                                           , time_bnds=cube_slice.coord('time').bounds)

    # Close the file (sorts the full naming)
    cmor.close(cmorvar, file_name=True)

if __name__ == '__main__':
    main()
