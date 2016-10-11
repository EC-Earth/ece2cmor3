import cmor
import os
import f90nml
import cmor_source
import cmor_target
import cmor_task
import nemo2cmor
import ifs2cmor

# ece2cmor master API.
exp_name_=None
prefix_=None
table_dir_=None
config_file_=None
targets_=[]
ifsdir_=None
nemodir_=None
tasks_=[]
startdate_=None
interval_=None

# Initialization function, must be called before starting
def initialize(exp_name,table_root,conf_path):
    global exp_name_
    global prefix_
    global table_dir_
    global conf_path_
    global targets_
    global ifsdir_
    global nemodir_
    global tasks_

    exp_name_=exp_name
    prefix_=os.path.splitext(os.path.basename(table_root))[0]
    table_dir_=os.path.dirname(table_root)
    conf_path_=conf_path

    cmor.setup(table_dir_)
    cmor.dataset_json(conf_path_)
    targets_=cmor_target.create_targets(table_dir_,prefix_)

    ifsdir_=None
    nemodir_=None
    tasks_=[]

# Closes cmor
def finalize():
    global exp_name_
    global prefix_
    global table_dir_
    global config_file_
    global targets_
    global ifsdir_
    global nemodir_

    cmor.close()
    exp_name_=None
    prefix_=None
    table_root_=None
    config_file_=None
    targets_=[]
    ifsdir_=None
    nemodir_=None
    tasks_=[]
    startdate_=None
    interval_=None

# Returns one or more cmor targets for task creation.
def get_cmor_target(var_id,tab_id=None):
    if(tab_id==None):
        return [t for t in targets_ if t.variable==var_id]
    else:
        results=[t for t in targets_ if t.variable==var_id and t.table==tab_id]
        if(len(results)==1):
            return results[0]
        elif(len(results)==0):
            return None
        else:
            raise Exception("Table validation error: multiple variables with id",var_id,"found in table",tab_id)

# Sets the IFS output directory
def set_ifs_dir(path):
    global ifsdir_
    if(os.path.isdir(path) and os.path.exists(path)):
        ifsdir_=path
    else:
        raise Exception("Invalid IFS output directory given:",path)

# Sets the nemo output directory
def set_nemo_dir(path):
    global nemodir_
    if(os.path.isdir(path) and os.path.exists(path)):
        nemodir_=path
    else:
        raise Exception("Invalid NEMO output directory given:",path)

# Sets start date and interval
def set_time_interval(startdate,interval):
    global startdate_
    global interval_
    startdate_=startdate
    interval_=interval

# Adds a task to the task list.
def add_task(tsk):
    global tasks_
    if(isinstance(tsk,cmor_task.cmor_task)):
        if(tsk.target not in targets_):
            raise Exception("Cannot append tasks with unknown target",tsk.target)
        duptasks=[t for t in tasks_ if t.target is tsk.target]
        if(len(duptasks)!=0):
            tasks_.remove(duptasks[0])
        tasks_.append(tsk)
    else:
        raise Exception("Can only append cmor_task to the list, attempt to append",tsk)

# Returns the currently defined tasks:
def get_tasks():
    global tasks_
    return tasks_

# Clears all tasks.
def clear_tasks():
    global tasks_
    tasks_=[]

# Performs an IFS cmorization processing:
def perform_ifs_tasks(postproc=True,tempdir=None):
    global tasks_
    global ifsdir_
    global startdate_
    global interval_
    global exp_name_
    global table_dir_
    global prefix_
    ifs_tasks=[t for t in tasks_ if isinstance(t.source,cmor_source.ifs_source)]
    tableroot=os.path.join(table_dir_,prefix_)
    # TODO: Add support for reference date other that startdate
    ifs2cmor.initialize(ifsdir_,exp_name_,tableroot,startdate_,interval_,startdate_,tempdir=tempdir)
    ifs2cmor.execute(ifs_tasks,postproc)

# Performs a NEMO cmorization processing:
def perform_nemo_tasks():
    global tasks_
    global nemodir_
    global startdate_
    global interval_
    global exp_name_
    global table_dir_
    global prefix_
    nemo_tasks=[t for t in tasks_ if isinstance(t.source,cmor_source.nemo_source)]
    tableroot=os.path.join(table_dir_,prefix_)
    nemo2cmor.initialize(nemodir_,exp_name_,tableroot,startdate_,interval_)
    nemo2cmor.execute(nemo_tasks)
