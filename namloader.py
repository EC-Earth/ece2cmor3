import re
import f90nml
import xml.etree.ElementTree as elemtree
import ece2cmor
import cmor_source
import cmor_task

IFS_source_tag = 1
Nemo_source_tag = 2
ifs_par_file = os.path.join(os.path.dirname(__file__),"resources","ifs.par")
nemo_par_file = os.path.join(os.path.dirname(__file__),"resources","nemo.par")
nemo_grid_dict = {}

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
                    grid=f.attrib.get(suffix_key)
                    for fld in f.findall(field_key):
                        nm=fld.attrib.get(name_key)
                        nemo_grid_dict[nm]=grid[1:] #split off the underscore


# Loads the legacy ece2cmor input namelists to tasks:
def load_task_namelists(varlist):
    targetlist = []
    if(isinstance(varlist,basestring)):
        targetlist = load_targets_namelist(varlist)
    elif(all(isinstance(t,cmor_target) for t in varlist)):
        targetlist = varlist
    elif(isinstance(varlist,dict)):
        targetlist=[]
        for table,val in varlist.iteritems():
            varseq = [val] if isinstance(val,basestring) else val
            for v in varseq: targetlist.append(ece2cmor.get_cmor_target(v,table))
    else:
        print "Cannot create a list of cmor-targets for argument",varlist
    make_tasks(targetlist)


# Creates tasks for the given targets, using the parameter tables in the resource folder
def make_tasks(targets):
    parlist = []
    ifsparlist = f90nml.read(ifs_par_file)
    parlist.extend(ifsparlist.get("parameter"))
    ifslen = len(parlist)
    nemoparlist = f90nml.read(nemo_par_file)
    parlist.extend(nemoparlist.get("parameter"))
    index = 0
    for p in parlist:
        tag = IFS_source_tag
        if(index >= ifslen):
            tag = Nemo_source_tag
        index += 1
        varname = p["out_name"]
        for tgt in targets:
            if(tgt.variable != varname): continue
            if(tag == Nemo_source_tag and not tgt.realm in ["ocean","seaIce ocean"]): continue
            ece2cmor.add_task(create_cmor_task(create_cmor_source(p,tag),tgt,tag))
            targets.remove(tgt)

# Loads the legacy ece2cmor input namelists to targets
def load_targets_namelist(varlist):
    vlist = f90nml.read(varlist)
    targetlist = []
    for sublist in vlist["varlist"]:
        freq = sublist["freq"]
        vars2d = sublist.get("vars2d",[])
        vars3d = sublist.get("vars3d",[])
        for v in (vars2d + vars3d):
            tlist = ece2cmor.get_cmor_target(v)
            tgt=[t for t in tlist if t.frequency == freq]
            targetlist.extend(tgt)
    return targetlist

# Creates a cmor_source for the given parameter dictionary
def create_cmor_source(paramdict,tag):
    if(tag == IFS_source_tag):
        codestr = str(paramdict["param"])
        return cmor_source.ifs_source(cmor_source.grib_code.read(codestr))
    elif(tag == Nemo_source_tag):
        parstr = paramdict["out_name"]
        ioname = paramdict["name"]
        if(not ioname in nemo_grid_dict):
            raise Exception("Variable",ioname,"could not be associated with a nemo output file")
        grid = nemo_grid_dict[ioname]
        grid_id = -1
        try:
            grid_id = cmor_source.nemo_grid.index(grid)
        except:
            raise Exception("Unknown grid detected:",grid,"for parameter",parstr)
        return cmor_source.nemo_source(parstr,grid_id)
    else:
        raise Exception("Unknown tag passed:",tag)

# Post-processing attributes for IFS output:
expressions = {(95,"rsus"):         "var95=var176-var169",
               (96,"rlus"):         "var96=var177-var175",
               (97,"rsut"):         "var97=var178-var212",
               (98,"rsutcs"):       "var98=var208-var212",
               (214,"sfcWind"):     "var214=sqrt(sq(var165)+sq(var166))",
               (214,"sfcWindmax"):  "var214=sqrt(sq(var165)+sq(var166))",
               (99,"mrsos"):        "var99=70*var39"
               (43,"mrso"):         "var43=70*var39+210*var40+720*var41+1890*var42"}

# Creates a cmor task, sets the correct post-processing attributes
def create_cmor_task(src,tgt,tag):
    task = cmor_task.cmor_task(src,tgt)
    if(tag == IFS_source_tag):
        code,oname = src.get_grib_code().var_id,tgt.out_name
        if((code,oname) in [(205,"mrro"),(8,"mrros"),(228,"pr"),(143,"prc"),(144,"prsn"),(44,"sbl"),(182,"evspsbl")]):
            setattr(task,"conversion","vol2flux")
        if((code,oname) in [(95,"rsus"),(96,"rlus"),(97,"rsut"),(98,"rsutcs"),(146,"hfls"),(147,"hfss"),(169,"rsds"),(175,"rlds"),(176,"ssr"),(177,"str"),\
                            (178,"tsr"),(179,"rlut"),(108,"tsrc"),(209,"rlutcs"),(210,"ssrc"),(211,"strc"),(212,"rsdt"),(180,"tauu"),(181,"tauv")]):
            setattr(task,"conversion","cum2inst")
        if((code,oname) in [(129,"zg"),(129,"orog")]):
            setattr(task,"conversion","pot2alt")
        if((code,oname) in expressions):
            setattr(task,"expr",expressions[(code,oname)])
