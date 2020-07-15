import datetime
import json
import logging
import os
import re
import resource
import threading

import numpy

from ece2cmor3 import cmor_target, cmor_source, cmor_task, cmor_utils, grib_file, cdoapi

# Log object.
log = logging.getLogger(__name__)

gridpoint_files = {}
spectral_files = {}
ini_gridpoint_file = None
ini_spectral_file = None
temp_dir = None
accum_key = "ACCUMFLD"
accum_codes = []
varsfreq = {}
spvar = None
fxvars = []

starttimes = {}


# Initializes the module, looks up previous month files and inspects the first
# day in the input files to set up an administration of the fields.
def update_sp_key(fname):
    global spvar
    for key in varsfreq:
        freq = varsfreq[key]
        if key[0] == 154:
            if spvar is None or spvar[1] >= freq:
                spvar = (154, freq, fname)
        if key[0] == 134:
            if spvar is None or spvar[1] > freq:
                spvar = (134, freq, fname)


def initialize(gpfiles, shfiles, tmpdir, ini_gpfile=None, ini_shfile=None):
    global gridpoint_files, spectral_files, ini_gridpoint_file, ini_spectral_file, temp_dir, varsfreq, accum_codes
    grib_file.initialize()
    gridpoint_files = {d: (get_prev_file(gpfiles[d]), gpfiles[d]) for d in gpfiles.keys()}
    spectral_files = {d: (get_prev_file(shfiles[d]), shfiles[d]) for d in shfiles.keys()}
    ini_gridpoint_file, ini_spectral_file = ini_gpfile, ini_shfile
    temp_dir = tmpdir
    accum_codes = load_accum_codes(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "grib_codes.json"))
    gpdate = sorted(gridpoint_files.keys())[0] if any(gridpoint_files) else None
    shdate = sorted(spectral_files.keys())[0] if any(spectral_files) else None
    gpfile = gridpoint_files[gpdate][1] if any(gridpoint_files) else None
    shfile = spectral_files[shdate][1] if any(spectral_files) else None
    if gpfile is not None:
        with open(gpfile) as gpf:
            varsfreq.update(inspect_day(grib_file.create_grib_file(gpf), grid=cmor_source.ifs_grid.point))
            update_sp_key(gpfile)
    if shfile is not None:
        with open(shfile) as shf:
            varsfreq.update(inspect_day(grib_file.create_grib_file(shf), grid=cmor_source.ifs_grid.spec))
            update_sp_key(shfile)
    if ini_gpfile is not None:
        with open(ini_gpfile) as gpf:
            fxvars.extend(inspect_hr(grib_file.create_grib_file(gpf), grid=cmor_source.ifs_grid.point))
    if ini_shfile is not None:
        with open(ini_shfile) as shf:
            fxvars.extend(inspect_hr(grib_file.create_grib_file(shf), grid=cmor_source.ifs_grid.spec))


# Function reading the file with grib-codes of accumulated fields
def load_accum_codes(path):
    global accum_key
    data = json.loads(open(path).read())
    if accum_key in data:
        return map(grib_tuple_from_string, data[accum_key])
    else:
        return []


# Utility to make grib tuple of codes from string
def grib_tuple_from_string(s):
    codes = s.split('.')
    return int(codes[0]), 128 if len(codes) < 2 else int(codes[1])


# Utility to make grib tuple of codes from string
def grib_tuple_from_int(i):
    if i < 256:
        return i, 128
    return i % 10 ** 3, i / 10 ** 3


# Inspects a single time point in the initial file
def inspect_hr(gribfile, grid):
    result = []
    while gribfile.read_next(headers_only=True):
        result.append(get_record_key(gribfile, grid) + (grid,))
    return result


# Inspects the first 24 hours in the input gridpoint and spectral files.
def inspect_day(gribfile, grid):
    inidate, initime = -99, -1
    records = {}
    while gribfile.read_next(headers_only=True):
        date = gribfile.get_field(grib_file.date_key)
        time = gribfile.get_field(grib_file.time_key) / 100
        if date == inidate + 1 and time == initime:
            break
        if inidate < 0:
            inidate = date
        if initime < 0:
            initime = time
        key = get_record_key(gribfile, grid) + (grid,)
        if key in records:
            if time not in records[key]:
                records[key].append(time)
        else:
            records[key] = [time]
        gribfile.release()
    result = {}
    for key, val in records.iteritems():
        hrs = numpy.array(val)
        if len(hrs) == 1:
            log.warning("Variable %d.%d on level %d of type %d has been detected once in first day "
                        "of file %s... Assuming daily frequency" % (key[0], key[1], key[3], key[2],
                                                                    gribfile.file_object.name))
            frqs = numpy.array([24])
        else:
            frqs = numpy.mod(hrs[1:] - hrs[:-1], numpy.repeat(24, len(hrs) - 1))
        frq = frqs[0]
        if any(frqs != frq):
            log.error("Variable %d.%d on level %d of type %d is not output on regular "
                      "intervals in first day in file %s" % (key[0], key[1], key[3], key[2], gribfile.file_object.name))
        else:
            result[key] = frq
    return result


# TODO: Merge the 2 functions below into one matching function:

# Creates a key (code + table + level type + level) for a grib message iterator
def get_record_key(gribfile, gridtype):
    codevar, codetab = grib_tuple_from_int(gribfile.get_field(grib_file.param_key))
    levtype, level = gribfile.get_field(grib_file.levtype_key), gribfile.get_field(grib_file.level_key)
    if levtype == grib_file.pressure_level_hPa_code:
        level *= 100
        levtype = grib_file.pressure_level_Pa_code
    if levtype == 112 or levtype == grib_file.depth_level_code:
        level = 0
        levtype = grib_file.depth_level_code
    if codevar in [49, 165, 166]:
        level = 10
        levtype = grib_file.height_level_code
    if codevar in [167, 168, 201, 202]:
        level = 2
        levtype = grib_file.height_level_code
    if codevar == 9:
        level = 0
        levtype = grib_file.surface_level_code
    if levtype == grib_file.pv_level_code:  # Mapping pv-levels to surface: we don't support more than one pv-level
        level = 0
        levtype = grib_file.surface_level_code
    # Fix for spectral height level fields in gridpoint file:
    if cmor_source.grib_code(codevar) in cmor_source.ifs_source.grib_codes_sh and \
            gridtype != cmor_source.ifs_grid.spec and \
            levtype == grib_file.hybrid_level_code:
        levtype = grib_file.height_level_code
    return codevar, codetab, levtype, level


# Used to distribute keys created above over cmor tasks
def soft_match_key(varid, tabid, levtype, level, gridtype, keys):
    if (varid, tabid, levtype, level, gridtype) in keys:
        return varid, tabid, levtype, level, gridtype
    # Fix for orog and ps: find them in either GG or SH file
    if varid in [134, 129] and tabid == 128 and levtype == grib_file.surface_level_code and level == 0:
        matches = [k for k in keys if k[0] == varid and k[1] == tabid and k[2] == grib_file.surface_level_code]
        if any(matches):
            return matches[0]
        matches = [k for k in keys if k[0] == varid and k[1] == tabid and k[2] == grib_file.hybrid_level_code and
                   k[3] == 0]
        if any(matches):
            return matches[0]
    # Fix for depth levels variables
    if levtype == grib_file.depth_level_code:
        matches = [k for k in keys if k[0] == varid and k[1] == tabid and k[2] == grib_file.depth_level_code]
        if any(matches):
            return matches[0]
    if levtype == grib_file.hybrid_level_code and level == -1:
        matches = [k for k in keys if k[0] == varid and k[1] == tabid and k[2] == grib_file.hybrid_level_code and
                   k[4] == gridtype]
        if any(matches):
            return matches[0]
    # Fix for spectral fields at height levels being written as model level fields in GG file
    if levtype == grib_file.height_level_code and gridtype == cmor_source.ifs_grid.spec:
        matches = [k for k in keys if k[:4] == (varid, tabid, grib_file.height_level_code, level)]
        if any(matches):
            return matches[0]
    return None


# Converts cmor-levels to grib levels code
def get_levels(task, code):
    global log
    # Special cases
    if code.tab_id == 128:
        gc = code.var_id
        if gc in [9, 134]:
            return grib_file.surface_level_code, [0]
        if gc in [35, 36, 37, 38, 39, 40, 41, 42, 139, 170, 183, 236]:
            return grib_file.depth_level_code, [0]
        if gc in [49, 165, 166]:
            return grib_file.height_level_code, [10]
        if gc in [167, 168, 201, 202]:
            return grib_file.height_level_code, [2]
    # Normal cases
    zaxis, levels = cmor_target.get_z_axis(task.target)
    if zaxis is None:
        return grib_file.surface_level_code, [0]
    if zaxis in ["sdepth"]:
        return grib_file.depth_level_code, [0]
    if zaxis in ["alevel", "alevhalf"]:
        return grib_file.hybrid_level_code, [-1]
    if zaxis == "air_pressure":
        return grib_file.pressure_level_Pa_code, [int(float(level)) for level in levels]
    if zaxis in ["height", "altitude"]:
        return grib_file.height_level_code, [int(float(level)) for level in levels]  # TODO: What about decimal places?
    log.error("Could not convert vertical axis type %s to grib vertical coordinate "
              "code for %s" % (zaxis, task.target.variable))
    return -1, []


# Searches the file system for the previous month file, necessary for the 0-hour
# fields.
def get_prev_file(grb_file):
    fname = os.path.basename(grb_file)
    exp, year, mon = fname[5:9], int(fname[10:14]), int(fname[14:16])
    if mon == 1:
        prev_year, prev_mon = year - 1, 12
    else:
        prev_year, prev_mon = year, mon - 1
    output_dir = os.path.abspath(os.path.join(os.path.dirname(grb_file), ".."))
    output_files = cmor_utils.find_ifs_output(output_dir, exp)
    ini_path = None
    for output_path in output_files:
        output_name = os.path.basename(output_path)
        if output_name == fname[:9] + "+000000":
            ini_path = output_path
        if output_name[:10] == fname[:10] and int(output_name[10:14]) == prev_year and \
                int(output_name[14:]) == prev_mon:
            log.info("Found previous month file for %s: %s" % (grb_file, output_path))
            return output_path
    ece_leg = os.path.split(os.path.dirname(grb_file))[-1]
    if re.match(r"^0*\d1$", ece_leg): # First leg
        if ini_path is None:
            log.error("Previous month file for %s could not be found because the initial state file hasn't been found"
                      % grb_file)
        else:
            log.info("Assumed previous month file for %s: %s" % (grb_file, ini_path))
    else:
        if ini_path is None:
            log.error("Previous month file for %s could not be found" % grb_file)
        else:
            log.error("Assumed previous month file for %s: %s, this is probably not correct!" % (grb_file, ini_path))
    return ini_path


# Splits the grib file for the given set of tasks
def mkfname(key):
    return '.'.join([str(key[0]), str(key[1]), str(key[2])])


# Construct files for keys and tasks
def cluster_files(valid_tasks, varstasks):
    task2files, task2freqs = {}, {}
    varsfx = set()
    for task in valid_tasks:
        task2files[task] = set()
        task2freqs[task] = set()
        for key, tsklist in varstasks.iteritems():
            if task in tsklist:
                task2files[task].add('.'.join([str(key[0]), str(key[1]), str(key[2])]))
                if key[3] == -1:
                    task2freqs[task].update([varsfreq[k] for k in varsfreq.keys() if
                                             (k[0], k[1], k[2]) == (key[0], key[1], key[2])])
                else:
                    if key in varsfreq:
                        task2freqs[task].add(varsfreq[key])
                    elif key in fxvars:
                        varsfx.add(key)
    for task, fnames in task2files.iteritems():
        codes = {(int(f.split('.')[0]), int(f.split('.')[1])): f for f in sorted(list(fnames))}
        cum_file = '_'.join([codes[k] for k in codes if k in accum_codes])
        inst_file = '_'.join([codes[k] for k in codes if k not in accum_codes])
        task2files[task] = filter(None, [cum_file, inst_file])
    for task, freqset in task2freqs.iteritems():
        maxfreq = max(freqset) if len(freqset) > 0 else 0
        if any([f for f in freqset if maxfreq % f != 0]):
            log.error("Task depends on input fields with incompatible time steps")
            task.status = cmor_task.status_failed
            task2files.pop(task, None)
        task2freqs[task] = maxfreq
        task2files[task] = ['.'.join([p, str(maxfreq)]) for p in task2files[task]]
    varsfiles = {key: set() for key in varstasks}
    for key in varsfiles:
        for t in varstasks[key]:
            f = task2files[t][0]
            if len(task2files[t]) == 2 and (key[0], key[1]) not in accum_codes:
                f = task2files[t][1]
            varsfiles[key].add((f, task2freqs[t]))
    return task2files, task2freqs, varsfx, varsfiles


# Main execution loop
def execute(tasks, filter_files=True, multi_threaded=False):
    valid_fx_tasks = execute_tasks([t for t in tasks if cmor_target.get_freq(t.target) == 0], filter_files,
                                   multi_threaded=False, once=True)
    valid_other_tasks = execute_tasks([t for t in tasks if cmor_target.get_freq(t.target) != 0], filter_files,
                                      multi_threaded=multi_threaded, once=False)
    return valid_fx_tasks + valid_other_tasks


def filter_fx_variables(gribfile, keys2files, gridtype, startdate, handles=None):
    timestamp = -1
    keys = set()
    while gribfile.read_next() and (handles is None or any(handles.keys())):
        t = gribfile.get_field(grib_file.time_key)
        key = get_record_key(gribfile, gridtype)
        if t == timestamp and key in keys:
            continue  # Prevent double grib messages
        if t != timestamp:
            keys = set()
            timestamp = t
        keys.add(key)
        write_record(gribfile, key, keys2files, shift=0, handles=handles, once=True, setdate=startdate)
        gribfile.release()


def execute_tasks(tasks, filter_files=True, multi_threaded=False, once=False):
    valid_tasks, varstasks = validate_tasks(tasks)
    task2files, task2freqs, fxkeys, keys2files = cluster_files(valid_tasks, varstasks)
    grids = [cmor_source.ifs_grid.point, cmor_source.ifs_grid.spec]
    if filter_files:
        filehandles = open_files(keys2files)
        fxkeys2files = {k: keys2files[k] for k in fxkeys}
        if any(gridpoint_files):
            gridpoint_start_date = sorted(gridpoint_files.keys())[0]
            first_gridpoint_file = gridpoint_files[gridpoint_start_date][0]
            if ini_gridpoint_file != first_gridpoint_file and ini_gridpoint_file is not None:
                with open(str(ini_gridpoint_file), 'r') as fin:
                    filter_fx_variables(grib_file.create_grib_file(fin), fxkeys2files, grids[0], gridpoint_start_date,
                                        filehandles)
        elif ini_gridpoint_file is not None:
            with open(str(ini_gridpoint_file), 'r') as fin:
                filter_fx_variables(grib_file.create_grib_file(fin), fxkeys2files, grids[0], None, filehandles)
        if any(spectral_files):
            spectral_start_date = sorted(spectral_files.keys())[0]
            first_spectral_file = spectral_files[spectral_start_date][0]
            if ini_spectral_file != first_spectral_file and ini_spectral_file is not None:
                with open(str(ini_spectral_file), 'r') as fin:
                    filter_fx_variables(grib_file.create_grib_file(fin), fxkeys2files, grids[1], spectral_start_date,
                                        filehandles)
        elif ini_spectral_file is not None:
            with open(str(ini_spectral_file), 'r') as fin:
                filter_fx_variables(grib_file.create_grib_file(fin), fxkeys2files, grids[1], None, filehandles)
        if multi_threaded:
            threads = []
            for file_list, grid in zip([gridpoint_files, spectral_files], grids):
                thread = threading.Thread(target=filter_grib_files, 
                                          args=(file_list, keys2files, grid, filehandles, 0, 0, once))
                threads.append(thread)
                thread.start()
            threads[0].join()
            threads[1].join()
        else:
            for file_list, grid in zip([gridpoint_files, spectral_files], grids):
                filter_grib_files(file_list, keys2files, grid, filehandles, month=0, year=0, once=once)
        for handle in filehandles.values():
            handle.close()
    for task in task2files:
        if task.status != cmor_task.status_failed:
            file_list = task2files[task]
            filter_output = os.path.join(temp_dir, file_list[0])
            if len(file_list) > 1:
                filter_output = os.path.join(temp_dir, '_'.join(file_list))
                if not os.path.isfile(filter_output):
                    cdoapi.cdo_command().merge([os.path.join(temp_dir, f) for f in file_list], filter_output)
            setattr(task, cmor_task.filter_output_key, [filter_output])
    for task in task2freqs:
        if task.status != cmor_task.status_failed:
            setattr(task, cmor_task.output_frequency_key, task2freqs[task])
    return valid_tasks


# Checks tasks that are compatible with the variables listed in grib_vars and
# returns those that are compatible.
def validate_tasks(tasks):
    varstasks = {}
    valid_tasks = []
    for task in tasks:
        if task.status == cmor_task.status_failed or not isinstance(task.source, cmor_source.ifs_source):
            continue
        codes = task.source.get_root_codes()
        target_freq = cmor_target.get_freq(task.target)
        matched_keys = []
        matched_grid = None
        for c in codes:
            if task.status == cmor_task.status_failed:
                break
            levtype, levels = get_levels(task, c)
            for level in levels:
                if task.status == cmor_task.status_failed:
                    break
                match_key = soft_match_key(c.var_id, c.tab_id, levtype, level, task.source.grid_, varsfreq.keys())
                if match_key is None:
                    if 0 < target_freq and c in cmor_source.ifs_source.grib_codes_fx:
                        match_key = soft_match_key(c.var_id, c.tab_id, levtype, level, task.source.grid_, fxvars)
                        if match_key is None:
                            log.error("Field missing in the initial state files: "
                                      "code %d.%d, level type %d, level %d. Dismissing task %s in table %s" %
                                      (c.var_id, c.tab_id, levtype, level, task.target.variable, task.target.table))
                            task.set_failed()
                            break
                    else:
                        log.error("Field missing in the first day of file: "
                                  "code %d.%d, level type %d, level %d. Dismissing task %s in table %s" %
                                  (c.var_id, c.tab_id, levtype, level, task.target.variable, task.target.table))
                        task.set_failed()
                        break
                elif 0 < target_freq < varsfreq[match_key]:
                    log.error("Field has too low frequency for target %s: "
                              "code %d.%d, level type %d, level %d. Dismissing task %s in table %s" %
                              (task.target.variable, c.var_id, c.tab_id, levtype, level, task.target.variable,
                               task.target.table))
                    task.set_failed()
                    break
                if matched_grid is None:
                    matched_grid = match_key[4]
                else:
                    if match_key[4] != matched_grid:
                        log.warning("Task %s in table %s depends on both gridpoint and spectral fields" %
                                    (task.target.variable, task.target.table))
                matched_keys.append(match_key)
        if task.status != cmor_task.status_failed:
            # Fix for zg and ps on gridpoints and spectral fields on height levels:
            task.source.grid_ = matched_grid
            for key in matched_keys:
                if key in varstasks:
                    varstasks[key].append(task)
                else:
                    varstasks[key] = [task]
            valid_tasks.append(task)
    return valid_tasks, varstasks


def open_files(vars2files):
    files = set()
    for fileset in vars2files.values():
        files.update(set([t[0] for t in fileset]))
    numreq = len(files)
    softlim = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
    if numreq > softlim + 1:
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (numreq + 1, -1))
        except ValueError:
            return {}
    return {f: open(os.path.join(temp_dir, f), 'w') for f in files}


# Processes month of grib data, including 0-hour fields in the previous month file.
def filter_grib_files(file_list, keys2files, grid, handles=None, month=0, year=0, once=False):
    dates = sorted(file_list.keys())
    for i in range(len(dates)):
        date = dates[i]
        if month != 0 and year != 0 and (date.month, date.year) != (month, year):
            continue
        prev_grib_file, cur_grib_file = file_list[date]
        prev_chained = i > 0 and (prev_grib_file == file_list[dates[i - 1]][1])
        if prev_grib_file is not None and not prev_chained:
            with open(prev_grib_file, 'r') as fin:
                proc_initial_month(date.month, grib_file.create_grib_file(fin), keys2files, grid, handles, once)
        next_chained = i < len(dates) - 1 and (cur_grib_file == file_list[dates[i + 1]][0])
        with open(cur_grib_file, 'r') as fin:
            log.info("Filtering grib file %s..." % cur_grib_file)
            if next_chained:
                proc_grib_file(grib_file.create_grib_file(fin), keys2files, grid, handles, once)
            else:
                proc_final_month(date.month, grib_file.create_grib_file(fin), keys2files, grid, handles, once)


# Function writing data from previous monthly file, writing the 0-hour fields
def proc_initial_month(month, gribfile, keys2files, gridtype, handles, once=False):
    timestamp = -1
    keys = set()
    while gribfile.read_next() and (handles is None or any(handles.keys())):
        date = gribfile.get_field(grib_file.date_key)
        if (date % 10 ** 4) / 10 ** 2 == month:
            t = gribfile.get_field(grib_file.time_key)
            key = get_record_key(gribfile, gridtype)
            if t == timestamp and key in keys:
                continue  # Prevent double grib messages
            if t != timestamp:
                keys = set()
                timestamp = t
            keys.add(key)
            if (key[0], key[1]) not in accum_codes:
                write_record(gribfile, key + (gridtype,), keys2files, handles=handles, once=once, setdate=None)
        gribfile.release()


model_level_cache = {}


# Function writing data from previous monthly file, writing the 0-hour fields
def proc_grib_file(gribfile, keys2files, gridtype, handles, once=False):
    for key in keys2files.keys():
        if key[2] == grib_file.hybrid_level_code:
            model_level_cache[key] = 0
    timestamp = -1
    keys = set()
    fast_forward_count = 0
    while gribfile.read_next(headers_only=(fast_forward_count > 0)) and (handles is None or any(handles.keys())):
        if fast_forward_count > 0:
            fast_forward_count -= 1
            continue
        key = get_record_key(gribfile, gridtype)
        if key[2] == grib_file.hybrid_level_code:
            fast_forward_count = model_level_cache.get((key[0], key[1]), 91)
        if fast_forward_count > 0:
            fast_forward_count -= 1
            continue
        t = gribfile.get_field(grib_file.time_key)
        if t == timestamp and key in keys:
            continue  # Prevent double grib messages
        if t != timestamp:
            keys = set()
            timestamp = t
        keys.add(key)
        write_record(gribfile, key + (gridtype,), keys2files, shift=-1 if (key[0], key[1]) in accum_codes else 0,
                     handles=handles, once=once, setdate=None)
        gribfile.release()


# Function writing data from previous monthly file, writing the 0-hour fields
def proc_final_month(month, gribfile, keys2files, gridtype, handles, once=False):
    timestamp = -1
    keys = set()
    while gribfile.read_next() and (handles is None or any(handles.keys())):
        date = gribfile.get_field(grib_file.date_key)
        mon = (date % 10 ** 4) / 10 ** 2
        if mon == month:
            t = gribfile.get_field(grib_file.time_key)
            key = get_record_key(gribfile, gridtype)
            if t == timestamp and key in keys:
                continue  # Prevent double grib messages
            if t != timestamp:
                keys = set()
                timestamp = t
            keys.add(key)
            write_record(gribfile, key + (gridtype,), keys2files, shift=-1 if (key[0], key[1]) in accum_codes else 0,
                         handles=handles, once=once, setdate=None)
        elif mon == month % 12 + 1:
            t = gribfile.get_field(grib_file.time_key)
            key = get_record_key(gribfile, gridtype)
            if t == timestamp and key in keys:
                continue  # Prevent double grib messages
            if t != timestamp:
                keys = set()
                timestamp = t
            keys.add(key)
            if (key[0], key[1]) in accum_codes:
                write_record(gribfile, key + (gridtype,), keys2files, shift=-1, handles=handles, once=once, setdate=None)
        gribfile.release()


# Writes the grib messages
def write_record(gribfile, key, keys2files, shift=0, handles=None, once=False, setdate=None):
    global starttimes
    var_infos = set()
    if key[2] == grib_file.hybrid_level_code:
        for k, v in keys2files.items():
            if k[:3] == key[:3]:
                var_infos.update(v)
    else:
        f = keys2files.get(key[:4], None)
        if f is not None:
            var_infos.update(f)
    if not any(var_infos):
        return
    if setdate is not None:
        gribfile.set_field(grib_file.date_key, int(setdate.strftime("%Y%m%d")))
        gribfile.set_field(grib_file.time_key, 0)
    timestamp = gribfile.get_field(grib_file.time_key)
    if shift != 0 and setdate is None:
        freq = varsfreq.get(key, 0)
        shifttime = timestamp + shift * freq * 100
        if shifttime < 0 or shifttime >= 2400:
            newdate, hours = fix_date_time(gribfile.get_field(grib_file.date_key), shifttime / 100)
            gribfile.set_field(grib_file.date_key, newdate)
            shifttime = 100 * hours
        timestamp = int(shifttime)
        gribfile.set_field(grib_file.time_key, timestamp)
    if gribfile.get_field(grib_file.levtype_key) == grib_file.pressure_level_Pa_code:
        gribfile.set_field(grib_file.levtype_key, 99)
    if gribfile not in starttimes:
        starttimes[gribfile] = timestamp
    for var_info in var_infos:
        if timestamp / 100 % var_info[1] != 0:
            continue
        handle = handles.get(var_info[0], None) if handles else None
        if handle:
            gribfile.write(handle)
            if once and handles is not None and timestamp != starttimes[gribfile]:
                handle.close()
                del handles[var_info[0]]
        else:
            if handles is None:
                with open(os.path.join(temp_dir, var_info[0]), 'a') as ofile:
                    gribfile.write(ofile)
            else:
                if not once:
                    log.error("Unexpected missing file handle encountered for code %s" % var_info[0])


# Converts 24 hours into extra days
def fix_date_time(date, time):
    timestamp = datetime.datetime(year=date / 10 ** 4, month=(date % 10 ** 4) / 10 ** 2,
                                  day=date % 10 ** 2) + datetime.timedelta(hours=time)
    return timestamp.year * 10 ** 4 + timestamp.month * 10 ** 2 + timestamp.day, timestamp.hour
