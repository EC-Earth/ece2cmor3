import cmor
import os
import f90nml
import logging
import cmor_source
import cmor_target
import cmor_task
import nemo2cmor
import ifs2cmor
import postproc

# Logger instance
log = logging.getLogger(__name__)

# ece2cmor master API.
exp_name = None
prefix = "CMIP6"
table_dir = os.path.join(os.path.dirname(__file__),"resources","tables")
tasks = []
targets = []
ifsdir = None
nemodir = None
startdate = None
interval = None

# Initialization function, must be called before starting
def initialize(conf_path = os.path.join(os.path.dirname(__file__),"test","test_data","cmor3_metadata.json"),exp_name_ = None):
    global exp_name,prefix,table_dir,targets
    exp_name = exp_name_
    conf_path_ = conf_path
    cmor.setup(table_dir)
    cmor.dataset_json(conf_path)
    targets = cmor_target.create_targets(table_dir,prefix)

# Closes cmor
def finalize():
    global tasks,targets
    cmor.close()
    targets = []
    tasks = []

# Returns one or more cmor targets for task creation.
def get_cmor_target(var_id,tab_id=None):
    global log,targets
    if(tab_id == None):
        return [t for t in targets if t.variable == var_id]
    else:
        results = [t for t in targets if t.variable == var_id and t.table == tab_id]
        if(len(results) == 1):
            return results[0]
        elif(len(results) == 0):
            return None
        else:
            log.error("Table validation error: multiple variables with name %s found in table %s" % (var_id,tab_id))

# Adds a task to the task list.
def add_task(tsk):
    global log,tasks,targets
    if(isinstance(tsk,cmor_task.cmor_task)):
        if(tsk.target not in targets):
            log.error("Cannot append tasks with unknown target %s" % str(tsk.target))
            return
        duptasks=[t for t in tasks if t.target is tsk.target]
        if(len(duptasks)!=0):
            tasks.remove(duptasks[0])
        tasks.append(tsk)
    else:
        log.error("Can only append cmor_task to the list, attempt to append %s" % str(tsk))

# Performs an IFS cmorization processing:
def perform_ifs_tasks(postprocmode = postproc.recreate,tempdir = None,taskthreads = 4,cdothreads = 4,cleanup = True,outputfreq = 3,maxsizegb = float("inf")):
    global log,tasks,exp_name,table_dir,prefix,ifsdir,startdate,interval
    ifs_tasks = [t for t in tasks if isinstance(t.source,cmor_source.ifs_source)]
    log.info("Selected %d IFS tasks from %d input tasks" % (len(ifs_tasks),len(tasks)))
#    if(len(ifs_tasks) == 0):
    log.info("Extra info for bug#16: the given input tasks are...")
    for t in tasks:
        log.info("Target variable: %s (table: %s), source: %s" % (t.target.variable,t.target.table,type(t.source)))
        if(isinstance(t.source,cmor_source.ifs_source)):
            log.info("...with grib code %s" % str(t.source.get_grib_code()))
    tableroot = os.path.join(table_dir,prefix)
    # TODO: Add support for reference date other that startdate
    if(not ifs2cmor.initialize(ifsdir,exp_name,tableroot,startdate,interval,startdate,outputfreq = outputfreq,tempdir=tempdir,maxsizegb = maxsizegb)):
        return
    postproc.postproc_mode = postprocmode
    postproc.cdo_threads = cdothreads
    postproc.task_threads = taskthreads
    try:
        ifs2cmor.execute(ifs_tasks)
    finally:
        if(cleanup):
            ifs2cmor.cleanup(ifs_tasks)

# Performs a NEMO cmorization processing:
def perform_nemo_tasks():
    global log,tasks,exp_name,table_dir,prefix,nemodir,startdate,interval
    nemo_tasks = [t for t in tasks if isinstance(t.source,cmor_source.nemo_source)]
    log.info("Selected %d NEMO tasks from %d input tasks" % (len(ifs_tasks),len(tasks)))
    tableroot = os.path.join(table_dir,prefix)
    if(not nemo2cmor.initialize(nemodir,exp_name,tableroot,startdate,interval)):
        return
    nemo2cmor.execute(nemo_tasks)
