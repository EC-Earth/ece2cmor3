import logging
import unittest
import cdoapi
import nose.tools

logging.basicConfig(level=logging.DEBUG)

class cdoapi_tests(unittest.TestCase):

    def test_select_code(self):
        command = cdoapi.cdo_command(130)
        commstr = command.create_command()
        nose.tools.eq_("-selcode,130",commstr)

    def test_select_codes(self):
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.select_code_operator,131,132)
        commstr = command.create_command()
        nose.tools.eq_("-selcode,130,131,132",commstr)

    def test_add_specmapping(self):
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.spectral_operator)
        commstr = command.create_command()
        nose.tools.eq_("-sp2gpl -selcode,130",commstr)

    def test_add_gridmapping(self):
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.gridtype_operator,cdoapi.cdo_command.regular_grid_type)
        commstr = command.create_command()
        nose.tools.eq_("-setgridtype,regular -selcode,130",commstr)

    def test_add_sellevel(self):
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.pressure)
        command.add_operator(cdoapi.cdo_command.gridtype_operator,cdoapi.cdo_command.regular_grid_type)
        command.add_operator(cdoapi.cdo_command.select_lev_operator,500,350,10)
        commstr = command.create_command()
        nose.tools.eq_("-setgridtype,regular -sellevel,500,350,10 -selzaxis,pressure -selcode,130",commstr)

    def test_add_monmean(self):
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
        command.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.pressure)
        command.add_operator(cdoapi.cdo_command.gridtype_operator,cdoapi.cdo_command.regular_grid_type)
        command.add_operator(cdoapi.cdo_command.select_lev_operator,500,350,10)
        commstr = command.create_command()
        nose.tools.eq_("-setgridtype,regular -monmean -sellevel,500,350,10 -selzaxis,pressure -selcode,130",commstr)

    def test_add_daymax(self):
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
        command.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.day])
        command.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.pressure)
        command.add_operator(cdoapi.cdo_command.gridtype_operator,cdoapi.cdo_command.regular_grid_type)
        command.add_operator(cdoapi.cdo_command.select_lev_operator,500,350,10)
        commstr = command.create_command()
        nose.tools.eq_("-monmean -daymax -setgridtype,regular -sellevel,500,350,10 -selzaxis,pressure -selcode,130",commstr)

    def test_expr(self):
        command = cdoapi.cdo_command(130)
        command.add_operator(cdoapi.cdo_command.spectral_operator)
        command.add_operator(cdoapi.cdo_command.expression_operator,"var91=sq(var130)")
        commstr = command.create_command()
        nose.tools.eq_("-expr,'var91=sq(var130)' -sp2gpl -selcode,130",commstr)
