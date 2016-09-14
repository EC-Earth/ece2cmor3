import os
import re
import numpy
import netCDF4
import datetime
import dateutil
import cmor_source

class nemo_output_factory(object):

    def __init__(self):
        self.lons=None
        self.lats=None
        self.gridtype=None
        self.startdate=None
        self.enddate=None
        self.frequency=None


    def make_grid(self,nlons_,nlats_,gridtype_):
        self.lons=numpy.fromfunction(lambda i,j:(i*360+0.5)/((nlons_+nlats_-j)+2),(nlons_,nlats_),dtype=numpy.float64)
        self.lats=numpy.fromfunction(lambda i,j:(j*180+0.5)/((nlats_+nlons_-i)+2)-90,(nlons_,nlats_),dtype=numpy.float64)
        if(gridtype_ < len(cmor_source.nemo_grid)):
            self.gridtype=cmor_source.nemo_grid[gridtype_]
        else:
            raise Exception("Unknown grid type: ",gridtype_)


    def set_timeframe(self,startdate_,enddate_,frequency_):
        self.startdate=startdate_
        self.enddate=enddate_
        expr=re.compile("^[1-9](h|d|m|y)$")
        if(re.match(expr,frequency_)):
            self.frequency=frequency_
        else:
            raise Exception("Invalid frequency argument given: ",frequency_)


    def get_path(self,dir_,prefix_):
        joinchar='_'
        startstr=self.startdate.strftime("%Y%m%d")
        stopstr=self.enddate.strftime("%Y%m%d")
        filename=joinchar.join([prefix_,startstr,stopstr,self.frequency,self.gridtype])+".nc"
        return os.path.join(dir_,filename)


    def get_times(self,reftim):
        fnum=int(self.frequency[0])
        funit=self.frequency[1]
        period=None
#        unit=None
        if(funit=='h'):
            period=dateutil.relativedelta.relativedelta(hours=+fnum)
#            unit="hours since "+str(reftim)
        elif(funit=='d'):
            period=dateutil.relativedelta.relativedelta(days=+fnum)
#            unit="days since "+str(reftim)
        elif(funit=='m'):
            period=dateutil.relativedelta.relativedelta(months=+fnum)
#            unit="months since "+str(reftim)
        elif(funit=='y'):
            period=dateutil.relativedelta.relativedelta(years=+fnum)
#            unit="years since "+str(reftim)
        else:
            raise Exception("Unknown period: ",period)
        d=datetime.datetime.combine(self.startdate,datetime.time())
        dstop=datetime.datetime.combine(self.enddate,datetime.time())
        tims=[]
        while(d<dstop):
            tims.append(d)
            d=d+period
        return tims


    def write_variables(self,path_,prefix_,vardict_={}):

        filepath=self.get_path(path_,prefix_)
        root=netCDF4.Dataset(filepath,"w")
        dimi=root.createDimension("i_index",self.lons.shape[0])
        dimj=root.createDimension("j_index",self.lons.shape[1])
        tims=self.get_times(self.startdate)
        dimt=root.createDimension("time_counter",len(tims))
        vartim=root.createVariable("time","f8",("time_counter",))
        vartim.units="hours since 1850-01-01 00:00:00.0"
        vartim.calendar="proleptic_gregorian"
        varlon=root.createVariable("nav_lon","f8",("i_index","j_index",))
        varlat=root.createVariable("nav_lat","f8",("i_index","j_index",))
        vartim[:]=netCDF4.date2num(tims,units=vartim.units,calendar=vartim.calendar)
        varlon[:,:]=self.lons
        varlat[:,:]=self.lats
        for k,v in vardict_.iteritems():
            var=root.createVariable(k,"f8",("time_counter","i_index","j_index",))
            var[:,:,:]=numpy.fromfunction(numpy.vectorize(v),(len(tims),self.lons.shape[0],self.lons.shape[1]),dtype=numpy.float64)
        root.close()
