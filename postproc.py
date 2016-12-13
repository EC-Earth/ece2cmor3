import logging
import threading
import os
import Queue
import cdoapi
import cmor_source
import cmor_target

# Log object
log = logging.getLogger(__name__)

# Threading parameters
task_threads = 1
cdo_threads = 4

# Flag to control whether to execute cdo.
apply_cdo = True

# Output frequency of IFS (in hours)
output_frequency_ = 3

# Post-processes a list of tasks
def post_process(tasks,path):
    comdict = {}
    commbuf = {}
    for task in tasks:
        command = create_command(task)
        commstr = command.create_command()
        if(commstr not in commbuf):
            commbuf[commstr] = command
        else:
            command = commbuf[commstr]
        if(command in comdict):
            comdict[command].append(task)
        else:
            comdict[command] = [task]
    for comm,tasklist in comdict.iteritems():
        if(not validate_tasklist(tasklist)):
            comdict.pop(comm)
    if(task_threads <= 2):
        for comm,tasklist in comdict.iteritems():
            apply_command(comm,tasklist,path)
    else:
        q = Queue.Queue()
        for i in range(task_threads):
            worker = threading.Thread(target = cdo_worker,args = (q,path))
            worker.setDaemon(True)
            worker.start()
        for (comm,tasklist) in comdict.iteritems():
            q.put((comm,tasklist))
        q.join()

# Checks whether the task grouping makes sense: only tasks for the same variable and frequency can be safely grouped.
def validate_tasklist(tasks):
    srcset = set(map(lambda t:t.source.get_grib_code().var_id,tasks))
    if(len(srcset) != 1):
        log.error("Multiple grib codes joined to single cdo command: %s" % str(srcset))
        return False
    tgtset = set(map(lambda t:t.target.variable,tasks))
#    if(len(tgtset) != 1):
#        log.error("Multiple target variables joined to single cdo command: %s" % str(tgtset))
#        return False
    freqset = set(map(lambda t:t.target.frequency,tasks))
    if(len(freqset) != 1):
        log.error("Multiple target variables joined to single cdo command: %s" % str(freqset))
        return False
    return True

# Creates a cdo postprocessing command for the given IFS task.
def create_command(task):
    if(not isinstance(task.source,cmor_source.ifs_source)):
        raise Exception("This function can only be used to create cdo commands for IFS tasks")
    expr = getattr(task.source,cmor_source.expression_key,None)
    result = cdoapi.cdo_command() if expr else cdoapi.cdo_command(code = task.source.get_grib_code().var_id)
    if(task.source.grid() == cmor_source.ifs_grid[cmor_source.ifs_grid.spec]):
        result.add_operator(cdoapi.cdo_command.spectral_operator)
    else:
        result.add_operator(cdoapi.cdo_command.gridtype_operator,cdoapi.cdo_command.regular_grid_type)
    if(expr):
        result.add_operator(cdoapi.cdo_command.expression_operator,expr)
        result.add_operator(cdoapi.cdo_command.select_code_operator,*[c.var_id for c in task.source.get_root_codes()])
    freq = getattr(task.target,cmor_target.freq_key,None)
    timops = getattr(task.target,"time_operator",["point"])
    add_time_operators(result,freq,timops)
    add_level_operators(result,task)
    return result

def cdo_worker(q,basepath):
    while True:
        args = q.get()
        apply_command(args[0],args[1],basepath)
        q.task_done()

# Executes the command (first item of tup), and replaces the path attribute for all tasks in the tasklist (2nd item of tup)
# to the output of cdo. This path is constructed from the basepath and the first task.
def apply_command(command,tasklist,basepath):
    if(not tasklist):
        log.warning("Encountered empty task list for post-processing command %s" % command.create_command())
    ifile = getattr(tasklist[0],"path")
    ofile = os.path.join(basepath,tasklist[0].target.variable + "_" + tasklist[0].target.table + ".nc")
    for task in tasklist:
        commstr = command.create_command()
        log.info("Post-processing target %s in table %s from file %s with cdo command %s" % (task.target.variable,task.target.table,ifile,commstr))
        setattr(task,"cdo_command",commstr)
    if(apply_cdo or not os.path.exists(ofile)):
        command.apply(ifile,ofile,cdo_threads)
    for task in tasklist:
        setattr(task,"path",ofile)

# Translates the cmor time post-processing operation to a cdo command-line option
def add_time_operators(cdo,freq,operators):
    timeshift = "-" + str(output_frequency_) + "hours"
    if(freq == "mon"):
        if(operators == ["point"]):
            cdo.add_operator(cdoapi.cdo_command.select_hour_operator,12)
            cdo.add_operator(cdoapi.cdo_command.select_day_operator,15)
            return
        if(operators == ["mean"]):
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
            cdo.add_operator(cdoapi.cdo_command.shift_time_operator,timeshift)
            return
        if(operators == ["maximum"]):
            cdo.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.month])
            cdo.add_operator(cdoapi.cdo_command.shift_time_operator,timeshift)
            return
        if(operators == ["minimum"]):
            cdo.add_operator(cdoapi.cdo_command.min_time_operators[cdoapi.cdo_command.month])
            cdo.add_operator(cdoapi.cdo_command.shift_time_operator,timeshift)
            return
        if(operators == ["maximum within days","mean over days"]):
            cdo.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.day])
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
            cdo.add_operator(cdoapi.cdo_command.shift_time_operator,timeshift)
            return
        if(operators == ["minimum within days","mean over days"]):
            cdo.add_operator(cdoapi.cdo_command.min_time_operators[cdoapi.cdo_command.day])
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
            cdo.add_operator(cdoapi.cdo_command.shift_time_operator,timeshift)
            return
    if(freq == "day"):
        if(operators == ["point"]):
            cdo.add_operator(cdoapi.cdo_command.select_hour_operator,12)
            return
        if(operators == ["mean"]):
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.day])
            cdo.add_operator(cdoapi.cdo_command.shift_time_operator,timeshift)
            return
        if(operators == ["maximum"]):
            cdo.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.day])
            cdo.add_operator(cdoapi.cdo_command.shift_time_operator,timeshift)
            return
        if(operators == ["minimum"]):
            cdo.add_operator(cdoapi.cdo_command.min_time_operators[cdoapi.cdo_command.day])
            cdo.add_operator(cdoapi.cdo_command.shift_time_operator,timeshift)
            return
    if(freq == "6hr"):
        if(operators == ["point"] or operators == ["mean"]):
            cdo.add_operator(cdoapi.cdo_command.select_hour_operator,0,6,12,18)
            return
    if(freq in ["1hr","3hr"]):
        if(operators == ["point"] or operators == ["mean"]): return
    raise Exception("Unsupported combination of frequency ",freq," with time operators ",operators,"encountered")


# Translates the cmor vertical level post-processing operation to a cdo command-line option
def add_level_operators(cdo,task):
    if(task.source.spatial_dims == 2): return
    zdims = getattr(task.target,"z_dims",[])
    if(len(zdims) == 0): return
    if(len(zdims) > 1):
        log.error("Multiple level dimensions in table %s are not supported by this post-processing software",(task.target.table))
    axisname = zdims[0]
    if(axisname == "alevel"):
        cdo.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.modellevel)
    if(axisname == "alevhalf"):
        log.error("Vertical half-levels in table %s are not supported by this post-processing software",(task.target.table))
        return
    axisinfos = cmor_target.axes.get(task.target.table,{})
    axisinfo = axisinfos.get(axisname,None)
    if(not axisinfo):
        log.error("Could not retrieve information for axis %s in table %s" % (axisname,task.target.table))
        return
    oname = axisinfo.get("standard_name",None)
    if(oname == "air_pressure"):
        cdo.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.pressure)
    elif(oname == "height"):
        cdo.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.height)
    elif(axisname not in ["alevel","alevhalf"]):
        log.error("Could not convert vertical axis type %s to CDO axis selection operator" % oname)
        return
    zlevs = axisinfo.get("requested",[])
    if(zlevs == "all"): return
    if(len(zlevs) == 0):
        val = axisinfo.get("value",None)
        if(val): zlevs = [val]
    if(len(zlevs) > 0):
        cdo.add_operator(cdoapi.cdo_command.select_lev_operator,*zlevs)
