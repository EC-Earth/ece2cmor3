import json
import logging
import datetime
import os
import threading

import dateutil
import numpy

import grib
import gribapi
import cmor_utils
from ece2cmor3 import cmor_target, cmor_source, cmor_task

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
    if not prev_spectral_file or not prev_gridpoint_file:
        return False
    with open(gpfile) as gpf, open(shfile) as shf:
        varsfreq.update(inspect_day(gpf))
        varsfreq.update(inspect_day(shf))


# Function reading the file with grib-codes of accumulated fields
def load_accum_codes(path):
    global accum_key
    data = json.loads(open(path).read())
    if accum_key in data:
        return map(make_grib_tuple, data[accum_key])
    else:
        return []


# Utility to make grib tuple of codes from string
def make_grib_tuple(s):
    codes = s.split('.')
    return int(codes[0]), 128 if len(codes) < 2 else int(codes[1])


# Inspects the first 24 hours in the input gridpoint and spectral files.
def inspect_day(gribfile):
    inidate, initime = -99, -1.
    records = {}
    while True:
        gid = gribapi.grib_new_from_file(gribfile)
        if not gid:
            break
        date = gribapi.grib_get(gid, "dataDate", int)
        time = gribapi.grib_get(gid, "dataTime", int) / 100.
        if date == inidate + 1 and time == initime:
            break
        if inidate < 0:
            inidate = date
        if initime < 0.:
            initime = time
        key = get_record_key(gid)
        if key in records:
            records[key].append(time)
        else:
            records[key] = [time]
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
def get_record_key(gid):
    codevar, codetab = make_grib_tuple(gribapi.grib_get(gid, "paramId", str))
    levtype = gribapi.grib_get(gid, "indicatorOfTypeOfLevel", int)
    level = gribapi.grib_get(gid, "level")
    key = (codevar, codetab, levtype, level)
    return key


# Searches the file system for the previous month file, necessary for the 0-hour
# fields.
def get_prev_files(gpfile):
    log.info("Searching for previous month file of %s" % gpfile)
    date = cmor_utils.get_ifs_date(gpfile)
    prevdate = date - dateutil.relativedelta.relativedelta(month=1)
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
            log.error("No initial gridpoint file found in %s" % ifsoutputdir)
        if not inishfile:
            log.error("No initial spectral file found in %s" % ifsoutputdir)
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
    global varstasks,varsfiles
    task2files = {}
    for task in valid_tasks:
        task2files[task] = {}
        for key, tsklist in varstasks.iteritems():
            if task in tsklist:
                task2files[task].add(mkfname(key))
    for task, fnames in task2files.iteritems():
        task2files[task] = '_'.join(sorted(list(fnames)))
    varsfiles = {key: {} for key in varstasks}
    for key in varsfiles:
        varsfiles[key].update([task2files[t] for t in varstasks[key]])
    return task2files


# Main execution loop
def execute(tasks, month):
    global varsfiles
    valid_tasks = validate_tasks(tasks)
    task2files = cluster_files(valid_tasks)
    threads = []
    for path, prev_path in [(gridpoint_file, prev_gridpoint_file), (spectral_file, prev_spectral_file)]:
        thread = threading.Thread(target=proc_mon, args=(month, path, prev_path))
        threads.append(thread)
        thread.start()
    threads[0].join()
    threads[1].join()
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
                              "code %d.%d, level type %d, level %d" % key)
                    task.set_failed()
                    break
                if 0 < target_freq < varsfreq[key]:
                    log.error("Field has too low frequency for target %s: "
                              "code %d.%d, level type %d, level %d" % task.target.variable, key)
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


# Processes month of grib data, including 0-hour fields in the previous month file.
def proc_mon(month, grib_file, prev_grib_file):
    proc_prev_month(month, prev_grib_file)
    proc_cur_month(month, grib_file)


# Converts cmor-levels to grib levels code
def get_levels(task):
    global log
    zaxis, levels = cmor_target.get_z_axis(task.target)
    if zaxis is None:
        return grib.surface_level_code, [0]
    if zaxis in ["alevel", "alevhalf"]:
        return grib.hybrid_level_code, [-1]
    if zaxis == "air_pressure":
        return grib.pressure_level_code, levels
    if zaxis in ["height", "altitude"]:
        return grib.height_level_code, levels
    log.error("Could not convert vertical axis type %s to grib vertical coordinate "
              "code for %s" % (zaxis, task.target.variable))
    return -1, []


def write_record(gid):
    key = get_record_key(gid)
    fname = varsfiles.get(key, None)
    if fname:
        gribapi.grib_write(gid, fname)


# Function writing data from previous monthly file, writing the 0-hour fields
def proc_prev_month(month, path):
    with open(path, 'r') as fin:
        while True:
            gid = gribapi.grib_new_from_file(fin)
            if not gid:
                break
            date = int(gribapi.grib_get(gid, "dataDate"))
            mon = (date % 10000) / 100
            if mon == month:
                code = make_grib_tuple(gribapi.grib_get(gid, "param"))
                if code in accum_codes:
                    continue
                fix_Pa_pressure_levels(gid)
                write_record(gid)
            gribapi.grib_release(gid)


# Function writing data from current monthly file, optionally shifting accumulated fields
# and skipping next month instantaneous fields
def proc_cur_month(month, path):
    gidinst, gidcum = -1, -1
    timinst, timcum = -1, -1
    procinst, proccum = True, True
    instmode = False
    with open(path, 'r') as fin1, open(path, 'r') as fin2:
        while True:
            if instmode:
                if procinst:
                    if gidinst != -1:
                        gribapi.grib_release(gidinst)
                    gidinst = gribapi.grib_new_from_file(fin1)
                if not gidinst:
                    break
                time = int(gribapi.grib_get(gidinst, "dataTime"))
                if timinst == -1:
                    timinst = time
                if time != timinst:
                    timinst = time
                    procinst = False
                    instmode = False
                    continue
                else:
                    procinst = True
                code = make_grib_tuple(gribapi.grib_get(gidinst, "param"))
                if code in accum_codes:
                    continue
                date = int(gribapi.grib_get(gidinst, "dataDate"))
                mon = (date % 10 ** 4) / 10 ** 2
                if mon == month:
                    fix_Pa_pressure_levels(gidinst)
                    write_record(gidinst)
            else:
                if proccum:
                    if gidinst != -1:
                        gribapi.grib_release(gidcum)
                    gidcum = gribapi.grib_new_from_file(fin2)
                if not gidcum:
                    procinst = False
                    instmode = True
                    continue
                time = int(gribapi.grib_get(gidcum, "dataTime"))
                if timcum == -1:
                    timcum = time
                if time != timcum:
                    timcum = time
                    proccum = False
                    instmode = True
                    continue
                else:
                    proccum = True
                code = make_grib_tuple(gribapi.grib_get(gidcum, "param"))
                if code not in accum_codes:
                    continue
                timeshift = get_frequency(gidcum)
                if timeshift > 0:
                    date = int(gribapi.grib_get(gidcum, "dataDate"))
                    mon = (date % 10 ** 4) / 10 ** 2
                    newdate = date
                    newtime = time - 100 * timeshift
                    if newtime < 0:
                        curdate = datetime.date(date / 10 ** 4, mon, date % 10 ** 2)
                        prevdate = curdate - datetime.timedelta(days=1)
                        mon = prevdate.month
                        newdate = prevdate.year * 10 ** 4 + mon * 10 ** 2 + prevdate.day
                        newtime = 2400 + newtime
                    gribapi.grib_set(gidcum, "dataDate", newdate)
                    gribapi.grib_set(gidcum, "dataTime", newtime)
                if mon == month:
                    fix_Pa_pressure_levels(gidcum)
                    write_record(gidcum)


# Sets the pressure level axis with levels < 1 hPa to a format that CDO can understand
def fix_Pa_pressure_levels(gid):
    levtype = gribapi.grib_get(gid, "indicatorOfTypeOfLevel", int)
    if levtype == 210:
        gribapi.grib_set(gid, "indicatorOfTypeOfLevel", 99)


# Retrieves the record frequency from the day-inspection result
def get_frequency(gid):
    codevar, codetab = make_grib_tuple(gribapi.grib_get(gid, "paramId", str))
    levtype = gribapi.grib_get(gid, "indicatorOfTypeOfLevel", int)
    level = gribapi.grib_get(gid, "level", int)
    return varsfreq.get((codevar, codetab, levtype, level), 0)
