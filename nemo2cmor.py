import netCDF4
import cmor_utils
import cmor_source
import numpy

# Initializes the processing loop.
def initialize(path,expname,tableroot,start,length):
    global nemo_files_
    nemo_files_=select_files(path,expname,start,length)
    cal=None
    for f in nemo_files_:
        cal=read_calendar(f)
        if(cal):
            break
    if(cal):
        cmor.set_cur_dataset_attribute("calendar",cal)
    create_time_axes(files)
    create_grids(files,tableroot+"_grids.json")

# Executes the processing loop.
def execute(tasks):
    raise Exception("Not implemented yet")

# Retrieves all NEMO output files in the input directory.
def select_files(path,expname,start,length):
    allfiles=cmor_utils.get_nemo_output(path,expname)
    return [f for f in allfiles if cmor_utils.get_nemo_interval(f)[0]>=start and cmor_utils.get_nemo_interval(f)[1]<=(start+length)]

# Reads the calendar attribute from the time dimension.
def read_calendar(ncfile):
    ds=netCDF4.Dataset(ncfile,'r')
    timvar=ds.dimensions["time_counter"]
    if(timvar):
        return getattr(timvar,"calendar")
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

# Creates time axes for all frequencies in the output
def create_time_axes(files):
    raise Exception("Not implemented yet")

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

# Files that are being processed in the current execution loop.
nemo_files_=[]

# Dictionary of NEMO grid type with cmor grid id.
grid_ids_={}

# Dictionary of output frequencies with cmor time axis id.
time_axes_={}
