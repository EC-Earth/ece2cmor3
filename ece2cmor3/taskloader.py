import json
import logging
import os

from ece2cmor3 import components
from ece2cmor3 import ece2cmorlib, cmor_source, cmor_target, cmor_task
from ece2cmor3.cmor_source import create_cmor_source

log = logging.getLogger(__name__)

json_source_key = "source"
json_target_key = "target"
json_table_key = "table"
json_mask_key = "mask"
json_masked_key = "masked"
json_filepath_key = "filepath"

omit_vars_file_01 = os.path.join(os.path.dirname(__file__), "resources/lists-of-omitted-variables",
                                 "list-of-omitted-variables-01.xlsx")
omit_vars_file_02 = os.path.join(os.path.dirname(__file__), "resources/lists-of-omitted-variables",
                                 "list-of-omitted-variables-02.xlsx")
omit_vars_file_03 = os.path.join(os.path.dirname(__file__), "resources/lists-of-omitted-variables",
                                 "list-of-omitted-variables-03.xlsx")
omit_vars_file_04 = os.path.join(os.path.dirname(__file__), "resources/lists-of-omitted-variables",
                                 "list-of-omitted-variables-04.xlsx")
omit_vars_file_05 = os.path.join(os.path.dirname(__file__), "resources/lists-of-omitted-variables",
                                 "list-of-omitted-variables-05.xlsx")
ignored_vars_file = os.path.join(os.path.dirname(__file__), "resources",
                                 "list-of-ignored-cmpi6-requested-variables.xlsx")
identified_missing_vars_file = os.path.join(os.path.dirname(__file__), "resources",
                                            "list-of-identified-missing-cmpi6-requested-variables.xlsx")

mask_predicates = {"=": lambda x, a: x == a,
                   "==": lambda x, a: x == a,
                   "!=": lambda x, a: x != a,
                   "<": lambda x, a: x < a,
                   "<=": lambda x, a: x <= a,
                   ">": lambda x, a: x > a,
                   ">=": lambda x, a: x >= a}

skip_tables = False
with_pingfile = False


# API function: loads the argument list of targets
def load_targets(varlist, active_components=None, silent=False, target_filters=[]):
    global log
    targetlist = []
    if isinstance(varlist, basestring):
        if os.path.isfile(varlist):
            fname, fext = os.path.splitext(varlist)
            if len(fext) == 0:
                targetlist = load_targets_f90nml(varlist)
            elif fext[1:] == "json":
                targetlist = load_targets_json(varlist)
            elif fext[1:] == "xlsx":
                targetlist = load_targets_excel(varlist)
            elif fext[1:] == "nml":
                targetlist = load_targets_f90nml(varlist)
            else:
                log.error("Cannot create a list of cmor-targets for file %s with unknown file type" % varlist)
    elif all(isinstance(t, cmor_target.cmor_target) for t in varlist):
        targetlist = varlist
    elif isinstance(varlist, dict):
        targetlist = []
        for table, val in varlist.iteritems():
            varseq = [val] if isinstance(val, basestring) else val
            for v in varseq:
                add_target(v, table, targetlist)
    else:
        log.error("Cannot create a list of cmor-targets for argument %s" % varlist)
    for f in target_filters:
        targetlist = filter(f, targetlist)
    log.info("Found %d cmor target variables in input variable list." % len(targetlist))
    return create_tasks(targetlist, active_components, silent)


# Loads a json file containing the cmor targets.
def load_targets_json(varlist):
    vartext = open(varlist).read()
    varlist = json.loads(vartext)
    targets = []
    for tab, var in varlist.iteritems():
        if isinstance(var, basestring):
            add_target(var, tab, targets)
        else:
            for v in var:
                add_target(v, tab, targets)
    return targets


# Loads the legacy ece2cmorlib input namelists to targets
def load_targets_f90nml(varlist):
    global log
    import f90nml
    vlist = f90nml.read(varlist)
    targets = []
    for sublist in vlist["varlist"]:
        freq = sublist["freq"]
        vars2d = sublist.get("vars2d", [])
        vars3d = sublist.get("vars3d", [])
        for v in (vars2d + vars3d):
            tlist = ece2cmorlib.get_cmor_target(v)
            tgt = [t for t in tlist if t.frequency == freq]
            if len(tgt) == 0:
                log.error(
                    "Could not find cmor targets of variable %s with frequency %s in current set of tables" % (v, freq))
            targets.extend(tgt)
    return targets


# Loads a drq excel file containing the cmor targets.
def load_targets_excel(varlist):
    global log
    import xlrd
    targets = []
    cmor_colname = "CMOR Name"
    vid_colname = "vid"
    priority_colname = "Priority"  # Priority column name for the experiment   cmvme_*.xlsx files
    default_priority_colname = "Default Priority"  # Priority column name for the mip overview cmvmm_*.xlsx files
    mip_list_colname = "MIPs (by experiment)"
    book = xlrd.open_workbook(varlist)
    for sheetname in book.sheet_names():
        if sheetname.lower() in ["notes", "fx"]:
            continue
        sheet = book.sheet_by_name(sheetname)
        row = sheet.row_values(0)
        if cmor_colname not in row:
            log.error(
                "Could not find cmor variable column in sheet %s for file %s: skipping variable" % (sheet, varlist))
            continue
        index = row.index(cmor_colname)
        vid_index = row.index(vid_colname)
        if priority_colname in row:
            priority_index = row.index(priority_colname)
        elif default_priority_colname in row:  # If no "Priority" column is found try to find a "Default Priority" column
            priority_index = row.index(default_priority_colname)
        else:  # If no "Priority" column and no "Default Priority" column are found, abort with message
            raise Exception(
                "Error: Could not find priority variable column in sheet %s for file %s. Program has been aborted." % (
                sheet, varlist))
        mip_list_index = row.index(mip_list_colname)
        varnames = [c.value for c in sheet.col_slice(colx=index, start_rowx=1)]
        vids = [c.value for c in sheet.col_slice(colx=vid_index, start_rowx=1)]
        priority = [c.value for c in sheet.col_slice(colx=priority_index, start_rowx=1)]
        mip_list = [c.value for c in sheet.col_slice(colx=mip_list_index, start_rowx=1)]
        for i in range(len(varnames)):
            add_target(str(varnames[i]), sheetname, targets, vids[i], priority[i], mip_list[i])
    return targets


# Small utility loading targets from the list
def add_target(variable, table, targetlist, vid=None, priority=None, mip_list=None):
    global log
    target = ece2cmorlib.get_cmor_target(variable, table)
    if target:
        if vid:
            target.vid = vid
        if priority:
            target.priority = priority
        if mip_list:
            target.mip_list = mip_list
        targetlist.append(target)
        return True
    else:
        log.error("The %s variable does not appear in the CMOR table file %s" % (variable, table))
    return False


# Loads the basic excel ignored file containing the cmor variables for which has been decided that they will be not
# taken into account or it loads the basic excel identified-missing file containing the cmor variables which have
# been identified but are not yet fully cmorized. This function can be used to read any excel file which has been
# produced by the checkvars.py script, in other words it can read the basic ignored, basic identified missing,
# available, ignored, identified-missing, and missing files.
def load_checkvars_excel(basic_ignored_excel_file):
    global log, skip_tables, with_pingfile
    import xlrd
    table_colname = "Table"
    var_colname = "variable"
    comment_colname = "comment"
    author_colname = "comment author"
    if with_pingfile:
        model_colname = "model component in ping file"
        units_colname = "units as in ping file"
        pingcomment_colname = "ping file comment"
    book = xlrd.open_workbook(basic_ignored_excel_file)
    varlist = {}
    for sheetname in book.sheet_names():
        if sheetname.lower() in ["notes"]:
            continue
        sheet = book.sheet_by_name(sheetname)
        header = sheet.row_values(0)
        coldict = {}
        for colname in [table_colname, var_colname, comment_colname, author_colname]:
            if colname not in header:
                log.error(
                    "Could not find the column '%s' in sheet %s for file %s: skipping sheet" % (
                    colname, sheet, varlist))
                continue
            coldict[colname] = header.index(colname)
        tablenames = [] if skip_tables else [c.value for c in
                                             sheet.col_slice(colx=coldict[table_colname], start_rowx=1)]
        varnames = [c.value for c in sheet.col_slice(colx=coldict[var_colname], start_rowx=1)]
        comments = [c.value for c in sheet.col_slice(colx=coldict[comment_colname], start_rowx=1)]
        authors = [c.value for c in sheet.col_slice(colx=coldict[author_colname], start_rowx=1)]
        if with_pingfile:
            if model_colname not in header:
                # log.error("Could not find the column '%s' in sheet %s for file %s: skipping sheet" % (model_colname, sheet, varlist))
                continue
            coldict[model_colname] = header.index(model_colname)
            model = [c.value for c in sheet.col_slice(colx=coldict[model_colname], start_rowx=1)]
            coldict[units_colname] = header.index(units_colname)
            units = [c.value for c in sheet.col_slice(colx=coldict[units_colname], start_rowx=1)]
            coldict[pingcomment_colname] = header.index(pingcomment_colname)
            pingcomment = [c.value for c in sheet.col_slice(colx=coldict[pingcomment_colname], start_rowx=1)]
        if skip_tables:
            for i in range(len(varnames)):
                if with_pingfile:
                    varlist[varnames[i]] = (comments[i], authors[i], model[i], units[i], pingcomment[i])
                else:
                    varlist[varnames[i]] = (comments[i], authors[i])
        else:
            for i in range(len(varnames)):
                varlist[(tablenames[i], varnames[i])] = (comments[i], authors[i])
    return varlist


# Creates tasks for the given targets, using the parameter tables in the resource folder
def create_tasks(targets, active_components=None, silent=False):
    global log, ignored_vars_file, json_table_key, skip_tables
    active_realms, model_vars = {}, {}
    for m in components.models:
        is_active = True if active_components is None else active_components.get(m, True)
        for r in components.models[m][components.realms]:
            active_realms[r] = is_active or active_realms.get(r, False)  # True if any model can produce the realm
        tabfile = components.models[m].get(components.table_file, "")
        if os.path.isfile(tabfile):
            with open(tabfile) as f:
                model_vars[m] = json.loads(f.read())
        else:
            log.warning("Could not read variable table file %s for component %s" % (tabfile, m))
            model_vars[m] = []

    omitvarlist_01 = load_checkvars_excel(omit_vars_file_01)
    omitvarlist_02 = load_checkvars_excel(omit_vars_file_02)
    omitvarlist_03 = load_checkvars_excel(omit_vars_file_03)
    omitvarlist_04 = load_checkvars_excel(omit_vars_file_04)
    omitvarlist_05 = load_checkvars_excel(omit_vars_file_05)
    ignoredvarlist = load_checkvars_excel(ignored_vars_file)
    identifiedmissingvarlist = load_checkvars_excel(identified_missing_vars_file)
    loadedtargets, ignoredtargets, identifiedmissingtargets, missingtargets = [], [], [], []

    for target in targets:
        realms = getattr(target, cmor_target.realm_key, None).split()
        if not any([active_realms.get(r, True) for r in realms]):
            continue  # If all variable's realms are flagged false, skip
        matchpars = {}
        for model in components.models:
            is_active = True if active_components is None else active_components.get(model, True)
            if is_active:  # Only consider models that are 'enabled'
                matches = [p for p in model_vars.get(model, []) if
                           matchvarpar(target.variable, p) and target.table == p.get(json_table_key, target.table)]
                if any(matches):
                    matchpars[model] = matches
        if not any(matchpars):
            key = target.variable if skip_tables else (target.table, target.variable)
            if key in ignoredvarlist:
                target.ecearth_comment, target.comment_author = ignoredvarlist[key]
                ignoredtargets.append(target)
                varword = "ignored"
            elif key in identifiedmissingvarlist:
                if with_pingfile:
                    target.ecearth_comment, target.comment_author, target.model, target.units, target.pingcomment = \
                    identifiedmissingvarlist[key]
                else:
                    target.ecearth_comment, target.comment_author = identifiedmissingvarlist[key]
                identifiedmissingtargets.append(target)
                varword = "identified missing"
            elif key in omitvarlist_01:
                varword = "omit 01"
            elif key in omitvarlist_02:
                varword = "omit 02"
            elif key in omitvarlist_03:
                varword = "omit 03"
            elif key in omitvarlist_04:
                varword = "omit 04"
            elif key in omitvarlist_05:
                varword = "omit 05"
            else:
                missingtargets.append(target)
                varword = "missing"
            if not silent:
                log.error("Could not find parameter table entry for %s in table %s ...skipping variable. "
                          "This variable is %s" % (target.variable, target.table, varword))
            continue
        modelmatch = None
        for model in matchpars:
            modelmatch = model
            if len(matchpars) == 1:
                break
            modelrealms = set(components.models.get(model, {}).get(components.realms, []))
            shared_realms = set(realms).intersection(modelrealms)
            if any(shared_realms):
                log.info("Multiple models %s found for variable %s, model %s matched by shared realms %s" % (
                    matchpars.keys(), target.variable, model, shared_realms))
                break
        pars = matchpars[modelmatch]
        table_pars = [p for p in pars if json_table_key in p]
        notable_pars = [p for p in pars if json_table_key not in p]
        if len(table_pars) > 1 or len(notable_pars) > 1:
            log.warning("Multiple entries found for variable %s, table %s in file %s...choosing first." % (
                target.variable, target.table, components.models[modelmatch][components.table_file]))
        parmatch = table_pars[0] if any(table_pars) else pars[0]
        task = create_cmor_task(parmatch, target, modelmatch)
        if task is None:
            continue
        ece2cmorlib.add_task(task)
        if parmatch.get(cmor_source.expression_key, None) is None:
            target.ecearth_comment = task.source.model_component() + ' code name = ' + parmatch.get(json_source_key,
                                                                                                    None)
        else:
            target.ecearth_comment = task.source.model_component() + ' code name = ' \
                                     + parmatch.get(json_source_key, None) + ', expression = ' \
                                     + parmatch.get(cmor_source.expression_key, None)
        target.comment_author = 'automatic'
        loadedtargets.append(target)
    log.info("Created %d ece2cmor tasks from input variable list." % len(loadedtargets))
    for par in model_vars["ifs"]:
        if json_mask_key in par:
            name = par[json_mask_key]
            expr = par.get(cmor_source.expression_key, None)
            if not expr:
                log.error("No expression given for mask %s, ignoring mask definition" % name)
            else:
                srcstr, func, val = parse_maskexpr(expr)
                if srcstr:
                    src = create_cmor_source({json_source_key: srcstr}, "ifs")
                    ece2cmorlib.add_mask(name, src, func, val)
    return loadedtargets, ignoredtargets, identifiedmissingtargets, missingtargets


# Parses the input mask expression
def parse_maskexpr(exprstring):
    global mask_predicates
    ops = list(mask_predicates.keys())
    ops.sort(key=len)
    for op in ops[::-1]:
        tokens = exprstring.split(op)
        if len(tokens) == 2:
            src = tokens[0].strip()
            if src.startswith("var"):
                src = src[3:]
            if len(src.split(".")) == 1:
                src += ".128"
            func = mask_predicates[op]
            val = float(tokens[1].strip())
            return src, func, val
    log.error("Expression %s could not be parsed to a valid mask expression")
    return None, None, None


# Checks whether the variable matches the parameter table block
def matchvarpar(variable, parblock):
    global json_target_key
    parvars = parblock.get(json_target_key, None)
    if isinstance(parvars, list):
        return variable in parvars
    if isinstance(parvars, basestring):
        return variable == parvars
    return False


# Creates a single task from the target and parameter table entry
def create_cmor_task(pardict, target, component):
    global log, json_source_key
    source = create_cmor_source(pardict, component)
    if source is None:
        log.error("Failed to construct a source for target variable %s in table %s...skipping task"
                  % (target.variable, target.table))
        return None
    task = cmor_task.cmor_task(source, target)
    mask = pardict.get(json_masked_key, None)
    if mask:
        setattr(task.target, cmor_target.mask_key, mask)
    for par in pardict:
        if par not in [json_source_key, json_target_key, json_mask_key, json_masked_key, json_table_key, "expr"]:
            setattr(task, par, pardict[par])
    return task
