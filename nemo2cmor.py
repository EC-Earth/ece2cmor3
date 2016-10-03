import netCDF4
import cmor
import cmor_utils
import cmor_source
import numpy
import datetime

# Experiment name
exp_name_=None

# Table root
table_root_=None

# Files that are being processed in the current execution loop.
nemo_files_=[]

# Dictionary of NEMO grid type with cmor grid id.
grid_ids_={}

# List of depth axis ids with cmor grid id.
depth_axes_={}

# Dictionary of output frequencies with cmor time axis id.
time_axes_={}


# Initializes the processing loop.
def initialize(path,expname,tableroot,start,length):
    global nemo_files_
    global exp_name_
    global table_root_

    exp_name_=expname
    table_root_=tableroot
    nemo_files_=select_files(path,expname,start,length)
    cal=None
    for f in nemo_files_:
        cal=read_calendar(f)
        if(cal):
            break
    if(cal):
        cmor.set_cur_dataset_attribute("calendar",cal)
    cmor.load_table(tableroot+"_grids.json")
    create_grids()


# Executes the processing loop. TODO: parallelize!
def execute(tasks):
    global time_axes_
    global depth_axes_
    global table_root_
    print "Executing nemo tasks..."
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
        files=select_freq_files(freq)
        if(len(files)==0):
            raise Exception("no NEMO output files found for frequency",freq,"in file list",nemo_files_)
        print "Loading CMOR table",tab,"..."
        tab_id=cmor.load_table("_".join([table_root_,tab])+".json")
        cmor.set_table(tab_id)
        time_axes_[tab_id]=create_time_axis(freq,files)
        if(not tab_id in depth_axes_):
            depth_axes_[tab_id]=create_depth_axes(tab_id,files)
        # Loop over files:
        for ncf in files:
            ds=netCDF4.Dataset(ncf,'r')
            filetasks=[t for t in tskgroup if t.source.var() in ds.variables]
            for t in filetasks:
                execute_netcdf_task(t,ds,tab_id)


# Resets the module:
def finalize():
    global time_axes_
    global depth_axes_
    global grid_ids_
    global nemo_files_

    exp_name_=None
    table_root_=None
    nemo_files_=[]
    grid_ids_={}
    depth_axes_={}
    time_axes_={}


# Performs a single task:
def execute_netcdf_task(task,dataset,tableid):
    global time_axes_
    global grid_ids_
    global depth_axes_
#TODO: Log this instead of printing...
    print "cmorizing source variable",task.source.var_id,"to target variable",task.target.variable,"..."
    dims=task.target.dims
    globvar=(task.source.grid()==cmor_source.nemo_grid[cmor_source.nemo_grid.scalar])
    if(globvar):
        axes=[]
    else:
        if(not task.source.grid() in grid_ids_):
            raise Exception("Grid axis for",task.source.grid(),"was not created, something has gone wrong")
        axes=[grid_ids_[task.source.grid()]]
    if((globvar and dims==1) or (not globvar and dims==3)):
        grid_index=cmor_source.nemo_grid.index(task.source.grid())
        if(not grid_index in cmor_source.nemo_depth_axes):
            raise Exception("Cannot create 3d variable on grid ",task.source.grid())
        zaxid=depth_axes_[tableid][grid_index]
        axes.append(zaxid)
    axes.append(time_axes_[tableid])
    srcvar=task.source.var()
    ncvar=dataset.variables[srcvar]
    ncunits=getattr(ncvar,"units")
    varid=0
    if(hasattr(task.target,"positive") and len(task.target.positive)!=0):
        varid=cmor.variable(table_entry=str(task.target.variable),units=str(ncunits),axis_ids=axes,original_name=str(srcvar),positive="down")
    else:
        varid=cmor.variable(table_entry=str(task.target.variable),units=str(ncunits),axis_ids=axes,original_name=str(srcvar))
    vals=numpy.zeros([1])
    # TODO: use time slicing in case of memory shortage
    if(dims==2):
        vals=numpy.transpose(ncvar[:,:,:],axes=[1,2,0]) # Convert to CMOR Fortran-style ordering
    elif(dims==3):
        vals=numpy.transpose(ncvar[:,:,:,:],axes=[2,3,1,0]) # Convert to CMOR Fortran-style ordering
    else:
        raise Exception("Arrays of dimensions",task.source.dims(),"are not supported by nemo2cmor")
    numpy.asfortranarray(vals)
    cmor.write(varid,vals)
    cmor.close(varid)


# Creates all depth axes for the given table from the given files
def create_depth_axes(tab_id,files):
    global depth_axes_
    global exp_name_

    result={}
    for f in files:
        gridstr=cmor_utils.get_nemo_grid(f,exp_name_)
        if(not gridstr in cmor_source.nemo_grid):
            raise Exception("Unknown NEMO grid: ",gridstr)
        index=cmor_source.nemo_grid.index(gridstr)
        if(not index in cmor_source.nemo_depth_axes):
            continue
        if(index in result):
            continue
        did=create_depth_axis(f,cmor_source.nemo_depth_axes[index])
        if(did!=0): result[index]=did
    return result


# Creates a cmor depth axis
def create_depth_axis(ncfile,gridchar):
    ds=netCDF4.Dataset(ncfile)
    varname="depth"+gridchar
    if(not varname in ds.variables):
        return 0
    depthvar=ds.variables[varname]
    depthbnd=getattr(depthvar,"bounds")
    units=getattr(depthvar,"units")
    bndvar=ds.variables[depthbnd]
    b=bndvar[:,:]
    b[b<0]=0
    return cmor.axis(table_entry="depth_coord",units=units,coord_vals=depthvar[:],cell_bounds=b)

timvals=None
timbnds=None

# Creates a tie axis for the corresponding table (which is suppoed to be loaded)
def create_time_axis(freq,files):
    global timvals
    global timbnds
    vals=None
    units=None
    ds=None
    for ncfile in files:
        try:
            ds=netCDF4.Dataset(ncfile)
            timvar=ds.variables["time_counter"]
            vals=timvar[:]
            bnds=getattr(timvar,"bounds")
            bndvar=ds.variables[bnds]
            units=getattr(timvar,"units")
            break
        except:
            if(ds):
                ds.close()
    if(len(vals)==0 or units==None):
        raise Exception("No time values or units could be read from NEMO output files",files)
    ax_id=cmor.axis(table_entry="time",units=units,coord_vals=vals,cell_bounds=bndvar[:,:])
    timvals=vals
    timbnds=bndvar[:,:]
    return ax_id


# Selects files with data with the given frequency
def select_freq_files(freq):
    global exp_name_

    freqmap={"1hr":"1h","3hr":"3h","6hr":"6h","day":"1d","mon":"1m"}
    if(not freq in freqmap):
        raise Exception("Unknown frequency detected:",freq)
    return [f for f in nemo_files_ if freqmap[freq]==cmor_utils.get_nemo_frequency(f,exp_name_)]


# Retrieves all NEMO output files in the input directory.
def select_files(path,expname,start,length):
    allfiles=cmor_utils.find_nemo_output(path,expname)
    starttime=cmor_utils.make_datetime(start)
    stoptime=cmor_utils.make_datetime(start+length)
    return [f for f in allfiles if cmor_utils.get_nemo_interval(f)[0]<=stoptime and cmor_utils.get_nemo_interval(f)[1]>=starttime]


# Reads the calendar attribute from the time dimension.
def read_calendar(ncfile):
    ds=netCDF4.Dataset(ncfile,'r')
    if(not ds):
        return None
    timvar=ds.variables["time_centered"]
    if(timvar):
        result=getattr(timvar,"calendar")
        ds.close()
        return result
    else:
        return None


# Reads all the NEMO grid data from the input files.
def create_grids():
    global grid_ids

    spatial_grids=[grd for grd in cmor_source.nemo_grid if grd!=cmor_source.nemo_grid.scalar]
    for g in spatial_grids:
        gridfiles=[f for f in nemo_files_ if f.endswith(g + ".nc")]
        if(len(gridfiles)!=0):
            grid=read_grid(gridfiles[0])
            grid_ids_[g]=write_grid(grid)


# Reads a particular NEMO grid from the given input file.
def read_grid(ncfile):
    ds=netCDF4.Dataset(ncfile,'r')
    lons=ds.variables['nav_lon'][:,:]
    lats=ds.variables['nav_lat'][:,:]
    return nemogrid(lons,lats)


# Transfers the grid to cmor.
def write_grid(grid):
    nx=grid.Nx()
    ny=grid.Ny()
    i_index_id=cmor.axis(table_entry="i_index",units="1",coord_vals=numpy.array(range(1,nx+1)))
    j_index_id=cmor.axis(table_entry="j_index",units="1",coord_vals=numpy.array(range(1,ny+1)))
    return cmor.grid(axis_ids=[i_index_id,j_index_id],
                     latitude=grid.lats,
                     longitude=grid.lons,
                     latitude_vertices=grid.vertex_lats,
                     longitude_vertices=grid.vertex_lons)


# Class holding a NEMO grid, including bounds arrays
class nemogrid(object):

    def __init__(self,lons_,lats_):
        flon=numpy.vectorize(nemogrid.modlon)
        flat=numpy.vectorize(nemogrid.modlat)
        self.lons=flon(nemogrid.smoothen(lons_))
        self.lats=flat(lats_)
        self.vertex_lons=nemogrid.create_vertex_lons(lons_)
        self.vertex_lats=nemogrid.create_vertex_lats(lats_)

    def Nx(self):
        return self.lons.shape[0]

    def Ny(self):
        return self.lons.shape[1]

    @staticmethod
    def create_vertex_lons(a):
        nx=a.shape[0]
        ny=a.shape[1]
        b=numpy.zeros([nx,ny,4])
        f=numpy.vectorize(nemogrid.modlon)
        b[1:nx,:,0]=f(0.5*(a[0:nx-1,:]+a[1:nx,:]))
        b[0,:,0]=b[nx-1,:,0]
        b[0:nx-1,:,1]=b[1:nx,:,0]
        b[nx-1,:,1]=b[1,:,1]
        b[:,:,2]=b[:,:,1]
        b[:,:,3]=b[:,:,0]
        return b

    @staticmethod
    def create_vertex_lats(a):
        nx=a.shape[0]
        ny=a.shape[1]
        b=numpy.zeros([nx,ny,4])
        f=numpy.vectorize(nemogrid.modlat)
        b[:,0,0]=f(1.5*a[:,0]-0.5*a[:,1])
        b[:,1:ny,0]=f(0.5*(a[:,0:ny-1]+a[:,1:ny]))
        b[:,:,1]=b[:,:,0]
        b[:,0:ny-1,2]=b[:,1:ny,0]
        b[:,ny-1,2]=f(1.5*a[:,ny-1]-0.5*a[:,ny-2])
        b[:,:,3]=b[:,:,2]
        return b

    @staticmethod
    def modlat(x):
        if(x<-90): return x+180.0
        elif(x>=90.0): return x-180.0
        else: return x

    @staticmethod
    def modlon(x):
        if(x<0): return x+360.0
        elif(x>=360.0): return x-360.0
        else: return x

    @staticmethod
    def modlon2(x,a):
        if(x<a): return x+360.0
        else: return x

    @staticmethod
    def smoothen(a):
        nx=a.shape[0]
        ny=a.shape[1]
        mod=numpy.vectorize(nemogrid.modlon2)
        b=numpy.empty([nx,ny])
        for i in range(0,nx):
            x=a[i,1]
            b[i,0]=a[i,0]
            b[i,1]=x
            b[i,2:]=mod(a[i,2:],x)
        return b
