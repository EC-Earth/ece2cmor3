import cmor
import cdo
import cmor_utils
import cmor_source
import dateutil
import gribapi

# Experiment name
exp_name_=None

# Table root
table_root_=None

# Files that are being processed in the current execution loop.
ifs_files_=[]

# List of depth axis ids with cmor grid id.
height_axes_={}

# Dictionary of output frequencies with cmor time axis id.
time_axes_={}

# Output interval. Denotes the o0utput file periods.
output_interval=None

# Initializes the processing loop.
def initialize(path,expname,tableroot,start,length,interval=dateutil.relativedelta(month=1)):
    global exp_name_
    global table_root_
    global ifs_files_
    global output_interval

    exp_name_=expname
    table_root_=tableroot
    output_interval=interval
    ifs_files_=select_files(path,start,length,output_interval)
#    cmor.set_cur_dataset_attribute("calendar","proleptic_gregorian")
#    cmor.load_table(tableroot+"_grids.json")
#    create_grids()

def execute(tasks):
    print "Executing IFS tasks..."
    postproc_irreg([t for t in tasks if not regular(t)])
    postproc([t for t in tasks if regular(t)])
    taskdict={}
    for t in tasks:
        freq=t.target.frequency
        if(freq in taskdict):
            taskdict[freq].append(t)
        else:
            taskdict[freq]=[t]
    for k,v in taskdict.iteritems():
        postproc(v,k)
        #TODO: Unit conversion
        #TODO: Cmorization

def regular(task):
    #TODO: Implement criterium
    return True

def postproc_irreg(tasks):
    if(len(tasks)!=0): raise Exception("The irregular post-processing jobs have not been implemented yet")

def postproc(tasks):
    taskdict={}
    for t in tasks:
        freq=t.target.frequency
        grd=cmor_source.ifs_grid.index(t.source.grid())
        if(tup in taskdict):
            taskdict[(freq,grd)].append(t)
        else:
            taskdict[(freq,grd)]=[t]
    # TODO: Distribute loop over processes
    for k,v in taskdict.iteritems():
        ppcdo(v,k[0],k[1])

#TODO: Check whether selmon is necessary...
def ppcdo(tasks,freq,grid):
    if(len(tasks)==0): return
    proj_op=None
    if(grid==cmor_source.ifs_grid.spec):
        proj_op="sp2gpl"
    timops=get_cdo_timop(freq)
    tim_avg=timops[0]
    tim_shift=timpops[1]
    codes=list(set(map(lambda t:t.source.get_grib_code().var_id,tasks)))
    sel_op="selcode,"+(",".join(map(lambda i:str(i),codes)))
    opstr=chain_cdo_commands(proj_op,timops,sel_op)
    if(grid==cmor_source.ifs_grid.pos):
        opstr="-R "+opstr
    cdo=cdo.Cdo()

def get_cdo_timop(freq):
    if(freq=="mon"):
        return ("timmean","shifttime,-3hours")
    elif(freq=="day"):
        return ("daymean","shifttime,-3hours")
    elif(freq="6hr"):
        return ("selhour,0,6,12,18",None)
    elif(freq=="3hr" or freq=="1hr"):
        return (None,None)
    else:
        raise Exception("Unknown target frequency encountered:",freq)

#TODO: move to utils
def chain_cdo_commands(*args):
    op=None
    if(len(args)==0): return op
    for arg in args:
        if(arg==None or arg==""): continue
        s=str(arg)
        if(op==None):
            op=s
        else:
            op+=(" -"+s)
    return op

# Retrieves all IFS output files in the input directory.
def select_files(path,expname,start,length,interval):
    allfiles=cmor_utils.find_ifs_output(path,expname)
    startdate=start.date()-interval
    enddate=(start+length).date()
    return [f for f in allfiles if cmor_utils.get_ifs_date(f)<enddate and cmor_utils.get_ifs_date(f)>startdate]


def create_grid():
    # TODO: Implement
    raise Exception("Not implemented yet")
