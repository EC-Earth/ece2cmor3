import logging
import unittest
import os
import numpy
from nose.tools import eq_,ok_,raises
import nemo2cmor

logging.basicConfig(level=logging.DEBUG)

class nemo2cmor_tests(unittest.TestCase):

    def test_create_grid(self):
        dim=1000
        lons=numpy.zeros([dim,dim],dtype=numpy.float64)
        lats=numpy.zeros([dim,dim],dtype=numpy.float64)
        for i in range(dim):
            lons[i,:]=(i*360+0.5)/(dim+2)
            lats[:,i]=(i*180+0.5)/(dim+2)-90

        grid=nemo2cmor.nemogrid(lons,lats)

        p1=(grid.vertex_lons[0,0,0],grid.vertex_lats[0,0,0])
        p2=(grid.vertex_lons[1,0,0],grid.vertex_lats[1,0,0])
        p3=(grid.vertex_lons[2,0,0],grid.vertex_lats[2,0,0])
        p4=(grid.vertex_lons[3,0,0],grid.vertex_lats[3,0,0])

        eq_(p1[0],p4[0])
        eq_(p2[0],p3[0])
        eq_(p1[1],p2[1])
        eq_(p3[1],p4[1])
