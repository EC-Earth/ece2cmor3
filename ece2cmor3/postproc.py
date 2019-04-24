import logging
import threading
import re
import Queue
import os

from ece2cmor3 import cmor_task

import grib_file
import cdoapi
import cmor_source
import cmor_target

# Log object
log = logging.getLogger(__name__)

# Threading parameters
task_threads = 1
cdo_threads = 4

# Flags to control whether to execute cdo.
skip = 1
append = 2
recreate = 3
modes = [skip, append, recreate]

# Mode for post-processing
mode = 3

# Output frequency of IFS (in hours)
output_frequency_ = 3

# Helper list of tasks
finished_tasks_ = []


# Post-processes a list of tasks
def post_process(tasks, path, max_size_gb=float("inf"), grid_descr=None):
    if grid_descr is None:
        grid_descr = {}
    global finished_tasks_, task_threads
    comm_dict = {}
    comm_buf = {}
    max_size = 1000000000. * max_size_gb
    for task in tasks:
        command = create_command(task, grid_descr)
        comm_string = command.create_command()
        if comm_string not in comm_buf:
            comm_buf[comm_string] = command
        else:
            command = comm_buf[comm_string]
        if task.status != cmor_task.status_failed:
            if command in comm_dict:
                comm_dict[command].append(task)
            else:
                comm_dict[command] = [task]
    invalid_commands = []
    for comm, task_list in comm_dict.iteritems():
        if not validate_task_list(task_list):
            invalid_commands.append(comm)
    for comm in invalid_commands:
        for t in comm_dict[comm]:
            t.set_failed()
        comm_dict.pop(comm)
    finished_tasks_ = []
    if task_threads <= 2:
        tmp_size = 0.
        for comm, task_list in comm_dict.iteritems():
            if tmp_size >= max_size:
                break
            f = apply_command(comm, task_list, path)
            if os.path.exists(f):
                tmp_size += float(os.path.getsize(f))
            finished_tasks_.extend(task_list)
    else:
        q = Queue.Queue()
        for i in range(task_threads):
            worker = threading.Thread(target=cdo_worker, args=(q, path, max_size))
            worker.setDaemon(True)
            worker.start()
        for (comm, task_list) in comm_dict.iteritems():
            q.put((comm, task_list))
        q.join()
    return [t for t in list(finished_tasks_) if t.status >= 0]


# Checks whether the task grouping makes sense: only tasks for the same variable and frequency can be safely grouped.
def validate_task_list(tasks):
    global log
    freqset = set(map(lambda t: cmor_target.get_freq(t.target), tasks))
    if len(freqset) != 1:
        log.error("Multiple target variables joined to single cdo command: %s" % str(freqset))
        return False
    return True


# Creates a cdo postprocessing command for the given IFS task.
def create_command(task, grid_descr=None):
    if grid_descr is None:
        grid_descr = {}
    if not isinstance(task.source, cmor_source.ifs_source):
        raise Exception("This function can only be used to create cdo commands for IFS tasks")
    if hasattr(task, "paths") and len(getattr(task, "paths")) > 1:
        raise Exception("Multiple merged cdo commands are not supported yet")
    result = cdoapi.cdo_command() if hasattr(task.source, cmor_source.expression_key) else cdoapi.cdo_command(
        code=task.source.get_grib_code().var_id)
    add_grid_operators(result, task, grid_descr)
    add_expr_operators(result, task)
    add_time_operators(result, task)
    add_level_operators(result, task)
    return result


# Checks whether the string expression denotes height level merging
def add_expr_operators(cdo, task):
    expr = getattr(task.source, cmor_source.expression_key, None)
    if not expr:
        return
    groups = re.search("^var([0-9]{1,3})\=", expr.replace(" ", ""))
    if groups is None:
        lhs = "var" + task.source.get_grib_code().var_id
        rhs = expr.replace(" ", "")
    else:
        lhs = groups.group(0)[:-1]
        rhs = expr.replace(" ", "")[len(lhs) + 1:]
    expr = '='.join([lhs, rhs])
    new_code = int(lhs[3:])
    if rhs.startswith("merge(") and rhs.endswith(")"):
        arg = rhs[6:-1]
        sub_expr_list = arg.split(',')
        if not any(getattr(task.target, "z_dims", [])):
            log.warning("Encountered 3d expression for variable with no z-axis: taking first field")
            sub_expr = sub_expr_list[0].strip()
            if not re.match("var[0-9]{1,3}", sub_expr):
                cdo.add_operator(cdoapi.cdo_command.expression_operator, "var" + str(new_code) + "=" + sub_expr)
            else:
                task.source = cmor_source.ifs_source.read(sub_expr)
            root_codes = [int(s.strip()[3:]) for s in re.findall("var[0-9]{1,3}", sub_expr)]
            cdo.add_operator(cdoapi.cdo_command.select_code_operator, *root_codes)
            return
        else:
            for sub_expr in sub_expr_list:
                if not re.match("var[0-9]{1,3}", sub_expr):
                    sub_vars = re.findall("var[0-9]{1,3}", sub_expr)
                    if len(sub_vars) != 1:
                        log.error("Merging expressions of multiple variables per layer is not supported.")
                        continue
                    cdo.add_operator(cdoapi.cdo_command.add_expression_operator, sub_vars[0] + "=" + sub_expr)
            cdo.add_operator(cdoapi.cdo_command.set_code_operator, new_code)
    else:
        cdo.add_operator(cdoapi.cdo_command.expression_operator, expr)
    cdo.add_operator(cdoapi.cdo_command.select_code_operator, *[c.var_id for c in task.source.get_root_codes()])


# Multi-thread function wrapper.
def cdo_worker(q, base_path, maxsize):
    global finished_tasks_
    while True:
        args = q.get()
        for task in finished_tasks_:
            if getattr(task, cmor_task.output_path_key, None) is None:
                log.error("Task %s in table %s has not produced any output... "
                          "setting it to failed status." % (task.target.variable, task.target.table))
                task.set_failed()
        files = list(set(map(lambda t: getattr(t, cmor_task.output_path_key, ""), finished_tasks_)))
        if sum(map(lambda fname: os.path.getsize(fname), [f for f in files if os.path.exists(f)])) < maxsize:
            tasks = args[1]
            apply_command(command=args[0], task_list=tasks, base_path=base_path)
            finished_tasks_.extend(tasks)
        q.task_done()


# Executes the command and replaces the path attribute for all tasks in the tasklist
# to the output of cdo. This path is constructed from the basepath and the first task.
def apply_command(command, task_list, base_path=None):
    global log, cdo_threads, skip, append, recreate, mode
    if not task_list:
        log.warning("Encountered empty task list for post-processing command %s" % command.create_command())
    if base_path is None and mode in [skip, append]:
        log.warning(
            "Executing post-processing in skip/append mode without directory given: this will skip the entire task.")
    input_files = getattr(task_list[0], cmor_task.filter_output_key, [])
    if isinstance(input_files, str):
        input_files = [input_files]
    if not any(input_files):
        log.error("Cannot execute cdo command %s for given task because it has no model "
                  "output attribute" % command.create_command())
        return None
    input_file = input_files[0]
    if len(input_files) > 1:
        directory = os.path.dirname(input_file)
        input_file = os.path.join(directory, '_'.join([os.path.basename(f) for f in input_files]))
        command.merge(input_files, input_file)
    output_file = task_list[0].target.variable + "_" + task_list[0].target.table + ".nc"
    ofile = os.path.join(base_path, output_file) if base_path else None
    for task in task_list:
        comm_string = command.create_command()
        log.info("Post-processing target %s in table %s from file %s with cdo command %s" % (
            task.target.variable, task.target.table, input_file, comm_string))
        setattr(task, "cdo_command", comm_string)
        task.next_state()
    result = ofile
    if mode != skip:
        if mode == recreate or (mode == append and not os.path.exists(ofile)):
            merge_expr = (cdoapi.cdo_command.set_code_operator in command.operators)
            output_path = command.apply(input_file, ofile, cdo_threads, grib_first=merge_expr)
            if not output_path:
                for task in task_list:
                    task.set_failed()
            if output_path and not base_path:
                tmp_path = os.path.dirname(output_path)
                ofile = os.path.join(tmp_path, output_file)
                os.rename(output_path, ofile)
                result = ofile
    for task in task_list:
        if task.status >= 0:
            setattr(task, cmor_task.output_path_key, result)
            task.next_state()
    return result


# Adds grid remapping operators to the cdo commands for the given task
def add_grid_operators(cdo, task, grid_descr):
    grid = task.source.grid_id()
    if grid == cmor_source.ifs_grid.spec:
        cdo.add_operator(cdoapi.cdo_command.spectral_operator)
    else:
        gridtype = grid_descr.get("gridtype", "gaussian reduced")
        if gridtype in ["gaussian reduced", "gaussian_reduced"]:
            cdo.add_operator(cdoapi.cdo_command.gridtype_operator, cdoapi.cdo_command.regular_grid_type)


# Adds time averaging operators to the cdo command for the given task
def add_time_operators(cdo, task):
    global output_frequency_
    freq = getattr(task.target, cmor_target.freq_key, None)
    operators = getattr(task.target, "time_operator", ["point"])
    if freq == "mon":
        if operators == ["point"]:
            cdo.add_operator(cdoapi.cdo_command.select_hour_operator, 12)
            cdo.add_operator(cdoapi.cdo_command.select_day_operator, 15)
        elif operators == ["mean"]:
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
        elif operators == ["mean within years", "mean over years"]:
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
        elif operators == ["maximum"]:
            cdo.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.month])
        elif operators == ["minimum"]:
            cdo.add_operator(cdoapi.cdo_command.min_time_operators[cdoapi.cdo_command.month])
        elif operators == ["maximum within days", "mean over days"]:
            cdo.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.day])
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
        elif operators == ["minimum within days", "mean over days"]:
            cdo.add_operator(cdoapi.cdo_command.min_time_operators[cdoapi.cdo_command.day])
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
        else:
            log.error(
                "Unsupported combination of frequency %s with time operators %s encountered" % (freq, str(operators)))
            task.set_failed()
    elif freq == "day":
        if operators == ["point"]:
            cdo.add_operator(cdoapi.cdo_command.select_hour_operator, 12)
        elif operators == ["mean"]:
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.day])
        elif operators == ["mean within years", "mean over years"]:
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.day])
        elif operators == ["maximum"]:
            cdo.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.day])
        elif operators == ["minimum"]:
            cdo.add_operator(cdoapi.cdo_command.min_time_operators[cdoapi.cdo_command.day])
        else:
            log.error(
                "Unsupported combination of frequency %s with time operators %s encountered" % (freq, str(operators)))
            task.set_failed()
    elif freq in ["6hr", "6hrPt"] and len(operators) == 1:
        add_high_freq_operator(cdo, 6, operators[0], task)
    elif freq in ["3hr", "3hrPt"] and len(operators) == 1:
        add_high_freq_operator(cdo, 3, operators[0], task)
    elif freq == 0 and operators == ["point"] or operators == ["mean"]:
        cdo.add_operator(cdoapi.cdo_command.select_step_operator, 1)
    else:
        log.error("Unsupported combination of frequency %s with time operators %s encountered" % (freq, str(operators)))
        task.set_failed()


def add_high_freq_operator(cdo_command, target_freq, operator, task):
    timestamps = [i * target_freq for i in range(24 / target_freq)]
    aggregators = {"mean": (cmor_source.ifs_source.grib_codes_accum, cdoapi.cdo_command.timselmean_operator),
                   "minimum": (cmor_source.ifs_source.grib_codes_min, cdoapi.cdo_command.timselmin_operator),
                   "maximum": (cmor_source.ifs_source.grib_codes_max, cdoapi.cdo_command.timselmax_operator)}
    if operator == "point":
        if any([c for c in task.source.get_root_codes() if c in cmor_source.ifs_source.grib_codes_accum]):
            log.warning("Sampling values of accumulated model output for variable %s in "
                        "table %s" % (task.target.variable, task.target.table))
        if any([c for c in task.source.get_root_codes() if c in cmor_source.ifs_source.grib_codes_min]):
            log.warning("Sampling values of minimum model output for variable %s in "
                        "table %s" % (task.target.variable, task.target.table))
        if any([c for c in task.source.get_root_codes() if c in cmor_source.ifs_source.grib_codes_max]):
            log.warning("Sampling values of maximum model output for variable %s in "
                        "table %s" % (task.target.variable, task.target.table))
        cdo_command.add_operator(cdoapi.cdo_command.select_hour_operator, *timestamps)
    elif operator in aggregators:
        if not all([c for c in task.source.get_root_codes() if c in aggregators[operator][0]]):
            source_freq = getattr(task, cmor_task.output_frequency_key, output_frequency_)
            steps = target_freq / source_freq
            if steps == 0:
                log.error("Requested %s at %d-hourly frequency cannot be computed for variable %s in table %s "
                          "because its output frequency is only %d" % (operator, target_freq, task.target.variable,
                                                                       task.target.table, source_freq))
                task.set_failed()
            else:
                log.warning("Computing inaccurate mean value over %d time steps for variable "
                            "%s in table %s" % (target_freq / source_freq, task.target.variable, task.target.table))
                if steps == 1:
                    cdo_command.add_operator(cdoapi.cdo_command.select_hour_operator, *timestamps)
                else:
                    cdo_command.add_operator(aggregators[operator][1], steps)
        else:
            cdo_command.add_operator(cdoapi.cdo_command.select_hour_operator, *timestamps)
    else:
        log.error("The operator %s is not supported by this post-processing software" % operator)
        task.set_failed()
    return cdo_command


# Translates the cmor vertical level post-processing operation to a cdo command-line option
def add_level_operators(cdo, task):
    global log
    if task.source.spatial_dims == 2:
        return
    zdims = getattr(task.target, "z_dims", [])
    if len(zdims) == 0:
        return
    if len(zdims) > 1:
        log.error("Multiple level dimensions in table %s are not supported by this post-processing software",
                  task.target.table)
        task.set_failed()
        return
    axisname = zdims[0]
    if axisname == "alevel":
        cdo.add_operator(cdoapi.cdo_command.select_z_operator, cdoapi.cdo_command.model_level)
    if axisname == "alevhalf":
        log.error("Vertical half-levels in table %s are not supported by this post-processing software",
                  task.target.table)
        task.set_failed()
        return
    axis_infos = cmor_target.get_axis_info(task.target.table)
    axisinfo = axis_infos.get(axisname, None)
    if not axisinfo:
        log.error("Could not retrieve information for axis %s in table %s" % (axisname, task.target.table))
        task.set_failed()
        return
    levels = axisinfo.get("requested", [])
    if len(levels) == 0:
        val = axisinfo.get("value", None)
        if val:
            levels = [val]
    level_types = [grib_file.hybrid_level_code, grib_file.pressure_level_hPa_code, grib_file.height_level_code]
    input_files = getattr(task, cmor_task.filter_output_key, [])
    if any(input_files):
        level_types = cdo.get_z_axes(input_files[0], task.source.get_root_codes()[0].var_id)
    name = axisinfo.get("standard_name", None)
    if name == "air_pressure":
        add_zaxis_operators(cdo, task, level_types, levels, cdoapi.cdo_command.pressure,
                            grib_file.pressure_level_hPa_code)
    elif name in ["height", "altitude"]:
        add_zaxis_operators(cdo, task, level_types, levels, cdoapi.cdo_command.height, grib_file.height_level_code)
    elif axisname not in ["alevel", "alevhalf"]:
        log.error("Could not convert vertical axis type %s to CDO axis selection operator" % name)
        task.set_failed()


# Helper function for setting the vertical axis and levels selection
def add_zaxis_operators(cdo, task, lev_types, req_levs, axis_type, axis_code):
    if axis_code not in lev_types and grib_file.hybrid_level_code in lev_types:
        log.warning(
            "Could not find %s levels for %s, will interpolate from model levels" % (axis_type, task.target.variable))
        cdo.add_operator(cdoapi.cdo_command.select_code_operator, *[134])
        cdo.add_operator(cdoapi.cdo_command.select_z_operator,
                         *[cdoapi.cdo_command.model_level, cdoapi.cdo_command.surf_level])
        if isinstance(req_levs, list) and any(req_levs):
            cdo.add_operator(cdoapi.cdo_command.ml2pl_operator, *req_levs)
    elif axis_code in lev_types:
        if isinstance(req_levs, list) and any(req_levs):
            levels = [float(s) for s in req_levs]
            input_files = getattr(task, cmor_task.filter_output_key, [])
            if any(input_files):
                levels = cdo.get_levels(input_files[0], task.source.get_root_codes()[0].var_id, axis_type)
            if set([float(s) for s in req_levs]) <= set(levels):
                cdo.add_operator(cdoapi.cdo_command.select_z_operator, axis_type)
                cdo.add_operator(cdoapi.cdo_command.select_lev_operator, *req_levs)
            else:
                log.error("Could not retrieve %s levels %s from levels %s in file for variable %s"
                          % (axis_type, req_levs, levels, task.target.variable))
                task.set_failed()
    else:
        log.error(
            "Could not retrieve %s levels for %s with axes %s" % (axis_type, task.target.variable, str(lev_types)))
        task.set_failed()
