import os
import re
import logging
import json
import ece2cmor
import cmor_source
import cmor_target
import cmor_task

log = logging.getLogger(__name__)

IFS_source_tag = 1
Nemo_source_tag = 2
ifs_par_file = os.path.join(os.path.dirname(__file__),"resources","ifspar.json")
nemo_par_file = os.path.join(os.path.dirname(__file__),"resources","nemopar.json")

json_source_key = "source"
json_target_key = "target"
json_table_key = "table"
json_grid_key = "grid"

# API function: loads the argument list of targets
def load_targets(varlist):
    targetlist = []
    if(isinstance(varlist,basestring)):
        targetlist = load_targets_json(varlist)
    elif(all(isinstance(t,cmor_target.cmor_target) for t in varlist)):
        targetlist = varlist
    elif(isinstance(varlist,dict)):
        targetlist=[]
        for table,val in varlist.iteritems():
            varseq = [val] if isinstance(val,basestring) else val
            for v in varseq:
                target = ece2cmor.get_cmor_target(v,table)
                if(target):
                    targetlist.append(target)
                else:
                    log.error("Could not find cmor target for variable %s in table %s" % (v,table))
    else:
        log.error("Cannot create a list of cmor-targets for argument %s" % varlist)
    create_tasks(targetlist)


# Loads a json file containing the cmor targets.
def load_targets_json(varlistfile):
    vartext = open(varlistfile).read()
    varlist = json.loads(varlistfile)
    targets = []
    for tab,var in varlist.iteritems():
        if(isinstance(var,basestring)):
            targets.append(ece2cmor.get_cmor_target(var,tab))
        else:
            for v in var:
                targets.append(ece2cmor.get_cmor_target(v,table))
    return targets


# Creates tasks for the given targets, using the parameter tables in the resource folder
def create_tasks(targets):
    parlist = []
    ifspartext = open(ifs_par_file).read()
    ifsparlist = json.loads(ifspartext)
    parlist.extend(ifsparlist)
    ifslen = len(parlist)
    nemopartext = open(nemo_par_file).read()
    nemoparlist = json.loads(nemopartext)
    parlist.extend(nemoparlist)
    for target in targets:
        pars = [p for p in parlist if target.variable == p[json_target_key] and target.table == p.get(json_table_key,target.table)]
        tabpars = [p for p in pars if json_table_key in p]
        if(len(pars) == 0):
            log.error("Could not find parameter table entry for %s...skipping variable." % target.variable)
            continue
        if(len(pars) > 1):
            if(len(tabpars) != 1):
                log.error("Multiple parameter table entries found for %s...choosing first found." % target.variable)
        par = pars[0] if len(tabpars) == 0 else tabpars[0]
        tag = IFS_source_tag if parlist.index(par) < ifslen else Nemo_source_tag
        task = create_cmor_task(par,target,tag)
        if task: ece2cmor.add_task(task)


# Creates a single task from the target and paramater table entry
def create_cmor_task(pardict,target,tag):
    src = pardict.get(json_source_key,None)
    expr = pardict.get(cmor_source.expression_key,None)
    if(not src and not expr):
        log.error("Could not find a source entry for parameter table entry %s...skipping variable %s for table %s." % (str(pardict.__dict__),target.variable,target.table))
        return None
    cmorsrc = None
    if(tag == IFS_source_tag):
        cmorsrc = cmor_source.ifs_source.read(expr if expr != None else src)
    elif(tag == Nemo_source_tag):
        grid = pardict.get(json_grid_key,None)
        if(not (grid in cmor_source.nemo_grid)):
            log.error("Could not find a grid value in the nemo parameter table for %s...skipping variable." % src)
            return None
        cmorsrc = cmor_source.nemo_source(src,cmor_source.nemo_grid.index(grid))
    task = cmor_task.cmor_task(cmorsrc,target)
    conv = pardict.get(cmor_task.conversion_key,None)
    if conv: setattr(task,cmor_task.conversion_key,conv)
    return task
