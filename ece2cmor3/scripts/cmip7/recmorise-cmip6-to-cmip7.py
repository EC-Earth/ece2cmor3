#!/usr/bin/env python

import cmor      # used for writing files
import iris      # used for reading files -- netCDF4 or xarray could be used here based on preference
import json
import os
import sys
import re
import argparse
import warnings
import xml.etree.ElementTree as ET
from importlib.metadata import version
from os.path import expanduser

print(' The CMIP7 dreq python api version is: v{}'  .format(version('CMIP7_data_request_api')))
print(' The CMOR       python api version is: v{}\n'.format(version('cmor'                  )))


LOCAL_CMIP6_ROOT             = expanduser('~/cmorize/test-data-ece3-ESM-1/CE37-test/')
#LOCAL_CMIP6_ROOT             = expanduser('/scratch/nktr/test-data/CE38-test/')        # On hpc2020

#cmip6_variable               = 'tas'
#cmip6_table                  = 'Amon'
production_date_version      = 'v20260213'
grid_label                   = 'gr'
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

def print_dimension_attributes_with_values(coordinates_file):
    for k, v in coordinates_file.items():
     for dim_name, dim_attribute_dict in v.items():
      if dim_name == selected_dimension:
       print('\n {}:'.format(dim_name))
       for dim_attribute_name, dim_attribute_value in dim_attribute_dict.items():
        print('  {:25}="{}"'.format(dim_attribute_name, dim_attribute_value))
       print()


def tweakedorder_dimensions(list_of_dimensions):
 if   list_of_dimensions == 'time'      : return  1
 elif list_of_dimensions == 'latitude'  : return  2
 elif list_of_dimensions == 'longitude' : return  3
 else:                                    return 10


def add_dimension(var_cube, coordinates_file, dim):
    # Construct time coordinate in a way that we can update with points and bounds later
    if dim == "time":
     cmordim = cmor.axis(dim                                                                               , units=dimension_attribute(coordinates_file, dim, 'units'))
    elif dim == "latitude" or dim == "longitude":
     cmordim = cmor.axis(dim, coord_vals=var_cube.coord(dim).points, cell_bounds=var_cube.coord(dim).bounds, units=dimension_attribute(coordinates_file, dim, 'units'))
   #elif vertical coordinates
    else:
     cmordim = None
    return cmordim


def main():

    args = parse_args()

    cmip6_table    = args.table
    cmip6_variable = args.var

    # Check if the file exists and is a file
    if not os.path.isfile(cmip7_cmip6_mapping_filename):
     sys.exit(' ERROR: The file {:} does not exist, therefore first run:\n  ./cmip6-cmip7-variable-mapping.py -r v1.2.2.3\n'.format(cmip7_cmip6_mapping_filename))

    # Initiate CMOR:
    cmor.setup(inpath=cmip7_cmor_tables_dir, netcdf_file_action=cmor.CMOR_REPLACE)

    # Load the XML file with the CMIP7 - CMIP7 mapping and all CMIP7 attributes:
    tree_cmip7_variables = ET.parse(cmip7_cmip6_mapping_filename)
    root_cmip7_variables = tree_cmip7_variables.getroot()

    xpath_expression = './/variable[@cmip6_compound_name="' + cmip6_table + '.' + cmip6_variable + '"]'
    for element in root_cmip7_variables.findall(xpath_expression):
     cmip7_compound_name   = element.get('cmip7_compound_name')
     branded_variable_name = element.get('branded_variable_name')
     cmip7_units           = element.get('units')
     cmip7_frequency       = element.get('frequency')
     cmip7_region          = element.get('region')
     cmip7_realm           = re.sub(r'\..*','', element.get('cmip7_compound_name'))
     cmip7_out_name        = element.get('out_name')
     cmip7_dimensions      = element.get('dimensions').split()
     print(' cmip7_compound_name="{}"  branded_variable_name="{}"  units="{}"  frequency="{}"  region="{}  realm="{}"\n'.format(cmip7_compound_name  , \
                                                                                                                                branded_variable_name, \
                                                                                                                                cmip7_units          , \
                                                                                                                                cmip7_frequency      , \
                                                                                                                                cmip7_region         , \
                                                                                                                                cmip7_realm          ))

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



    # Load the file with the CMIP7 coordinates (with the coordinate units):
    with open(cmip7_cmor_tables_dir + 'CMIP7_coordinate.json', 'r') as file:
        cmip7_coordinates = json.load(file)


    # Looking around in the loaded CMIP7 coordinates:
    if False:
     selected_dimensions = ['time', 'latitude', 'longitude', 'height2m', 'alevel']

     for selected_dimension in selected_dimensions:
      print(' The selected dimension {:15} has units: {}'.format(selected_dimension, dimension_attribute(cmip7_coordinates, selected_dimension, 'units')))
      print_dimension_attributes_with_values(cmip7_coordinates)
     print()


    with open('input.json', 'w') as fh:
        json.dump(DATASET_INFO, fh, indent=2)

    cmor.dataset_json('input.json')

    cmor.load_table('CMIP7_{}.json'.format(cmip7_realm))

    # Load all existing data of the considered variable as a single iris cube:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cubelist = iris.load(LOCAL_CMIP6_ROOT + drs_expirement_member   + '/' \
                                              + cmip6_table             + '/' \
                                              + cmip6_variable          + '/' \
                                              + grid_label              + '/' \
                                              + production_date_version + '/' \
                                              + cmip6_variable          + '*.nc')

    for i in cubelist:
        i.attributes = {}

    var_cube = cubelist.concatenate_cube()


    # Define the CMOR variable object

    cmoraxes = []
    for dimension in sorted(cmip7_dimensions, key=tweakedorder_dimensions):
     print(' {}'.format(dimension))
     cmordim = add_dimension(var_cube, cmip7_coordinates, dimension)
     if cmordim is not None:
      cmoraxes.append(cmordim)
    print()

    cmorvar = cmor.variable(branded_variable_name, cmip7_units, cmoraxes)

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
        print(s)
        cube_slice = var_cube[s]
        cmor.write(
            cmorvar,
            cube_slice.data,
            time_vals=cube_slice.coord('time').points,
            time_bnds=cube_slice.coord('time').bounds)

    # Close the file (sorts the full naming)
    cmor.close(cmorvar, file_name=True)

if __name__ == '__main__':
    main()
