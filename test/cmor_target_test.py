import logging
import os
import unittest

from nose.tools import eq_, ok_

from ece2cmor3 import cmor_target

logging.basicConfig(level=logging.DEBUG)


def get_table_path(tab_id=None):
    directory = os.path.join(os.path.dirname(cmor_target.__file__), "resources", "tables")
    return os.path.join(directory, "CMIP6_" + tab_id + ".json") if tab_id else directory


class cmor_target_tests(unittest.TestCase):

    @staticmethod
    def test_get_table_id():
        fname = "dir1/dir2/dir3/CMIP6_Omon.json"
        tid = cmor_target.get_table_id(fname, "CMIP6")
        eq_("Omon", tid)

    @staticmethod
    def test_make_Omon_vars():
        abspath = get_table_path("Omon")
        targets = cmor_target.create_targets(abspath, "CMIP6")
        ok_(len(targets) > 0)
        toss = [t for t in targets if t.variable == "tos"]
        eq_(len(toss), 1)
        tos = toss[0]
        eq_(tos.frequency, "mon")
        eq_(tos.units, "degC")
        eq_(tos.dimensions, "longitude latitude time")

    @staticmethod
    def test_make_CMIP6_vars():
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        ok_(len(targets) > 0)
        toss = [t for t in targets if t.variable == "tos"]
        eq_(len(toss), 4)
        tos_freqs = [v.frequency for v in toss]
        ok_("mon" in tos_freqs)
        ok_("day" in tos_freqs)

    @staticmethod
    def test_cell_measures():
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        tasmin = [t for t in targets if t.table == "day" and t.variable == "tasmin"][0]
        ok_(hasattr(tasmin, "time_operator"))
        ok_(getattr(tasmin, "time_operator"), "minimum")

    @staticmethod
    def test_zhalfo_zdims():
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        zhalfo = [t for t in targets if t.variable == "zhalfo"][0]
        eq_(cmor_target.get_z_axis(zhalfo)[0], "olevhalf")

    @staticmethod
    def test_siu_time_method():
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        siu = [t for t in targets if t.variable == "siu" and t.table == "SIday"][0]
        eq_(getattr(siu, "time_operator", None), ["mean where sea_ice"])
