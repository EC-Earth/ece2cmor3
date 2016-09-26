import re
import f90nml
import xml.etree.ElementTree as elemtree
import ece2cmor
import cmor_source
import cmor_task

IFS_source_tag=1
Nemo_source_tag=2

nemo_grid_dict={}

# Loads the nemo 'iodef' xml file which contains information about which variable is defined on which grid
def load_nemo_iodef(xmlpath):
    global nemo_grid_dict

    context_key="context"
    file_def_key="file_definition"
    file_group_key="file_group"
    file_key="file"
    field_key="field"
    name_key="name"
    suffix_key="name_suffix"

    tree=elemtree.parse(xmlpath)
    root=tree.getroot()
    for ct in root.findall(context_key):
        for fdef in ct.findall(file_def_key):
            for fgrp in fdef.findall(file_group_key):
                for f in fgrp.findall(file_key):
                    grid=f.attrib.get(suffix_key)
                    for fld in f.findall(field_key):
                        nm=fld.attrib.get(name_key)
                        nemo_grid_dict[nm]=grid[1:] #split off the underscore


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
        varname=p["out_name"]
        for tgt in targetlist:
            if(tgt.variable!=varname): continue
            src=create_cmor_source(p,tag)
            ece2cmor.add_task(cmor_task.cmor_task(src,tgt))
            targetlist.remove(tgt)

# Creates a cmor_source for the given parameter dictionary
def create_cmor_source(paramdict,tag):
    parstr=paramdict["out_name"]
    if(tag==IFS_source_tag):
        return cmor_source.ifs_source(grib_code.read(parstr))
    elif(tag==Nemo_source_tag):
        ioname=paramdict["name"]
        if(not ioname in nemo_grid_dict):
            raise Exception("Variable",ioname,"could not be associated with a nemo output file")
        grid=nemo_grid_dict[ioname]
        grid_id=-1
        try:
            grid_id=cmor_source.nemo_grid.index(grid)
        except:
            raise Exception("Unknown grid detected:",grid,"for parameter",parstr)
        return cmor_source.nemo_source(parstr,grid_id)
    else:
        raise Exception("Unknown tag passed:",tag)

# Loads the legacy ece2cmor input namelists to targets
def load_targets_namelist(varlist):
    vlist=f90nml.read(varlist)
    targetlist=[]
    for sublist in vlist["varlist"]:
        freq=sublist["freq"]
        vars2d=sublist.get("vars2d",[])
        vars3d=sublist.get("vars3d",[])
        for v in (vars2d+vars3d):
            tlist=ece2cmor.get_cmor_target(v)
            tgt=[t for t in tlist if t.frequency==freq]
            targetlist.extend(tgt)
    return targetlist
