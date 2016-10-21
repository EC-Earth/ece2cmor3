import os
import re
import math
import numpy
import datetime
import cmor

# Enum utility class
class cmor_enum(tuple): __getattr__=tuple.index

# Grouping to dictionary utility function
def group(objects,func):
    d={}
    for o in objects:
        k=func(o)
        if(k in d):
            d[k].append(o)
        else:
            d[k]=[o]
    return d

# Turns a date or datetime into a datetime
def make_datetime(time):
    if(isinstance(time,datetime.date)):
        return datetime.datetime.combine(time,datetime.datetime.min.time())
    elif(isinstance(time,datetime.datetime)):
        return time
    else:
        raise Exception("Cannot convert object",time,"to datetime")

#TODO: Make more flexible
def make_cmor_frequency(s):
    if(s=="mon" or s=="monClim"):
        return dateutil.relativedelta(month=1)
    elif(s=="day"):
        return dateutil.relativedelta(day=1)
    elif(s=="6hr"):
        return dateutil.relativedelta(hours=6)
    elif(s=="3hr"):
        return dateutil.relativedelta(hours=3)
    else:
        raise Exception("Could not convert argument",s,"to a relative time interval")

# Creates time intervals between start and end with length delta. Last interval may be cut to match end-date.
def make_time_intervals(start,end,delta):
    if(end<start):
        raise Exception("start date later than end date",start,end)
    if(start+delta==start):
        raise Exception("time interval should be positive",delta)
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
        raise Exception("unable to parse time stamp from ifs file name",fname)
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
        raise Exception("unable to parse dates from nemo file name",fname)
    start=datetime.datetime.strptime(regex[0][1:],"%Y%m%d")
    end=datetime.datetime.strptime(regex[1][1:],"%Y%m%d")
    return (start,end)

# Returns the frequency string for a given nemo output file.
def get_nemo_frequency(filepath,expname):
    f=os.path.basename(filepath)
    expr=re.compile("^"+expname+".*_[0-9]{8}_[0-9]{8}_.*.nc$")
    if(not re.match(expr,f)):
        raise Exception("file path",filepath,"does not correspond to nemo output of experiment",expname)
    fstr=f[len(expname)+1:].split("_")[0]
    expr=re.compile("^(\d+)(h|d|m|y)")
    if(not re.match(expr,fstr)):
        raise Exception("file path",filepath,"does not contain a valid frequency indicator")
    n=int(fstr[0:len(fstr)-1])
    if(n==0):
        raise Exception("invalid frequency 0 parsed from file path",filepath)
    return fstr

# Returns the grid for the given file name.
def get_nemo_grid(filepath,expname):
    f=os.path.basename(filepath)
    expr=re.compile("(?<=^"+expname+"_.{2}_[0-9]{8}_[0-9]{8}_).*.nc$")
    result=re.search(expr,f)
    if(not result):
        raise Exception("file path",filepath,"does not contain a grid string")
    match=result.group(0)
    return match[0:len(match)-3]

# TODO: Move to cmorapi, rename as it works for numpy arrays too.
def netcdf2cmor(varid,ncvar,factor = 1.0,psvarid = None,ncpsvar = None):
    times = ncvar.shape[0]
    dims = len(ncvar.shape)
    size = ncvar.size / times
    chunk = int(math.floor(4.0E+9 / (8 * size))) # Use max 4 GB of memory
    for i in range(0,times,chunk):
        imax = min(i + chunk,times)
        vals = None
        if(dims == 3):
            vals = numpy.transpose(ncvar[i:imax,:,:],axes = [1,2,0]) * factor     # Convert to CMOR Fortran-style ordering
        elif(dims == 4):
            vals = numpy.transpose(ncvar[i:imax,:,:,:],axes = [2,3,1,0]) * factor # Convert to CMOR Fortran-style ordering
        else:
            raise Exception("Arrays of dimensions",dims,"are not supported by ece2cmor")
        cmor.write(varid,numpy.asfortranarray(vals),ntimes_passed = (imax-i))
        if(psvarid and ncpsvar):
            spvals = numpy.transpose(ncpsvar[i:imax,:,:],axes = [1,2,0])
            cmor.write(psvarid,numpy.asfortranarray(spvals),ntimes_passed = (imax-i),store_with = varid)
