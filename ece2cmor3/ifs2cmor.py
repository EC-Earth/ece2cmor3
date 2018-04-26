import logging
import os

import dateutil.relativedelta

from ece2cmor3 import grib_filter, cmor_source, cmor_target, cmor_task, cmor_utils
from ece2cmor3.postproc import grids, factory

# Logger construction
log = logging.getLogger(__name__)

# Experiment name
exp_name_ = None

# Table root
table_root_ = None

# Files that are being processed in the current execution loop.
ifs_gridpoint_file_ = None
ifs_spectral_file_ = None
ifs_init_gridpoint_file_ = None

# IFS surface pressure grib codes
surface_pressure = cmor_source.grib_code(134)
ln_surface_pressure = cmor_source.grib_code(152)

# IFS grid description data
ifs_grid_descr_ = {}

# Start date of the processed data
start_date_ = None

# Output interval. Denotes the output file periods.
output_interval_ = None

# Output frequency (hrs). Minimal interval between output variables.
output_frequency_ = 6

# Fast storage temporary path
temp_dir_ = os.getcwd()
tempdir_created_ = False
max_size_ = float("inf")

# Reference date, times will be converted to hours since refdate
ref_date_ = None

# Available geospatial masks, assigned by ece2cmorlib
masks = {}


# Initializes the processing loop.
def initialize(path, expname, tableroot, start, length, refdate, interval=dateutil.relativedelta.relativedelta(month=1),
               outputfreq=6, tempdir=None):
    global log, exp_name_, table_root_, ifs_gridpoint_file_, ifs_spectral_file_, ifs_init_gridpoint_file_, \
        output_interval_, ifs_grid_descr_, temp_dir_, tempdir_created_, max_size_, ref_date_, start_date_, \
        output_frequency_

    exp_name_ = expname
    table_root_ = tableroot
    start_date_ = start
    output_interval_ = interval
    output_frequency_ = outputfreq
    ref_date_ = refdate

    datafiles = select_files(path, exp_name_, start, length)
    inifiles = [f for f in datafiles if os.path.basename(f) == "ICMGG" + exp_name_ + "+000000"]
    gpfiles = [f for f in datafiles if os.path.basename(f).startswith("ICMGG")]
    shfiles = [f for f in datafiles if os.path.basename(f).startswith("ICMSH")]
    if len(gpfiles) > 1 or len(shfiles) > 1:
        # TODO: Support postprocessing over multiple files
        log.warning("Expected a single grid point and spectral file in %s, found %s and %s; \
                     will take first file of each list." % (path, str(gpfiles), str(shfiles)))
    ifs_gridpoint_file_ = gpfiles[0] if len(gpfiles) > 0 else None
    ifs_spectral_file_ = shfiles[0] if len(shfiles) > 0 else None
    if any(inifiles):
        ifs_init_gridpoint_file_ = inifiles[0]
        if len(inifiles) > 1:
            log.warning("Multiple initial gridpoint files found, will proceed with %s" % ifs_init_gridpoint_file_)
    else:
        ifs_init_gridpoint_file_ = ifs_gridpoint_file_
    if tempdir:
        temp_dir_ = os.path.abspath(tempdir)
        if not os.path.exists(temp_dir_):
            os.makedirs(temp_dir_)
            tempdir_created_ = True
    grib_filter.initialize(ifs_gridpoint_file_, ifs_spectral_file_, temp_dir_)
    return True


# Execute the postprocessing+cmorization tasks.
def execute(tasks):
    global log, tempdir_created_, start_date_, ifs_grid_descr_
    supported_tasks = [t for t in filter_tasks(tasks) if t.status == cmor_task.status_initialized]
    factory.table_root, factory.masks = table_root_, masks
    for task in supported_tasks:
        first_operator, last_operator = factory.create_operators(task)
        if first_operator is not None and last_operator is not None:
            grib_filter.task_operators[task] = first_operator
            grib_filter.cmor_operators[task] = last_operator
            key = getattr(last_operator, "store_var_key", None)
            if key in grib_filter.store_vars:
                grib_filter.store_vars[key].append(last_operator)
            elif key is not None:
                grib_filter.store_vars[key] = [last_operator]
            key = getattr(last_operator, "mask_var_key", None)
            if key in grib_filter.mask_vars:
                grib_filter.mask_vars[key].append(last_operator)
            elif key is not None:
                grib_filter.mask_vars[key] = [last_operator]
    log.info("Executing %d IFS tasks..." % len(supported_tasks))
    grib_filter.execute(supported_tasks, start_date_.month)


# Creates a sub-list of tasks that we believe we can successfully process
def filter_tasks(tasks):
    global log
    log.info("Inspecting %d tasks." % len(tasks))
    result = []
    for task in tasks:
        tgtdims = getattr(task.target, cmor_target.dims_key, []).split()
        haslat = "latitude" in tgtdims
        haslon = "longitude" in tgtdims
        if (haslat and haslon) or (not haslat and not haslon):
            result.append(task)
        else:
            # TODO: Support zonal variables
            log.error("Variable %s has unsupported combination of dimensions %s and will be skipped." % (
                task.target.variable, tgtdims))
    log.info("Validated %d tasks for processing." % len(result))
    return result


# Retrieves all IFS output files in the input directory.
def select_files(path, expname, start, length):
    allfiles = cmor_utils.find_ifs_output(path, expname)
    start_date = cmor_utils.make_datetime(start).date()
    end_date = cmor_utils.make_datetime(start + length).date()
    return [f for f in allfiles if f.endswith("ICMGG" + expname + "+000000") or
            (end_date > cmor_utils.get_ifs_date(f) >= start_date)]
