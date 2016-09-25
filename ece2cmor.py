import cmor
import os
import cmor_target
import cmor_task
import f90nml

# ece2cmor master API.
prefix_=None
table_path_=None
config_file_=None
targets_=[]
ifsdir_=None
nemodir_=None
tasks_=[]
startdate_=None
interval_=None

# Initialization function, must be called before starting
def initialize(table_root,conf_path):
    global prefix_
    global table_path_
    global conf_path_
    global targets_
    global ifsdir_
    global nemodir_
    global tasks_

    prefix_=os.path.splitext(os.path.basename(table_root))[0]
    table_path_=os.path.dirname(table_root)
    conf_path_=conf_path

    cmor.setup(table_path_)
    cmor.dataset_json(conf_path_)
    targets_=cmor_target.create_targets(table_path_,prefix_)

    ifsdir_=None
    nemodir_=None
    tasks_=[]

# Closes cmor
def finalize():
    global prefix_
    global table_path_
    global config_file_
    global targets_
    global ifsdir_
    global nemodir_

    cmor.close()
    prefix_=None
    table_path_=None
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
    interval=interval

# Adds a task to the task list.
def add_task(tsk):
    global tasks_
    print id(tsk.target)
    if(isinstance(tsk,cmor_task.cmor_task)):
        if(tsk.target not in targets_):
            raise Exception("Cannot append tasks with unknown target",tsk.target)
        duptasks=[t for t in tasks_ if t.target is tsk.target]
        if(len(duptasks)!=0):
            tasks_.remove(duptasks[0])
        tasks_.append(tsk)
    else:
        raise Exception("Can only append cmor_task to the list, attempt to append",tsk)

# Loads the legacy ece2cmor input namelists to tasks:
def load_task_namelists(varlist,ifspar=None,nemopar=None):
    targetlist=load_targets_namelist(varlist)
    ifsparlist=[]
    if(ifspar):
        ifsparlist=f90nml.read(ifspar)
        for p in ifsparlist.get("parameter"):
            codestr=p["param"]
            varname=p["out_name"]
            src=ifs_source(grib_code.read(codestr))
            for t in targetlist:
                if(t.variable!=varname) continue
                add_task(cmor_task(src,t))
                targetlist.remove(t)
    nemoparlist=[]
    if(nemopar):
        nemoparlist=f90nml.read(nemopar)
        for p in nemoparlist.get("parameter"):
            vstr=p["param"]
            varname=p["out_name"]
            src=nemo_source(vstr) #TODO: add dimensions and grid type
            for t in targetlist:
                if(t.variable!=varname) continue
                add_task(cmor_task(src,t))
                targetlist.remove(t)

# Loads the legacy ece2cmor input namelists to targets
def load_targets_namelist(varlist):
    vlist=f90nml.read(varlist)
    targetlist=[]
    for sublist in vlist["varlist"]:
        freq=sublist["freq"]
        vars2d=sublist.get("vars2d",[])
        vars3d=sublist.get("vars3d",[])
        for v in (vars2d+vars3d):
            tlist=get_cmor_targets(v)
            tgt=[t for t in tlist if t.frequency==freq]
            targetlist.extend(tgt)
    return targetlist


# Returns the currently defined tasks:
def get_tasks():
    global tasks_
    return tasks_

# Clears all tasks.
def clear_tasks():
    global tasks_
    tasks_=[]

# Performs a NEMO cmorization processing:
def perform_nemo_tasks():
    global tasks_
    global nemodir_
    global startdate_
    global interval_
    global prefix_
    global table_path_
    nemo_tasks=[t for t in tasks_ if isinstance(t.source,cmor_source.nemo_source)]
    nemo2cmor.initialize(nemodir_,prefix_,table_path_,startdate_,interval_)
    nemo2cmor.execute(nemo_tasks,nemodir_,startdate,interval)
