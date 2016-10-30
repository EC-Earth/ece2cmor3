import os
import numpy
import cmor

# Wrapper for cmor external dependency. All calls to cmor should go via this class.
class cmorapi:

    def __init__(self,table_root_,config_file):
        self.table_root = table_root_
        self.current_table = None
        self.tables = {}
        self.grids = {}
        self.time_axes = {}
        self.depth_axes = {}
        self.surface_pressure_id = None
        self.surface_pressure_vals = None
        cmor.setup(os.path.dirname(table_root_))
        cmor.dataset_json(config_file)

# Loads the given table (string) and adds the resulting id to the table dictionary. Stores the loaded table as current table.
    def load_table(self,table):
        if(self.current_table == table): return self.tables[table]
        tabid = 0
        if(table in self.tables):
            tabid = self.tables[table]
            cmor.set_table(tabid)
        else:
            tabid = cmor.load_table(self.table_root + "_" + table + ".json")
        self.tables[table] = tabid
        self.current_table = table
        return tabid

# Sets the calendar attribute
    def set_calendar(cal):
        cmor.set_cur_dataset_attribute("calendar",cal)

# Lookup whether an axis for the (table,entry) pair has been created. If not calls the createfunc function to do so.
# This function should return a dictionary {"units":<string>,"values":<numpy.array>,"bounds":<numpy.array>}
    def create_axis(self,table,entry,axeslist,createfunc):
        if((table,entry) in axeslist): return axeslist[(table,entry)]
        self.load_table(table)
        d=createfunc()
        axisname=d["name"]
        axeslist[(table,axisname)] = cmor.axis(table_entry = axisname,
                                               units = d["units"],
                                               coord_vals = d["values"],
                                               cell_bounds = d["bounds"])
        return axeslist[(table,axisname)]

# Time axis version of create_axis
    def create_time_axis(self,table,entry,createfunc):
        return create_axis(self,table,self.time_axes,createfunc)

# Depth axis version of create_axis
    def create_depth_axis(self,table,entry,createfunc):
        return create_axis(self,table,self.depth_axes,createfunc)

# Grid creation wrapper function, keeps track whether a grid with the same name already exists.
    def create_grid(self,gridname,axes,createfunc):
        if(gridname in self.grids): return self.grids[gridname]
        self.load_table("grids")
        d = createfunc()
        axisids={}
        for axis in axes:
            axisinfo = d[axis]
            axid = cmor.axis(axisinfo["name"],axisinfo["units"],axisinfo["values"])
            axisids.append(axid)
        self.grids[gridname]=cmor.grid(axis_ids = axisids,
                                       latitude = d["lats"],
                                       longitude = d["lons"],
                                       latitude_vertices = d["lat_bounds"],
                                       longitude_vertices = d["lon_bounds"])
        return self.grids[gridname]

# Creates a cmor variable.
    def create_variable(self,varname,table,axisnames,gridname,unit,zdir=None,originalname=None):
        self.load_table(table)
        axisids,anames = [],axisnames
        if("latitude" in axisnames and "longitude" in axisnames):
            if(not gridname in self.grids): raise Exception("Grid",gridname,"was not created by this class")
            anames.remove("latitude")
            anames.remove("longitude")
            axisids.append(self.grids[gridname])
        for axis in anames:
            if((table,axis) in self.depth_axes):
                axisids.append(self.depth_axes[(table,axis)])
                anames.remove(axis)
                break
        for axis in anames:
            if((table,axis) in self.time_axes):
                axisids.append(self.time_axes[(table,axis)])
                anames.remove(axis)
                break
        if(len(anames) != 0): raise Exception("Combination of axes",axisnames,"could not be converted to valid id's. Axes causing problems are",anames)
        return cmor.variable(table_entry=varname,units=unit,axis_ids=axisids,positive=zdir,original_name=originalname)

# Writes the input array valarray to cmor,
    def writevals(self,varid,valarray,factor = 1.0,psvarid = None,ncpsvar = None):
        dims = len(valarray.shape)
        times = if dims == 2 ? 1 else valarray.shape[0]
        size = valarray.size / times
        chunk = int(math.floor(4.0E+9 / (8 * size))) # Use max 4 GB of memory
        for i in range(0,times,chunk):
            imax = min(i + chunk,times)
            vals = None
            if(dims == 1): # We assume a time series here
                vals = valarray[i:imax] * factor
            elif(dims == 2): # We assume time constant lat/lon field
                vals = valarray[:,:] * factor
            elif(dims == 3): # We assume a time-varying lat/lon field
                vals = numpy.transpose(valarray[i:imax,:,:],axes = [1,2,0]) * factor
            elif(dims == 4): # We assume a time-varying volume field.
                vals = numpy.transpose(valarray[i:imax,:,:,:],axes = [2,3,1,0]) * factor
            else:
                raise Exception("Arrays of dimensions",dims,"are not supported by ece2cmor")
                cmor.write(varid,numpy.asfortranarray(vals),ntimes_passed = (imax-i))
                if(psvarid and ncpsvar):
                    spvals = numpy.transpose(ncpsvar[i:imax,:,:],axes = [1,2,0])
                    cmor.write(psvarid,numpy.asfortranarray(spvals),ntimes_passed = (imax-i),store_with = varid)
