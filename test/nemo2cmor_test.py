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

logging.basicConfig(level=logging.DEBUG)

def circwave(t,i,j):
    print i
    return math.cos((i*i+j*j)/10000.0 + t/2.)

class nemo2cmor_tests(unittest.TestCase):

    def test_create_grid(self):
        dim=1000
        lons=numpy.zeros([dim,dim],dtype=numpy.float64)
        lons=numpy.fromfunction(lambda i,j:(i*360+0.5)/(0.5*(dim+j)+2),(dim,dim),dtype=numpy.float64)
        lats=numpy.fromfunction(lambda i,j:(j*180+0.5)/(0.5*(dim+i)+2)-90,(dim,dim),dtype=numpy.float64)

        grid=nemo2cmor.nemogrid(lons,lats)

        p1=(grid.vertex_lons[0,0,0],grid.vertex_lats[0,0,0])
        p2=(grid.vertex_lons[1,0,0],grid.vertex_lats[1,0,0])
        p3=(grid.vertex_lons[2,0,0],grid.vertex_lats[2,0,0])
        p4=(grid.vertex_lons[3,0,0],grid.vertex_lats[3,0,0])

        nose.tools.eq_(p1[0],p4[0])
        nose.tools.eq_(p2[0],p3[0])
        nose.tools.eq_(p1[1],p2[1])
        nose.tools.eq_(p3[1],p4[1])

    def test_write_nc(self):
        dim=100
        opf=test_utils.nemo_output_factory()
        opf.make_grid(75,85,cmor_source.nemo_grid.gridT)
        opf.set_timeframe(datetime.date(1990,1,1),datetime.date(1991,1,1),"1m")
        opf.write_variables(os.path.dirname(__file__),"exp",{"tos":circwave})
