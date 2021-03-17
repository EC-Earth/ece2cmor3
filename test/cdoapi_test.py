import logging
import unittest
from ece2cmor3 import cdoapi

logging.basicConfig(level=logging.DEBUG)


class cdoapi_tests(unittest.TestCase):

    @staticmethod
    def test_select_code():
        command = cdoapi.cdo_command(130)
        commstr = command.create_command()
        assert commstr == "-selcode,130"

    @staticmethod
    def test_select_codes():
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.select_code_operator, 131, 132)
        commstr = command.create_command()
        assert commstr == "-selcode,130,131,132"

    @staticmethod
    def test_add_specmapping():
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.spectral_operator)
        commstr = command.create_command()
        assert commstr == "-sp2gpl -selcode,130"

    @staticmethod
    def test_add_gridmapping():
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.gridtype_operator, cdoapi.cdo_command.regular_grid_type)
        commstr = command.create_command()
        assert commstr == "-setgridtype,regular -selcode,130"

    @staticmethod
    def test_add_sellevel():
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.select_z_operator, cdoapi.cdo_command.pressure)
        command.add_operator(cdoapi.cdo_command.gridtype_operator, cdoapi.cdo_command.regular_grid_type)
        command.add_operator(cdoapi.cdo_command.select_lev_operator, 500, 350, 10)
        commstr = command.create_command()
        assert commstr == "-setgridtype,regular -sellevel,500,350,10 -selzaxis,pressure -selcode,130"

    @staticmethod
    def test_add_monmean():
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.month + cdoapi.cdo_command.mean)
        command.add_operator(cdoapi.cdo_command.select_z_operator, cdoapi.cdo_command.pressure)
        command.add_operator(cdoapi.cdo_command.gridtype_operator, cdoapi.cdo_command.regular_grid_type)
        command.add_operator(cdoapi.cdo_command.select_lev_operator, 500, 350, 10)
        commstr = command.create_command()
        assert commstr == "-setgridtype,regular -monmean -sellevel,500,350,10 -selzaxis,pressure -selcode,130"

    @staticmethod
    def test_add_daymax():
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.month + cdoapi.cdo_command.mean)
        command.add_operator(cdoapi.cdo_command.day + cdoapi.cdo_command.max)
        command.add_operator(cdoapi.cdo_command.select_z_operator, cdoapi.cdo_command.pressure)
        command.add_operator(cdoapi.cdo_command.gridtype_operator, cdoapi.cdo_command.regular_grid_type)
        command.add_operator(cdoapi.cdo_command.select_lev_operator, 500, 350, 10)
        commstr = command.create_command()
        assert commstr == "-monmean -daymax -setgridtype,regular -sellevel,500,350,10 -selzaxis,pressure -selcode,130"

    @staticmethod
    def test_add_daymin():
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.year + cdoapi.cdo_command.mean)
        command.add_operator(cdoapi.cdo_command.day + cdoapi.cdo_command.max)
        command.add_operator(cdoapi.cdo_command.select_z_operator, cdoapi.cdo_command.pressure)
        command.add_operator(cdoapi.cdo_command.gridtype_operator, cdoapi.cdo_command.regular_grid_type)
        command.add_operator(cdoapi.cdo_command.select_lev_operator, 500, 350, 10)
        commstr = command.create_command()
        assert commstr == "-yearmean -daymax -setgridtype,regular -sellevel,500,350,10 -selzaxis,pressure -selcode,130"

    @staticmethod
    def test_expr():
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.spectral_operator)
        command.add_operator(cdoapi.cdo_command.expression_operator, "var91=sq(var130)")
        commstr = command.create_command()
        assert commstr == "-expr,'var91=sq(var130)' -sp2gpl -selcode,130"

    @staticmethod
    def test_monmean_expr():
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.expression_operator, "var91=sq(var130)")
        command.add_operator(cdoapi.cdo_command.month + cdoapi.cdo_command.mean)
        commstr = command.create_command()
        assert commstr == "-monmean -expr,'var91=sq(var130)' -selcode,130"

    @staticmethod
    def test_expr_monmean():
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.post_expr_operator, "var91=sq(var130)")
        command.add_operator(cdoapi.cdo_command.month + cdoapi.cdo_command.mean)
        commstr = command.create_command()
        assert commstr == "-expr,'var91=sq(var130)' -monmean -selcode,130"
