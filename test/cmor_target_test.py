import logging
import os
import unittest

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
        assert tid == "Omon"

    @staticmethod
    def test_make_Omon_vars():
        abspath = get_table_path("Omon")
        targets = cmor_target.create_targets(abspath, "CMIP6")
        assert len(targets) > 0
        toss = [t for t in targets if t.variable == "tos"]
        assert len(toss) == 1
        tos = toss[0]
        assert tos.frequency == "mon"
        assert tos.units == "degC"
        assert tos.dimensions == "longitude latitude time"

    @staticmethod
    def test_make_CMIP6_vars():
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        assert len(targets) > 0
        toss = [t for t in targets if t.variable == "tos"]
        assert len(toss) == 4
        tos_freqs = [v.frequency for v in toss]
        assert "mon" in tos_freqs
        assert "day" in tos_freqs

    @staticmethod
    def test_cell_measures():
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        tasmin = [t for t in targets if t.table == "day" and t.variable == "tasmin"][0]
        assert hasattr(tasmin, "time_operator")
        assert getattr(tasmin, "time_operator") == ["minimum"]

    @staticmethod
    def test_zhalfo_zdims():
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        zhalfo = [t for t in targets if t.variable == "zhalfo"][0]
        assert cmor_target.get_z_axis(zhalfo)[0] == "olevhalf"

    @staticmethod
    def test_siu_time_method():
        abspath = get_table_path()
        targets = cmor_target.create_targets(abspath, "CMIP6")
        siu = [t for t in targets if t.variable == "siu" and t.table == "SIday"][0]
        assert getattr(siu, "time_operator", None) == ["mean where sea_ice"]
