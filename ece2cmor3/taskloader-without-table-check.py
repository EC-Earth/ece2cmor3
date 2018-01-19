import os
import re
import logging
import json
import ece2cmorlib
import cmor_source
import cmor_target
import cmor_task

log = logging.getLogger(__name__)

IFS_source_tag = 1
Nemo_source_tag = 2
ifs_par_file = os.path.join(os.path.dirname(__file__),"resources","ifspar.json")
nemo_par_file = os.path.join(os.path.dirname(__file__),"resources","nemopar.json")
ignored_vars_file = os.path.join(os.path.dirname(__file__),"resources","list-of-ignored-cmpi6-requested-variables.xlsx")
identified_missing_vars_file = os.path.join(os.path.dirname(__file__),"resources","list-of-identified-missing-cmpi6-requested-variables.xlsx")

json_source_key = "source"
json_target_key = "target"
json_table_key = "table"
json_grid_key = "grid"
json_mask_key = "mask"
json_masked_key = "masked"

mask_predicates = {"=": lambda x,a: x == a,
                   "==":lambda x,a: x == a,
                   "!=":lambda x,a: x != a,
                   "<": lambda x,a: x < a,
                   "<=":lambda x,a: x <= a,
                   ">": lambda x,a: x > a,
                   ">=":lambda x,a: x >= a}

# API function: loads the argument list of targets
def load_targets(varlist,load_atm_tasks = True,load_oce_tasks = True):
    global log
    targetlist = []
    if(isinstance(varlist,basestring)):
        if(os.path.isfile(varlist)):
            fname,fext = os.path.splitext(varlist)
            if(len(fext) == 0):
                targetlist = load_targets_f90nml(varlist)
            elif(fext[1:] == "json"):
                targetlist = load_targets_json(varlist)
            elif(fext[1:] == "xlsx"):
                targetlist = load_targets_excel(varlist)
            elif(fext[1:] == "nml"):
                targetlist = load_targets_f90nml(varlist)
            else:
                log.error("Cannot create a list of cmor-targets for file %s with unknown file type" % varlist)
    elif(all(isinstance(t,cmor_target.cmor_target) for t in varlist)):
        targetlist = varlist
    elif(isinstance(varlist,dict)):
        targetlist=[]
        for table,val in varlist.iteritems():
            varseq = [val] if isinstance(val,basestring) else val
            for v in varseq:
		add_target(v,table,targetlist)
    else:
        log.error("Cannot create a list of cmor-targets for argument %s" % varlist)
    log.info("Found %d cmor target variables in input variable list." % len(targetlist))
    return create_tasks(targetlist,load_atm_tasks,load_oce_tasks)


# Loads a json file containing the cmor targets.
def load_targets_json(varlist):
    vartext = open(varlist).read()
    varlist = json.loads(vartext)
    targets = []
    for tab,var in varlist.iteritems():
        if(isinstance(var,basestring)):
            add_target(var,tab,targets)
        else:
            for v in var:
		add_target(v,tab,targets)
    return targets


# Loads the legacy ece2cmorlib input namelists to targets
def load_targets_f90nml(varlist):
    global log
    import f90nml
    vlist = f90nml.read(varlist)
    targets = []
    for sublist in vlist["varlist"]:
        freq = sublist["freq"]
        vars2d = sublist.get("vars2d",[])
        vars3d = sublist.get("vars3d",[])
        for v in (vars2d + vars3d):
            tlist = ece2cmorlib.get_cmor_target(v)
            tgt = [t for t in tlist if t.frequency == freq]
            if(len(tgt) == 0):
                log.error("Could not find cmor targets of variable %s with frequency %s in current set of tables" % (v,freq))
            targets.extend(tgt)
    return targets


# Loads a drq excel file containing the cmor targets.
def load_targets_excel(varlist):
    global log
    import xlrd
    targets = []
    cmor_colname = "CMOR Name"
    vid_colname = "vid"
    priority_colname = "Priority"
    book = xlrd.open_workbook(varlist)
    for sheetname in book.sheet_names():
        if(sheetname.lower() in ["notes","fx","Ofx"]): continue
        sheet = book.sheet_by_name(sheetname)
        row = sheet.row_values(0)
        if(cmor_colname not in row):
            log.error("Could not find cmor variable column in sheet %s for file %s: skipping variable" % (sheet,varlist))
            continue
        index          = row.index(cmor_colname)
        vid_index      = row.index(vid_colname)
        priority_index = row.index(priority_colname)
        varnames = [c.value for c in sheet.col_slice(colx =          index,start_rowx = 1)]
        vids     = [c.value for c in sheet.col_slice(colx =      vid_index,start_rowx = 1)]
        priority = [c.value for c in sheet.col_slice(colx = priority_index,start_rowx = 1)]
        for i in range(len(varnames)):
            add_target(str(varnames[i]),sheetname,targets,vids[i],priority[i])
    return targets


# Small utility loading targets from the list
def add_target(variable,table,targetlist,vid = None, priority = None):
    global log
    target = ece2cmorlib.get_cmor_target(variable,table)
    if(target):
        if(vid):
          target.vid = vid
        if(priority):
          target.priority = priority
        targetlist.append(target)
        return True
    else:
        log.error("The %s variable does not appear in the CMOR table file CMIP6_%s.json" % (variable,table))
	return False


# Loads the basic excel ignored file containing the cmor variables for which has been decided that they will be not taken into account or
# it loads the basic excel identifiedmissing file containing the cmor variables which have been identified but are not yet fully cmorized.
# This function can be used to read any excel file which has been produced by the checkvars.py script, in other words it can read the
# basic ignored, basic identified missing, available, ignored, identifiedmissing, and missing files.
def load_checkvars_excel(basic_ignored_excel_file):
    global log
    import xlrd
    targets = []
    var_colname = "variable"
    comment_colname = "comment"
    author_colname = "comment author"
    book = xlrd.open_workbook(basic_ignored_excel_file)
    varlist = {}
    for sheetname in book.sheet_names():
        if(sheetname.lower() in ["notes"]): continue
        sheet = book.sheet_by_name(sheetname)
        header = sheet.row_values(0)
        coldict = {}
        for colname in [var_colname,comment_colname,author_colname]:
            if(colname not in header):
                log.error("Could not find the column %s in sheet %s for file %s: skipping sheet" % (colname,sheet,varlist))
                continue
            coldict[colname] = header.index(colname)
        varnames = [c.value for c in sheet.col_slice(colx = coldict[var_colname],start_rowx = 1)]
        comments = [c.value for c in sheet.col_slice(colx = coldict[comment_colname],start_rowx = 1)]
        authors  = [c.value for c in sheet.col_slice(colx = coldict[author_colname],start_rowx = 1)]
        for i in range(len(varnames)):
            varlist[varnames[i]] = (comments[i], authors[i])
    return varlist


# Creates tasks for the given targets, using the parameter tables in the resource folder
def create_tasks(targets,load_atm_tasks = True,load_oce_tasks = True):
    global log,IFS_source_tag,Nemo_source_tag,ifs_par_file,nemo_par_file,ignored_vars_file,json_table_key
    parlist = []
    if(os.path.isfile(ifs_par_file)):
        with open(ifs_par_file) as f:
            ifsparlist = json.loads(f.read())
            parlist.extend(ifsparlist)
    ifslen = len(parlist)
    if(os.path.isfile(nemo_par_file)):
        with open(nemo_par_file) as f:
            nemoparlist = json.loads(f.read())
            parlist.extend(nemoparlist)

    ignoredvarlist           = load_checkvars_excel(ignored_vars_file)
    identifiedmissingvarlist = load_checkvars_excel(identified_missing_vars_file)

    loadedtargets,ignoredtargets,identifiedmissingtargets,missingtargets = [],[],[],[]

    for target in targets:
        realms = getattr(target,cmor_target.realm_key,None).split()
        atmrealms = ["atmos","atmosChem","land","landIce"]
        if(not load_atm_tasks and any([r for r in atmrealms if r in realms])):
            continue
        ocnrealms = ["ocean","ocnBgChem","seaIce"]
        if(not load_oce_tasks and any([r for r in ocnrealms if r in realms])):
            continue
        pars = [p for p in parlist if matchvarpar(target.variable,p) and target.table == p.get(json_table_key,target.table)]
        if(len(pars) == 0):
            if(target.variable in ignoredvarlist):
            	varword = "ignored"
                target.ecearth_comment, target.comment_author = ignoredvarlist[target.variable]
                ignoredtargets.append(target)
            elif(target.variable in identifiedmissingvarlist):
            	varword = "identified missing"
                target.ecearth_comment, target.comment_author = identifiedmissingvarlist[target.variable]
                identifiedmissingtargets.append(target)
            else:
            	varword = "missing"
                missingtargets.append(target)
            log.error("Could not find parameter table entry for %s in table %s...skipping variable. This variable is %s" % (target.variable,target.table,varword))
            continue
        tabpars = [p for p in pars if json_table_key in p]
        if(len(pars) > 1):
            if(len(tabpars) != 1):
                log.warning("Multiple parameter table entries found for %s in table %s...choosing first found." % (target.variable,target.table))
                for p in pars: log.warning("Parameter table entry found: %s" % str(p))
        par = pars[0] if len(tabpars) == 0 else tabpars[0]
        tag = IFS_source_tag if parlist.index(par) < ifslen else Nemo_source_tag
        task = create_cmor_task(par,target,tag)
        ece2cmorlib.add_task(task)
        loadedtargets.append(target)
    log.info("Created %d ece2cmor tasks from input variable list." % len(loadedtargets))
    for par in ifsparlist:
        if(json_mask_key in par):
            name = par[json_mask_key]
            expr = par.get(cmor_source.expression_key,None)
            if(not expr):
                log.error("No expression given for mask %s, ignoring mask definition" % name)
            else:
                srcstr,func,val = parse_maskexpr(expr)
                if(srcstr):
                    src = create_cmor_source({json_source_key: srcstr},IFS_source_tag)
                    ece2cmorlib.add_mask(name,src,func,val)
    return loadedtargets,ignoredtargets,identifiedmissingtargets,missingtargets


# Parses the input mask expression
def parse_maskexpr(exprstring):
    global mask_predicates
    ops = list(mask_predicates.keys())
    ops.sort(key=len)
    for op in ops[::-1]:
        tokens = exprstring.split(op)
        if(len(tokens) == 2):
            src = tokens[0].strip()
            if(src.startswith("var")): src = src[3:]
            if(len(src.split("."))==1): src += ".128"
            func = mask_predicates[op]
            val = float(tokens[1].strip())
            return src,func,val
    log.error("Expression %s could not be parsed to a valid mask expression")
    return None,None,None


# Checks whether the variable matches the parameter table block
def matchvarpar(variable,parblock):
    global json_target_key
    parvars = parblock.get(json_target_key,None)
    if(isinstance(parvars,list)): return (variable in parvars)
    if(isinstance(parvars,basestring)): return (variable == parvars)
    return False


# Creates a single task from the target and paramater table entry
def create_cmor_task(pardict,target,tag):
    global log,IFS_source_tag,Nemo_source_tag,json_source_key,json_grid_key
    task = cmor_task.cmor_task(create_cmor_source(pardict,tag),target)
    mask = pardict.get(json_masked_key,None)
    if mask: setattr(task.target,cmor_target.mask_key,mask)
    conv = pardict.get(cmor_task.conversion_key,None)
    if conv: setattr(task,cmor_task.conversion_key,conv)
    return task


# Creates an ece2cmor task source from the input dictionary
def create_cmor_source(pardict,tag):
    src = pardict.get(json_source_key,None)
    expr = pardict.get(cmor_source.expression_key,None)
    if(not src and not expr):
        log.error("Could not find a source entry for parameter table entry %s...skipping variable %s for table %s." % (str(pardict.__dict__),target.variable,target.table))
        return None
    cmorsrc = None
    if(tag == IFS_source_tag):
        return cmor_source.ifs_source.read(expr if expr != None else src)
    elif(tag == Nemo_source_tag):
        grid = pardict.get(json_grid_key,None)
        if(not (grid in cmor_source.nemo_grid)):
            log.error("Could not find a grid value in the nemo parameter table for %s...skipping variable." % src)
            return None
        return cmor_source.nemo_source(src,cmor_source.nemo_grid.index(grid))
    return None
