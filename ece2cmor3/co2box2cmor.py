import os
import re
import numpy
import datetime
import json
import logging
import netCDF4
import cmor
import cdo
import Ngl
import warnings
from cdo import *
from ece2cmor3 import cdoapi, cmor_source, cmor_target, cmor_task, cmor_utils, postproc

# Logger object
log = logging.getLogger(__name__)

# Experiment name
exp_name_ = None

# Table root
table_root_ = None

# Files that are being processed in the current execution loop.
co2box_files_ = []

# Dictionary of co2box grid type with cmor grid id.
dim_ids_ = {}

# Dictionary of output frequencies with cmor time axis id.
time_axes_ = {}

time_axis_ids = {}

# Reference date, times will be converted to hours since refdate
ref_date_ = None

unit_miss_match =[]
failed  = []

#
#using_grid_=False
path_=None
# Initializes the processing loop.
def initialize(path,expname,tabledir, prefix,refdate):
    """initialize the cmorization for CO2BOX
    Description:
        
    Input variables:
        path, String: path to CO2BOX files
        expname, string: name of the experiment
        tabledir, string: path to tables
        prefix, string: table prefix
    Returns:
        boolean: success
    """
    global log,co2box_files_,exp_name_,table_root_,ref_date_,path_
    exp_name_ = expname
    path_ = path
    table_root_ =os.path.join(tabledir, prefix)
    # select all CO2BOX files with expname from path
    co2box_files_ = cmor_utils.find_co2box_output(path_,exp_name_)
    if len(co2box_files_) == 0:
        log.error('no CO2BOX varibles found, exiting!')
        exit()
    cal = None
    ref_date_ = refdate

    # read pressure level definitions from CMIP6_coordante file
    # and save globally
    coordfile = os.path.join(tabledir, prefix + "_coordinate.json")
    if os.path.exists(coordfile):
        with open(coordfile) as f:
            data = json.loads(f.read())
    else:
        log.warning('Using default pressure level definitions')

    cmor.load_table(table_root_ + "_grids.json")
    return True


# Resets the module globals.
def finalize():
    """finalize, clear variables
    Args:
        none
    Retruns:
        none
    """
    global co2box_files_,dim_ids_,time_axes_
    log.info( 'Unit miss match variables %s '%(unit_miss_match))
    co2box_files_ = []
    dim_ids_ = {}
    time_axes_ = {}

# Executes the processing loop.
def execute(tasks):
    """execute the cmorization tasks for CO2BOX
    Description:
        
    Args:
        tasks (list): list of tasks 
    Returns:
        boolean: success
    """
    global log,time_axes_,table_root_,co2box_files_,using_grid_,path_,exp_name_
    log.info("Executing %d co2box tasks..." % len(tasks))
    log.info("Cmorizing co2box tasks...")
    #Assign file to each task
    for task in tasks:
        setattr(task,cmor_task.output_path_key,None)
        if not task.target.frequency in ['day', 'mon']:
            task.set_failed()
            log.info('Variable %s in table %s has frequency %s and thus not available in CO2BOX.'%(task.target.variable,task.target.table,task.target.frequency))
            continue

        # if the target frequency is monthly, create monthly file from daily output with "cdo monmean"
        if task.target.frequency == 'mon':
            co2box_files = cmor_utils.find_co2box_output(path_,exp_name_,task.target.variable,"day")
            if len(co2box_files) != 1:
                log.info('Did not find one file for variable %s in table %s from CO2BOX'%(task.target.variable,task.target.table))
                task.set_failed()
            else:
                cdo = Cdo()
                ifile=co2box_files[0]
                ofile=ifile.replace("_day_","_mon_")
                log.info('Creating temporary monthly mean file %s'%(ofile))
                cdo.monmean(input=ifile, output=ofile)

        co2box_files = cmor_utils.find_co2box_output(path_,exp_name_,task.target.variable,task.target.frequency)
        if len(co2box_files) != 1:
            log.info('Did not find one file for variable %s in table %s from CO2BOX'%(task.target.variable,task.target.table))
            task.set_failed()
        else:
            setattr(task,cmor_task.output_path_key,co2box_files[0])

    #group the taks according to table
    taskdict = cmor_utils.group(tasks,lambda t:t.target.table)
    for table,tasklist in taskdict.items():
        try:
            log.info("Loading CMOR table %s to process %d variables..." % (table,len(tasklist)))
            tab_id = cmor.load_table("_".join([table_root_, table]) + ".json")
            cmor.set_table(tab_id)
        except Exception as e:
            log.error("ERR -6: CMOR failed to load table %s, skipping variables %s. Reason: %s"
                      % (table, ','.join([tsk.target.variable for tsk in tasklist]), e.message))
            continue
        dim_ids_['lat']=create_lat()
        dim_ids_['lon']=create_lon()
        # create or assign time axes to tasks
        log.info("Creating time axes for table %s..." % table)
        #create_time_axes(tasklist)
        time_axes_=create_time_axes(tasklist)#time_axes

        taskmask = dict([t,False] for t in tasklist)
        for task in tasklist:
            tmpfile = None
            ncf=getattr(task,cmor_task.output_path_key)
            try:
                tgtdims = getattr(task.target, cmor_target.dims_key).split()
            except:
                tgtdims = getattr(task.target, cmor_target.dims_key)
            if "latitude" in tgtdims and "longitude" in tgtdims:
                setattr(task, 'lon', dim_ids_['lon'])
                setattr(task, 'lat', dim_ids_['lat'])
            if "site" in tgtdims:
                log.critical('Z-dimension site not implemented ')
                task.set_failed()
                continue
            if task.status==cmor_task.status_failed:
                continue
            if(taskmask[task] ):
                log.warning("Ignoring source variable in nc file %s, since it has already been cmorized." % ncf)
            else:
                if task.status not in [cmor_task.status_failed]:
                    log.info("Cmorizing source variable %s to target variable %s from file %s." % (task.source.variable(),task.target.variable,ncf))
                    execute_netcdf_task(task,tab_id)
                    if task.status<0:
                        log.error("ERR -13: Cmorizing failed for %s" % (task.target.variable))
                    else:
                        taskmask[task] = True
                        # remove temp file
                        if task.target.frequency == 'mon' and os.path.basename(ncf).endswith('.nc.tmp'):
                            os.unlink(ncf)
                else:
                    log.info("Skipping variable %s for unknown reason..." % (task.source.variable()))
        for task,executed in taskmask.items():
            if(not executed):
                log.error("ERR -14: The source variable %s of target %s in  table %s failed to cmorize" % (task.source.variable(),task.target.variable,task.target.table))
                failed.append([task.target.variable,task.target.table])
    if len(unit_miss_match)>0:
        log.info('Unit problems: %s'% unit_miss_match)
    if len(failed)>0:
        for ifail in failed:
            log.info('Cmorization failed for : %s'%ifail)

# Performs a single task.
def execute_netcdf_task(task,tableid):
    """excute task for netcdf data
    Args:
        task (cmor.task): task which will be handled
        tableid (cmor.table): table which will have this task
    Returns:
        boolean: success of writing a variable
    """
    global log,dim_ids_,time_axes_
    interpolate_to_pressure=False
    task.status = cmor_task.status_cmorizing
    filepath = getattr(task, cmor_task.output_path_key, None)

    if not filepath:
        log.error("ERR -15: Could not find file containing data for variable %s in table %s" % (task.target.variable,task.target.table))
        task.set_failed()
        return

    store_var = getattr(task, "store_with", None)
    if( task.target.dims >= 3):
        if  ('lon' in dim_ids_ and 'lat' in dim_ids_):
            axes = [dim_ids_['lat'],dim_ids_['lon']]
        else:
            dim_ids_['lat']=create_lat()
            dim_ids_['lon']=create_lon()
            axes=[dim_ids_['lat'],dim_ids_['lon']]
        log.error('ERR -17: No z_axis_id found.')
    elif ( task.target.dims == 2):
        if not  hasattr(task, "z_axis_id"):
            ''' 
            2D variables lon+lat

            '''
            if not ('lon' in dim_ids_ and 'lat' in dim_ids_):
                dim_ids_['lat']=create_lat()
                dim_ids_['lon']=create_lon()
                axes=[dim_ids_['lat'],dim_ids_['lon']]
            else:
                axes = [dim_ids_['lat'],dim_ids_['lon']]
        else:
            log.error('ERR -18: unsupported 2D dimensions %s'%task.target.dims)
            exit('Exiting!')
    elif task.target.dims==0:
        axes=[]
    else:
        log.error('ERR -19: unsupported dimensions %s for variable'%(task.target.dims,task.target.variable))
        exit()
    time_id = getattr(task, "time_axis", 0)
    if time_id != 0:
        axes.append(time_id)
    try:
        dataset = netCDF4.Dataset(filepath, 'r')
    except Exception as e:
        log.error("ERR -20: Could not read netcdf file %s while cmorizing variable %s in table %s. Cause: %s" % (
            filepath, task.target.variable, task.target.table, e.message))
        return
    varid = create_cmor_variable(task,dataset,axes)
    if varid <0:
        return False

    ncvar = dataset.variables[task.source.variable()]

    #handle normal case - global means
    if True:# assumption: data is shape [time,lat,lon] (we need to roll longitude dimension so that 
        #  the data corresponds to the dimension definition of tables (from [-180 , 180] to [0,360] deg).)
        #  so by half the longitude dimension
        missval = getattr(task.target, cmor_target.missval_key, 1.e+20)
        # hack for co2s, we need the lowest model-level data only (assuming data is in form [time,level,lat,lon]
        if task.target.variable == "co2s" and task.source.variable() == "co2":
            vals=numpy.copy(ncvar[:,0,:,:])
            # hack to convert units from mol/mol to ppm, cmor_task.conversion_key doesn't work fos some reason
            if getattr(task.target,"units")=="1e-06" and getattr(ncvar,"units",None)=="mole mole-1":
                vals=vals*1e6
        else:
            vals=numpy.copy(ncvar[:])
        dims = numpy.shape(vals)
        nroll=dims[-1]//2
        ncvar = numpy.roll(vals,nroll,len(dims)-1)
        vals=numpy.copy(ncvar[:,:,:])
    # Default values
    factor = 1.0
    term=0.0
    timdim=0
    #check for missing values
    if numpy.isnan(ncvar).any():
        nanmask=~numpy.isnan(ncvar)
    else:
        nanmask=None
    cmor_utils.netcdf2cmor(varid, ncvar, timdim, factor, term, store_var, None,
                               swaplatlon=False, fliplat=True, mask=nanmask,missval=missval)
    cmor.close(varid)

    if store_var:
        cmor.close(store_var)
    task.status = cmor_task.status_cmorized
   

# Creates a variable in the cmor package
def create_cmor_variable(task,dataset,axes):
    """ Create cmor variable object
    Args:
        task (cmor.task): task for which we are creating a variable object
        dataset (netcdf-dataset): netcdf dataset containing the data for CO2BOX for this variable
        axes (list): list of axes ids for creation of cmor.variable object
    Returns:
        cmor.variable object: object identifier of created variable
    
    """
    srcvar = task.source.variable()
    ncvar = dataset.variables[srcvar]
    unit = getattr(ncvar,"units",None)
    if unit != getattr(task.target,"units"):
        if unit=='mole mole-1':
            # files have mole mole-1 but should be mol mol-1
            unit = getattr(task.target,"units")
        elif srcvar=='toz'or srcvar=='tropoz':
            # unit is just different
            if unit=='DU':
                setattr(task,cmor_task.conversion_key,1e-5)
            unit =  getattr(task.target,"units")
        elif srcvar=='co2mass':
            # co2mass gets converted to area sum
            unit = getattr(task.target,"units")
        else:
            unit_miss_match.append(task.target.variable)
            log.error("ERR -21: unit miss match, variable %s" % (task.target.variable))
            return task.set_failed()

    if((not unit) or hasattr(task,cmor_task.conversion_key)): # Explicit unit conversion
        unit = getattr(task.target,"units")
    if(hasattr(task.target,"positive") and len(task.target.positive) != 0):
        return cmor.variable(table_entry = str(task.target.variable),units = str(unit),axis_ids = axes,original_name = str(srcvar),positive = "down")
    else:
        return cmor.variable(table_entry = str(task.target.variable),units = str(unit),axis_ids = axes,original_name = str(srcvar))

# Creates time axes in cmor and attach the id's as attributes to the tasks
def create_time_axes(tasks):
    """ Create  time axes for all tasks
    Args:
        tasks (list): list of tasks for which time axes need to be created
    Returns:
        time_axes (dictionary): dictionary of time axes, with table+dimension combination as key
    
    """

    global log#,time_axes_
    time_axes = {}
    for task in tasks:
        freq=task.target.frequency
        tgtdims = getattr(task.target, cmor_target.dims_key)
        if getattr(task, cmor_task.output_path_key)==None:
            continue
        try:
            time_dim_list = [d for d in list(set(tgtdims.split())) if d.startswith("time")]
        except:
            time_dim_list = [d for d in tgtdims if d.startswith("time")]
        for time_dim in time_dim_list:
            key=(task.target.table,time_dim)
            if key in time_axes:
                tid = time_axes[key]
            else:
                time_operator = getattr(task.target, "time_operator", ["point"])
                log.info("Creating time axis using variable %s..." % task.target.variable)
                tid = create_time_axis(path=getattr(task, cmor_task.output_path_key),
                                       name=time_dim, has_bounds=(time_operator != ["point"]))
                time_axes[key] = tid
            setattr(task, "time_axis", tid)
            break
    return time_axes

# Creates a tie axis for the corresponding table (which is suppoed to be loaded)
def create_time_axis(path,name,has_bounds):
    """ creage time axis for a give frequency
    Args:
        path (string): full path to netcdf file with this freq
        name (string): tablename
        has_bounds (boolean): true if it has bounds
    Returns:
        cmor.axis-object: time axis object with given freq
    """
    global log,ref_date_
    vals = None
    units = None
    ds = None
    #
    ncfile=path
    refdate = ref_date_
    try:
        ds = netCDF4.Dataset(ncfile)
        timvar = ds.variables["time"]
        co2boxunit = ds.variables["time"].units
        vals = timvar[:]
        units = getattr(timvar,"units")
        if has_bounds:
            bnds = getattr(timvar,"bounds")
            bndvar = ds.variables[bnds]
    except:
        ds.close()
    co2boxrefdate=datetime.datetime.strptime(co2boxunit,"days since %Y-%m-%d %H:%M:%S")
    # delta days for change of reftime
    diff_days= (refdate-co2boxrefdate).total_seconds()/86400
    vals=vals-diff_days
    if has_bounds:
        bndvar2=numpy.zeros_like(bndvar)
        bndvar2[:,0]=bndvar[:,0]-int(diff_days)
        bndvar2[:,1]=bndvar[:,1]-int(diff_days)
        bndvar=bndvar2
        # hourly bounds can have overlap by -1e-14, which is caught by cmor library as an error
        # so just correct it always
        for i in range(numpy.shape(bndvar2)[0]-1):
            bndvar2[i+1,0]=bndvar2[i,1]
    if(len(vals) == 0 or units == None):
        log.error("ERR -22: No time values or units could be read from co2box output files %s" % str(path))
        return -1
    units="days since " + str(ref_date_)
    ####
    if has_bounds:
        return cmor.axis(table_entry = str(name), units=units, coord_vals = vals,cell_bounds = bndvar[:,:])
    else:
        return cmor.axis(table_entry = str(name), units=units, coord_vals = vals)

      
def create_lat():
    """Create latitude dimension
    Args:
        none
    Returns:
        lat_id (cmor.axis): cmor.axis-object 
    """
    lat_id=cmor.axis(table_entry="latitude", units="degrees_north",
                                    coord_vals=[0.], cell_bounds=[0.,0.])
    return lat_id

def create_lon():
    """Create longitude dimension
    Args:
        none
    Returns:
        lon_id (cmor_axis): cmor.axis-object 
    """
    lon_id=cmor.axis(table_entry="longitude", units="degrees_east",
                                    coord_vals=[0.], cell_bounds=[0.,0.])
    return lon_id
    

