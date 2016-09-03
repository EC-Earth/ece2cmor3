import os
import re

def make_time_intervals(start,end,delta):
    if(end<start):
        raise Exception('start date later than end date',start,end)
    if(start+delta==start):
        raise Exception('time interval should be positive',delta)
    result=list()
    istart=start
    while((istart+delta)<end):
        iend=istart+delta
        result.append((istart,iend))
        istart=iend
    result.append((istart,end))
    return result


def find_ifs_output(path,expname=None):
    subexpr='.*'
    if(expname):
        subexpr=expname
    expr=re.compile('^(ICMGG|ICMSH)'+subexpr+'\+00[0-9]{4}$')
    return [os.path.join(path,f) for f in os.listdir(path) if re.match(expr,f)]


def get_ifs_steps(filepath):
    print "the file path is",filepath
    fname=os.path.basename(filepath)
    regex=re.search('\+00[0-9]{4}',fname)
    if(not regex):
        raise Exception('unable to parse time stamp from file name',fname)
    ss=regex.group()[3:]
    return int(ss)




def find_nemo_output(path,expname=None):
    subexpr=expname
    if(not subexpr):
        subexpr='.*'
    expr=re.compile(subexpr+'_.*_[0-9]{8}_[0-9]{8}_.*.nc')
