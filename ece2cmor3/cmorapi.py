import os
import numpy
import cmor

# Wrapper for cmor external dependency. All calls to cmor should go via this class.
class cmorapi:

    float cache_size_gb = 4.

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
        return cmor.variable(table_entry = varname,units = unit,axis_ids = axisids,positive = zdir,original_name = originalname)

# Writes the input array valarray to cmor. Returns the number of time slices written
    @staticmethod
    def writevals(varid,valarray,time_index = 0,factor = 1.0,store_with = None):
        times = 1 if time_index < 0 else valarray.shape[time_index]
        size = valarray.size / times
        chunk = int(math.floor(cache_size_gb / (8 * size))) # Use max 4 GB of memory
        for i in range(0,times,chunk):
            imin = i
            imax = min(i + chunk,times)
            vals = cmorapi.timeslice(valarray,time_index,imin,imax)
            if(not vals): return i
            if(store_with == None):
                cmor.write(varid,numpy.asfortranarray(factor * vals),ntimes_passed = (0 if timdim < 0 else (imax - imin)))
            else:
                cmor.write(varid,numpy.asfortranarray(factor * vals),ntimes_passed = (0 if timdim < 0 else (imax - imin)),store_with = store_with)
        return times

# Takes the appropriate slices and transposes the resulting array to suitable chunk of data for CMOR
    @staticmethod
    def timeslice(valarray,time_index,imin,imax):
        rank = len(valarray.shape)
        if(time_index >= rank):
            log.error("Invalid time index %d assigned to array of rank %d" % (time_index,rank))
            return None
        if(rank == 1):
            if(time_index < 0):
                return valarray[:]
            if(time_index == 0):
                return valarray[imin:imax]
        if(rank == 2):
            if(time_index < 0):
                return valarray[:,:]
            if(time_index == 0):
                return numpy.transpose(valarray[imin:imax,:],axes = [1,0])
            if(time_index == 1):
                return valarray[:,imin:imax]
        if(rank == 3):
            if(time_index < 0):
                return numpy.transpose(valarray[:,:,:],axes = [1,2,0])
            if(time_index == 0):
            	return numpy.transpose(valarray[imin:imax,:,:],axes = [1,2,0])
            if(time_index == 2):
                return valarray[:,:,imin:imax]
            log.error("Unsupported array structure with 3 dimensions and time dimension index 1")
            return None
        if(rank == 4):
            if(time_index == 0):
            	return numpy.transpose(valarray[imin:imax,:,:,:],axes = [2,3,1,0])
            if(time_index == 3):
                return valarray[:,:,:,i:imax]
            log.error("Unsupported array structure with 4 dimensions and time dimension index %d" % time_index)
            return None
        logger.error("Cmorizing arrays of rank %d is not supported" % rank)
        return None
