import cmor
import cmor_target

targets_=[]
ifsdir_=None
nemodir_=None
tasks_=[]

def initialize(table_path,metadata_json):
    cmor.cmor_setup(table_path)
    cmor.cmor_dataset_json(metadata_file)
    targets_=cmor_target.create_targets()

def get_cmor_target(var_id,tab_id=None):
    results=[t for t in targets_ if t.variable==var_id and t.table==tab_id]
    if(len(results)==1):
        return results[0]
    else:
        return results

def set_ifs_dir(path):
    ifsdir_=path

def set_nemo_dir(path):
    nemodir_=path

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
