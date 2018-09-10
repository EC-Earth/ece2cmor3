import cmor
import os
import logging
from ece2cmor3 import cmor_source, cmor_target, cmor_task, nemo2cmor, ifs2cmor, lpjg2cmor, tm52cmor, postproc

# Logger instance
log = logging.getLogger(__name__)

# Module configuration defaults
conf_path_default = os.path.join(os.path.dirname(__file__), "resources", "metadata-template.json")
cmor_mode_default = cmor.CMOR_PRESERVE
prefix_default = "CMIP6"
table_dir_default = os.path.join(os.path.dirname(__file__), "resources", "tables")

# ece2cmor master API.
conf_path = conf_path_default
cmor_mode = cmor_mode_default
prefix = prefix_default
table_dir = table_dir_default
tasks = []
targets = []
masks = {}
enable_masks = True
auto_filter = True

# CMOR modes
APPEND = cmor.CMOR_APPEND
APPEND_NC3 = cmor.CMOR_APPEND_3
REPLACE = cmor.CMOR_REPLACE
REPLACE_NC3 = cmor.CMOR_REPLACE_3
PRESERVE = cmor.CMOR_PRESERVE
PRESERVE_NC3 = cmor.CMOR_PRESERVE_3


# Initialization function without using the cmor library, must be called before starting
def initialize_without_cmor(metadata=conf_path_default, mode=cmor_mode_default, tabledir=table_dir_default,
                            tableprefix=prefix_default):
    global prefix, table_dir, targets, conf_path, cmor_mode
    conf_path = metadata
    cmor_mode = mode
    table_dir = tabledir
    prefix = tableprefix
    validate_setup_settings()
    targets = cmor_target.create_targets(table_dir, prefix)


# Initialization function, must be called before starting
def initialize(metadata=conf_path_default, mode=cmor_mode_default, tabledir=table_dir_default,
               tableprefix=prefix_default):
    global prefix, table_dir, targets, conf_path, cmor_mode
    conf_path = metadata
    cmor_mode = mode
    table_dir = tabledir
    prefix = tableprefix
    validate_setup_settings()
    cmor.setup(table_dir, cmor_mode)
    cmor.dataset_json(conf_path)
    targets = cmor_target.create_targets(table_dir, prefix)


# Validation of setup configuration
def validate_setup_settings():
    global prefix, table_dir, conf_path, cmor_mode
    if not conf_path or not isinstance(conf_path, str):
        log.error("Invalid metadata json file string given...aborting")
        raise Exception("Metadata file path is empty or not a string")
    if not os.path.isfile(conf_path):
        log.error("Metadata json file %s does not exist...aborting" % conf_path)
        raise Exception("Metadata file does not exist or has invalid extension")
    if not table_dir or not isinstance(table_dir, str):
        log.error("Invalid cmorization table string given...aborting")
        raise Exception("Cmorization table directory is empty or not a string")
    if not os.path.exists(table_dir):
        log.error("Cmorization table directory %s does not exist" % table_dir)
        raise Exception("Cmorization table directory does not exist")
    if not prefix or not isinstance(prefix, str):
        log.error("Cmorization table prefix is empty or not a string")
        raise Exception("Cmorization table prefix is empty or not a string")
    if cmor_mode not in [APPEND, APPEND_NC3, REPLACE, REPLACE_NC3, PRESERVE, PRESERVE_NC3]:
        log.error("Invalid CMOR netcdf file action %s given" % str(cmor_mode))
        raise Exception("Invalid CMOR netcdf file action")
    return 0


# Closes cmor
def finalize_without_cmor():
    global tasks, targets, masks
    targets = []
    tasks = []
    masks = {}


# Closes cmor
def finalize():
    global tasks, targets, masks
    cmor.close()
    targets = []
    tasks = []
    masks = {}


# Returns one or more cmor targets for task creation.
def get_cmor_target(var_id, tab_id=None):
    global log, targets
    if tab_id is None:
        return [t for t in targets if t.variable == var_id]
    else:
        results = [t for t in targets if t.variable == var_id and t.table == tab_id]
        if len(results) == 1:
            return results[0]
        elif len(results) == 0:
            return None
        else:
            log.error("Table validation error: multiple variables with name %s found in table %s" % (var_id, tab_id))


# Adds a task to the task list.
def add_task(tsk):
    global log, tasks, targets
    if isinstance(tsk, cmor_task.cmor_task):
        if tsk.target not in targets:
            log.error("Cannot append tasks with unknown target %s" % str(tsk.target))
            return
        duptasks = [t for t in tasks if t.target is tsk.target]
        if len(duptasks) != 0:
            tasks.remove(duptasks[0])
        tasks.append(tsk)
    else:
        log.error("Can only append cmor_task to the list, attempt to append %s" % str(tsk))


# Adds a mask
def add_mask(name, src, func, val):
    global masks
    masks[name] = {"source": src, "operator": func, "rhs": val}


# Performs an IFS cmorization processing:
def perform_ifs_tasks(datadir, expname, startdate, interval, refdate=None,
                      postprocmode=postproc.recreate,
                      tempdir="/tmp/ece2cmor",
                      taskthreads=4,
                      cdothreads=4,
                      cleanup=True,
                      outputfreq=3,
                      maxsizegb=float("inf")):
    global log, tasks, table_dir, prefix, masks
    validate_setup_settings()
    validate_run_settings(datadir, expname)
    ifs_tasks = [t for t in tasks if t.source.model_component() == "ifs"]
    log.info("Selected %d IFS tasks from %d input tasks" % (len(ifs_tasks), len(tasks)))
    tableroot = os.path.join(table_dir, prefix)
    if enable_masks:
        ifs2cmor.masks = {k: masks[k] for k in masks if masks[k]["source"].model_component() == "ifs"}
    else:
        ifs2cmor.masks = {}
    ofreq = -1 if auto_filter else outputfreq
    if (not ifs2cmor.initialize(datadir, expname, tableroot, startdate, interval, refdate if refdate else startdate,
                                outputfreq=ofreq, tempdir=tempdir, maxsizegb=maxsizegb, autofilter=auto_filter)):
        return
    postproc.postproc_mode = postprocmode
    postproc.cdo_threads = cdothreads
    ifs2cmor.execute(ifs_tasks, cleanup=cleanup, autofilter=auto_filter, nthreads=taskthreads)


# Performs a NEMO cmorization processing:
def perform_nemo_tasks(datadir, expname, startdate, interval):
    global log, tasks, table_dir, prefix
    validate_setup_settings()
    validate_run_settings(datadir, expname)
    nemo_tasks = [t for t in tasks if t.source.model_component() == "nemo"]
    log.info("Selected %d NEMO tasks from %d input tasks" % (len(nemo_tasks), len(tasks)))
    tableroot = os.path.join(table_dir, prefix)
    if not nemo2cmor.initialize(datadir, expname, tableroot, startdate, interval):
        return
    nemo2cmor.execute(nemo_tasks)

# Performs a LPJG cmorization processing:
def perform_lpjg_tasks(datadir, ncdir, expname, startdate, interval):
    global log ,tasks, table_dir, prefix
    validate_setup_settings()
    validate_run_settings(datadir, expname)
    lpjg_tasks = [t for t in tasks if t.source.model_component() == "lpjg"]
    log.info("Selected %d LPJG tasks from %d input tasks" % (len(lpjg_tasks), len(tasks)))
    if(not lpjg2cmor.initialize(datadir, ncdir, expname, table_dir, prefix, startdate, interval)):
        return
    lpjg2cmor.execute(lpjg_tasks)

# Performs a LPJG cmorization processing:
def perform_tm5_tasks(datadir, ncdir, expname, startdate, interval):
    global log ,tasks, table_dir, prefix
    validate_setup_settings()
    validate_run_settings(datadir, expname)
    tm5_tasks = [t for t in tasks if t.source.model_component() == "tm5"]
    log.info("Selected %d TM5 tasks from %d input tasks" % (len(tm5_tasks), len(tasks)))
    print '22222',table_dir
    if(not tm52cmor.initialize(datadir, expname, table_dir, prefix, startdate, interval)):
        return
    tm52cmor.execute(tm5_tasks)

#def perform_NEWCOMPONENT_tasks(datadir, expname, startdate, interval):
#    global log, tasks, table_dir, prefix
#    validate_setup_settings()
#    validate_run_settings(datadir, expname)
#    NEWCOMPONENT_tasks = [t for t in tasks if isinstance(t.source, cmor_source.NEWCOMPONENT_source)]
#    log.info("Selected %d NEWCOMPONENT tasks from %d input tasks" % (len(NEWCOMPONENT_tasks), len(tasks)))
#    tableroot = os.path.join(table_dir, prefix)
#    if not NEWCOMPONENT2cmor.initialize(datadir, expname, tableroot, startdate, interval):
#        return
#    NEWCOMPONENT2cmor.execute(NEWCOMPONENT_tasks)


# Validation of cmor session configuration
def validate_run_settings(datadir, expname):
    if not datadir or not isinstance(datadir, str):
        log.error("Invalid output data directory string given...aborting")
        raise Exception("Output data directory is empty or not a string")
    if not os.path.exists(datadir):
        log.error("Output data directory %s does not exist" % table_dir)
        raise Exception("Output data directory does not exist")
    if not expname:
        log.error("Invalid empty experiment name given...aborting")
        raise Exception("Experiment name is empty string or None")
