import os
import re
import datetime

# Enum utility class
class cmor_enum(tuple): __getattr__=tuple.index

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
