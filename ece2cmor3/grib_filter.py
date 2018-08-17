import json
import logging
import datetime
import os
import resource
import threading
from dateutil import relativedelta
import numpy
from ece2cmor3 import cmor_target, cmor_source, cmor_task, cmor_utils, grib_file

# Log object.
log = logging.getLogger(__name__)

accum_key = "ACCUMFLD"

# def get_sp_key(fname, varsfreq):
#     spvar = None
#     for key in varsfreq:
#         freq = varsfreq[key]
#         if key[0] == 154:
#             if spvar is None or spvar[1] >= freq:
#                 spvar = (154, freq, fname)
#         if key[0] == 134:
#             if spvar is None or spvar[1] > freq:
#                 spvar = (134, freq, fname)
#     return spvar

# Utility to make grib tuple of codes from string
def grib_tuple_from_int(i):
    if i < 256:
        return i, 128
    return i % 10 ** 3, i / 10 ** 3


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
        key = get_record_key(gribfile) + (grid,)
        if key in records:
            if time not in records[key]:
                records[key].append(time)
        else:
            records[key] = [time]
        gribfile.release()
    result = {}
    for key, val in records.iteritems():
        hrs = numpy.array(val)
        frqs = 24 if len(hrs) == 1 else numpy.mod(hrs[1:] - hrs[:-1], numpy.repeat(24, len(hrs) - 1))
        frq = frqs[0]
        if any(frqs != frq):
            log.error("Variable %d.%d on level %d or type %s is not output on regular "
                      "intervals in first day in file %s" % (key[0], key[1], key[3], key[2], gribfile))
        else:
            result[key] = frq
    return result


# Creates a key (code + table + level type + level) for a grib message iterator
def get_record_key(gribfile):
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
    if codevar in [9]:
        level = 0
        levtype = grib_file.surface_level_code
    if codevar == 134 and levtype == grib_file.hybrid_level_code:
        level = 0
        levtype = grib_file.surface_level_code
    if levtype == grib_file.pv_level_code:  # Mapping pv-levels to surface: we don't support more than one pv-level
        level = 0
        levtype = grib_file.surface_level_code
    return codevar, codetab, levtype, level


# Checks tasks that are compatible with the variables listed in grib_vars and
# returns those that are compatible.
def validate_tasks(tasks, varsfreq):
    varstasks = {}
    validtasks = []
    for task in tasks:
        if not isinstance(task.source, cmor_source.ifs_source):
            continue
        codes = task.source.get_root_codes()
        target_freq = cmor_target.get_freq(task.target)
        grid_key = task.source.grid_
        for c in codes:
            levtype, levels = get_levels(task, c)
            for l in levels:
                if task.status == cmor_task.status_failed:
                    break
                key = (c.var_id, c.tab_id, levtype, l, task.source.grid_)
                match_key = key
                if levtype == grib_file.hybrid_level_code:
                    matches = [k for k in varsfreq.keys() if k[:3] == key[:3] and k[4] == key[4]]
                    match_key = key if not any(matches) else matches[0]
                if c.var_id == 134 and len(codes) == 1:
                    matches = [k for k in varsfreq.keys() if k[:3] == key[:3]]
                    match_key = key if not any(matches) else matches[0]
                    if any(matches):
                        grid_key = match_key[4]
                if match_key not in varsfreq:
                    log.error("Field missing in the first day of file: "
                              "code %d.%d, level type %d, level %d. Dismissing task %s" %
                              (key[0], key[1], key[2], key[3], str(task)))
                    task.set_failed()
                    break
                if 0 < target_freq < varsfreq[match_key]:
                    log.error("Field has too low frequency for target %s: "
                              "code %d.%d, level type %d, level %d. Dismissing task %s" %
                              (task.target.variable, key[0], key[1], key[2], key[3], str(task)))
                    task.set_failed()
                    break
        if task.status != cmor_task.status_failed:
            for c in codes:
                levtype, levels = get_levels(task, c)
                for l in levels:
                    key = (c.var_id, c.tab_id, levtype, l, grid_key)
                    if key in varstasks:
                        varstasks[key].append(task)
                    else:
                        varstasks[key] = [task]
            validtasks.append(task)
    return validtasks, varstasks


# Splits the grib file for the given set of tasks
def mkfname(key):
    return '.'.join([str(key[0]), str(key[1]), str(key[2])])


# Construct files for keys and tasks
def cluster_files(valid_tasks, vars_tasks, vars_freq):
    task2files, task2freqs = {}, {}
    for task in valid_tasks:
        task2files[task] = set()
        task2freqs[task] = set()
        for key, tsklist in vars_tasks.iteritems():
            if task in tsklist:
                task2files[task].add(mkfname(key))
                if key[3] == -1:
                    task2freqs[task].update([vars_freq[k] for k in vars_freq.keys() if
                                             (k[0], k[1], k[2]) == (key[0], key[1], key[2])])
                else:
                    task2freqs[task].add(vars_freq[key])
    accum_codes = get_accum_codes()
    for task, fnames in task2files.iteritems():
        codes = {(int(f.split('.')[0]), int(f.split('.')[1])): f for f in sorted(list(fnames))}
        cum_file = '_'.join([codes[k] for k in codes if k in accum_codes])
        inst_file = '_'.join([codes[k] for k in codes if k not in accum_codes])
        task2files[task] = filter(None, [cum_file, inst_file])
    for task, freqset in task2freqs.iteritems():
        maxfreq = max(freqset)
        if any([f for f in freqset if maxfreq % f != 0]):
            log.error("Task depends on input fields with incompatible time steps")
            task.status = cmor_task.status_failed
            task2files.pop(task, None)
        task2freqs[task] = maxfreq
        task2files[task] = ['.'.join([p, str(maxfreq)]) for p in task2files[task]]
    varsfiles = {key: set() for key in vars_tasks}
    for key in varsfiles:
        for t in vars_tasks[key]:
            f = task2files[t][0]
            if len(task2files[t]) == 2 and (key[0], key[1]) not in accum_codes:
                f = task2files[t][1]
            varsfiles[key].add((f, task2freqs[t]))
    return varsfiles, task2files, task2freqs


def open_files(vars2files, tempdir):
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
    return {f: open(os.path.join(tempdir, f), 'w') for f in files}


# Processes month of grib data, including 0-hour fields in the previous month file.
def proc_mon(month, cur_grib_file, prev_grib_file, vars_files, vars_freqs, handles=None):
    if prev_grib_file:
        with open(prev_grib_file, 'r') as fin:
            proc_prev_month(month, grib_file.create_grib_file(fin), vars_files, vars_freqs, handles)
    with open(cur_grib_file, 'r') as fin:
        proc_next_month(month, grib_file.create_grib_file(fin), vars_files, vars_freqs, handles)


# Function reading the file with grib-codes of accumulated fields
def get_accum_codes():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "grib_codes.json")
    data = json.loads(open(path).read())
    if accum_key in data:
        return map(grib_tuple_from_string, data[accum_key])
    else:
        return []


# Utility to make grib tuple of codes from string
def grib_tuple_from_string(s):
    codes = s.split('.')
    return int(codes[0]), 128 if len(codes) < 2 else int(codes[1])


# Converts cmor-levels to grib levels code
def get_levels(task, code):
    global log
    if (code.var_id, code.tab_id) == (134, 128):
        return grib_file.surface_level_code, [0]
    if 34 < code.var_id < 43 and code.tab_id == 128:
        return grib_file.depth_level_code, [0]
    if code.var_id in [139, 170, 183, 236] and code.tab_id == 128:
        return grib_file.depth_level_code, [0]
    zaxis, levels = cmor_target.get_z_axis(task.target)
    if zaxis is None:
        return grib_file.surface_level_code, [0]
    if zaxis in ["sdepth"]:
        return grib_file.depth_level_code, [0]
    if zaxis in ["alevel", "alevhalf"]:
        return grib_file.hybrid_level_code, [-1]
    if zaxis == "air_pressure":
        return grib_file.pressure_level_Pa_code, [int(float(l)) for l in levels]
    if zaxis in ["height", "altitude"]:
        return grib_file.height_level_code, [int(float(l)) for l in levels]  # TODO: What about decimal places?
    log.error("Could not convert vertical axis type %s to grib vertical coordinate "
              "code for %s" % (zaxis, task.target.variable))
    return -1, []


# Converts 24 hours into extra days
def fix_date_time(date, time):
    timestamp = datetime.datetime(year=date / 10 ** 4, month=(date % 10 ** 4) / 10 ** 2,
                                  day=date % 10 ** 2) + datetime.timedelta(hours=time)
    return timestamp.year * 10 ** 4 + timestamp.month * 10 ** 2 + timestamp.day, timestamp.hour


# Writes the grib messages
def write_record(gribfile, varsfiles, varsfreqs, shift=0, handles=None):
    key = get_record_key(gribfile)
    if key[2] == grib_file.hybrid_level_code:
        matches = [varsfiles[k] for k in varsfiles if k[:3] == key[:3]]
    else:
        matches = [varsfiles[k] for k in varsfiles if k[:4] == key[:4]]
    var_infos = set()
    for match in matches:
        var_infos.update(match)
    if not any(var_infos):
        return
    timestamp = gribfile.get_field(grib_file.time_key)
    if shift:
        matches = [k for k in varsfreqs.keys() if k[:-1] == key]
        freq = varsfreqs[matches[0]] if any(matches) else 0
        shifttime = timestamp + shift * freq * 100
        if shifttime < 0 or shifttime >= 2400:
            newdate, hours = fix_date_time(gribfile.get_field(grib_file.date_key), shifttime / 100)
            gribfile.set_field(grib_file.date_key, newdate)
            shifttime = 100 * hours
        timestamp = int(shifttime)
        gribfile.set_field(grib_file.time_key, timestamp)
    levtype = gribfile.get_field(grib_file.levtype_key)
    if levtype == 210:
        gribfile.set_field(grib_file.levtype_key, 99)
    for var_info in var_infos:
        if timestamp / 100 % var_info[1] != 0:
            continue
        handle = handles.get(var_info[0], None) if handles else None
        if handle:
            gribfile.write(handle)
        else:
            with open(var_info[0], 'a') as ofile:
                gribfile.write(ofile)


# Function writing data from previous monthly file, writing the 0-hour fields
def proc_prev_month(month, gribfile, varsfiles, varsfreqs, handles):
    accum_codes = get_accum_codes()
    while gribfile.read_next():
        if get_mon(gribfile) == month:
            code = grib_tuple_from_int(gribfile.get_field(grib_file.param_key))
            if code not in accum_codes:
                write_record(gribfile, varsfiles, varsfreqs, handles=handles)
        gribfile.release()


# Function writing data from previous monthly file, writing the 0-hour fields
def proc_next_month(month, gribfile, varsfiles, varsfreqs, handles):
    accum_codes = get_accum_codes()
    while gribfile.read_next():
        mon = get_mon(gribfile)
        code = grib_tuple_from_int(gribfile.get_field(grib_file.param_key))
        cumvar = code in accum_codes
        if mon == month:
            write_record(gribfile, varsfiles, varsfreqs, shift=-1 if cumvar else 0, handles=handles)
        elif mon == (month + 1) % 12:
            if cumvar:
                write_record(gribfile, varsfiles, varsfreqs, shift=-1, handles=handles)
        gribfile.release()


def get_mon(gribfile):
    date = gribfile.get_field(grib_file.date_key)
    return (date % 10 ** 4) / 10 ** 2
