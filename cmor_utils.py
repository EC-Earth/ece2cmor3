import os
import sys
import re
import math
import numpy
import datetime
import logging
import cmor
import dateutil.relativedelta

# Log object
log = logging.getLogger(__name__)

# Enum utility class
class cmor_enum(tuple): __getattr__ = tuple.index


# Grouping to dictionary utility function
def group(objects,func):
    d = {}
    for o in objects:
        k=func(o)
        if(k in d):
            d[k].append(o)
        else:
            d[k] = [o]
    return d


# Turns a date or datetime into a datetime
def make_datetime(time):
    if(isinstance(time,datetime.date)):
        return datetime.datetime.combine(time,datetime.datetime.min.time())
    elif(isinstance(time,datetime.datetime)):
        return time
    else:
        raise Exception("Cannot convert object",time,"to datetime")


# Creates a time interval from the input string, assuming ec-earth conventions
def make_cmor_frequency(s):
    if(isinstance(s,dateutil.relativedelta.relativedelta) or isinstance(s,datetime.timedelta)):
        return s
    if(isinstance(s,basestring)):
        if(s == "monClim"):
            return dateutil.relativedelta.relativedelta(month=1)
        elif(s.endswith("mon")):
            n = 1 if s == "mon" else int(s[:-3])
            return dateutil.relativedelta.relativedelta(month=n)
        elif(s.endswith("day")):
            n = 1 if s == "day" else int(s[:-3])
            return dateutil.relativedelta.relativedelta(day=n)
        elif(s.endswith("hr")):
            n = 1 if s == "hr" else int(s[:-2])
            return dateutil.relativedelta.relativedelta(hours=n)
    raise Exception("Could not convert argument",s,"to a relative time interval")


# Creates time intervals between start and end with length delta. Last interval may be cut to match end-date.
def make_time_intervals(start,end,delta):
    if(end<start):
        log.warning("Start date %s later than end date %s" % (str(start),str(end)))
        return []
    if(start+delta==start):
        log.warning("Cannot partition time interval into zero-length intervals")
        return []
    result=list()
    istart=start
    while((istart+delta)<end):
        iend=istart+delta
        result.append((istart,iend))
        istart=iend
    result.append((istart,end))
    return result


# Finds all ifs output in the given directory. If expname is given, matches according output files.
def find_ifs_output(path,expname=None):
    subexpr=".*"
    if(expname):
        subexpr=expname
    expr=re.compile("^(ICMGG|ICMSH)"+subexpr+"\+[0-9]{6}$")
    return [os.path.join(path,f) for f in os.listdir(path) if re.match(expr,f)]


# Returns the start date for the given file path
def get_ifs_date(filepath):
    fname=os.path.basename(filepath)
    regex=re.search("\+[0-9]{6}",fname)
    if(not regex):
        log.error("Unable to parse time stamp from ifs file name %s" % fname)
        return None
    ss=regex.group()[1:]
    return datetime.datetime.strptime(ss,"%Y%m").date()


# Finds all nemo output in the given directory. If expname is given, matches according output files.
def find_nemo_output(path,expname=None):
    subexpr='.*'
    if(expname):
        subexpr=expname
    expr=re.compile(subexpr+"_.*_[0-9]{8}_[0-9]{8}_.*.nc$")
    return [os.path.join(path,f) for f in os.listdir(path) if re.match(expr,f)]


# Returns the start and end date corresponding to the given nemo output file.
def get_nemo_interval(filepath):
    fname=os.path.basename(filepath)
    regex=re.findall("_[0-9]{8}",fname)
    if(not regex or len(regex)!=2):
        log.error("Unable to parse dates from nemo file name %s" % fname)
    start=datetime.datetime.strptime(regex[0][1:],"%Y%m%d")
    end=datetime.datetime.strptime(regex[1][1:],"%Y%m%d")
    return (start,end)


# Returns the frequency string for a given nemo output file.
def get_nemo_frequency(filepath,expname):
    f=os.path.basename(filepath)
    expr=re.compile("^"+expname+".*_[0-9]{8}_[0-9]{8}_.*.nc$")
    if(not re.match(expr,f)):
        logger.error("File path %s does not correspond to nemo output of experiment %s" % (filepath,expname))
        return None
    fstr=f[len(expname)+1:].split("_")[0]
    expr=re.compile("^(\d+)(h|d|m|y)")
    if(not re.match(expr,fstr)):
        logger.error("File path %s does not contain a valid frequency indicator" % filepath)
        return None
    n=int(fstr[0:len(fstr)-1])
    if(n==0):
        logger.error("Invalid frequency 0 parsed from file path %s" % filepath)
        return None
    return fstr


# Returns the grid for the given file name.
def get_nemo_grid(filepath,expname):
    f=os.path.basename(filepath)
    expr=re.compile("(?<=^"+expname+"_.{2}_[0-9]{8}_[0-9]{8}_).*.nc$")
    result=re.search(expr,f)
    if(not result):
        logger.error("File path %s does not contain a grid string" % filepath)
        return None
    match=result.group(0)
    return match[0:len(match)-3]


# Writes the ncvar (numpy array or netcdf variable) to CMOR variable with id varid
def netcdf2cmor(varid,ncvar,timdim = 0,factor = 1.0,psvarid = None,ncpsvar = None):
    dims = len(ncvar.shape)
    times = 1 if timdim < 0 else ncvar.shape[timdim]
    size = ncvar.size / times
    chunk = int(math.floor(1.0E+9 / (8 * size))) # Use max 4 GB of memory
    for i in range(0,times,chunk):
        imax = min(i + chunk,times)
        vals = None
        if(dims == 1):
            if(timdim < 0):
                vals = ncvar[:]
            elif(timdim == 0):
                vals = ncvar[i:imax]
        elif(dims == 2):
            if(timdim < 0):
                vals = ncvar[:,:]
            elif(timdim == 0):
                vals = numpy.transpose(ncvar[i:imax,:],axes = [1,0])
            elif(timdim == 1):
                vals = ncvar[:,i:imax]
        elif(dims == 3):
            if(timdim < 0):
                vals = numpy.transpose(ncvar[:,:,:],axes = [1,2,0])
            elif(timdim == 0):
            	vals = numpy.transpose(ncvar[i:imax,:,:],axes = [1,2,0])
            elif(timdim == 2):
                vals = ncvar[:,:,i:imax]
            else:
                log.error("Unsupported array structure with 3 dimensions and time dimension index 1")
                return
        elif(dims == 4):
            if(timdim == 0):
            	vals = numpy.transpose(ncvar[i:imax,:,:,:],axes = [2,3,1,0])
            elif(timdim == 3):
                vals = ncvar[:,:,:,i:imax]
            else:
                log.error("Unsupported array structure with 4 dimensions and time dimension index %d" % timdim)
                return
        else:
            logger.error("Cmorizing arrays of rank %d is not supported" % dims)
            return
        cmor.write(varid,numpy.asfortranarray(factor * vals),ntimes_passed = (0 if timdim < 0 else (imax - i)))
        if(psvarid and ncpsvar):
            if(len(ncpsvar.shape) == 3):
            	spvals = numpy.transpose(ncpsvar[i:imax,:,:],axes = [1,2,0])
            elif(len(ncpsvar.shape) == 4):
            	spvals = numpy.transpose(ncpsvar[i:imax,0,:,:],axes = [1,2,0])
            cmor.write(psvarid,numpy.asfortranarray(spvals),ntimes_passed = (0 if timdim < 0 else (imax - i)),store_with = varid)
