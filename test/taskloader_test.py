import os

import json
import logging
import unittest
from nose.tools import eq_

from ece2cmor3 import taskloader, ece2cmorlib, cmor_source, cmor_task, cmor_target

logging.basicConfig(level=logging.DEBUG)

drqpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data", "testdrq.json")


class taskloader_test(unittest.TestCase):

    @staticmethod
    def setup_drq(d):
        with open(drqpath) as drqfile:
            json.dump(d, drqfile)

    @staticmethod
    def cleanup_drq():
        os.remove(drqpath)

    @staticmethod
    def test_load_clt():
        ece2cmorlib.initialize()
        try:
            clt3hr = {"3hr": ["clt"]}
            taskloader.load_tasks_from_drq(clt3hr)
            eq_(len(ece2cmorlib.tasks), 1)
            src = ece2cmorlib.tasks[0].source
            eq_(src.get_grib_code().var_id, 164)
        finally:
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_clt_json():
        ece2cmorlib.initialize()
        try:
            clt3hr = {"3hr": ["clt"]}
            taskloader_test.setup_drq(clt3hr)
            taskloader.load_tasks_from_drq(drqpath)
            eq_(len(ece2cmorlib.tasks), 1)
            src = ece2cmorlib.tasks[0].source
            eq_(src.get_grib_code().var_id, 164)
        finally:
            taskloader_test.cleanup_drq()
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_avars():
        ece2cmorlib.initialize()
        try:
            avars = {"ifs": {"3hr": ["clt", "uas", "vas"], "Amon": ["vas", "tas"]}}
            taskloader.load_tasks(avars)
            eq_(len(ece2cmorlib.tasks), 5)
            eq_(2, len([t.source.get_grib_code().var_id for t in ece2cmorlib.tasks if t.target.variable == "vas"]))
        finally:
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_avars_json():
        ece2cmorlib.initialize()
        try:
            avars = {"ifs": {"3hr": ["clt", "uas", "vas"], "Amon": ["vas", "tas"]}}
            taskloader_test.setup_drq(avars)
            taskloader.load_tasks(drqpath)
            eq_(len(ece2cmorlib.tasks), 5)
            eq_(2, len([t.source.get_grib_code().var_id for t in ece2cmorlib.tasks if t.target.variable == "vas"]))
        finally:
            taskloader_test.cleanup_drq()
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_avars_drq():
        ece2cmorlib.initialize()
        try:
            taskloader.load_tasks_from_drq({"3hr": ["clt", "uas", "vas"], "Amon": ["vas", "tas"]})
            eq_(len(ece2cmorlib.tasks), 5)
            eq_(2, len([t.source.get_grib_code().var_id for t in ece2cmorlib.tasks if t.target.variable == "vas"]))
        finally:
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_avars_drq_json():
        ece2cmorlib.initialize()
        try:
            avars = {"3hr": ["clt", "uas", "vas"], "Amon": ["vas", "tas"]}
            taskloader_test.setup_drq(avars)
            taskloader.load_tasks_from_drq(drqpath)
            eq_(len(ece2cmorlib.tasks), 5)
            eq_(2, len([t.source.get_grib_code().var_id for t in ece2cmorlib.tasks if t.target.variable == "vas"]))
        finally:
            taskloader_test.cleanup_drq()
            ece2cmorlib.finalize()

    @staticmethod
    def test_skip_alevel():
        def ifs_model_level_variable(target):
            zaxis, levs = cmor_target.get_z_axis(target)
            return zaxis not in ["alevel", "alevhalf"]

        ece2cmorlib.initialize()
        try:
            taskloader.load_tasks_from_drq({"3hr": ["clt", "uas", "vas"], "CFmon": ["clwc", "hur", "ps"]},
                                           target_filters={"model level": ifs_model_level_variable})
            eq_(len(ece2cmorlib.tasks), 4)
            eq_(len([t for t in ece2cmorlib.tasks if t.target.table == "CFmon"]), 1)
        finally:
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_ovars():
        ece2cmorlib.initialize()
        try:
            taskloader.load_tasks_from_drq({"Omon": ["tossq", "so", "thetao"], "Oday": ["sos"]})
            eq_(len(ece2cmorlib.tasks), 4)
        finally:
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_oavars():
        ece2cmorlib.initialize()
        try:
            taskloader.load_tasks_from_drq({"3hr": ["clt", "uas"], "Amon": ["vas", "tas"], "Omon": ["tossq"]})
            eq_(len(ece2cmorlib.tasks), 5)
            eq_(4, len([t for t in ece2cmorlib.tasks if isinstance(t.source, cmor_source.ifs_source)]))
            eq_(1, len([t for t in ece2cmorlib.tasks if isinstance(t.source, cmor_source.netcdf_source)]))
        finally:
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_oavars_ocean():
        ece2cmorlib.initialize()
        try:
            taskloader.load_tasks_from_drq({"3hr": ["clt", "uas"], "Amon": ["vas", "tas"], "Omon": ["tossq"]},
                                           active_components=["nemo"])
            eq_(len(ece2cmorlib.tasks), 1)
            eq_(1, len([t for t in ece2cmorlib.tasks if isinstance(t.source, cmor_source.netcdf_source)]))
        finally:
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_unit_conv():
        ece2cmorlib.initialize()
        try:
            taskloader.load_tasks_from_drq({"Amon": ["prc", "rsus", "zg"]})
            eq_(len(ece2cmorlib.tasks), 3)
            prctask = [t for t in ece2cmorlib.tasks if t.target.variable == "prc"][0]
            rsustask = [t for t in ece2cmorlib.tasks if t.target.variable == "rsus"][0]
            zgtask = [t for t in ece2cmorlib.tasks if t.target.variable == "zg"][0]
            eq_("vol2flux", getattr(prctask, cmor_task.conversion_key))
            eq_("cum2inst", getattr(rsustask, cmor_task.conversion_key))
            eq_("pot2alt", getattr(zgtask, cmor_task.conversion_key))
        finally:
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_expressions():
        ece2cmorlib.initialize()
        try:
            taskloader.load_tasks_from_drq({"day": ["sfcWindmax"]})
            eq_("var214=sqrt(sqr(var165)+sqr(var166))", getattr(ece2cmorlib.tasks[0].source, "expr"))
        finally:
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_tos_3hr():
        ece2cmorlib.initialize()
        try:
            taskloader.load_tasks_from_drq({"3hr": ["tos"]}, active_components={"ifs": True})
            eq_(len(ece2cmorlib.tasks), 0)
            taskloader.load_tasks_from_drq({"3hr": ["tos"]}, active_components=["nemo"])
            eq_(len(ece2cmorlib.tasks), 1)
        finally:
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_ps_AERmon_prefs():
        ece2cmorlib.initialize()
        try:
            matches = taskloader.load_drq({"AERmon": ["ps"]}, check_prefs=False)
            eq_(len(matches["ifs"]), 1)
            eq_(len(matches["tm5"]), 1)
            matches = taskloader.load_drq({"AERmon": ["ps"]}, check_prefs=True)
            eq_(len(matches["ifs"]), 0)
            eq_(len(matches["tm5"]), 1)
        finally:
            ece2cmorlib.finalize()

    @staticmethod
    def test_load_cfc12_Omon_prefs():
        ece2cmorlib.initialize()
        try:
            matches = taskloader.load_drq({"Omon": ["cfc12"]}, check_prefs=False, config="EC-Earth-HR")
            eq_(len(matches["nemo"]), 0)
            matches = taskloader.load_drq({"Omon": ["cfc12"]}, check_prefs=False, config="EC-Earth-CC")
            eq_(len(matches["nemo"]), 1)
        finally:
            ece2cmorlib.finalize()
