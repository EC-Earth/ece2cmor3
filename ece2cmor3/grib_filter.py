import logging
import gribapi
import cmor_utils

gridpoint_file = None
prev_gridpoint_file = None
spectral_file = None
prev_spectral_file = None
temp_dir = None
grib_vars = {}

# Initializes the module, looks up previous month files and inspects the first
# day in the input files to set up an administration of the fields.
def initialize(gpfile,shfile,tmpdir):
    global gridpoint_file,prev_gridpoint_file,spectral_file,prev_spectral_file,temp_dir,grib_vars
    gridpoint_file = gpfile
    spectral_file = shfile
    temp_dir = tmpdir
    prev_gridpoint_file,prev_spectral_file = get_prev_files(gridpoint_file)
    if(not prev_spectral_file or not prev_gridpoint_file):
        return False
    grib_vars.update(inspect_day(gpfile))
    grib_vars.update(inspect_day(shfile))

# Utility to make grib tuple of codes from string
def make_grib_tuple(s):
    codes = s.split('.')
    return int(codes[0]),int(codes[1])

# Inspects the first 24 hours in the input gridpoint and spectral files.
def inspect_day(gribfile):
    inidate,initime = -99,-1.
    records = {}
    while True:
        gid = gribapi.grib_new_from_file(gribfile)
        if(not gid): break
        date = gribapi.grib_get(gid,"dataDate",int)
        time = gribapi.grib_get(gid,"dataTime",int)/100.
        if(date == inidate + 1 and time == initime): break
        if(inidate < 0): inidate = date
        if(initime < 0.): initime = time
        codevar,codetab = make_grib_tuple(gribapi.grib_get(gid,"paramId",str))
        levtype = gribapi.grib_get(gid,"indicatorOfTypeOfLevel",int)
        level = gribapi.grib_get(gid,"level")
        key = (codevar,codetab,levtype,level)
        if(key in records):
            records[key].append(time)
        else:
            records[key] = [time]
    for key,val in records:
        hrs = numpy.array(val)
        frqs = 24. if len(hrs) == 1 else numpy.mod(hrs[1:] - hrs[:-1],numpy.repeat(24,len(hrs)))
        frq = frqs[0]
        if(any(frqs != frq)):
            log.error("Variable %d.%d on level %d or type %s is not output on regular "
            "intervals in first day in file %s" % (key[0],key[1],key[3],key[2],gribfile))
            records.pop(key,None)
        else:
            records[key] = frq
    return records

# Searches the file system for the previous month file, necessary for the 0-hour
# fields.
def get_prev_files(gpfile):
    log.info("Searching for previous month file of %s" % gpfile)
    date = cmor_utils.get_ifs_date(gpfile)
    prevdate = date - dateutil.relativedelta(month = 1)
    ifsoutputdir = os.path.abspath(os.path.join(os.path.dirname(gridpoint_file),".."))
    expname = os.path.basename(gpfile)[5:9]
    inigpfile,inishfile = None,None
    prevgpfiles,prevshfiles = [],[]
    for f in cmor_utils.find_ifs_output(ifsoutputdir,exp = expname):
        if(f.endswith("+000000")):
            if(os.path.basename(f).startswith("ICMGG")): inigpfile = f
            if(os.path.basename(f).startswith("ICMSH")): inishfile = f
        elif(cmor_utils.get_ifs_date(f) == prevdate):
            if(os.path.basename(f).startswith("ICMGG")): prevgpfiles.append(f)
            if(os.path.basename(f).startswith("ICMSH")): prevshfiles.append(f)
    if(not any(prevgpfiles) or not any(prevshfiles)):
        log.info("No regular previous month files found, taking initial state files...")
        if(not inigpfile):
            log.error("No initial gridpoint file found in %s" % ifsoutputdir)
        if(not inishfile):
            log.error("No initial spectral file found in %s" % ifsoutputdir)
        return inigpfile,inishfile
    if(len(prevgpfiles) > 1):
        log.warning("Multiple previous month gridpoint files found: %s. Taking first match" % ",".join(prevgpfiles))
    if(len(prevshfiles) > 1):
        log.warning("Multiple previous month spectral files found: %s. Taking first match" % ",".join(prevshfiles))
    return prevgpfiles[0],prevshfiles[0]

# Splits the grib file for the given set of tasks
def execute(tasks):
    validtasks = validate_tasks(tasks)
    return True

# Checks tasks that are compatible with the variables listed in grib_vars and
# returns those that are compatible.
def validate_tasks(tasks):
    return tasks
