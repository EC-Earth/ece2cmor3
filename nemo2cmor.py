import netCDF4
import cmor_utils

def read_calendar(ncfile):
    ds=netCDF4.DataSet(ncfile,'r')
    timvar=ds.dimensions["time_counter"]
    if(timvar):
        return getattr(timvar,"calendar")
    else:
        return None



def select_files(path,expname,start,length):
    allfiles=cmor_utils.get_nemo_output(path,expname)
    return [f in allfiles if cmor_utils.get_nemo_interval(f)[0]>=start and cmor_utils.get_nemo_interval(f)[1]<=(start+length)]


def execute(tasks,path,expname,start,length):
    files=select_files(path,expname,start,length)
    cal=None
    for f in files:
        cal=read_calendar(f)
        if(cal): break
    if(cal): cmor.set_cur_dataset_attribute("calendar",cal)
    nemo_grids=read_grids(files)
