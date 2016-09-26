import re
import f90nml
import ece2cmor
import cmor_source

IFS_source_tag=1
Nemo_source_tag=2

# Loads the legacy ece2cmor input namelists to tasks:
def load_task_namelists(varlist,ifspar=None,nemopar=None):
    targetlist=load_targets_namelist(varlist)
    parlist=[]
    if(ifspar):
        ifsparlist=f90nml.read(ifspar)
        parlist.extend(ifsparlist.get("parameter"))
    ifslen=len(parlist)
    if(nemopar):
        nemoparlist=f90nml.read(nemopar)
        parlist.extend(nemoparlist.get("parameter"))
    index=0
    for p in parlist:
        tag=1
        if(index>=ifslen):
            tag=2
        index+=1
        src=create_cmor_source(p,tag)
        varname=p["out_name"]
        for tgt in targetlist:
            if(tgt.variable!=varname) continue
            ece2cmor.add_task(cmor_task(src,tgt))
            targetlist.remove(tgt)


def create_cmor_source(paramdict,tag):
    parstr=p["param"]
    if(tag==IFS_source_tag):
        return cmor_source.ifs_source(grib_code.read(parstr))
    elif(tag==Nemo_source_tag):
        varstr=p["param"]
        return cmor_source.nemo_source(parstr) #TODO: get grid and dim


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
