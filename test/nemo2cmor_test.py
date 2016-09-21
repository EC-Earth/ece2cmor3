import logging
import unittest
import os
import numpy
import math
import datetime
import nose.tools
import nemo2cmor
import test_utils
import cmor_source
import cmor_target
import cmor_task
import shutil
import cmor

logging.basicConfig(level=logging.DEBUG)

def circwave(t,j,i):
    return 15*math.cos((i*i+j*j)/1000.+0.1*t)

def circwave3d(t,z,j,i):
    return 15*math.cos((i*i+j*j)/1000.+0.1*t)*(z/12)

def hypwave(t,j,i):
    return 0.001*math.sin((i*i-j*j)/1000.+0.1*t)

def datapath():
    return os.path.join(os.path.dirname(__file__),"test_data","nemodata")

def set_up():

    cmordir=os.path.join(os.getcwd(),"tmp")
    if(os.path.exists(cmordir)):
        shutil.rmtree(cmordir)
    datadir=datapath()
    if(os.path.exists(datadir)):
        shutil.rmtree(datadir)

    dimx=65
    dimy=75
    dimz=10

    dirname=datapath()
    os.mkdir(dirname)

    opf=test_utils.nemo_output_factory()

    opf.make_grid(dimx,dimy,cmor_source.nemo_grid.grid_U,dimz)
    opf.set_timeframe(datetime.date(1990,1,1),datetime.date(1991,1,1),"1d")
    uto={"name":"uto",
    "dims":2,
    "function":circwave,
    "standard_name":"temperature_transport_x",
    "long_name":"Product of x-ward sea water velocity and temperature",
    "units":"m degC s-1"}
    uso={"name":"uso",
    "dims":2,
    "function":hypwave,
    "standard_name":"salinity_transport_x",
    "long_name":"Product of x-ward sea water velocity and salinity",
    "units":"kg m-2 s-1"}
    opf.write_variables(dirname,"exp",[uto,uso])

    opf.make_grid(dimx,dimy,cmor_source.nemo_grid.grid_V,dimz)
    opf.set_timeframe(datetime.date(1990,1,1),datetime.date(1991,1,1),"1d")
    vto={"name":"vto",
    "dims":2,
    "function":circwave,
    "standard_name":"temperature_transport_y",
    "long_name":"Product of y-ward sea water velocity and temperature",
    "units":"m degC s-1"}
    vso={"name":"vso",
    "dims":2,
    "function":hypwave,
    "standard_name":"salinity_transport_y",
    "long_name":"Product of y-ward sea water velocity and salinity",
    "units":"kg m-2 s-1"}
    opf.write_variables(dirname,"exp",[vto,vso])

    opf.make_grid(dimx,dimy,cmor_source.nemo_grid.grid_T,dimz)
    opf.set_timeframe(datetime.date(1990,1,1),datetime.date(1991,1,1),"1m")
    tos={"name":"tos",
    "dims":2,
    "function":circwave,
    "standard_name":"sea_surface_temperature",
    "long_name":"Sea surface temperature",
    "units":"degC"}
    to={ "name":"to",
    "dims":3,
    "function":circwave3d,
    "standard_name":"sea_water_temperature",
    "long_name":"Sea water temperature",
    "units":"degC"}
    sos={"name":"sos",
    "dims":2,
    "function":hypwave,
    "standard_name":"sea_surface_salinity",
    "long_name":"Sea surface salinity",
    "units":"kg m-3"}
    opf.write_variables(dirname,"exp",[tos,to,sos])

    opf.make_grid(dimx,dimy,cmor_source.nemo_grid.icemod)
    opf.set_timeframe(datetime.date(1990,1,1),datetime.date(1991,1,1),"6h")
    sit={"name":"sit","dims":2,"function":circwave,"standard_name":"sea_ice_temperature","long_name":"Sea ice temperature","units":"degC"}
    opf.write_variables(dirname,"exp",[sit])


class nemo2cmor_tests(unittest.TestCase):

    set_up()

    def test_create_grid(self):
        dim=1000
        lons=numpy.zeros([dim,dim],dtype=numpy.float64)
        lons=numpy.fromfunction(lambda i,j:(i*360+0.5)/(0.5*(dim+j)+2),(dim,dim),dtype=numpy.float64)
        lats=numpy.fromfunction(lambda i,j:(j*180+0.5)/(0.5*(dim+i)+2)-90,(dim,dim),dtype=numpy.float64)

        grid=nemo2cmor.nemogrid(lons,lats)

        p1=(grid.vertex_lons[0,0,0],grid.vertex_lats[0,0,0])
        p2=(grid.vertex_lons[0,0,1],grid.vertex_lats[0,0,1])
        p3=(grid.vertex_lons[0,0,2],grid.vertex_lats[0,0,2])
        p4=(grid.vertex_lons[0,0,3],grid.vertex_lats[0,0,3])

#        nose.tools.eq_(p1[0],p4[0])
        nose.tools.eq_(p2[0],p3[0])
        nose.tools.eq_(p1[1],p2[1])
        nose.tools.eq_(p3[1],p4[1])

    def test_init_nemo2cmor(self):
        dirname=datapath()
        tabdir=os.path.abspath(os.path.dirname(nemo2cmor.__file__)+"/../../input/cmip6/cmip6-cmor-tables/Tables")
        confpath=os.path.join(os.path.dirname(__file__),"test_data","cmor3_metadata.json")
        cmor.setup(tabdir)
        cmor.dataset_json(confpath)
        nemo2cmor.initialize(dirname,"exp",os.path.join(tabdir,"CMIP6"),datetime.datetime(1990,3,1),datetime.timedelta(days=100))
        nemo2cmor.finalize()
        cmor.close()

    def test_cmor_single_task(self):
        dirname=datapath()
        tabdir=os.path.abspath(os.path.dirname(nemo2cmor.__file__)+"/../../input/cmip6/cmip6-cmor-tables/Tables")
        confpath=os.path.join(os.path.dirname(__file__),"test_data","cmor3_metadata.json")
        cmor.setup(tabdir)
        cmor.dataset_json(confpath)
        nemo2cmor.initialize(dirname,"exp",os.path.join(tabdir,"CMIP6"),datetime.datetime(1990,3,1),datetime.timedelta(days=365))
        src=cmor_source.nemo_source("tos",cmor_source.nemo_grid.grid_T)
        tgt=cmor_target.cmor_target("tos","Omon")
        setattr(tgt,"frequency","mon")
        tsk=cmor_task.cmor_task(src,tgt)
        nemo2cmor.execute([tsk])
        nemo2cmor.finalize()
        cmor.close()

    def test_cmor_single_task3d(self):
        dirname=datapath()
        tabdir=os.path.abspath(os.path.dirname(nemo2cmor.__file__)+"/../../input/cmip6/cmip6-cmor-tables/Tables")
        confpath=os.path.join(os.path.dirname(__file__),"test_data","cmor3_metadata.json")
        cmor.setup(tabdir)
        cmor.dataset_json(confpath)
        nemo2cmor.initialize(dirname,"exp",os.path.join(tabdir,"CMIP6"),datetime.datetime(1990,3,1),datetime.timedelta(days=365))
        src=cmor_source.nemo_source("to",cmor_source.nemo_grid.grid_T,3)
        tgt=cmor_target.cmor_target("thetao","Omon")
        setattr(tgt,"frequency","mon")
        tsk=cmor_task.cmor_task(src,tgt)
        nemo2cmor.execute([tsk])
        nemo2cmor.finalize()
        cmor.close()
