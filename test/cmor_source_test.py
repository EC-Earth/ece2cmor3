import logging
import unittest
from nose.tools import eq_,ok_
from testfixtures import LogCapture
from ece2cmor3.cmor_source import ifs_source, grib_code, nemo_source, nemo_grid

logging.basicConfig(level=logging.DEBUG)

class cmor_source_tests(unittest.TestCase):

    def test_default_ifs_source(self):
        src = ifs_source(None)
        eq_(src.grid(),None)
        eq_(src.get_grib_code(),None)
        eq_(src.get_root_codes(),[])

    def test_surface_pressure(self):
        code=grib_code(134,128)
        ok_(code in ifs_source.grib_codes_2D_dyn)

    def test_specific_humidity(self):
        code=grib_code(135,128)
        src=ifs_source(code)
        eq_(src.grid(),"spec")
        eq_(src.dims(),3)

    def test_snow_depth(self):
        code=grib_code(141,128)
        src=ifs_source(code)
        eq_(src.grid(),"point")
        eq_(src.dims(),2)

    def test_create_from_ints(self):
        src=ifs_source.create(133,128)
        eq_(src.get_grib_code(),grib_code(133,128))

    def test_invalid_codes(self):
        with LogCapture() as logc:
            src=ifs_source.create(88,128)
            ok_("cmor_source ERROR" in str(logc))

    def test_create_from_string(self):
        src=ifs_source.read("133.128")
        eq_(src.get_grib_code(),grib_code(133,128))

    def test_create_from_expr(self):
        expr="var88=sqrt(sq(var165)+sq(var166))"
        src=ifs_source.read(expr)
        eq_(src.get_grib_code(),grib_code(88,128))
        eq_(src.get_root_codes(),[grib_code(165,128),grib_code(166,128)])
        eq_(getattr(src,"expr"),expr)
        eq_(src.grid(),"point")
        eq_(src.spatial_dims,2)

    def test_invalid_expression1(self):
        with LogCapture() as logc:
            expr="var141=sqrt(sq(var165)+sq(var166))"
            src=ifs_source.read(expr)
            ok_("cmor_source ERROR" in str(logc))

    def test_invalid_expression2(self):
        with LogCapture() as logc:
            expr="var89=sqrt(sq(var88)+sq(var166))"
            src=ifs_source.read(expr)
            ok_("cmor_source ERROR" in str(logc))

    def test_create_nemo_source(self):
        src=nemo_source("tos",nemo_grid.grid_T)
        eq_(src.grid(),"grid_T")
        eq_(src.dims(),-1)
