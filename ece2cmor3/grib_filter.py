import json
import logging
import datetime
import os
import resource
import threading

from dateutil import relativedelta
import numpy

from ece2cmor3 import cmor_target, cmor_source, cmor_task, cmor_utils, grib_file

log = logging.getLogger(__name__)
gridpoint_file = None
prev_gridpoint_file = None
spectral_file = None
prev_spectral_file = None
temp_dir = None
accum_key = "ACCUMFLD"
accum_codes = []
varsfreq = {}
varstasks = {}
varsfiles = {}


# Initializes the module, looks up previous month files and inspects the first
# day in the input files to set up an administration of the fields.
def initialize(gpfile, shfile, tmpdir):
    global gridpoint_file, prev_gridpoint_file, spectral_file, prev_spectral_file, temp_dir, varsfreq, accum_codes
    gridpoint_file = gpfile
    spectral_file = shfile
    temp_dir = tmpdir
    accum_codes = load_accum_codes(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "grib_codes.json"))
    prev_gridpoint_file, prev_spectral_file = get_prev_files(gridpoint_file)
    with open(gpfile) as gpf, open(shfile) as shf:
        varsfreq.update(inspect_day(grib_file.create_grib_file(gpf)))
        varsfreq.update(inspect_day(grib_file.create_grib_file(shf)))


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


# Inspects the first 24 hours in the input gridpoint and spectral files.
def inspect_day(gribfile):
    inidate, initime = -99, -1.
    records = {}
    while gribfile.read_next(headers_only=True):
        date = gribfile.get_field(grib_file.date_key)
        time = gribfile.get_field(grib_file.time_key) / 100.
        if date == inidate + 1 and time == initime:
            break
        if inidate < 0:
            inidate = date
        if initime < 0.:
            initime = time
        key = get_record_key(gribfile)
        if key in records:
            records[key].append(time)
        else:
            records[key] = [time]
        gribfile.release()
    result = {}
    for key, val in records.iteritems():
        hrs = numpy.array(val)
        frqs = 24. if len(hrs) == 1 else numpy.mod(hrs[1:] - hrs[:-1], numpy.repeat(24, len(hrs) - 1))
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
    if levtype == grib_file.pressure_level_code:
        level *= 100
    if codevar in [38, 42, 236]:
        level = 289
    if codevar in [165, 166]:
        level = 10
        levtype = grib_file.height_level_code
    return codevar, codetab, levtype, level


# Searches the file system for the previous month file, necessary for the 0-hour
# fields.
def get_prev_files(gpfile):
    log.info("Searching for previous month file of %s" % gpfile)
    date = cmor_utils.get_ifs_date(gpfile)
    prevdate = date - relativedelta.relativedelta(months=1)
    ifsoutputdir = os.path.abspath(os.path.join(os.path.dirname(gridpoint_file), ".."))
    expname = os.path.basename(gpfile)[5:9]
    inigpfile, inishfile = None, None
    prevgpfiles, prevshfiles = [], []
    for f in cmor_utils.find_ifs_output(ifsoutputdir, expname=expname):
        if f.endswith("+000000"):
            if os.path.basename(f).startswith("ICMGG"):
                inigpfile = f
            if os.path.basename(f).startswith("ICMSH"):
                inishfile = f
        elif cmor_utils.get_ifs_date(f) == prevdate:
            if os.path.basename(f).startswith("ICMGG"):
                prevgpfiles.append(f)
            if os.path.basename(f).startswith("ICMSH"):
                prevshfiles.append(f)
    if not any(prevgpfiles) or not any(prevshfiles):
        log.info("No regular previous month files found, taking initial state files...")
        if not inigpfile:
            log.warning("No initial gridpoint file found in %s" % ifsoutputdir)
        if not inishfile:
            log.warning("No initial spectral file found in %s" % ifsoutputdir)
        return inigpfile, inishfile
    if len(prevgpfiles) > 1:
        log.warning("Multiple previous month gridpoint files found: %s. Taking first match" % ",".join(prevgpfiles))
    if len(prevshfiles) > 1:
        log.warning("Multiple previous month spectral files found: %s. Taking first match" % ",".join(prevshfiles))
    return prevgpfiles[0], prevshfiles[0]


# Splits the grib file for the given set of tasks
def mkfname(key):
    return '.'.join([str(key[0]), str(key[1]), str(key[2])])


# Construct files for keys and tasks
def cluster_files(valid_tasks):
    global varstasks, varsfiles
    task2files, task2freqs = {}, {}
    for task in valid_tasks:
        task2files[task] = set()
        task2freqs[task] = set()
        for key, tsklist in varstasks.iteritems():
            if task in tsklist:
                task2files[task].add(mkfname(key))
                task2freqs[task].add(varsfreq[key])
    for task, fnames in task2files.iteritems():
        task2files[task] = '_'.join(sorted(list(fnames)))
    for task, freqset in task2freqs.iteritems():
        maxfreq = max(freqset)
        if any([f for f in freqset if maxfreq % f != 0]):
            log.error("Task depends on input fields with incompatible time steps")
            task.status = cmor_task.status_failed
            task2files.pop(task, None)
        task2freqs[task] = maxfreq
    varsfiles = {key: set() for key in varstasks}
    for key in varsfiles:
        varsfiles[key].update([(task2files[t], task2freqs[t]) for t in varstasks[key]])
    return task2files


# Main execution loop
def execute(tasks, month, multi_threaded=False):
    global varsfiles
    valid_tasks = validate_tasks(tasks)
    task2files = cluster_files(valid_tasks)
    filehandles = open_files(varsfiles)
    if multi_threaded:
        threads = []
        for path, prev_path in [(gridpoint_file, prev_gridpoint_file), (spectral_file, prev_spectral_file)]:
            thread = threading.Thread(target=proc_mon, args=(month, path, prev_path, filehandles))
            threads.append(thread)
            thread.start()
        threads[0].join()
        threads[1].join()
    else:
        for path, prev_path in [(gridpoint_file, prev_gridpoint_file), (spectral_file, prev_spectral_file)]:
            proc_mon(month, path, prev_path, filehandles)
    for handle in filehandles.values():
        handle.close()
    for task in task2files:
        if not task.status == cmor_task.status_failed:
            setattr(task, "path", task2files[task])
    return valid_tasks


# Checks tasks that are compatible with the variables listed in grib_vars and
# returns those that are compatible.
def validate_tasks(tasks):
    global varstasks
    varstasks = {}
    valid_tasks = []
    for task in tasks:
        if not isinstance(task.source, cmor_source.ifs_source):
            continue
        codes = task.source.get_root_codes()
        levtype, levels = get_levels(task)
        if levtype < 0:
            task.set_failed()
            continue
        target_freq = cmor_target.get_freq(task.target)
        for c in codes:
            for l in levels:
                if task.status == cmor_task.status_failed:
                    break
                key = (c.var_id, c.tab_id, levtype, l)
                if key not in varsfreq:
                    log.error("Field missing in the first day of file: "
                              "code %d.%d, level type %d, level %d" % (key[0], key[1], key[2], key[3]))
                    task.set_failed()
                    break
                if 0 < target_freq < varsfreq[key]:
                    log.error("Field has too low frequency for target %s: "
                              "code %d.%d, level type %d, level %d" % (
                                  task.target.variable, key[0], key[1], key[2], key[3]))
                    task.set_failed()
                    break
        if task.status != cmor_task.status_failed:
            for c in codes:
                for l in levels:
                    key = (c.var_id, c.tab_id, levtype, l)
                    if key in varstasks:
                        varstasks[key].append(task)
                    else:
                        varstasks[key] = [task]
            valid_tasks.append(task)
    return valid_tasks


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
    return {f: open(f, 'w') for f in files}


# Processes month of grib data, including 0-hour fields in the previous month file.
def proc_mon(month, cur_grib_file, prev_grib_file, handles=None):
    if prev_grib_file:
        with open(prev_grib_file, 'r') as fin:
            proc_prev_month(month, grib_file.create_grib_file(fin), handles)
    with open(cur_grib_file, 'r') as fin:
        proc_next_month(month, grib_file.create_grib_file(fin), handles)


# Converts cmor-levels to grib levels code
def get_levels(task):
    global log
    zaxis, levels = cmor_target.get_z_axis(task.target)
    if zaxis is None:
        return grib_file.surface_level_code, [0]
    if zaxis in ["alevel", "alevhalf"]:
        return grib_file.hybrid_level_code, [-1]
    if zaxis == "air_pressure":
        return grib_file.pressure_level_code, [float(l) for l in levels]
    if zaxis in ["height", "altitude"]:
        return grib_file.height_level_code, [float(l) for l in levels]
    log.error("Could not convert vertical axis type %s to grib vertical coordinate "
              "code for %s" % (zaxis, task.target.variable))
    return -1, []


# Converts 24 hours into extra days
def fix_date_time(date, time):
    timestamp = datetime.datetime(year=date / 10 ** 4, month=(date % 10 ** 4) / 10 ** 2,
                                  day=date % 10 ** 2) + datetime.timedelta(hours=time)
    return timestamp.year * 10 ** 4 + timestamp.month * 10 ** 2 + timestamp.day, timestamp.hour


# Writes the grib messages
def write_record(gribfile, shift=0, handles=None):
    key = get_record_key(gribfile)
    var_infos = varsfiles.get(key, [])
    if not any(var_infos):
        return
    timestamp = gribfile.get_field(grib_file.time_key)
    if shift:
        freq = varsfreq.get(key, 0)
        shifttime = timestamp + shift * freq * 100
        if shifttime < 0 or shifttime >= 2400:
            newdate, hours = fix_date_time(timestamp, shifttime / 100)
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
def proc_prev_month(month, gribfile, handles):
    while gribfile.read_next():
        if get_mon(gribfile) == month:
            code = grib_tuple_from_string(gribfile.get_field(grib_file.param_key))
            if code not in accum_codes:
                write_record(gribfile, handles=handles)
        gribfile.release()


# Function writing data from previous monthly file, writing the 0-hour fields
def proc_next_month(month, gribfile, handles):
    while gribfile.read_next():
        mon = get_mon(gribfile)
        code = grib_tuple_from_int(gribfile.get_field(grib_file.param_key))
        cumvar = code in accum_codes
        if mon == month:
            write_record(gribfile, shift=-1 if cumvar else 0, handles=handles)
        elif mon == (month + 1) % 12:
            if cumvar:
                write_record(gribfile, shift=-1, handles=handles)
        gribfile.release()


def get_mon(gribfile):
    date = gribfile.get_field(grib_file.date_key)
    return (date % 10 ** 4) / 10 ** 2


# Retrieves the record frequency from the day-inspection result
# def get_frequency(gribfile):
#    codevar, codetab = grib_tuple_from_int(gribfile.get_field(grib_file.param_key))
#    levtype = gribfile.get_field(grib_file.levtype_key)
#    level = gribfile.get_field(grib_file.level_key)
#    return varsfreq.get((codevar, codetab, levtype, level), 0)
