import os
import re
import logging
import f90nml
import xml.etree.ElementTree as elemtree
import ece2cmor
import cmor_source
import cmor_target
import cmor_task

log = logging.getLogger(__name__)

IFS_source_tag = 1
Nemo_source_tag = 2
ifs_par_file = os.path.join(os.path.dirname(__file__),"resources","ifs.par")
nemo_par_file = os.path.join(os.path.dirname(__file__),"resources","nemo.par")
nemo_iodef_file = os.path.join(os.path.dirname(__file__),"resources","iodef.xml")
nemo_grid_dict = {}


# API function: loads the argument list of targets
def load_targets(varlist):
    global log
    targetlist = []
    if(isinstance(varlist,basestring)):
        targetlist = load_targets_namelist(varlist)
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


# Creates tasks for the given targets, using the parameter tables in the resource folder
def create_tasks(targets):
    global log,IFS_source_tag,Nemo_source_tag,ifs_par_file,nemo_par_file,nemo_iodef_file
    parlist = []
    ifsparlist = f90nml.read(ifs_par_file)
    parlist.extend(ifsparlist.get("parameter"))
    ifslen = len(parlist)
    nemoparlist = f90nml.read(nemo_par_file)
    parlist.extend(nemoparlist.get("parameter"))
    load_nemo_iodef(nemo_iodef_file)
    for target in targets:
        pars = [p for p in parlist if target.variable == p["out_name"]]
        if(len(pars) == 0):
            log.error("Could not find parameter table entry for %s...skipping variable" % target.variable)
            continue
        if(len(pars) > 1):
            log.error("Multiple parameter table entries found for %s...choosing first" % target.variable)
            print "All the parameter blocks are"
            for par in pars:
                print "the source is ",par["param"]
        par = pars[0]
        tag = IFS_source_tag if parlist.index(par) < ifslen else Nemo_source_tag
        ece2cmor.add_task(create_cmor_task(create_cmor_source(par,tag),target,tag))


# Loads the legacy ece2cmor input namelists to targets
def load_targets_namelist(varlist):
    global log
    vlist = f90nml.read(varlist)
    targetlist = []
    for sublist in vlist["varlist"]:
        freq = sublist["freq"]
        vars2d = sublist.get("vars2d",[])
        vars3d = sublist.get("vars3d",[])
        for v in (vars2d + vars3d):
            tlist = ece2cmor.get_cmor_target(v)
            tgt=[t for t in tlist if t.frequency == freq]
            if(len(tgt) == 0):
                log.error("Could not find cmor targets of variable %s with frequency %s in current set of tables" % (v,freq))
            targetlist.extend(tgt)
    return targetlist


# Post-processing attributes for IFS output:
expressions = {(80,"hurs"):         "var80=100.*exp(17.62*((var168-273.15)/(var168-30.03)-(var167-273.15)/(var167-30.03)))",
               (80,"rhs"):          "var80=100.*exp(17.62*((var168-273.15)/(var168-30.03)-(var167-273.15)/(var167-30.03)))",
               (80,"rhsmin"):       "var80=100.*exp(17.62*((var168-273.15)/(var168-30.03)-(var167-273.15)/(var167-30.03)))",
               (80,"rhsmax"):       "var80=100.*exp(17.62*((var168-273.15)/(var168-30.03)-(var167-273.15)/(var167-30.03)))",
               (81,"huss"):         "var81=1./(1.+1.608*(var134*exp(-17.62*(var168-273.15)/(var168-30.03))/611.-1.))",
               (95,"rsus"):         "var95=var176-var169",
               (96,"rlus"):         "var96=var177-var175",
               (97,"rsut"):         "var97=var178-var212",
               (98,"rsutcs"):       "var98=var208-var212",
               (214,"sfcWind"):     "var214=sqrt(sqr(var165)+sqr(var166))",
               (214,"sfcWindmax"):  "var214=sqrt(sqr(var165)+sqr(var166))",
               (99,"mrsos"):        "var99=70*var39",
               (43,"mrso"):         "var43=70*var39+210*var40+720*var41+1890*var42"}


# Creates a cmor_source for the given parameter dictionary
def create_cmor_source(paramdict,tag):
    global IFS_source_tag,Nemo_source_tag,nemo_grid_dict
    parstr = paramdict["out_name"]
    if(tag == IFS_source_tag):
        code = str(paramdict["param"])
        arg = expressions.get((int(code.split('.')[0]),parstr),code)
        return cmor_source.ifs_source.read(arg)
    elif(tag == Nemo_source_tag):
        ioname = paramdict["name"]
        if(not ioname in nemo_grid_dict):
            raise Exception("Variable",ioname,"could not be associated with a nemo output file")
        grid = nemo_grid_dict[ioname]
        grid_id = -1
        try:
            grid_id = cmor_source.nemo_grid.index(grid)
        except:
            raise Exception("Unknown grid detected:",grid,"for parameter",parstr)
        return cmor_source.nemo_source(ioname,grid_id)
    else:
        return None


# Creates a cmor task, sets the correct post-processing attributes
def create_cmor_task(src,tgt,tag):
    global IFS_source_tag,Nemo_source_tag
    task = cmor_task.cmor_task(src,tgt)
    if(tag == Nemo_source_tag):
        if((src.var(),tgt.variable) == ("tossq","tossq")):
            setattr(task,cmor_task.conversion_key,"tossqfix")
    if(tag == IFS_source_tag):
        code,oname = src.get_grib_code().var_id,tgt.variable
        if((code,oname) in [(205,"mrro"),(8,"mrros"),(228,"pr"),(143,"prc"),(144,"prsn"),(44,"sbl"),(182,"evspsbl")]):
            setattr(task,cmor_task.conversion_key,"vol2flux")
        if((code,oname) in [(95,"rsus"),(96,"rlus"),(97,"rsut"),(98,"rsutcs"),(146,"hfls"),(147,"hfss"),(169,"rsds"),(175,"rlds"),(176,"ssr"),(177,"str"),\
                            (178,"tsr"),(179,"rlut"),(108,"tsrc"),(209,"rlutcs"),(210,"ssrc"),(211,"strc"),(212,"rsdt"),(180,"tauu"),(181,"tauv")]):
            setattr(task,cmor_task.conversion_key,"cum2inst")
        if((code,oname) in [(129,"zg"),(129,"orog")]):
            setattr(task,cmor_task.conversion_key,"pot2alt")
    return task


# Loads the nemo 'iodef' xml file which contains information about which variable is defined on which grid
def load_nemo_iodef(xmlpath):
    global nemo_grid_dict

    context_key = "context"
    file_def_key = "file_definition"
    file_group_key = "file_group"
    file_key = "file"
    field_key = "field"
    name_key = "name"
    suffix_key = "name_suffix"

    tree = elemtree.parse(xmlpath)
    root = tree.getroot()
    for ct in root.findall(context_key):
        for fdef in ct.findall(file_def_key):
            for fgrp in fdef.findall(file_group_key):
                for f in fgrp.findall(file_key):
                    grid = f.attrib.get(suffix_key)
                    for fld in f.findall(field_key):
                        nm = fld.attrib.get(name_key)
                        nemo_grid_dict[nm] = grid[1:] #split off the underscore
