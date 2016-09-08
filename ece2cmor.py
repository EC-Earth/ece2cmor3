import cmor
import os
import cmor_target

# ece2cmor master API.

prefix_=None
table_path_=None
config_file_=None
targets_=[]
ifsdir_=None
nemodir_=None
tasks_=[]

# Initialization function, must be called before starting

def initialize(table_root,conf_path):
    prefix_=os.path.splitext(os.path.basename(table_root))[0]
    table_path_=os.path.dirname(table_root)
    conf_path_=conf_path

    cmor.setup(table_path_)
    cmor.dataset_json(conf_path_)
    targets_=cmor_target.create_targets(table_path_,prefix_)

# Returns one or more cmor targets for task creation.

def get_cmor_target(var_id,tab_id=None):
    results=[t for t in targets_ if t.variable==var_id and t.table==tab_id]
    if(len(results)==1):
        return results[0]
    else:
        return results

# Sets the IFS output directory

def set_ifs_dir(path):
    ifsdir_=path

# Sets the nemo output directory

def set_nemo_dir(path):
    nemodir_=path

# Adds a task to the task list.

def add_task(tsk):
    if(tsk.isinstance(cmor_task)):
        if(tsk.target not in targets_):
            raise Exception("Cannot append tasks with unknown target",tsk.target)
        duptasks=[t for t in tasks_ if t.target != tsk.target]
        if(len(duptasks)!=0):
            dtset=set(duptasks)
            tasks_=[t for t in tasks_ if t not in dtset]
        tasks_.append(tsk)
    else:
        raise Exception("Can only append cmor_task to the list, attempt to append",tsk)

# Clears all tasks.

def clear_tasks():
    tasks_.clear()
