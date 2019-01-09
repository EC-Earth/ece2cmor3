import logging
import unittest
from nose.tools import eq_, ok_
from testfixtures import LogCapture

from ece2cmor3.cmor_source import ifs_source, netcdf_source, grib_code

logging.basicConfig(level=logging.DEBUG)


class cmor_source_tests(unittest.TestCase):

    @staticmethod
    def test_default_ifs_source():
        src = ifs_source(None)
        eq_(src.grid(), None)
        eq_(src.get_grib_code(), None)
        eq_(src.get_root_codes(), [])

    @staticmethod
    def test_surface_pressure():
        code = grib_code(134, 128)
        ok_(code in ifs_source.grib_codes_2D_dyn)

    @staticmethod
    def test_specific_humidity():
        code = grib_code(135, 128)
        src = ifs_source(code)
        eq_(src.grid(), "spec")
        eq_(src.spatial_dims, 3)

    @staticmethod
    def test_snow_depth():
        code = grib_code(141, 128)
        src = ifs_source(code)
        eq_(src.grid(), "point")
        eq_(src.spatial_dims, 2)

    @staticmethod
    def test_create_from_ints():
        src = ifs_source.create(133, 128)
        eq_(src.get_grib_code(), grib_code(133, 128))

    @staticmethod
    def test_create_from_string():
        src = ifs_source.read("133.128")
        eq_(src.get_grib_code(), grib_code(133, 128))

    @staticmethod
    def test_create_from_short_string():
        src = ifs_source.read("133")
        eq_(src.get_grib_code(), grib_code(133, 128))

    @staticmethod
    def test_create_from_var_string():
        src = ifs_source.read("var133")
        eq_(src.get_grib_code(), grib_code(133, 128))

    @staticmethod
    def test_create_from_expr():
        src = ifs_source.read("88.128", "sqrt(sq(var165)+sq(var166))")
        eq_(src.get_grib_code(), grib_code(88, 128))
        eq_(src.get_root_codes(), [grib_code(165, 128), grib_code(166, 128)])
        eq_(getattr(src, "expr"), "var88=sqrt(sq(var165)+sq(var166))")
        eq_(src.grid(), "point")
        eq_(src.spatial_dims, 2)

    @staticmethod
    def test_create_from_expr2():
        src = ifs_source.read("var88", "sqrt(sq(var131)+sq(var132))")
        eq_(src.get_grib_code(), grib_code(88, 128))
        eq_(src.get_root_codes(), [grib_code(131, 128), grib_code(132, 128)])
        eq_(getattr(src, "expr"), "var88=sqrt(sq(var131)+sq(var132))")
        eq_(src.grid(), "spec")
        eq_(src.spatial_dims, 3)

    @staticmethod
    def test_create_from_expr3():
        src = ifs_source.read("var88", "sqrt(sq(var128131)+sq(var128132))")
        eq_(src.get_grib_code(), grib_code(88, 128))
        eq_(src.get_root_codes(), [grib_code(131, 128), grib_code(132, 128)])
        eq_(getattr(src, "expr"), "var88=sqrt(sq(var131)+sq(var132))")
        eq_(src.grid(), "spec")
        eq_(src.spatial_dims, 3)

    @staticmethod
    def test_create_from_expr4():
        src = ifs_source.read("var129124", "var126094 + var126099 + var126106 + var126110")
        eq_(src.get_grib_code(), grib_code(124, 129))
        eq_(src.get_root_codes(), [grib_code(94, 126), grib_code(99, 126), grib_code(106, 126), grib_code(110, 126)])
        eq_(getattr(src, "expr"), "var124=var94 + var99 + var106 + var110")
        eq_(src.grid(), "point")
        eq_(src.spatial_dims, 3)

    @staticmethod
    def test_invalid_expression1():
        with LogCapture() as logc:
            src = ifs_source.read("141.128", "sqrt(sq(var165)+sq(var166))")
            ok_("cmor_source ERROR" in str(logc))

    @staticmethod
    def test_invalid_expression2():
        with LogCapture() as logc:
            src = ifs_source.read("89.128", "sqrt(sq(var88)+sq(var166))")
            ok_("cmor_source ERROR" in str(logc))

    @staticmethod
    def test_create_netcdf_source():
        src = netcdf_source("tos", "nemo")
        eq_(src.variable(), "tos")
        eq_(src.model_component(), "nemo")
