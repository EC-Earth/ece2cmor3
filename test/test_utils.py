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
        self.depthaxis=None
        self.layers=0


    def make_grid(self,nlons_,nlats_,gridtype_,nlayers=0):
        self.lons=numpy.fromfunction(lambda i,j:(i*360+0.5)/((nlons_+nlats_-j)+2),(nlons_,nlats_),dtype=numpy.float64)
        self.lats=numpy.fromfunction(lambda i,j:(j*180+0.5)/((nlats_+nlons_-i)+2)-90,(nlons_,nlats_),dtype=numpy.float64)
        if(gridtype_ < len(cmor_source.nemo_grid)):
            self.gridtype=cmor_source.nemo_grid[gridtype_]
            self.depthaxis=cmor_source.nemo_depth_axes.get(gridtype_,None)
            self.layers=nlayers
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
        filename=joinchar.join([prefix_,self.frequency,startstr,stopstr,self.gridtype])+".nc"
        return os.path.join(dir_,filename)


    def get_times(self,reftim):
        fnum=int(self.frequency[0])
        funit=self.frequency[1]
        period=None
        if(funit=='h'):
            period=dateutil.relativedelta.relativedelta(hours=+fnum)
        elif(funit=='d'):
            period=dateutil.relativedelta.relativedelta(days=+fnum)
        elif(funit=='m'):
            period=dateutil.relativedelta.relativedelta(months=+fnum)
        elif(funit=='y'):
            period=dateutil.relativedelta.relativedelta(years=+fnum)
        else:
            raise Exception("Unknown period: ",period)
        d=datetime.datetime.combine(self.startdate,datetime.time())
        dstop=datetime.datetime.combine(self.enddate,datetime.time())
        tims=[]
        while(d<dstop):
            tims.append(d)
            d=d+period
        return tims


    def write_variables(self,path_,prefix_,vars_={}):

        filepath=self.get_path(path_,prefix_)
        root=netCDF4.Dataset(filepath,"w")

        dimt=root.createDimension("time_counter")
        dimi=root.createDimension("y",self.lons.shape[0])
        dimj=root.createDimension("x",self.lons.shape[1])
        tbnddim=root.createDimension("axis_nbounds",2)
        tims=self.get_times(self.startdate)

        z=None
        if(self.depthaxis and self.layers):
            z="depth"+self.depthaxis
            dimz=root.createDimension(z,self.layers)

        varlat=root.createVariable("nav_lat","f8",("y","x",))
        varlat.standard_name="latitude"
        varlat.long_name="Latitude"
        varlat.units="degrees north"
        varlat.nav_model=self.gridtype
        varlat[:,:]=self.lats

        varlon=root.createVariable("nav_lon","f8",("y","x",))
        varlon.standard_name="longitude"
        varlon.long_name="Longitude"
        varlon.units="degrees east"
        varlon.nav_model=self.gridtype
        varlon[:,:]=self.lons

        if(z):
            varz=root.createVariable(z,"f8",(z,))
            varz.long_name="Vertical "+self.depthaxis.upper()+" levels"
            varz.units="m"
            varz.positive="down"
            varz.bounds=z+"_bounds"
            maxdepth=6000.
            nz=self.layers
            step=maxdepth/nz
            zarray=numpy.arange(0.1*step,maxdepth,step)
            varz[:]=zarray

            varzbnd=root.createVariable(z+"_bounds","f8",(z,"axis_nbounds",))
            toparray=numpy.zeros(nz)
            botarray=numpy.zeros(nz)
            for i in range(0,nz-1):
                mid=0.5*(zarray[i]+zarray[i+1])
                toparray[i+1]=mid
                botarray[i]=mid
            botarray[nz-1]=zarray[nz-1]+0.5*(zarray[nz-1]-zarray[nz-2])
            varzbnd[:,0]=toparray
            varzbnd[:,1]=botarray


        vartimc=root.createVariable("time_centered","f8",("time_counter",))
        vartimc.standard_name="time"
        vartimc.long_name="Time axis"
        vartimc.calendar="gregorian"
        vartimc.origin="1950-01-01 00:00:00.0"
        vartimc.units="seconds since "+vartimc.origin
        vartimc.bounds="time_centered_bounds"

        vartim=root.createVariable("time_counter","f8",("time_counter",))
        vartim.axis="T"
        vartim.standard_name="time"
        vartim.long_name="Time axis"
        vartim.calendar="gregorian"
        vartim.origin="1950-01-01 00:00:00.0"
        vartim.units="seconds since "+vartim.origin
        vartim.bounds="time_counter_bounds"

        vartimcbnd=root.createVariable("time_centered_bounds","f8",("time_counter","axis_nbounds",))
        vartimbnd=root.createVariable("time_counter_bounds","f8",("time_counter","axis_nbounds",))

        timarray=netCDF4.date2num(tims,units=vartimc.units,calendar=vartimc.calendar)
        vartim[:]=timarray
        vartimc[:]=timarray

        n=len(timarray)
        bndlarray=numpy.zeros(n)
        bndrarray=numpy.zeros(n)
        bndlarray[0]=timarray[0]-0.5*(timarray[1]-timarray[0])
        for i in range(0,n-1):
            mid=0.5*(timarray[i]+timarray[i+1])
            bndlarray[i+1]=mid
            bndrarray[i]=mid
        bndrarray[n-1]=timarray[n-1]+0.5*(timarray[n-1]-timarray[n-2])
        vartimbnd[:,0]=bndlarray
        vartimbnd[:,1]=bndrarray
        vartimcbnd[:,0]=bndlarray
        vartimcbnd[:,1]=bndrarray

        for v in vars_:
            var=None
            atts=v.copy()
            name = atts.pop("name")
            dims = atts.pop("dims")
            func = atts.pop("function")
            if(name):
                if(dims==2):
                    var=root.createVariable(name,"f8",("time_counter","y","x",))
                elif(dims==3):
                    var=root.createVariable(name,"f8",("time_counter",z,"y","x",))
                else:
                    raise Exception("Writing a variable with ",dims,"dimensions is not supported")
            else:
                raise Exception("Variable must have a name to be included in netcdf file")
            for k in atts:
                setattr(var,k,atts[k])
            if(func):
                if(dims==2):
                    var[:,:,:]=numpy.fromfunction(numpy.vectorize(func),(len(tims),self.lons.shape[1],self.lons.shape[0]),dtype=numpy.float64)
                elif(dims==3):
                    var[:,:,:,:]=numpy.fromfunction(numpy.vectorize(func),(len(tims),self.layers,self.lons.shape[1],self.lons.shape[0]),dtype=numpy.float64)
                else:
                    raise Exception("Variables with dimensions ",d," are not supported")
            else:
                if(dims==2):
                    var[:,:,:]=numpy.zeros(len(tims),self.lons.shape[1],self.lons.shape[0],dtype=numpy.float64)
                elif(dims==3):
                    var[:,:,:,:]=numpy.zeros(len(tims),self.layers,self.lons.shape[1],self.lons.shape[0],dtype=numpy.float64)
                else:
                    raise Exception("Variables with dimensions ",d," are not supported")
        root.close()
