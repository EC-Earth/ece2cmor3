import cmor
import cdo
import cmor_utils
import cmor_source
import cmor_target
from dateutil.relativedelta import relativedelta as deltat
import os
import numpy
import datetime

# Experiment name
exp_name_=None

# Table root
table_root_=None

# Files that are being processed in the current execution loop.
ifs_gridpoint_file_=None
ifs_spectral_file_=None

# List of depth axis ids with cmor grid id.
height_axes_={}

# Start date of the processed data
start_date_=None

# Output interval. Denotes the 0utput file periods.
output_interval_=None

# Fast storage temporary path
temp_dir_=os.getcwd()

# Reference date, times will be converted to hours since refdate
# TODO: set in init
ref_date_=None

# Initializes the processing loop.
def initialize(path,expname,tableroot,start,length,refdate,interval=deltat(month=1),tempdir=None):
    global exp_name_
    global table_root_
    global ifs_gridpoint_file_
    global ifs_spectral_file_
    global output_interval
    global temp_dir_
    global ref_date_
    global start_date_

    exp_name_=expname
    table_root_=tableroot
    start_date_=start
    output_interval=interval
    ref_date_=refdate
    datafiles=select_files(path,exp_name_,start,length,output_interval)
    gpfiles=[f for f in datafiles if os.path.basename(f).startswith("ICMGG")]
    shfiles=[f for f in datafiles if os.path.basename(f).startswith("ICMSH")]
    if(not (len(gpfiles)==1 and len(shfiles)==1)):
        #TODO: Support postprocessing over multiple files
        raise Exception("Expected a single grid point and spectral file to process, found:",datafiles)
    ifs_gridpoint_file_=gpfiles[0]
    ifs_spectral_file_=shfiles[0]
    if():
        # TODO: Create directory if necessary
        temp_dir_=tempdir
    cmor.set_cur_dataset_attribute("calendar","proleptic_gregorian")

# Execute the postprocessing+cmorization tasks
def execute(tasks,postprocess=True):
    print "Post-processing IFS data..."
    postproc_irreg([t for t in tasks if not regular(t)],postprocess)
    postproc([t for t in tasks if regular(t)],postprocess)
    print "Cmorizing IFS data..."
    cmor.load_table(table_root_+"_grids.json")
    create_grid_from_grib(getattr(tasks[0],"path"))
    cmorize(tasks)

# Do the cmorization tasks
def cmorize(tasks):
    taskdict={}
    for t in tasks:
        tab=t.target.table
        if(tab in taskdict):
            taskdict[tab].append(t)
        else:
            taskdict[tab]=[t]
    for k,v in taskdict.iteritems():
        tab=k
        tskgroup=v
        freq=tskgroup[0].target.frequency
        print "Loading CMOR table",tab,"..."
        tab_id=-1
        try:
            tab_id=cmor.load_table("_".join([table_root_,tab])+".json")
            cmor.set_table(tab_id)
        except:
            print "CMOR failed to load table",tab,", the following variables will be skipped: ",[t.target.variable for t in tskgroup]
            continue
        # TODO: unify with nemo logic
        ifiles=[getattr(t,"path") for t in tskgroup]
        time_axis_id=create_time_axis(freq,files=ifiles)
        for t in tskgroup:
            setattr(t,"time_axis",time_axis_id)
        create_depth_axes(tab_id,tab,tskgroup)
        # TODO: paralelize
#        for t in tskgroup:
#            execute_grib_task(t,tab_id)

def create_depth_axes(tab_id,table,tasks):
    depth_axes={}
    for t in tasks:
        tgtdims=getattr(t.target,cmor_target.dims_key)
        zdims=list(set(tgtdims.split())-set(["latitude","longitude","time","time1"]))
        if(len(zdims)!=1): continue
        zdim=zdims[0]
        print "The z-dimension for",t.target.out_name,"is",zdim
        if zdim in cmor_target.axes[table]:
            print "we found this axis!"
            print cmor_target.axes[table][zdim]


# Makes a time axis for the given table
def create_time_axis(freq,files):
    command=cdo.Cdo()
    datetimes=[]
    for gribfile in set(files):
        try:
            times=command.showtimestamp(input=gribfile)[0].split()
            datetimes=sorted(set(map(lambda s:datetime.datetime.strptime(s,"%Y-%m-%dT%H:%M:%S"),times)))
            break
        except:
            print "Problem reading atmosphere output time steps from file",gribfile,", trying next file"
    if(len(datetimes)==0):
        raise Exception("Empty time step list encountered at time axis creation for files",files)
    timhrs=[(d-cmor_utils.make_datetime(ref_date_)).total_seconds()/3600 for d in datetimes]
    n=len(timhrs)
    times=numpy.array(timhrs)
    bndvar=numpy.empty([n,2])
    if(n==1):
        bndvar[0,0]=(cmor_utils.make_datetime(start_date_)-cmor_utils.make_datetime(ref_date_)).total_seconds()/3600
        bndvar[0,1]=2*times[0]-bndvar[0,0]
    else:
        midtimes=0.5*(times[0:n-1]+times[1:n])
        bndvar[0,0]=1.5*times[0]-0.5*times[1]
        bndvar[1:n,0]=midtimes[:]
        bndvar[0:n-1,1]=midtimes[:]
        bndvar[n-1,1]=1.5*times[n-1]-0.5*times[n-2]
    ax_id=cmor.axis(table_entry="time",units="hours since "+str(ref_date_),coord_vals=times,cell_bounds=bndvar)
    return ax_id
    return 0

# Tests whether the task is 'regular' or needs additional pre-postprocessing
def regular(task):
    #TODO: Implement criterium
    return True

# Does the postprocessing of irregular tasks
def postproc_irreg(tasks,postprocess=True):
    if(len(tasks)!=0): raise Exception("The irregular post-processing jobs have not been implemented yet")

# Does the postprocessing of regular tasks
def postproc(tasks,postprocess=True):
    taskdict={}
    for t in tasks:
        freq=t.target.frequency
        grd=cmor_source.ifs_grid.index(t.source.grid())
        if((freq,grd) in taskdict):
            taskdict[(freq,grd)].append(t)
        else:
            taskdict[(freq,grd)]=[t]
    # TODO: Distribute loop over processes
    for k,v in taskdict.iteritems():
        ppcdo(v,k[0],k[1],postprocess)

# Does splitting of files according to frequency and remaps the grids.
#TODO: Add selmon...
def ppcdo(tasks,freq,grid,callcdo=True):
    print "Post-processing IFS tasks with frequency",freq,"on the",cmor_source.ifs_grid[grid],"grid"
    if(len(tasks)==0): return
    timops=get_cdo_timop(freq)
    tim_avg=timops[0]
    tim_shift=timops[1]
    codes=list(set(map(lambda t:t.source.get_grib_code().var_id,tasks)))
    sel_op="selcode,"+(",".join(map(lambda i:str(i),codes)))
    opstr=chain_cdo_commands(tim_avg,tim_shift,sel_op)
    command=cdo.Cdo()
    ifile=None
    if(grid==cmor_source.ifs_grid.point):
        ofile=os.path.join(temp_dir_,"ICMGG_"+freq)
        if(callcdo):
            command.copy(input=opstr+ifs_gridpoint_file_,output=ofile,options="-R -P 4")
    else:
        ofile=os.path.join(temp_dir_,"ICMSH_"+freq)
        if(callcdo):
            command.sp2gpl(input=opstr+ifs_spectral_file_,output=ofile,options="-P 4")
    for t in tasks:
        setattr(t,"path",ofile)

# Helper function for cdo time-averaging commands
def get_cdo_timop(freq):
    if(freq=="mon"):
        return ("timmean","shifttime,-3hours")
    elif(freq=="day"):
        return ("daymean","shifttime,-3hours")
    elif(freq=="6hr"):
        return ("selhour,0,6,12,18",None)
    elif(freq=="3hr" or freq=="1hr"):
        return (None,None)
    else:
        raise Exception("Unknown target frequency encountered:",freq)

# Utility to chain cdo commands
#TODO: move to utils
def chain_cdo_commands(*args):
    op=""
    if(len(args)==0): return op
    for arg in args:
        if(arg==None or arg==""): continue
        s=str(arg)
        op+=(" -"+s)
    return op+" "

# Retrieves all IFS output files in the input directory.
def select_files(path,expname,start,length,interval):
    allfiles=cmor_utils.find_ifs_output(path,expname)
    startdate=cmor_utils.make_datetime(start).date()
    enddate=cmor_utils.make_datetime(start+length).date()
    return [f for f in allfiles if cmor_utils.get_ifs_date(f)<enddate and cmor_utils.get_ifs_date(f)>=startdate]

# Creates the regular gaussian grids from the postprocessed file argument.
def create_grid_from_grib(filepath):
    command=cdo.Cdo()
    griddescr=command.griddes(input=filepath)
    xsize=0
    ysize=0
    yvals=[]
    xstart=0.0
    reading_ys=False
    for s in griddescr:
        sstr=str(s)
        if(reading_ys):
            yvals.extend([float(s) for s in sstr.split()])
            continue
        if(sstr.startswith("gridtype")):
            gtype=sstr.split("=")[1].strip()
            if(gtype!="gaussian"):
                raise Exception("Cannot read other grids then regular gaussian grids, current grid type was:",gtype)
        if(sstr.startswith("xsize")):
            xsize=int(sstr.split("=")[1].strip())
            continue
        if(sstr.startswith("xfirst")):
            xfirst=float(sstr.split("=")[1].strip())
            continue
        if(sstr.startswith("ysize")):
            ysize=int(sstr.split("=")[1].strip())
            continue
        if(sstr.startswith("yvals")):
            reading_ys=True
            ylist=sstr.split("=")[1].strip()
            yvals.extend([float(s) for s in ylist.split()])
            continue
    if(len(yvals)!=ysize):
        raise Exception("Invalid number of y-values given in file",filepath)
    create_gauss_grid(xsize,xstart,ysize,numpy.array(yvals))

# Creates the regular gaussian grid from its arguments.
def create_gauss_grid(nx,x0,ny,yvals):
    i_index_id=cmor.axis(table_entry="i_index",units="1",coord_vals=numpy.array(range(1,nx+1)))
    j_index_id=cmor.axis(table_entry="j_index",units="1",coord_vals=numpy.array(range(ny,0,-1)))
    xincr=360./nx
    xvals=numpy.array([x0+i*xincr for i in range(nx)])
    lonarr=numpy.tile(xvals,(ny,1)).transpose()
    latarr=numpy.tile(yvals,(nx,1))
    lonmids=numpy.append(xvals-0.5*xincr,360.-0.5*xincr)
    lonmids[0]=lonmids[nx]
    latmids=numpy.empty([ny+1])
    latmids[0]=90.
    latmids[1:ny]=0.5*(yvals[0:ny-1]+yvals[1:ny])
    latmids[ny]=-90.
    numpy.append(latmids,-90.)
    vertlats=numpy.empty([nx,ny,4])
    vertlats[:,:,0]=numpy.tile(latmids[0:ny],(nx,1))
    vertlats[:,:,1]=vertlats[:,:,0]
    vertlats[:,:,2]=numpy.tile(latmids[1:ny+1],(nx,1))
    vertlats[:,:,3]=vertlats[:,:,2]
    vertlons=numpy.empty([nx,ny,4])
    vertlons[:,:,0]=numpy.tile(lonmids[0:nx],(ny,1)).transpose()
    vertlons[:,:,3]=vertlons[:,:,0]
    vertlons[:,:,1]=numpy.tile(lonmids[1:nx+1],(ny,1)).transpose()
    vertlons[:,:,2]=vertlons[:,:,1]
    return cmor.grid(axis_ids=[i_index_id,j_index_id],
                     latitude=latarr,
                     longitude=lonarr,
                     latitude_vertices=vertlats,
                     longitude_vertices=vertlons)
