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

def postproc(tasks,freq):
    spectral_sources=[t.source for t in tasks if t.source.grid()=="spec_grid"]
    gridpoint_sources=[t.source for t in tasks if t.source.grid()=="pos_grid"]
    #TODO: Spawn multiple processes splitting and mapping concurrently...

# Retrieves all IFS output files in the input directory.
def select_files(path,expname,start,length,interval):
    allfiles=cmor_utils.find_ifs_output(path,expname)
    startdate=start.date()-interval
    enddate=(start+length).date()
    return [f for f in allfiles if cmor_utils.get_ifs_date(f)<enddate and cmor_utils.get_ifs_date(f)>startdate]


def create_grid():
    # TODO: Implement
    raise Exception("Not implemented yet")
