import logging
import os

import numpy
import pygrib
from dateutil import relativedelta

from ece2cmor3 import cmor_target, cmor_source, cmor_task, cmor_utils, grib_file, ppmsg, pplevels, ppopfac, ppsh

# Log object.
log = logging.getLogger(__name__)

gridpoint_file = None
prev_gridpoint_file = None
spectral_file = None
prev_spectral_file = None
temp_dir = None
varsfreq = {}
varstasks = {}
task_operators = {}
extra_operators = {}


# Initializes the module, looks up previous month files and inspects the first
# day in the input files to set up an administration of the fields.
def initialize(gpfile, shfile, tmpdir):
    global gridpoint_file, prev_gridpoint_file, spectral_file, prev_spectral_file, temp_dir, varsfreq
    gridpoint_file = gpfile
    spectral_file = shfile
    temp_dir = tmpdir
    prev_gridpoint_file, prev_spectral_file = get_prev_files(gridpoint_file)
    with pygrib.open(gpfile) as gpf, pygrib.open(shfile) as shf:
        varsfreq.update(inspect_day(grib_file.create_grib_file(gpf), grid=cmor_source.ifs_grid.point))
        varsfreq.update(inspect_day(grib_file.create_grib_file(shf), grid=cmor_source.ifs_grid.spec))


# Inspects the first 24 hours in the input gridpoint and spectral files.
def inspect_day(gribfile, grid):
    inidate, initime = -99, -1
    records = {}
    while gribfile.read_next():
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
    if levtype == grib_file.pressure_level_code:
        level *= 100
    if levtype == grib_file.depth_level_code:
        level = 0
        levtype = grib_file.surface_level_code
    if codevar in [165, 166]:
        level = 10
        levtype = grib_file.height_level_code
    if codevar in [167, 168, 201, 202]:
        level = 2
        levtype = grib_file.height_level_code
    if codevar in [9, 134]:
        level = 0
        levtype = grib_file.surface_level_code
    return codevar, codetab, levtype, level


# Utility to make grib tuple of codes from string
def grib_tuple_from_int(i):
    if i < 256:
        return i, 128
    return i % 10 ** 3, i / 10 ** 3


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


# Main execution loop
def execute(tasks, month):
    valid_tasks = determine_frequencies(validate_tasks(tasks))
    for icmggpath, icmshpath in [(prev_gridpoint_file, prev_spectral_file), (gridpoint_file, spectral_file)]:
        if icmggpath is None or icmshpath is None:
            continue
        with pygrib.open(icmggpath) as ggf, pygrib.open(icmshpath) as shf:
            icmgg, icmsh = grib_file.create_grib_file(ggf), grib_file.create_grib_file(shf)
            cmorize_files(month, icmgg, icmsh)
    return valid_tasks


# Cmorized gridpoint and spectral file in lock-step mode
def cmorize_files(month, icmgg, icmsh):
    front_grib, back_grib = icmsh, icmgg
    front_grib.read_next()
    back_grib.read_next()
    stop_time = front_grib.get_field(grib_file.time_key)
    while True:
        stop_time_front = read_grib_passed_time(front_grib, stop_time, month)
        stop_time_back = read_grib_passed_time(back_grib, stop_time_front, month)
        if stop_time_back == -1:
            break
        stop_time = stop_time_back


def read_grib_passed_time(grib, stop_time, month):
    time = grib.get_field(grib_file.time_key)
    reached_stop = time == stop_time
    if not grib.eof() and get_mon(grib) == month:
        pplevels.get_pv_array(grib)
        cmorize_msg(grib)
    while grib.read_next():
        time = grib.get_field(grib_file.time_key)
        if reached_stop and time != stop_time:
            grib.release()
            return time
        if get_mon(grib) == month:
            pplevels.get_pv_array(grib)
            cmorize_msg(grib)
        reached_stop = time == stop_time
        grib.release()
    return -1

msgcounter = 0

def cmorize_msg(grb):
    global msgcounter
    msgcounter += 1
#    if msgcounter % 100 == 0:
#        from guppy import hpy
#        h = hpy()
#        print "Printing heap..."
#        print h.heap()
    key = get_record_key(grb)
    time = grb.get_field(grib_file.time_key) / 100
    tasks = set()
    index = 3 if key[2] == grib_file.hybrid_level_code else 4
    for k in varstasks:
        if k[:index] == key[:index]:
            matches = [t for t in varstasks[k] if time % getattr(t, cmor_task.output_frequency_key, 1) == 0]
            tasks.update(matches)
    msg = ppmsg.grib_message(grb)
    if key in extra_operators:
        extra_operators[key].receive_msg(msg)
    if any(tasks):
        #        print "GRIB keys:", key
        mapper = ppsh.pp_remap_sh()
        mapper.receive_msg(msg)
        mapped_msg = mapper.create_msg()
        for task in tasks:
            operator = task_operators.get(task, None)
            if operator is not None:
                #                print "processing task", task.target.variable, "in", task.target.table
                if not operator.receive_msg(mapped_msg):
                    return False
    return True


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
        target_freq = cmor_target.get_freq(task.target)
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
                if match_key not in varsfreq:
                    log.error("Field missing in the first day of file: "
                              "code %d.%d, level type %d, level %d" % (key[0], key[1], key[2], key[3]))
                    task.set_failed()
                    break
                if 0 < target_freq < varsfreq[match_key]:
                    log.error("Field has too low frequency for target %s: "
                              "code %d.%d, level type %d, level %d" % (
                                  task.target.variable, key[0], key[1], key[2], key[3]))
                    task.set_failed()
                    break
        if task.status != cmor_task.status_failed:
            for c in codes:
                levtype, levels = get_levels(task, c)
                for l in levels:
                    key = (c.var_id, c.tab_id, levtype, l, task.source.grid_)
                    if key in varstasks:
                        varstasks[key].append(task)
                    else:
                        varstasks[key] = [task]
            valid_tasks.append(task)
    return valid_tasks


# Construct files for keys and tasks
def determine_frequencies(valid_tasks):
    global varstasks
    task2freqs = {}
    for task in valid_tasks:
        task2freqs[task] = set()
        for key, tsklist in varstasks.iteritems():
            if task in tsklist:
                if key[3] == -1:
                    task2freqs[task].update([varsfreq[k] for k in varsfreq.keys() if
                                             (k[0], k[1], k[2]) == (key[0], key[1], key[2])])
                else:
                    task2freqs[task].add(varsfreq[key])
    new_valid_tasks = []
    for task in task2freqs:
        freqset = task2freqs[task]
        maxfreq = max(freqset)
        if any([f for f in freqset if maxfreq % f != 0]):
            log.error("Task %s in table %s depends on input fields with incompatible time steps" %
                      (task.target.variable, task.target.table))
            task.status = cmor_task.status_failed
        else:
            setattr(task, cmor_task.output_frequency_key, maxfreq)
            new_valid_tasks.append(task)
    return new_valid_tasks


# Converts cmor-levels to grib levels code
def get_levels(task, code):
    global log
    if (code.var_id, code.tab_id) == (134, 128):
        return grib_file.surface_level_code, [0]
    axis_name, axis_variable, levels = cmor_target.get_z_axis(task.target)
    if axis_variable is None:
        return grib_file.surface_level_code, [0]
    if axis_variable in ["alevel", "alevhalf"]:
        return grib_file.hybrid_level_code, [-1]
    if axis_variable == "air_pressure":
        return grib_file.pressure_level_code, [int(float(l)) for l in levels]
    if axis_variable in ["height", "altitude"]:
        return grib_file.height_level_code, [int(float(l)) for l in levels]  # TODO: What about decimal places?
    log.error("Could not convert vertical axis type %s to grib vertical coordinate "
              "code for %s" % (axis_variable, task.target.variable))
    return -1, []


def get_mon(gribfile):
    date = gribfile.get_field(grib_file.date_key)
    return (date % 10 ** 4) / 10 ** 2
