import cmor
import cdo
import cmor_utils
import cmor_source
import dateutil
import gribapi
import os

# Experiment name
exp_name_=None

# Table root
table_root_=None

# Files that are being processed in the current execution loop.
ifs_gridpoint_file_=None
ifs_spectral_file_=None

# List of depth axis ids with cmor grid id.
height_axes_={}

# Dictionary of output frequencies with cmor time axis id.
time_axes_={}

# Output interval. Denotes the 0utput file periods.
output_interval_=None

# Fast storage temporary path
temp_path_=os.getcwd()

# Initializes the processing loop.
def initialize(path,expname,tableroot,start,length,interval=dateutil.relativedelta(month=1),temp_path=None):
    global exp_name_
    global table_root_
    global ifs_gridpoint_file_
    global ifs_spectral_file_
    global output_interval

    exp_name_=expname
    table_root_=tableroot
    output_interval=interval
    datafiles=select_files(path,start,length,output_interval)
    gpfiles=[f for f in datafiles if os.path.basename(f).startswith("ICMGG")]
    shfiles=[f for f in datafiles if os.path.basename(f).startswith("ICMSH")]
    if(not (len(gpfiles)==1 and len(shfiles)==1)):
        #TODO: Support postprocessing over multiple files
        raise Exception("Expected a single grid point and spectral file to process, found:",datafiles)
    ifs_gridpoint_file_=gpfiles[0]
    ifs_spectral_file_=shfiles[0]
    cmor.set_cur_dataset_attribute("calendar","proleptic_gregorian")

def execute(tasks):
    print "Post-processing IFS data..."
    postproc_irreg([t for t in tasks if not regular(t)])
    postproc([t for t in tasks if regular(t)])
    print "Cmorizing IFS data..."
    create_grid_from_grib(getattr(tasks[0],"path"))
    cmorize(tasks)

def cmorize(tasks):
    #TODO: implemented
    pass

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

#TODO: Add selmon...
def ppcdo(tasks,freq,grid):
    if(len(tasks)==0): return
    tim_avg=timops[0]
    tim_shift=timpops[1]
    codes=list(set(map(lambda t:t.source.get_grib_code().var_id,tasks)))
    sel_op="selcode,"+(",".join(map(lambda i:str(i),codes)))
    opstr=chain_cdo_commands(timops,sel_op)
    command=cdo.Cdo()
    ifile=None
    if(grid==cmor_source.ifs_grid.point):
        ofile=os.path.join(temp_path,"ICMGG_"+freq)
        command.copy(input=timops+ifs_gridpoint_file_,output=ofile,options="-R")
    else:
        ofile=os.path.join(temp_path,"ICMSH_"+freq)
        command.sp2gpl(input=timops+ifs_spectral_file_,output=ofile)
    for t in tasks:
        setattr(t,"path",ofile)


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
    return op+" "

# Retrieves all IFS output files in the input directory.
def select_files(path,expname,start,length,interval):
    allfiles=cmor_utils.find_ifs_output(path,expname)
    startdate=start.date()-interval
    enddate=(start+length).date()
    return [f for f in allfiles if cmor_utils.get_ifs_date(f)<enddate and cmor_utils.get_ifs_date(f)>startdate]


def create_grid_from_grib(filepath):
    # TODO: Implement
    command=cdo.Cdo()
    raise Exception("Not implemented yet")
