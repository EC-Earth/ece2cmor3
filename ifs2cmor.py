import cmor
import cdo
import cmor_utils
import cmor_source
import cmor_target
from dateutil.relativedelta import relativedelta as deltat
import os
import numpy
import datetime
import netCDF4

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
    if(tempdir):
        if(not os.path.exists(tempdir)):
            os.makedirs(tempdir)
        temp_dir_=tempdir
    #TODO: set after conversion to netcdf
    cmor.set_cur_dataset_attribute("calendar","proleptic_gregorian")

# Execute the postprocessing+cmorization tasks
def execute(tasks,postprocess=True):
    print "Post-processing IFS data..."
    postproc_irreg([t for t in tasks if not regular(t)],postprocess)
    postproc([t for t in tasks if regular(t)],postprocess)
    print "Cmorizing IFS data..."
    cmor.load_table(table_root_+"_grids.json")
    gridid=create_grid_from_grib(getattr(tasks[0],"path"))
    for t in tasks: setattr(t,"grid_id",gridid)
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
        print "Loading CMOR table",tab,"..."
        tab_id=-1
        try:
            tab_id=cmor.load_table("_".join([table_root_,tab])+".json")
            cmor.set_table(tab_id)
        except:
            print "CMOR failed to load table",tab,", the following variables will be skipped: ",[t.target.variable for t in tskgroup]
            continue
        # TODO: unify with nemo logic
        create_time_axes(tskgroup)
        create_depth_axes(tskgroup)
        # TODO: paralelize
        for t in tskgroup:
            #try:
            execute_netcdf_task(t)
            #except:
            #    print "Skipping cmorization of",t.target.variable


def get_cdo_level_commands(task):
    axisname=getattr(task,"z_axis",None)
    if not axisname:
        return [None,None]
    if(axisname=="alevel"):
        return ["selzaxis,hybrid",None]
    if(axisname=="alevhalf"):
        raise Exception("Half-level fields are not implemented yet")
    axisinfos=cmor_target.axes.get(task.target.table,{})
    axisinfo=axisinfos.get(axisname,None)
    if(not axisinfo):
        raise Exception("Could not retrieve information for axis",axisname,"in table",task.target.table)
    ret=[None,None]
    oname=axisinfo.get("standard_name",None)
    if(oname=="air_pressure"):
        ret[0]="selzaxis,pressure"
    elif(oname=="height"):
        ret[0]="selzaxis,height"
    else:
        #TODO: Figure out what axis to select
        raise Exception("This needs to be implemented")
    zlevs=axisinfo.get("requested",[])
    if(len(zlevs)==0):
        val=axisinfo.get("value",None)
        if(val):
            zlevs=[val]
    if(len(zlevs)!=0):
        ret[1]=",".join(["sellevel"]+zlevs)
    return ret

# Executes a single task
def execute_netcdf_task(task):
    print "cmorizing source variable",task.source.get_grib_code(),"to target variable",task.target.variable,"..."
    axes=[]
    grid_id=getattr(task,"grid_id",0)
    if(grid_id!=0):
        axes.append(grid_id)
    z_axis=getattr(task,"z_axis",None)
    if(z_axis):
        axes.append(getattr(task,"z_axis_id"))
    time_id=getattr(task,"time_axis",0)
    if(time_id!=0):
        axes.append(time_id)
    filepath=getattr(task,"path")
    #TODO: unit conversion
    cdocmd=cdo.Cdo()
    codestr=str(task.source.get_grib_code().var_id)
    sel_op="selcode,"+codestr
    lev_ops=get_cdo_level_commands(task)
    command=chain_cdo_commands(lev_ops[0],lev_ops[1],sel_op)+filepath
    print "CDO command:",command
    ncvars=[]
    try:
        ncvars=cdocmd.copy(input=command,returnCdf=True).variables
    except Exception:
        print "CDO command failed:",command
        return
    varlist=[v for v in ncvars if str(getattr(ncvars[v],"code",None))==codestr]
    if(not len(varlist)==1):
        raise Exception("Cdo final post-processing resulted in ",len(varlist),"netcdf variables, 1 expected")
    ncvar=ncvars[varlist[0]]
    ncunits=getattr(ncvar,"units")
    varid=0
    if(hasattr(task.target,"positive") and len(task.target.positive)!=0):
        varid=cmor.variable(table_entry=str(task.target.variable),units=str(ncunits),axis_ids=axes,positive="down")
    else:
        varid=cmor.variable(table_entry=str(task.target.variable),units=str(ncunits),axis_ids=axes)
    vals=numpy.zeros([1])
    # TODO: use time slicing in case of memory shortage
    times=ncvar.shape[0]
    chunk=2
    for i in range(0,times,chunk):
        imax=min(i+chunk,times)
        if(len(ncvar.dimensions)==3):
            vals=numpy.transpose(ncvar[i:imax,:,:],axes=[2,1,0]) # Convert to CMOR Fortran-style ordering
        elif(len(ncvar.dimensions)==4):
            vals=numpy.transpose(ncvar[i:imax,:,:,:],axes=[3,2,1,0]) # Convert to CMOR Fortran-style ordering
        else:
            raise Exception("Arrays of dimensions",len(ncvar.dimensions),"are not supported by ifs2cmor")
        shape=vals.shape
        cmor.write(varid,numpy.asfortranarray(vals),ntimes_passed=(imax-i))
        storevar=getattr(task,"store_with",None)
        if(storevar):
            print "Using uniform surface pressure of 800 hPa--TODO: readout. shape=",shape
            sp=80000.0
            if(len(shape)==3):
                psvals=numpy.full(shape=shape,fill_value=sp,dtype=numpy.float64)
            else:
                psvals=numpy.full(shape=[shape[0],shape[1],shape[3]],fill_value=sp,dtype=numpy.float64)
            cmor.write(storevar,numpy.asfortranarray(psvals),ntimes_passed=(imax-i),store_with=varid)
    cmor.close(varid)


# Creates time axes in cmor and attach the id's as attributes to the tasks
def create_time_axes(tasks):
    time_axis_id=create_time_axis(freq=tasks[0].target.frequency,files=[getattr(t,"path") for t in tasks])
    for t in tasks:
        setattr(t,"time_axis",time_axis_id)


# Creates depth axes in cmor and attach the id's as attributes to the tasks
def create_depth_axes(tasks):
    depth_axes={}
    ps_id=0
    for t in tasks:
        tgtdims=getattr(t.target,cmor_target.dims_key)
        zdims=list(set(tgtdims.split())-set(["latitude","longitude","time","time1"]))
        if(len(zdims)==0): continue
        if(len(zdims)>1):
            raise Exception("Variable",t.target.variable,"with dimensions",tgtdims,"cannot be interpreted as 3d variable")
        zdim=str(zdims[0])
        setattr(t,"z_axis",zdim)
        if zdim in depth_axes:
            setattr(t,"z_axis_id",depth_axes[zdim])
            if(zdim=="alevel"):
                if(ps_id):
                    setattr(t,"store_with",ps_id)
                else:
                    raise Exception("Hybrid model level axis was created, but the surface pressure variable not.")
            continue
        elif zdim=="alevel":
            axisid,psid=create_hybrid_level_axis(t)
            depth_axes[zdim]=axisid
            ps_id=psid
            setattr(t,"z_axis_id",axisid)
            setattr(t,"store_with",ps_id)
            continue
        elif zdim in cmor_target.axes[t.target.table]:
            axisid=0
            axis=cmor_target.axes[t.target.table][zdim]
            levels=axis.get("requested",[])
            if(levels==""):
                levels=[]
            value=axis.get("value",None)
            if(value):
                levels.append(value)
            unit=axis.get("units",None)
            if(len(levels)==0):
                print "Skipping axis",zdim,"with no values"
                continue
            else:
                vals=[float(l) for l in levels]
                axisid=cmor.axis(table_entry=str(zdim),coord_vals=vals,units=unit)
            depth_axes[zdim]=axisid
            setattr(t,"z_axis_id",axisid)
        else:
            raise Exception("Vertical dimension",zdim,"not found in table header")


def create_hybrid_level_axis(task):
    pref=80000 # TODO: Move reference pressure level to model config
    path=getattr(task,"path")
    ds=netCDF4.Dataset(path)
    am=ds.variables["hyam"]
    aunit=getattr(am,"units")
    bm=ds.variables["hybm"]
    bunit=getattr(bm,"units")
    hcm=am[:]/pref+bm[:]
    n=hcm.shape[0]
    ai=ds.variables["hyai"]
    abnds=numpy.empty([n,2])
    abnds[:,0]=ai[0:n]
    abnds[:,1]=ai[1:n+1]
    bi=ds.variables["hybi"]
    bbnds=numpy.empty([n,2])
    bbnds[:,0]=bi[0:n]
    bbnds[:,1]=bi[1:n+1]
    hcbnds=abnds/pref+bbnds
    axid=cmor.axis(table_entry="alternate_hybrid_sigma",coord_vals=hcm,cell_bounds=hcbnds,units="1")
    cmor.zfactor(zaxis_id=axid,zfactor_name="ap",units=str(aunit),axis_ids=[axid],zfactor_values=am[:],zfactor_bounds=abnds)
    cmor.zfactor(zaxis_id=axid,zfactor_name="b",units=str(bunit),axis_ids=[axid],zfactor_values=bm[:],zfactor_bounds=bbnds)
    storewith=cmor.zfactor(zaxis_id=axid,zfactor_name="ps",axis_ids=[getattr(task,"grid_id"),getattr(task,"time_axis")],units="Pa")
    return (axid,storewith)


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
    command=cdo.Cdo()
    ifile=None
    if(grid==cmor_source.ifs_grid.point):
        opstr=chain_cdo_commands("setgridtype,regular",tim_avg,tim_shift,sel_op)
        ofile=os.path.join(temp_dir_,"ICMGG_"+freq+".nc")
        if(callcdo):
            command.copy(input=opstr+ifs_gridpoint_file_,output=ofile,options="-P 4 -f nc")
    else:
        opstr=chain_cdo_commands(tim_avg,tim_shift,sel_op)
        ofile=os.path.join(temp_dir_,"ICMSH_"+freq+".nc")
        if(callcdo):
            command.sp2gpl(input=opstr+ifs_spectral_file_,output=ofile,options="-P 4 -f nc")
    for t in tasks:
        setattr(t,"path",ofile)


# Helper function for cdo time-averaging commands
# TODO: move to cdo_utils
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
#TODO: move to cdo_utils and add input file argument
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
    return create_gauss_grid(xsize,xstart,ysize,numpy.array(yvals))


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
