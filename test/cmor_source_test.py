import logging
import unittest
from cmor_source import ifs_source,grib_code,nemo_source,nemo_grid
from nose.tools import eq_,ok_

logging.basicConfig(level=logging.DEBUG)

class cmor_source_tests(unittest.TestCase):

    def test_surface_pressure(self):
        code=grib_code(134,128)
        ok_(code in ifs_source.grib_codes_2D_dyn)

    def test_specific_humidity(self):
        code=grib_code(133,128)
        src=ifs_source(code)
        eq_(src.grid(),"spec_grid")
        eq_(src.dims(),3)
        eq_(src.realm(),"atmos")

    def test_snow_depth(self):
        code=grib_code(141,128)
        src=ifs_source(code)
        eq_(src.grid(),"pos_grid")
        eq_(src.dims(),2)

    def test_create_from_ints(self):
        src=ifs_source.create(133,128)
        eq_(src.get_grib_code(),grib_code(133,128))

    def test_create_from_string(self):
        src=ifs_source.read("133.128")
        eq_(src.get_grib_code(),grib_code(133,128))

    def test_create_nemo_source(self):
        src=nemo_source("tos",nemo_grid.T)
        eq_(src.grid(),"gridT")
        eq_(src.dims(),2)
        eq_(src.realm(),"ocean")
