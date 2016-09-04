import logging
import unittest
from cmor_source import ifs_source,grib_code
from nose.tools import eq_,ok_

logging.basicConfig(level=logging.DEBUG)

class cmor_source_tests(unittest.TestCase):

    def test_surface_pressure(self):
        code=grib_code(134,128)
        ok_(code in ifs_source.grib_codes_2D_dyn)

    def test_specific_humidity(self):
        code=grib_code(133,128)
        src=ifs_source(code)
        eq_(src.grid,"spec_grid")
        eq_(src.dims,3)

    def test_snow_depth(self):
        code=grib_code(141,128)
        src=ifs_source(code)
        eq_(src.grid,"pos_grid")
        eq_(src.dims,2)
