#!/usr/bin/env python

# Call example:
#  for i in `/usr/bin/ls -1 /scratch/nktr/test-data/CE42-test/CMIP6/CMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-piControl/r1i1p1f1/fx`; do echo "./recmorise-cmip6-to-cmip7.py fx ${i}"; done

# Or use the bash script to loop over (nearly) all test files in the CMIP6 directory (note in this test data each subdir has contains one file):
#  ./recmorise-cmip6-to-cmip7.sh       # Produces the script below
#  ./run-recmorise-cmip6-to-cmip7.sh

# For hpc2020 a submit script for parallel handling is available, for usage instructions run the script without arguments:
#  ./submit-at-hpc2020-recmorise-cmip6-to-cmip7.sh

import cmor      # used for writing files
import iris      # used for reading files -- netCDF4 or xarray could be used here based on preference
import json
import os
import sys
import glob
import re
import argparse
import warnings
import cftime
import math
import numpy as np
import xml.etree.ElementTree as ET
from importlib.metadata import version
from os.path import expanduser
from pathlib import Path

LOCAL_CMIP6_ROOT             = expanduser('/scratch/nktr/test-data/CE42-test/')                             # On hpc2020
#LOCAL_CMIP6_ROOT            = expanduser('~/cmorize/test-data-ece/CE37-test/')
#LOCAL_CMIP6_ROOT            = expanduser('~/optimesm/cmorized/CE42-test/')

OUTPUT_CMIP7_ROOT            = expanduser('/scratch/nktr/cmorised-results/converted-to-cmip7/CE42-test/')   # On hpc2020
#OUTPUT_CMIP7_ROOT           = expanduser('~/cmip7-cmorised')
#OUTPUT_CMIP7_ROOT           = expanduser('~/optimesm/cmorized/CE42-test-cmip7')

production_date_version      = 'v*'
experiment_id                = 'esm-piControl'
parent_experiment_id         = 'esm-piControl-spinup'
branch_time_in_child         = 30.0
branch_time_in_parent        = 10800.0
institution_id               = 'EC-Earth-Consortium'
source_id                    = 'EC-Earth3-ESM-1'
parent_source_id             = 'EC-Earth3-ESM-1'
ripf_r                       = 'r1'
ripf_i                       = 'i1'
ripf_p                       = 'p1'
ripf_f                       = 'f1'
ripf                         = ripf_r + ripf_i + ripf_p + ripf_f
activity_id                  = 'CMIP'
time_units                   = 'days since 1850-01-01'                                 # probably

cmip7_cmip6_mapping_filename = './cmip7-variables-and-metadata-all.xml'                # Created by:  ./cmip6-cmip7-variable-mapping.py -r v1.2.2.3
cmip7_cmor_tables_dir        = '../../../../cmip7-cmor-tables/tables/'                 # The cmor API allows only relative paths
cmip7_cmor_tables_cvs_dir    = '../../../../cmip7-cmor-tables/tables-cvs/'

drs_expirement_member = 'CMIP6' + '/' + activity_id + '/' + institution_id + '/' + source_id + '/' + experiment_id + '/' + ripf

# suppress iris warning
iris.FUTURE.date_microseconds = True

def parse_args():
    """
    Parse command-line arguments
    """
    parser = argparse.ArgumentParser(
        description='Recmorise ECE3 CMIP6 cmorised data towards ECE3 CMIP7 cmorised data.'
    )
    # Posisional arguments
    parser.add_argument('table'               , metavar='cmip6_table'    , type=str                     , help='The CMIP6 table    of the variable to convert, for instance: Amon')
    parser.add_argument('var'                 , metavar='cmip6_variable' , type=str                     , help='The CMIP6 variable of the variable to convert, for instance: tas.')
    # Optional input arguments
    parser.add_argument('-v', '--verbose'     , action='store_true'                                     , help="Verbose messaging (default off)")
    parser.add_argument('-d', '--debug'       , action='store_true'                                     , help="Debug   messaging (default off)")
    parser.add_argument('-e', '--stderr'      , action='store_true'                                     , help="Duplicate the basic message to the stderr (default off)")
    parser.add_argument('-l', '--filelocking' , action='store_true'                                     , help="HDF5 file locking (default False, which is often required on HPC platforms)")
    parser.add_argument('-o', '--omit'        , action='store_true'                                     , help="Omit the variables: 6hrPlevPt ta, ua & va (default False)")
    parser.add_argument('-t', '--tmpdir'      , metavar='tmpdir'         , type=str, default='./tmpdir' , help='Temporary directory [default: ./tmpdir]')
    parser.add_argument('-i', '--year1'       , metavar='year1'          , type=int, default=None       , help='The first year to process [default: None]')
    parser.add_argument('-j', '--year2'       , metavar='year2'          , type=int, default=None       , help='The last  year to process [default: None]')
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
 if   list_of_dimensions in ['time', 'time1', 'time2', 'time3', 'time4'] : return  1  # Without time3 here it wordks as well for variables like Amon rsdt
 elif list_of_dimensions in ['latitude', 'gridlatitude']                 : return  4
 elif list_of_dimensions == 'longitude'                                  : return  5
 elif list_of_dimensions == 'basin'                                      : return  2
 else:                                                                     return  3  # The vertical coordinate has to be before the latitude & longitude


def add_dimension(var_cube, coordinates_file, dim, dim_standard_name):
    # Construct time coordinate in a way that we can update with points and bounds later
    if dim in ['time']:
     cmordim = cmor.axis(dim, \
                         units=dimension_attribute(coordinates_file, dim, 'units'))
    elif dim in ['time1', 'time2', 'time3', 'time4']:
     cmordim = cmor.axis(dim, \
                         units=dimension_attribute(coordinates_file, dim_standard_name, 'units'))
    elif dim in ['latitude', 'longitude', 'plev19', 'plev3', 'landuse', 'sdepth', 'depth_coord', 'gridlatitude', 'basin', 'osurf', 'iceband']:
     if debug:
      print('\nINFO 1 from add_dimension:\n{}'  .format(var_cube))
      print('\nINFO 2 from add_dimension:\n{}\n'.format(var_cube.coord(dim_standard_name)))
     cmordim = cmor.axis(dim,                                                           \
                         coord_vals =var_cube.coord(dim_standard_name).points,          \
                         cell_bounds=var_cube.coord(dim_standard_name).bounds,          \
                         units      =dimension_attribute(coordinates_file, dim, 'units'))
    elif dim in ['vegtype']:
     cmordim = cmor.axis(dim, \
                         coord_vals = var_cube.coord(dimensions=1).points, \
                         units      = dimension_attribute(coordinates_file, dim, 'units'))
    elif dim in ['olevel']:
     cmordim = cmor.axis('depth_coord', \
                         coord_vals = var_cube.coord('depth').points, \
                         cell_bounds= var_cube.coord('depth').bounds,          \
                         units      = dimension_attribute(coordinates_file, 'depth_coord', 'units'))
    else:
     cmordim = None
    return cmordim



def main():

    global verbose
    global debug

    args = parse_args()

    cmip6_table          = args.table
    cmip6_variable       = args.var
    file_locking         = args.filelocking
    verbose              = args.verbose
    debug                = args.debug
    duplicate_for_stderr = args.stderr
    omit_variables       = args.omit
    tmpdir               = args.tmpdir
    year1                = args.year1
    year2                = args.year2
    if year1 and not year2: year2=year1
    if year2 and not year1: year1=year2
    
    if year1:
        if year1 > year2:
            print('\n Stop from {}: The starting year {} is later than the ending year {}\n'.format(sys.argv[0], year1, year2))
            sys.exit()

    if verbose:
        print(' The CMIP7 dreq python api version is: v{}'  .format(version('CMIP7_data_request_api')))
        print(' The CMOR       python api version is: v{}\n'.format(version('cmor'                  )))

    # Prevent the CMOR Warning in case this directory is not existing yet:
    root_of_output_path = Path(OUTPUT_CMIP7_ROOT).parts[0] + Path(OUTPUT_CMIP7_ROOT).parts[1]
    if not os.path.isdir(root_of_output_path):
        print("\n ERROR from {}: Can't create the ouput directory:\n  {}\n because the root directory  {}  does not exist.\n".format(sys.argv[0], OUTPUT_CMIP7_ROOT, root_of_output_path))
        sys.exit()
    os.makedirs(OUTPUT_CMIP7_ROOT, exist_ok=True)

    # Create the directory which will contain the varlists and the CMOR metadata json input files:
    os.makedirs(tmpdir, exist_ok=True)

    # Check if the file exists and is a file
    if not os.path.isfile(cmip7_cmip6_mapping_filename):
        print('\n ERROR: The file {:} does not exist, therefore first run:\n  ./cmip6-cmip7-variable-mapping.py -r v1.2.2.3\n'.format(cmip7_cmip6_mapping_filename))
        sys.exit()

    # Load the XML file with the CMIP7 - CMIP6 mapping and all CMIP7 attributes:
    tree_cmip7_variables = ET.parse(cmip7_cmip6_mapping_filename)
    root_cmip7_variables = tree_cmip7_variables.getroot()

    if file_locking:
     os.environ["HDF5_USE_FILE_LOCKING"] = "TRUE"
    else:
     os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"
    if verbose:
     print(' HDF5_USE_FILE_LOCKING = {}\n'.format(file_locking))

    # handle exceptions in CMIP7 - CMIP6 mapping tables
    if cmip6_table in ['day'] and cmip6_variable in ['ta','ua','va','hur','hus','wap','zg']:
        print(' Sorry, {} {:3} was saved on plev8 for CMIP6 but for CMIP7 this is requested on plev19'.format(cmip6_table, cmip6_variable))
        sys.exit()
    elif cmip6_table in ['Omon'] and cmip6_variable in ['soga','thetaoga']:
        print(" Sorry, {} {:3} can't be recmorised because the 3D fied was not saved in the CMIP6 output.".format(cmip6_table, cmip6_variable))
        sys.exit()
    elif cmip6_table == 'Eday'    and cmip6_variable in ['ta','ua','va','hus','wap','zg']:
        xpath_expression = './/variable[@cmip6_compound_name="' + 'day'       + '.' + cmip6_variable + '"]'
    elif cmip6_table == 'LPJGday' and cmip6_variable in ['mrsll','tsl','mrsol']:
        xpath_expression = './/variable[@cmip6_compound_name="' + 'Eday'      + '.' + cmip6_variable + '"]'
    elif cmip6_table == 'LPJGday' and cmip6_variable in ['mrro','mrsos','mrso']:
        xpath_expression = './/variable[@cmip6_compound_name="' + 'day'       + '.' + cmip6_variable + '"]'
    elif cmip6_table == 'LPJGmon' and cmip6_variable in ['evspsbl','fco2nat']:
        xpath_expression = './/variable[@cmip6_compound_name="' + 'Amon'      + '.' + cmip6_variable + '"]'
    elif cmip6_table == 'LPJGmon' and cmip6_variable in ['evspsblsoi','mrfso','mrros','mrro','mrso','mrsos','tran','tsl']:
        xpath_expression = './/variable[@cmip6_compound_name="' + 'Lmon'      + '.' + cmip6_variable + '"]'
    elif cmip6_table == 'LPJGmon' and cmip6_variable in ['evspsblpot','mrsll','mrsol','mrsosLut']:
        xpath_expression = './/variable[@cmip6_compound_name="' + 'Emon'      + '.' + cmip6_variable + '"]'
    elif cmip6_table == 'LPJGmon' and cmip6_variable in ['snc','snd','snw']:
        xpath_expression = './/variable[@cmip6_compound_name="' + 'LImon'     + '.' + cmip6_variable + '"]'
    elif cmip6_table == 'SImon'   and cmip6_variable in ['sfdsi']:
        xpath_expression = './/variable[@cmip6_compound_name="' + 'Omon'      + '.' + cmip6_variable + '"]'
    elif cmip6_table == 'Omon'   and cmip6_variable in ['hfx','hfy']:
        xpath_expression = './/variable[@cmip6_compound_name="' + 'Omon'      + '.' + cmip6_variable + 'int"]'
    else:
        xpath_expression = './/variable[@cmip6_compound_name="' + cmip6_table + '.' + cmip6_variable + '"]'
        # For plev3 cases like: ta_tpt-p3-hxy-air, ua_tpt-p3-hxy-air & va_tpt-p3-hxy-air
        if cmip6_table in ['6hrPlevPt'] and cmip6_variable in ['ta','ua', 'va']:
            if omit_variables:
             print(' WARNING: The omit_variables option is active, therefore omitting {} {}'.format(cmip6_table, cmip6_variable))
             sys.exit()

    match = False
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
        cmip7_long_name       = element.get('long_name')
        if verbose:
            print(' {:12} {:18}  ==>  cmip7_compound_name={:50} branded_variable_name={:40} units={:20} frequency={:10} region={:15} realm={:15} long_name={}'.format( \
                    cmip6_table                , \
                    cmip6_variable             , \
                    '"' + cmip7_compound_name   + '"', \
                    '"' + branded_variable_name + '"', \
                    '"' + cmip7_units           + '"', \
                    '"' + cmip7_frequency       + '"', \
                    '"' + cmip7_region          + '"', \
                    '"' + cmip7_realm           + '"', \
                    '"' + cmip7_long_name       + '"'))
        else:
            print(' {:12} {:18}  ==>  cmip7_compound_name={:50} branded_variable_name={:36} units={:15} long_name={}'.format( \
                    cmip6_table                , \
                    cmip6_variable             , \
                    '"' + cmip7_compound_name   + '"', \
                    '"' + branded_variable_name + '"', \
                    '"' + cmip7_units           + '"', \
                    '"' + cmip7_long_name       + '"'))
        # Also write this to the stderr output:
        if duplicate_for_stderr:
         sys.stderr.write(' {:12} {:18}  ==>  cmip7_compound_name={:50} branded_variable_name={:36} units={:15} long_name={}\n'.format( \
                     cmip6_table                , \
                     cmip6_variable             , \
                     '"' + cmip7_compound_name   + '"', \
                     '"' + branded_variable_name + '"', \
                     '"' + cmip7_units           + '"', \
                     '"' + cmip7_long_name       + '"'))

    else: # The for-else:
        if not match:
         print(' Sorry, no CMIP7 equivalent for: {:12} {}'.format(cmip6_table, cmip6_variable))
         sys.exit()


    # Overwrite grid label when::

    if   cmip6_variable in ['co2s', 'co2mass']:
        grid_label = 'gm'
    elif cmip6_variable in ['siconca']:
        grid_label = 'gr'
    elif cmip7_realm    in ['ocean', 'seaIce', 'ocnBgchem']:
        grid_label = 'gn'
    else:
        grid_label = 'gr'

    # Load all existing data of the considered variable as a single iris cube:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
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
        else:
            cubelist = iris.load(matched_cmip6_files)
            if verbose:
                print('\n The files detected for this time interval are:')
                for matched_cmip6_file in matched_cmip6_files:
                    print('  {}'.format(matched_cmip6_file))
                print()

        # strip attributes, this is needed for concatenation
        for i in cubelist:
            i.attributes = {}

        try:
            var_cube_all = cubelist.concatenate_cube()
        except:
            if verbose: print(' Problem with lon/lat, so use the lon/lat from the first file.')
            for i in cubelist[1:]:
                for dim_coord in ['longitude','latitude']:
                    i.coord(dim_coord).points = cubelist[0].coord(dim_coord).points
                    i.coord(dim_coord).bounds = cubelist[0].coord(dim_coord).bounds
            var_cube_all = cubelist.concatenate_cube()

    # loop over chunks of given length
    if 'yr' in cmip6_table or 'fx' in cmip6_table:
        tsteps_per_year = 1
    elif 'mon' in cmip6_table:
        tsteps_per_year = 12
    elif 'day' in cmip6_table:
        tsteps_per_year = 365.25
    elif '6h' in cmip6_table:
        tsteps_per_year = 365.25 * 4
    elif '3h' in cmip6_table:
        tsteps_per_year = 365.25 * 8
    else:
        print(' Stop: unknown timestep of {}'.format(cmip6_table))
        sys.exit()

    # use NEMO 3-d grid to dimension the output
    # 7 years with monthly means results in ~1 GB
    grdpts = math.prod(var_cube_all.shape[-2:])
    if var_cube_all.ndim <=3:
        nlevs = 1
    else:
        nlevs = var_cube_all.shape[1]
    nyears = int((12*75*362*262)/(nlevs*grdpts*tsteps_per_year) * 7)
    # select 1, 5, or multiple of 10 yrs (up to 50 yrs)
    if   nyears < 5:
         nyears = 1
    elif nyears < 10:
         nyears = 5
    elif nyears < 20:
         nyears = 10
    elif nyears < 50:
         nyears = 20
    else:
         nyears = 50
    if verbose:
        print(' Output will be saved in files with maximum {} years in each'.format(nyears))

    if not 'fx' in cmip6_table:
        time_axis = var_cube_all.coord('time').units.num2date(var_cube_all.coord('time').points)
        first_year = int(time_axis[0].strftime("%Y"))
        last_year  = int(time_axis[-1].strftime("%Y"))
    else:
        first_year = 1
        last_year = 1
    for y in range(int(first_year/nyears)*nyears,last_year+1,nyears):
        if not 'fx' in cmip6_table:
            if year1:
                if max(y,year1)>min(y+nyears,year2): continue
                time1=cftime.datetime(max(y,year1),1,1)
                time2=cftime.datetime(min(y+nyears,year2+1),1,1)
            else:
                time1=cftime.datetime(y,1,1)
                time2=cftime.datetime(y+nyears,1,1)
            if verbose: print(' Process time chunk from {} to {}'.format(time1, time2))
            var_cube = var_cube_all.extract(iris.Constraint(time=lambda cell: time1<= cell.point <time2))
        else:
            var_cube = var_cube_all

        # Initiate CMOR:
        cmor.setup(inpath=cmip7_cmor_tables_dir, netcdf_file_action=cmor.CMOR_REPLACE)

        DATASET_INFO = {
            "_AXIS_ENTRY_FILE"           : cmip7_cmor_tables_dir + 'CMIP7_coordinate.json',
            "_FORMULA_VAR_FILE"          : cmip7_cmor_tables_dir + 'CMIP7_formula_terms.json',
            "_cmip7_option"              : 1,
            "_controlled_vocabulary_file": cmip7_cmor_tables_cvs_dir + 'cmor-cvs.json',
            "activity_id"                : activity_id,
            "branch_method"              : "standard",
            "branch_time_in_child"       : branch_time_in_child,
            "branch_time_in_parent"      : branch_time_in_parent,
            "calendar"                   : "proleptic_gregorian",
            "drs_specs"                  : "MIP-DRS7",
            "data_specs_version"         : "MIP-DS7.0.0.0",
            "experiment_id"              : experiment_id,
            "forcing_index"              : ripf_f,
            "grid"                       : "N96",                                 # check
            "grid_label"                 : "g999",                                # check: currently using a DEMO number
            "initialization_index"       : ripf_i,
            "institution_id"             : institution_id,
            "license_id"                 : "CC-BY-4.0",
            "nominal_resolution"         : "100 km",
            "outpath"                    : OUTPUT_CMIP7_ROOT,
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

        no_time_dimension = True
        for var_dimension in sorted_cmip7_dimensions:
            if var_dimension in ['time', 'time1', 'time2', 'time3', 'time4']:
                no_time_dimension = False
        if verbose:
            if no_time_dimension:
                print('\n This variable has no time dimension.\n')

        # Looking around in the CMIP7 coordinates of the considered variable:
        if debug:
            print('\n The dimensions: {}'.format(sorted_cmip7_dimensions))
            for var_dimension in sorted_cmip7_dimensions:
                if var_dimension not in ['time', 'longitude', 'latitude']:
                    print_dimension_attributes_with_values(cmip7_coordinates, var_dimension)

        if 'deltasigt' in sorted_cmip7_dimensions:
            sorted_cmip7_dimensions.remove('deltasigt') # Remove a vertical coorinate for mlotst_tavg-u-hxy-sea

        dataset_info_file = '{}/{}-{}-input.json'.format(tmpdir, cmip7_compound_name, experiment_id)
        with open(dataset_info_file, 'w') as fh:
            json.dump(DATASET_INFO, fh, indent=2)

        cmor.dataset_json(dataset_info_file)

        cmor.load_table(cmor_table_of_selected_realm)



        # Define the CMOR variable object
        variable_attrib = variable_attribute(cmip7_cmor_table_with_var, branded_variable_name, 'positive')

        # In case of the ocean grid:
        if cmip7_realm in ['ocean', 'seaIce', 'ocnBgchem'] and \
        'longitude' in sorted_cmip7_dimensions             and \
        'latitude'  in sorted_cmip7_dimensions:
            orca_grid_case = True
            if cmip6_variable in ['siconca']:
                orca_grid_case = False
        else:
            orca_grid_case = False

        if orca_grid_case:
            if   'time'  in sorted_cmip7_dimensions:
                name_time_dim = 'time'
            elif 'time1' in sorted_cmip7_dimensions:
                name_time_dim = 'time1'
            elif 'time2' in sorted_cmip7_dimensions:
                name_time_dim = 'time2'
            elif 'time3' in sorted_cmip7_dimensions:
                name_time_dim = 'time3'
            elif 'time4' in sorted_cmip7_dimensions:
                name_time_dim = 'time4'
            else:
                name_time_dim = None
                if verbose:
                 print('\n No time dimension for ORCA grid case.\n')

            if not no_time_dimension:
                dim_standard_name = dimension_attribute(cmip7_coordinates, name_time_dim, 'standard_name')
                time_axis_id = add_dimension(var_cube, cmip7_coordinates, name_time_dim, dim_standard_name)

            vertical_ocean_coordinate = False
            # ORCA cases without a time dimension are not covered yet:
            if len(sorted_cmip7_dimensions) >= 2:
                for dimension in sorted_cmip7_dimensions:
                    if dimension not in [name_time_dim, 'longitude', 'latitude', 'osurf', 'depth100m', 'gridlatitude', 'basin']:
                        vertical_ocean_coordinate = True
                        dim_standard_name = dimension_attribute(cmip7_coordinates, dimension, 'standard_name')
                        vertical_dim_id = add_dimension(var_cube, cmip7_coordinates, dimension, dim_standard_name)
                        if verbose:
                            print('\n The vertical ocean coordinate {} has a standard_name="{}".\n Note that currently depth_coord is used instead of the ocean coordinate name.\n'.format(dimension, dim_standard_name))

                # Here load the grids table to set up x and y axes and the lat-long grid:
                cmor.load_table('CMIP7_grids.json')

                y_axis_id = cmor.axis(table_entry='j_index',coord_vals=np.arange(292),units="1")
                x_axis_id = cmor.axis(table_entry='i_index',coord_vals=np.arange(362),units="1")
                grid_id   = cmor.grid(axis_ids=[y_axis_id, x_axis_id],
                                    latitude=var_cube.coord('latitude').points,
                                    longitude=var_cube.coord('longitude').points,
                                    latitude_vertices=var_cube.coord('latitude').bounds,
                                    longitude_vertices=var_cube.coord('longitude').bounds)

                # Load again the realm table of the variable:
                cmor.load_table(cmor_table_of_selected_realm)
                if no_time_dimension:
                    if vertical_ocean_coordinate:
                        cmorvar = cmor.variable(branded_variable_name, cmip7_units, axis_ids=[              vertical_dim_id, grid_id], positive=variable_attrib)
                    else:
                        cmorvar = cmor.variable(branded_variable_name, cmip7_units, axis_ids=[                               grid_id], positive=variable_attrib)
                else:
                    if vertical_ocean_coordinate:
                        cmorvar = cmor.variable(branded_variable_name, cmip7_units, axis_ids=[time_axis_id, vertical_dim_id, grid_id], positive=variable_attrib)
                    else:
                        cmorvar = cmor.variable(branded_variable_name, cmip7_units, axis_ids=[time_axis_id,                  grid_id], positive=variable_attrib)
        else:

            # Define the CMOR variable object

            cmoraxes = []
            if verbose: print('\n Dimensions:')
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
        cmor.set_variable_attribute(cmorvar, 'cell_measures', 'c', value_cell_measures)

        # Override long names if necessary
        with open(cmip7_cmor_tables_dir + 'CMIP7_long_name_overrides.json') as fh:
            long_name_overrides = json.load(fh)
        if cmip7_compound_name in long_name_overrides['long_name_overrides']:
            new_value_long_name = long_name_overrides['long_name_overrides'][cmip7_compound_name]
            cmor.set_variable_attribute(cmorvar, 'long_name', 'c', new_value_long_name)


        # Slice up data into N time record chunks and push through CMOR.write
        if not no_time_dimension:
            N = max(1,min(64,int(75/nlevs*10/12)*12))
            if verbose:
                print(' Chunksize for time record: {}'.format(N))
            ntimes = len(var_cube.coord('time').points)
            for i in range(0, ntimes, N):
                s = slice(i, i+N)
                cube_slice = var_cube[s]
                cmor.write(cmorvar, cube_slice.data, time_vals=cube_slice.coord('time').points
                                                   , time_bnds=cube_slice.coord('time').bounds)
        else:
            cmor.write(cmorvar, var_cube.data)

        # Close the file (sorts the full naming)
        fname = cmor.close(cmorvar, file_name=True)
        if verbose:
            print('\n View result with:\n  ncview {}\n'.format(fname))

if __name__ == '__main__':
    main()
