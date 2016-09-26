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
#    cal=None
#    for f in ifs_files_:
#        cal=read_calendar(f)
#        if(cal):
#            break
#    if(cal):
#        cmor.set_cur_dataset_attribute("calendar",cal)
#    cmor.load_table(tableroot+"_grids.json")
#    create_grids()


# Retrieves all IFS output files in the input directory.
def select_files(path,expname,start,length,interval):
    allfiles=cmor_utils.find_ifs_output(path,expname)
    startdate=start.date()-interval
    enddate=(start+length).date()
    return [f for f in allfiles if cmor_utils.get_ifs_date(f)<enddate and cmor_utils.get_ifs_date(f)>startdate]


def create_grids():
    # TODO: Implement
    raise Exception("Not implemented yet")
