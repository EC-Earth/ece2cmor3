import os

import json
import logging
import unittest

from ece2cmor3 import taskloader, ece2cmorlib, cmor_source, cmor_task, cmor_target

logging.basicConfig(level=logging.DEBUG)

drqpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data", "testdrq.json")


class taskloader_test(unittest.TestCase):

    @staticmethod
    def setup_drq(d):
        with open(drqpath, 'w') as drqfile:
            json.dump(d, drqfile)

    @staticmethod
    def cleanup_drq():
        os.remove(drqpath)

    @staticmethod
    def test_load_clt():
        ece2cmorlib.initialize_without_cmor()
        try:
            clt3hr = {"3hr": ["clt"]}
            taskloader.load_tasks_from_drq(clt3hr)
            assert len(ece2cmorlib.tasks) == 1
            src = ece2cmorlib.tasks[0].source
            assert src.get_grib_code().var_id == 164
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_clt_json():
        ece2cmorlib.initialize_without_cmor()
        try:
            clt3hr = {"3hr": ["clt"]}
            taskloader_test.setup_drq(clt3hr)
            taskloader.load_tasks_from_drq(drqpath)
            assert len(ece2cmorlib.tasks) == 1
            src = ece2cmorlib.tasks[0].source
            assert src.get_grib_code().var_id == 164
        finally:
            taskloader_test.cleanup_drq()
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_avars():
        ece2cmorlib.initialize_without_cmor()
        try:
            avars = {"ifs": {"3hr": ["clt", "uas", "vas"], "Amon": ["vas", "tas"]}}
            taskloader.load_tasks(avars)
            assert len(ece2cmorlib.tasks) == 5
            assert len([t.source.get_grib_code().var_id for t in ece2cmorlib.tasks if t.target.variable == "vas"]) == 2
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_avars_json():
        ece2cmorlib.initialize_without_cmor()
        try:
            avars = {"ifs": {"3hr": ["clt", "uas", "vas"], "Amon": ["vas", "tas"]}}
            taskloader_test.setup_drq(avars)
            taskloader.load_tasks(drqpath)
            assert len(ece2cmorlib.tasks) == 5
            assert len([t.source.get_grib_code().var_id for t in ece2cmorlib.tasks if t.target.variable == "vas"]) == 2
        finally:
            taskloader_test.cleanup_drq()
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_avars_drq():
        ece2cmorlib.initialize_without_cmor()
        try:
            taskloader.load_tasks_from_drq({"3hr": ["clt", "uas", "vas"], "Amon": ["vas", "tas"]})
            assert len(ece2cmorlib.tasks) == 5
            assert len([t.source.get_grib_code().var_id for t in ece2cmorlib.tasks if t.target.variable == "vas"]) == 2
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_avars_drq_json():
        ece2cmorlib.initialize_without_cmor()
        try:
            avars = {"3hr": ["clt", "uas", "vas"], "Amon": ["vas", "tas"]}
            taskloader_test.setup_drq(avars)
            taskloader.load_tasks_from_drq(drqpath)
            assert len(ece2cmorlib.tasks) == 5
            assert len([t.source.get_grib_code().var_id for t in ece2cmorlib.tasks if t.target.variable == "vas"]) == 2
        finally:
            taskloader_test.cleanup_drq()
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_skip_alevel():
        def ifs_model_level_variable(target):
            zaxis, levs = cmor_target.get_z_axis(target)
            return zaxis not in ["alevel", "alevhalf"]

        ece2cmorlib.initialize_without_cmor()
        try:
            taskloader.load_tasks_from_drq({"3hr": ["clt", "uas", "vas"], "CFmon": ["clwc", "hur", "ps"]},
                                           target_filters={"model level": ifs_model_level_variable})
            assert len(ece2cmorlib.tasks) == 4
            assert len([t for t in ece2cmorlib.tasks if t.target.table == "CFmon"]) == 1
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_ovars():
        ece2cmorlib.initialize_without_cmor()
        try:
            taskloader.load_tasks_from_drq({"Omon": ["tossq", "so", "thetao"], "Oday": ["sos"]})
            assert len(ece2cmorlib.tasks) == 4
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_ignored_variables():
        ece2cmorlib.initialize_without_cmor()
        try:
            matches, omissions = taskloader.load_drq({"Emon": ["rsdsdiff"], "Amon": ["clivi"]})
            ignored, identified_missing, missing, dismissed = taskloader.split_targets(omissions)
            assert len(matches["nemo"]) == 0
            assert len(matches["ifs"]) == 1
            assert len(ignored) == 1
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_oavars():
        ece2cmorlib.initialize_without_cmor()
        try:
            taskloader.load_tasks_from_drq({"3hr": ["clt", "uas"], "Amon": ["vas", "tas"], "Omon": ["tossq"]})
            assert len(ece2cmorlib.tasks) == 5
            assert len([t for t in ece2cmorlib.tasks if isinstance(t.source, cmor_source.ifs_source)]) == 4
            assert len([t for t in ece2cmorlib.tasks if isinstance(t.source, cmor_source.netcdf_source)]) == 1
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_oavars_ocean():
        ece2cmorlib.initialize_without_cmor()
        try:
            taskloader.load_tasks_from_drq({"3hr": ["clt", "uas"], "Amon": ["vas", "tas"], "Omon": ["tossq"]},
                                           active_components=["nemo"])
            assert len(ece2cmorlib.tasks) == 1
            assert len([t for t in ece2cmorlib.tasks if isinstance(t.source, cmor_source.netcdf_source)]) == 1
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_unit_conv():
        ece2cmorlib.initialize_without_cmor()
        try:
            taskloader.load_tasks_from_drq({"Amon": ["prc", "rsus", "zg"]})
            assert len(ece2cmorlib.tasks) == 3
            prctask = [t for t in ece2cmorlib.tasks if t.target.variable == "prc"][0]
            rsustask = [t for t in ece2cmorlib.tasks if t.target.variable == "rsus"][0]
            zgtask = [t for t in ece2cmorlib.tasks if t.target.variable == "zg"][0]
            assert getattr(prctask, cmor_task.conversion_key) == "vol2flux"
            assert getattr(rsustask, cmor_task.conversion_key) == "cum2inst"
            assert getattr(zgtask, cmor_task.conversion_key) == "pot2alt"
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_expressions():
        ece2cmorlib.initialize_without_cmor()
        try:
            taskloader.load_tasks_from_drq({"day": ["sfcWindmax"]})
            assert getattr(ece2cmorlib.tasks[0].source, "expr") == "var214=sqrt(sqr(var165)+sqr(var166))"
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_tos_3hr():
        ece2cmorlib.initialize()
        try:
            taskloader.load_tasks_from_drq({"3hr": ["tos"]}, active_components=["ifs"])
            assert not any(ece2cmorlib.tasks)
            taskloader.load_tasks_from_drq({"3hr": ["tos"]}, active_components=["nemo"])
            assert len(ece2cmorlib.tasks) == 1
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_ps_AERmon_prefs():
        ece2cmorlib.initialize_without_cmor()
        try:
            matches, omitted = taskloader.load_drq({"AERmon": ["ps"]}, check_prefs=False)
            assert len(matches["ifs"]) == 1
            assert len(matches["tm5"]) == 1
            matches, omitted = taskloader.load_drq({"AERmon": ["ps"]}, check_prefs=True)
            assert len(matches["ifs"]) == 0
            assert len(matches["tm5"]) == 1
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_dismiss_duplicates():
        ece2cmorlib.initialize_without_cmor()
        try:
            matches, omitted = taskloader.load_drq({"AERmon": ["ps"]}, check_prefs=False)
            assert len(matches["ifs"]) == 1
            assert len(matches["tm5"]) == 1
            tasks = taskloader.load_tasks(matches, active_components=["ifs"], target_filters=None,
                                          check_duplicates=True)
            assert not any(tasks)
            tasks = taskloader.load_tasks(matches, active_components=["ifs"], target_filters=None,
                                          check_duplicates=False)
            assert len(tasks) == 1
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_cfc12_Omon_prefs():
        ece2cmorlib.initialize_without_cmor()
        try:
            matches, omitted = taskloader.load_drq({"Omon": ["cfc12"]}, config="EC-EARTH-AOGCM")
            assert not any(matches["nemo"])
            matches, omitted = taskloader.load_drq({"Omon": ["cfc12"]}, config="EC-EARTH-CC")
            assert len(matches["nemo"]) == 1
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_use_level_preferences():
        ece2cmorlib.initialize_without_cmor()
        try:
            matches, omitted = taskloader.load_drq({"6hrPlevPt": ["ua", "ua7h"]}, check_prefs=False)
            assert len(matches["ifs"]) == 2
            matches, omitted = taskloader.load_drq({"6hrPlevPt": ["ua", "ua7h"]}, check_prefs=True)
            assert len(matches["ifs"]) == 1
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_use_zg_preferences():
        ece2cmorlib.initialize_without_cmor()
        try:
            matches, omitted = taskloader.load_drq({"6hrPlevPt": ["zg7h", "zg27"]}, check_prefs=False)
            assert len(matches["ifs"]) == 2
            matches, omitted = taskloader.load_drq({"6hrPlevPt": ["zg7h", "zg27"]}, check_prefs=True)
            assert len(matches["ifs"]) == 1
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_tsl_table_override():
        ece2cmorlib.initialize_without_cmor()
        try:
            tasks = taskloader.load_tasks_from_drq({"6hrPlevPt": ["tsl"], "Lmon": ["tsl"]})
            assert len(tasks) == 2
            for t in tasks:
                if t.target.table == "6hrPlevPt":
                    assert not hasattr(t.source, "expr")
                    assert t.source.get_grib_code() == cmor_source.grib_code(139)
                else:
                    assert "merge" in getattr(t.source, "expr")
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_oclim_variable():
        ece2cmorlib.initialize_without_cmor()
        try:
            matches, omitted = taskloader.load_drq({"Oclim": ["difvho"]}, check_prefs=False)
            assert len(matches["nemo"]) == 1
            assert not any(omitted)
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_cdnc_variable():
        ece2cmorlib.initialize_without_cmor()
        try:
            tasks = taskloader.load_tasks({"ifs": {"AERmon": ["cdnc"]}})
            assert len(tasks) == 1
            src = tasks[0].source
            assert isinstance(src, cmor_source.ifs_source)
            assert getattr(src, "expr_order", 0) == 1
        finally:
            ece2cmorlib.finalize_without_cmor()

    @staticmethod
    def test_load_script_variable():
        ece2cmorlib.initialize_without_cmor()
        try:
            tasks = taskloader.load_tasks({"ifs": {"EmonZ": ["epfy"]}})
            assert len(tasks) == 1
            src = tasks[0].source
            assert isinstance(src, cmor_source.ifs_source)
            script = getattr(tasks[0], "post-proc", None)
            assert script in list(ece2cmorlib.scripts.keys()) and ece2cmorlib.scripts[script]["component"] == "ifs"
        finally:
            ece2cmorlib.finalize_without_cmor()
