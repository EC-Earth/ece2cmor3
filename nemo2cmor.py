import netCDF4
import cmor
import cmor_utils
import cmor_source
import numpy
from itertools import groupby

# Experiment name
exp_name_=None

# Table root
table_root_=None

# Files that are being processed in the current execution loop.
nemo_files_=[]

# Dictionary of NEMO grid type with cmor grid id.
grid_ids_={}

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
    create_grids(nemo_files_,tableroot+"_grids.json")


# Executes the processing loop.
def execute(tasks):
    global time_axes_
    global table_root_
    for k,v in groupby(tasks,lambda t: t.target.table):
        tab=k
        tskgroup=list(v)
        freq=tskgroup[0].target.frequency
        files=select_freq_files(freq)
        if(len(files)==0):
            raise Exception("no NEMO output files found for frequency",freq,"in file list",files)
        tab_id=cmor.load_table("_".join([table_root_,tab])+".json")
        if(not tab_id in time_axes_):
            time_axes_[tab_id]=create_time_axis(freq,files)
#        if(not tab_id in depth_axes_):
#            depth_axes_[tab_id]=create_depth_axes(tab_id)
#        create_variables()


#def execute_tasks(tasks,files):
#    for t in tasks:
#        grid=cmor_source.nemo_grid[t.source.grid()]
#        flist=[f in files if f.endswith(grid+".nc")]
#        if(len(flist)==0):
#            raise Exception("no NEMO output files found with grid ",grid)



# Creates a tie axis for the corresponding table (which is suppoed to be loaded)
def create_time_axis(freq,files):
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
    return cmor.axis(table_entry="time",units=units,coord_vals=vals,cell_bounds=bndvar[:,:])


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
    return [f for f in allfiles if cmor_utils.get_nemo_interval(f)[0]<=(start+length) and cmor_utils.get_nemo_interval(f)[1]>=start]


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
def create_grids(files,table):
    global grid_ids
    for g in cmor_source.nemo_grid:
        extension="_grid"+g+".nc"
        gridfiles=[f for f in files if f.endswith(extension)]
        if(len(gridfiles)!=0):
            grid=read_grid(gridfiles[0])
            grid_ids_[g]=write_grid(grid,table)


# Reads a particular NEMO grid from the given input file.
def read_grid(ncfile):
    ds=netCDF4.Dataset(ncfile,'r')
    lons=ds.variables['nav_lon'][:,:]
    lats.ds.variables['nav_lat'][:,:]
    return nemogrid(lons,lats)


# Transfers the grid to cmor.
def write_grid(grid,table):
    nx=grid.Nx()
    ny=grid.Ny()
    i_index_id=cmor.axis(table=table,table_entry="i_index",units="1",coord_vals=numpy.array(range(nx)))
    j_index_id=cmor.axis(table=table,table_entry="j_index",units="1",coord_vals=numpy.array(range(ny)))
    return cmor.grid(axis_ids=[i_index_id,j_index_id],
                     latitude=grid.lats,
                     longitude=grid.lons,
                     latitude_vertices=grid.vertex_lats,
                     longitude_vertices=grid.vertex_lons)


# Class holding a NEMO grid, including bounds arrays
class nemogrid(object):

    def __init__(self,lons_,lats_):
        f=numpy.vectorize(nemogrid.moddegrees)
        self.lons=lons_
        self.lats=lats_
        self.vertex_lons=f(nemogrid.create_vertex_lons(lons_))
        self.vertex_lats=nemogrid.create_vertex_lats(lats_)
        self.lons=f(self.lons)

    def Nx(self):
        return self.lons.shape(0)

    def Ny(self):
        return self.lons.shape(1)

    @staticmethod
    def create_vertex_lons(a):
        nx=a.shape[0]
        ny=a.shape[1]
        b=numpy.zeros([4,nx,ny])
        b[0,1:nx,:]=0.5*(a[0:nx-1,:]+a[1:nx,:])
        b[0,0,:]=b[0,nx-1,:]
        b[1,0:nx-1,:]=b[0,1:nx,:]
        b[1,nx-1,:]=b[1,1,:]
        b[2,:,:]=b[1,:,:]
        b[3,:,:]=b[0,:,:]
        return b

    @staticmethod
    def create_vertex_lats(a):
        nx=a.shape[0]
        ny=a.shape[1]
        b=numpy.zeros([4,nx,ny])
        b[0,:,0]=1.5*a[:,0]-0.5*a[:,1]
        b[0,:,1:ny]=0.5*(a[:,0:ny-1]+a[:,1:ny])
        b[1,:,:]=b[0,:,:]
        b[2,:,0:ny-1]=b[0,:,1:ny]
        b[2,:,ny-1]=1.5*a[:,ny-1]-0.5*a[:,ny-2]
        b[3,:,:]=b[2,:,:]
        return b

    @staticmethod
    def moddegrees(x):
        if(x<0):
            return x+360.0
        elif(x>=360.0):
            return x-360.0
        else:
            return x
