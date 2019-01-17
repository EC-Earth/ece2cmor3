import os
import re
import numpy
import datetime
import json
import logging
import netCDF4
import cmor
import cmor_utils
import cmor_source
import cmor_target
import cmor_task
import cdo
from ece2cmor3 import cdoapi
import Ngl

# Logger object
log = logging.getLogger(__name__)

# Experiment name
exp_name_ = None

# Table root
table_root_ = None

# Files that are being processed in the current execution loop.
tm5_files_ = []

# Dictionary of tm5 grid type with cmor grid id.
grid_ids_ = {}

# List of depth axis ids with cmor grid id.
depth_axes_ = {}

# Dictionary of output frequencies with cmor time axis id.
time_axes_ = {}

# Dictionary of sea-ice output types, 1 by default...
type_axes_ = {}

ps_tasks = {}

time_axis_ids = {}
depth_axis_ids = {}

# Reference date, times will be converted to hours since refdate
ref_date_ = None

unit_miss_match =[]
failed  = []

# Pressure levels
plev19_ = numpy.array([100000.,92500.,85000.,70000.,60000.,50000.,40000.,30000.,25000.,20000.,15000.,10000.,7000.,5000.,3000.,2000.,1000.,500.,100.])
plev39_ = numpy.array([1000.,925.,850.,700.,600.,500.,400.,300.,250.,200.,170.,150.,130.,115.,100.,90.,80.,70.,50.,30.,20.,15.,10.,7.,5.,3.,2.,1.5,1.,0.7,0.5,0.4,0.3,0.2,0.15,0.1,0.07,0.05,0.03])

#
ignore_frequency=['subhrPt','6hrPt']
# Initializes the processing loop.
def initialize(path,expname,tabledir, prefix,refdate):
    global log,tm5_files_,exp_name_,table_root_,ref_date_,plev39_,plev19_
    exp_name_ = expname
    table_root_ =os.path.join(tabledir, prefix)
    #tm5_files_ = select_files(path,expname,start)#,length)
    tm5_files_ = cmor_utils.find_tm5_output(path,expname)
    cal = None
    ref_date_ = refdate
    for f in tm5_files_:
        cal = read_calendar(f)
        if(cal):
            break
    if(cal):
        cmor.set_cur_dataset_attribute("calendar",cal)

    # read pressure level definitions from CMIP6_coordante file
    # and save globally
    coordfile = os.path.join(tabledir, prefix + "_coordinate.json")
    if os.path.exists(coordfile):
        with open(coordfile) as f:
            data = json.loads(f.read())
        axis_entries = data.get("axis_entry", {})
        axis_entries = {k.lower(): v for k, v in axis_entries.iteritems()}
        plev19=numpy.array([numpy.float(value) for value in  axis_entries['plev19']['requested']])
        plev19_=plev19
        plev39=numpy.array([numpy.float(value) for value in  axis_entries['plev39']['requested']])
        plev39_=plev39

    cmor.load_table(table_root_ + "_grids.json")
    return True


# Resets the module globals.
def finalize():
    global tm5_files_,grid_ids_,depth_axes_,time_axes_,plev19_,plev39_
    log.info( 'Unit miss match variables %s '%(unit_miss_match))
    tm5_files_ = []
    grid_ids_ = {}
    depth_axes_ = {}
    time_axes_ = {}
    plev39_ = []
    plev19_ = []

# Executes the processing loop.
def execute(tasks):
    global log,time_axes_,depth_axes_,table_root_,tm5_files_
    log.info("Executing %d tm5 tasks..." % len(tasks))
    log.info("Cmorizing tm5 tasks...")
    #Assign file to each task
    for task in tasks:
        #print task.target.variable,task.target.frequency
        setattr(task,cmor_task.output_path_key,None)
        if task.target.frequency=='1hr':
            freqid='hr'
            #print freqid,fstr,freqid in fstr
        elif task.target.frequency=='6hrPt':
            freqid='6hr'
            #print freqid,fstr,freqid in fstr
        elif task.target.frequency=='3hrPt':
            freqid='3hr'
            #print freqid,fstr,freqid in fstr
        elif task.target.frequency=='fx':
            log.info('fx frequency has no variables from TM5')
            task.set_failed()
            continue
        elif task.target.frequency=='CFday':

            freqid='AERday'
        elif task.target.frequency in ignore_frequency:
            log.info('frequency %s ignored, no data prduced at this frequency'%task.target.frequency)
            continue
        else:
            freqid=task.target.frequency
        # also check that frequencies match
        if task.target.table=='AERmonZ':
            freqid='AER'+freqid+'Z'
        elif task.target.table=='AERhr':
            freqid='AER'+freqid
        elif task.target.table=='Amon':
            # ps is only an auxilliary variable for creating vertical axis for variables
            # Tables say Amon... but TM5 file has a description AERmon
            if task.target.variable=='ps':
                freqid='AER'+freqid
            #else:
            #    freqid='A'+freqid
        elif task.target.table=='AERmon':
            # Select only by frequency to catch variables which are read from AERmon and written to Amon
            freqid=freqid
        
        for fstr in tm5_files_:
            # only select files which start with variable name and have _ behind (e.g. o3 .neq. o3loss)
            # and freqid has _ behing (e.g. monZ .neq. mon)
            
            # catch variablename + '_' to prevent o3 and o3loss mixing up...
            if os.path.basename(fstr).startswith(task.source.variable()+"_") and   freqid+'_' in fstr  :
                fname=fstr
                if getattr(task,cmor_task.output_path_key) == None:
                    setattr(task,cmor_task.output_path_key,fstr)
                else: 
                    log.critical('Second file with same frequency and name. Currently supporting only one year per directory.')
                    log.critical(fstr)
                    exit(' Exiting ece2cmor.')
            if not os.path.exists(fstr):
                log.info('No path found for variable %s from TM5'%(task.target.variable))
                task.set_failed()
                continue
        # save ps task for frequency
        if task.target.variable=='ps':
            #print 'ps',task.target.frequency, getattr(task,cmor_task.output_path_key)
            if task.target.frequency not in ps_tasks:
                ps_tasks[task.target.frequency]=task
    log.info('Creating TM5 3x2 deg lon-lat grid')
    grid = create_lonlat_grid()#xsize, xfirst, yvals)
    
    grid_ids_['lonlat']=grid

    cmor.set_cur_dataset_attribute("calendar", "proleptic_gregorian")
    #cmor.load_table(table_root_ + "_grids.json")

    #group the taks according to table
    taskdict = cmor_utils.group(tasks,lambda t:t.target.table)
    for table,tasklist in taskdict.iteritems():
        try:
            log.info("Loading CMOR table %s to process %d variables..." % (table,len(tasklist)))
            tab_id = cmor.load_table("_".join([table_root_, table]) + ".json")
            cmor.set_table(tab_id)
        except Exception as e:
            log.error("CMOR failed to load table %s, skipping variables %s. Reason: %s"
                      % (table, ','.join([tsk.target.variable for tsk in tasklist]), e.message))
            continue
        #     #postprocess data to zonal mean and plev39, or do it before this point
        if table == '3hr' :
            for task in tasklist:
                task.set_failed()
            log.error("Table %s not implemented yet" %(table))
            log.error("Skipping variable %s not implemented yet" %(task.target.variable))
            continue
            #postprocess data to zonal mean and plev39, or do it before this point
        if table== '6hrLev':
            for task in tasklist:
                task.set_failed()
            log.error("Table %s not implemented yet  due to error in CMIP6 tables." %(table))
            log.error("Skipping variable %s not implemented yet" %(task.target.variable))
            continue
        if table== 'Eday':
            print 'EDAY: ',task.target.variable
        # create or assign time axes to tasks
        log.info("Creating time axes for table %s..." % table)
        create_time_axes(tasklist)

        taskmask = dict([t,False] for t in tasklist)
        for task in tasklist:
            #define task properties 
            #2D grid

            ncf=getattr(task,cmor_task.output_path_key)
            tgtdims = getattr(task.target, cmor_target.dims_key).split()
            if "latitude" in tgtdims and "longitude" in tgtdims:
                setattr(task, "grid_id", grid)
            #ZONAL
            if "latitude" in tgtdims and not "longitude" in tgtdims:
                setattr(task, "zonal", True)
            
            #Vertical
            if "alevel" in tgtdims:
                if task.target.frequency not in ps_tasks:
                    log.error("ps task not available for frequency %s !!" % (task.target.frequency))
                    continue
                setattr(task,"ps_task",ps_tasks[task.target.frequency])
            if "site" in tgtdims:
                log.critical('Z-dimension site not implemented ')
                task.set_failed()
                continue

            create_depth_axes(task)
            if(taskmask[task] ):
                log.warning("Ignoring source variable in nc file %s, since it has already been cmorized." % ncf)
            else:
                if task.status not in [cmor_task.status_failed]:
                    log.info("Cmorizing source variable %s to target variable %s from file %s." % (task.source.variable(),task.target.variable,ncf))
                    execute_netcdf_task(task,tab_id)
                    if task.status<0:
                        if task.target.variable=='cdnc':
                            log.error("Cmorizing failed for %s, but variable is produced by IFS." % (task.target.variable))
                        elif task.target.variable=='o3Clim':
                            log.error("Cmorizing failed for %s, check tm5par.json since source will be o3 instead of %s." % (task.target.variable, task.source.variable()))
                        elif task.target.variable=='ch4Clim' or task.target.variable=='ch4global' or task.target.variable=='ch4globalClim':
                            log.error("Cmorizing failed for %s, check tm5par.json since source will be ch4 instead of %s." % (task.target.variable, task.source.variable()))
                        else:
                            log.error("Cmorizing failed for %s" % (task.target.variable))
                    else:
                        taskmask[task] = True
                else:
                    log.info("Skipping variable %s for unknown reason..." % (task.source.variable()))
        for task,executed in taskmask.iteritems():
            if(not executed):
                log.error("The source variable %s of table %s failed to cmorize" % (task.source.variable(),task.target.table))
                failed.append([task.target.variable,task.target.table])

    log.info('Unit problems: %s'% unit_miss_match)
    log.info('Cmorization failed: %s'%failed)
# Performs a single task.
def execute_netcdf_task(task,tableid):
    global log,grid_ids_,depth_axes_,time_axes_
    interpolate_to_pressure=False
    task.status = cmor_task.status_cmorizing
    filepath = getattr(task, cmor_task.output_path_key, None)

    if not filepath:
        log.error("Could not find file containing data for variable %s in table %s" % (task.target.variable,task.target.table))
        task.set_failed()
        return

    store_var = getattr(task, "store_with", None)
    axes = [grid_ids_['lonlat']]
    #if task.target.table =='AERmonZ':
    #    print 'aermonz: ',task.target.dims,task.target.variable
    if( task.target.dims == 3):
        grid_index = axes#cmor_source.tm5_grid.index(task.grid_id)
        #grid_ids_['lat2']=create_lat()
        #grid_ids_['lon2']=create_lon()
        axes = [grid_ids_['lonlat']]
        #axes = [grid_ids_['lat2'],grid_ids_['lon2']]
        axes = [grid_ids_['lonlat']]
        if hasattr(task, "z_axis_id"):
            axes.append(getattr(task, "z_axis_id"))
    elif ( task.target.dims == 2):
        if task.target.table=='AERmonZ':
            '''
            2D Zonal lat+lev
            '''
            #cmor.load_table(table_root_ + "_coordinate.json")
            if hasattr(grid_ids_,'lat2'):
                axes=[grid_ids_['lat2']]
            else:
                grid_ids_['lat2']=create_lat()
                axes=[grid_ids_['lat2']]
            #cmor.load_table(table_root_ + "_grids.json")

            # zonal variables...
            #needs lat only, no grid....
            grid_index = axes#cmor_source.tm5_grid.index(task.grid_id)
            if hasattr(task, "z_axis_id"):
                axes.append(getattr(task, "z_axis_id"))
                #print axes
                if 'plev19' in getattr(task.target, cmor_target.dims_key).split():
                    interpolate_to_pressure=True
                elif'plev39'  in getattr(task.target, cmor_target.dims_key).split():
                    interpolate_to_pressure=True
        elif not  hasattr(task, "z_axis_id"):
            ''' 
            2D variables lon+lat

            '''
            if hasattr(grid_ids_,'lon2'):
                axes=[grid_ids_['lat2']]
                axes=[grid_ids_['lon2']]
            else:
                grid_ids_['lat2']=create_lat()
                grid_ids_['lon2']=create_lon()
                #grid_ids_['lat2']=create_lat()
                axes=[grid_ids_['lat2'],grid_ids_['lon2']]
            #grid_ids_['lat2']=create_lat()
            #grid_ids_['lon2']=create_lon()
            #axes = [grid_ids_['lonlat']]
            axes = [grid_ids_['lat2'],grid_ids_['lon2']]
        else:
            print 'unsupported 2D dimensions'
            sadf

    else:
        print 'unsupported dimesnsions'
        print task.target.variable
        #dfsadfa#task.set_failed()
        #return false
    time_id = getattr(task, "time_axis", 0)
    if time_id != 0:
        axes.append(time_id)
    for type in type_axes_:
        if type in getattr(task.target, cmor_target.dims_key):
            axes.append(type_axes_[type])
    try:
        dataset = netCDF4.Dataset(filepath, 'r')
    except Exception as e:
        log.error("Could not read netcdf file %s while cmorizing variable %s in table %s. Cause: %s" % (
            filepath, task.target.variable, task.target.table, e.message))
        return
    varid = create_cmor_variable(task,dataset,axes)
    if varid <0:
        return False

    ## for pressure level variables we need to do interpolation, for which we need
    ## pyngl module
    if interpolate_to_pressure:
        psdata=get_ps_var(getattr(ps_tasks[task.target.frequency],cmor_task.output_path_key,None))
        pnew=getattr(task,'pnew')
        ncvar=interpolate_plev(pnew,dataset,psdata,task.source.variable())
    else:  
        ncvar = dataset.variables[task.source.variable()]
    if task.target.table=='AERmonZ': 
        # assumption: data is shape [time,lat,lon] (roll longitude dimensio
        #print numpy.shape(ncvar),interpolate_to_pressure
        #print getattr(task.target, cmor_target.dims_key).split()
        vals=numpy.copy(ncvar[:])
        # zonal mean so mean over longitudes
        vals=numpy.mean(vals,axis=-1)
        # change shape, swap lat<->lev
        vals=numpy.swapaxes(vals,1,2)

        dims = numpy.shape(vals)
        #print dims
        #nroll=dims[-1]/2
        #ncvar = numpy.roll(vals,nroll,len(dims)-1)
        missval = getattr(ncvar,"missing_value",getattr(ncvar,"_FillValue",numpy.nan))
        #vals=numpy.copy(ncvar[:,:,:])
        ncvar=vals.copy()
    else:# assumption: data is shape [time,lat,lon] (roll longitude dimension)
        vals=numpy.copy(ncvar[:])
        dims = numpy.shape(vals)
        nroll=dims[-1]/2
        ncvar = numpy.roll(vals,nroll,len(dims)-1)
        missval = getattr(ncvar,"missing_value",getattr(ncvar,"_FillValue",numpy.nan))
        vals=numpy.copy(ncvar[:,:,:])
    #factor 1. keep it for time being
    # Default values
    factor = 1.0
    term=0.0
    timdim=0
    # 3D variables need the surface pressure for calculating the pressure at model levels
    if store_var:
        #get the ps-data associated with this data
        psdata=get_ps_var(getattr(ps_tasks[task.target.frequency],cmor_task.output_path_key,None))
        # roll psdata like the original
        psdata=numpy.roll(psdata[:],nroll,len(numpy.shape(psdata[:]))-1)
        cmor_utils.netcdf2cmor(varid, ncvar, timdim, factor, term, store_var, psdata,
                               swaplatlon=False, fliplat=True, mask=None,missval=missval)
        #cmor_utils.netcdf2cmor(varid, ncvar, timdim, factor, term, store_var, get_ps_var(getattr(ps_tasks[task.target.frequency],cmor_task.output_path_key,None)),
        #                       swaplatlon=False, fliplat=True, mask=None,missval=missval)
    else:
        cmor_utils.netcdf2cmor(varid, ncvar, timdim, factor, term, store_var, None,
                               swaplatlon=False, fliplat=True, mask=None,missval=missval)
    cmor.close(varid)
    if store_var:
        cmor.close(store_var)
    task.status = cmor_task.status_cmorized
   

# Creates a variable in the cmor package
def create_cmor_variable(task,dataset,axes):
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

        else:
            unit_miss_match.append(task.target.variable)
            log.error("unit miss match, variable %s" % (task.target.variable))
            return task.set_failed()
    if((not unit) or hasattr(task,cmor_task.conversion_key)): # Explicit unit conversion
        unit = getattr(task.target,"units")
    if(hasattr(task.target,"positive") and len(task.target.positive) != 0):
        return cmor.variable(table_entry = str(task.target.variable),units = str(unit),axis_ids = axes,original_name = str(srcvar),positive = "down")
    else:
        return cmor.variable(table_entry = str(task.target.variable),units = str(unit),axis_ids = axes,original_name = str(srcvar))

def interpolate_plev(pnew,dataset,psdata,varname):
    ####
    # Interpolate data from model levels to pressure levels
    # pnew defines the pressure levels
    # Based on pyngl example: 
    # https://www.pyngl.ucar.edu/Examples/Scripts/vinth2p.py 
    ####

    # Reference pressure 1e5 Pa in TM5, here in hPa 
    p0mb=1000

    # Vertical coordinate must be from top to bottom: [::-1]
    hyam = dataset.variables["hyam"][:]
    # Vertical interplation routine expects formula a*p0 + b*ps, 
    # TM5 has a + b*ps, change a-> a*p0 by dividing a by the reference in TM5 p0=1e5 (1000 mb / hPa)
    hyam = hyam[::-1]/(100000)
    # Vertical coordinate must be from top to bottom: [::-1]

    hybm = dataset.variables["hybm"][:]
    hybm = hybm[::-1]
    # Vertical coordinate must be from top to bottom: [::-1]
    data   = dataset.variables[varname][:,:,:,:]
    data = data[:,::-1,:,:]

    interpolation=1 #1 linear, 2 log, 3 loglog
    datanew = Ngl.vinth2p(data,hyam,hybm,pnew,psdata[:,:,:],interpolation,p0mb,1,True)
    return datanew


# Creates time axes in cmor and attach the id's as attributes to the tasks
def create_time_axes(tasks):
    global log
    time_axes = {}
    for task in tasks:
        freq=task.target.frequency
        tgtdims = getattr(task.target, cmor_target.dims_key)
        if getattr(task, cmor_task.output_path_key)==None:
            continue
        # TODO: better to check in the table axes if the standard name of the dimension equals "time"
        for time_dim in [d for d in list(set(tgtdims.split())) if d.startswith("time")]:
            key=(task.target.table,time_dim)
            if key in time_axes:
                tid = time_axes[key]
            else:
                time_operator = getattr(task.target, "time_operator", ["point"])
                log.info("Creating time axis using variable %s..." % task.target.variable)
                tid = create_time_axis(freq=task.target.frequency, path=getattr(task, cmor_task.output_path_key),
                                       name=time_dim, has_bounds=(time_operator != ["point"]))
                time_axes[key] = tid
            setattr(task, "time_axis", tid)
            break

# Creates a tie axis for the corresponding table (which is suppoed to be loaded)
def create_time_axis(freq,path,name,has_bounds):
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
        tm5unit = ds.variables["time"].units
        vals = timvar[:]
        #if 'bounds' in ds.variables:
        has_bounds=True
        bnds = getattr(timvar,"bounds")
        bndvar = ds.variables[bnds]
        units = getattr(timvar,"units")
    except:
        ds.close()
    #print len(vals),vals[1]-vals[0]
    tm5refdate=datetime.datetime.strptime(tm5unit,"days since %Y-%m-%d %H:%M:%S")
    #print tm5refdate  
    diff_days= (refdate-tm5refdate).total_seconds()/86400
    vals=vals-diff_days
    bndvar2=numpy.zeros_like(bndvar)
    bndvar2[:,0]=bndvar[:,0]-int(diff_days)
    bndvar2[:,1]=bndvar[:,1]-int(diff_days)
    bndvar=bndvar2
    # hourly bounds can have overlap by -1e-14, which is caught by cmor library as an error
    # so just correct it always
    for i in range(numpy.shape(bndvar2)[0]-1):
        bndvar2[i+1,0]=bndvar2[i,1]

    if(len(vals) == 0 or units == None):
        log.error("No time values or units could be read from tm5 output files %s" % str(files))
        return 0
    
    units="days since " + str(ref_date_)
    #DEBUG for hourly output
    if freq=='1hr':
        print str(name),bndvar[0,0],bndvar[0,1],bndvar[1,0],bndvar[1,1]
    ####
    if has_bounds:
        return cmor.axis(table_entry = str(name), units=units, coord_vals = vals,cell_bounds = bndvar[:,:])
    else:
        return cmor.axis(table_entry = str(name), units=units, coord_vals = vals)
    


# Reads the calendar attribute from the time dimension.
def read_calendar(ncfile):
    try:
        ds = netCDF4.Dataset(ncfile,'r')
        if(not ds):
            return None
        timvar = ds.variables["time"]
        if(timvar):
            result = getattr(timvar,"calendar")
            return result
        else:
            return None
    finally:
        ds.close()

def create_depth_axes(task):
    global log_depth_axis_ids
    #depth_axes = {}
    #for task in tasks:
    tgtdims = getattr(task.target, cmor_target.dims_key)
    zdims = getattr(task.target, "z_dims", [])
    if len(zdims) == 0:
        return False
    if len(zdims) > 1:
        log.error("Skipping variable %s in table %s with dimensions %s with multiple z-directions." % (
            task.target.variable, task.target.table, tgtdims))
        task.set_failed()
        return False
    zdim=str(zdims[0])
    key = (task.target.table, zdim)
    if key not in depth_axis_ids:
        log.info("Creating vertical axis for table %s..." % task.target.table)

    if key in depth_axis_ids:
        #setattr(task, "z_axis_id", depth_axis_ids[zdim])
        if zdim == "alevel":
            setattr(task, "z_axis_id", depth_axis_ids[key][0])
            setattr(task, "store_with", depth_axis_ids[key][1])
        elif zdim == "plev19":
            setattr(task, "z_axis_id", depth_axis_ids[key])
            setattr(task, "pnew", plev19_)
        elif zdim == "plev39":
            setattr(task, "z_axis_id", depth_axis_ids[key])
            setattr(task, "pnew", plev39_)
        else:
            setattr(task, "z_axis_id", depth_axis_ids[key])
        return True
    elif zdim == 'alevel':
        log.info("Creating model level axis for variable %s..." % task.target.variable)
        axisid, psid = create_hybrid_level_axis(task)
        depth_axis_ids[key] = (axisid, psid)
        setattr(task, "z_axis_id", axisid)
        setattr(task, "store_with", psid)
        return True
    elif zdim == 'alevhalf':
        # if zdim not in depth_axis_ids:
        #     log.info("Creating model level axis for variable %s..." % task.target.variable)
        #     axisid, psid = create_hybrid_level_axis(task)
        #     depth_axis_ids[zdim] = (axisid, psid)
        #     setattr(task, "z_axis_id", axisid)
        #     setattr(task, "store_with", psid)
        #     return 
        log.error("Vertical axis %s not implemented yet" %(zdim))
        task.set_failed()
        return False
    elif zdim=="lambda550nm":
        log.info("Creating wavelength axis for variable %s..." % task.target.variable)
        log.info("TOBE CORRECTED:  wavelength axis BOUNDS will be removed in new tables (1.00.28) for variable %s..." % task.target.variable)
        axisid=cmor.axis(table_entry = zdim,units ="nm" ,coord_vals = [550.0],cell_bounds=[549,551])
        depth_axis_ids[key]=axisid
        setattr(task, "z_axis_id", axisid)
        return True
    elif zdim=="plev19":
        axisid=cmor.axis(table_entry = zdim,units ="Pa" ,coord_vals = plev19_)
        depth_axis_ids[key]=axisid
        setattr(task, "z_axis_id", axisid)
        setattr(task, "pnew", plev19_)
        return True
    elif zdim=="plev39":
        axisid=cmor.axis(table_entry = zdim,units ="Pa" ,coord_vals = plev39_)
        depth_axis_ids[key]=axisid
        setattr(task, "z_axis_id", axisid)
        setattr(task, "pnew", plev39_)
        return True
    elif zdim=="site":
        log.critical('Z-dimension %s will not be implemented.'%zdim)
        return False
    else:
        log.critical("Z-dimension %s not found for variable %s..." % (zdim,task.target.variable))
        return False


# Creates the hybrid model vertical axis in cmor.
def create_hybrid_level_axis(task):
    pref = 80000  # TODO: Move reference pressure level to model config
    path = getattr(task, cmor_task.output_path_key)
    ds = None
    try:
        ds = netCDF4.Dataset(path)
        am = ds.variables["hyam"]
        aunit = getattr(am, "units")
        bm = ds.variables["hybm"]
        bunit = getattr(bm, "units")
        hcm = am[:] / pref + bm[:]
        n = hcm.shape[0]
        
        if "hyai" in ds.variables: 
            ai = ds.variables["hyai"]
            abnds = numpy.empty([n, 2])
            abnds[:, 0] = ai[0:n]
            abnds[:, 1] = ai[1:n + 1]
            bi = ds.variables["hybi"]
            bbnds = numpy.empty([n, 2])
            bbnds[:, 0] = bi[0:n]
            bbnds[:, 1] = bi[1:n + 1]
            hcbnds = abnds / pref + bbnds
        # temporary solution for current output
        else:
            ai=numpy.empty([n+1]    )
            bi=numpy.empty([n+1]    )
            ai[1:-1]=(am[1:]+am[0:-1])/2
            
            ai[0]=am[0]/2
            ai[-1]=am[-1]
            abnds = numpy.empty([n, 2])
            abnds[:, 0] = ai[0:n]
            abnds[:, 1] = ai[1:n + 1]

            bi[1:-1]=(bm[1:]+bm[0:-1])/2
            bi[0]=1.0
            bi[-1]=0.0
            bbnds = numpy.empty([n, 2])
            bbnds[:, 0] = bi[0:n]
            bbnds[:, 1] = bi[1:n + 1]
            hcbnds = abnds / pref + bbnds
            hcbnds[0,0]=1.0
        axisid = cmor.axis(table_entry="alternate_hybrid_sigma", coord_vals=hcm, cell_bounds=hcbnds, units="1")
        
        cmor.zfactor(zaxis_id=axisid, zfactor_name="ap", units=str(aunit), axis_ids=[axisid], zfactor_values=am[:],
                     zfactor_bounds=abnds)
        cmor.zfactor(zaxis_id=axisid, zfactor_name="b", units=str(bunit), axis_ids=[axisid], zfactor_values=bm[:],
                     zfactor_bounds=bbnds)
        axes=[]
        axes.append(getattr(task, "grid_id"))
        #print axes
        axes.append( getattr(task, "time_axis"))
        #print axes
        storewith = cmor.zfactor(zaxis_id=axisid, zfactor_name="ps",
                                axis_ids=axes, units="Pa")
        return axisid, storewith
    finally:
        if ds is not None:
            ds.close()
def create_lat():#nx, x0, yvals):
    yvals=numpy.linspace(89,-89,90)
    ny = len(yvals)
    lat_bnd=numpy.linspace(90,-90,91)
    lat_id2=cmor.axis(table_entry="latitude", units="degrees_north",
                                    coord_vals=yvals, cell_bounds=lat_bnd)
    return lat_id2

def create_lon():#nx, x0, yvals):
    xvals=numpy.linspace(1.5,358.5,120)
    nx = len(xvals)
    lon_bnd=numpy.linspace(0,360,121)
    lon_id2=cmor.axis(table_entry="longitude", units="degrees_east",
                                    coord_vals=xvals, cell_bounds=lon_bnd)
    return lon_id2

def create_lonlat_grid():#nx, x0, yvals):
    nx=120
    x0=0
    yvals=numpy.linspace(89,-89,90)
    ny = len(yvals)
    #print numpy.array(range(1, nx + 1))
    i_index_id = cmor.axis(table_entry="i_index", units="1", coord_vals=numpy.array(range(1, nx + 1)))
    j_index_id = cmor.axis(table_entry="j_index", units="1", coord_vals=numpy.array(range(1, ny + 1)))
    #print 'axisid',i_index_id,j_index_id
    dx = 360. / nx
    x_vals = numpy.array([x0 + (i + 0.5) * dx for i in range(nx)])
    lon_arr = numpy.tile(x_vals, (ny, 1))
    #lat_arr = numpy.tile(yvals[::-1], (nx, 1)).transpose()
    lat_arr = numpy.tile(yvals[:], (nx, 1)).transpose()
    lon_mids = numpy.array([x0 + i * dx for i in range(nx + 1)])
    lat_mids = numpy.empty([ny + 1])
    lat_mids[0] = 90.
    lat_mids[1:ny] = 0.5 * (yvals[0:ny-1] + yvals[1:ny])
    lat_mids[ny] = -90.
    vert_lats = numpy.empty([ny, nx, 4])
    vert_lats[:, :, 0] = numpy.tile(lat_mids[0:ny], (nx, 1)).transpose()
    vert_lats[:, :, 1] = vert_lats[:, :, 0]
    vert_lats[:, :, 2] = numpy.tile(lat_mids[1:ny + 1], (nx, 1)).transpose()
    vert_lats[:, :, 3] = vert_lats[:, :, 2]
    vert_lons = numpy.empty([ny, nx, 4])
    vert_lons[:, :, 0] = numpy.tile(lon_mids[0:nx], (ny, 1))
    vert_lons[:, :, 3] = vert_lons[:, :, 0]
    vert_lons[:, :, 1] = numpy.tile(lon_mids[1:nx + 1], (ny, 1))
    vert_lons[:, :, 2] = vert_lons[:, :, 1]

    lon_bnd=numpy.stack((lon_mids[:-1],lon_mids[1:]),axis=-1)
    lat_bnd=numpy.stack((lat_mids[:-1],lat_mids[1:]),axis=-1)
    lon_id=cmor.axis(table_entry="longitude", units="degrees_east",
                                    coord_vals=x_vals, cell_bounds=lon_bnd)
    lat_id=cmor.axis(table_entry="latitude", units="degrees_north",
                                    coord_vals=yvals, cell_bounds=lat_bnd)
    #return cmor.grid(axis_ids=[j_index_id, i_index_id], latitude=lat_arr, longitude=lon_arr,latitude_vertices=vert_lats, longitude_vertices=vert_lons)#,
    #return cmor.grid(axis_ids=[lat_id, lon_id], latitude=lat_arr, longitude=lon_arr,latitude_vertices=vert_lats, longitude_vertices=vert_lons)
    return cmor.grid(axis_ids=[lat_id, lon_id], latitude=lat_arr, longitude=lon_arr,latitude_vertices=vert_lats, longitude_vertices=vert_lons)
    #return [lon_id,lat_id]
    
# Surface pressure variable lookup utility
def get_ps_var(ncpath):
    if not ncpath:
        log.error("No path defined for surface pressure (ps).")
        return None
    if not os.path.exists(ncpath):
        log.error("Path does not exist for surface pressure (ps).")
        return None
    ds = None
    try:
        ds = netCDF4.Dataset(ncpath)
        if "ps" in ds.variables:
            return ds.variables["ps"]
        else:
            log.error("Variable ps not present in pressure file.")
            return None
    except Exception as e:
        log.error("Could not read netcdf file %s for surface pressure, reason: %s" % (ncpath, e.message))
        return None

