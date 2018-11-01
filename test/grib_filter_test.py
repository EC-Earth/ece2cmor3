from datetime import datetime

import logging
import unittest

import os

from ece2cmor3 import grib_filter, grib_file, ece2cmorlib, cmor_source, cmor_task, cmor_target
from nose.tools import eq_, ok_, with_setup

logging.basicConfig(level=logging.DEBUG)

test_data_path = os.path.join(os.path.dirname(__file__), "test_data", "ifs", "001")
tmp_path = os.path.join(os.path.dirname(__file__), "tmp")


def setup():
    grib_file.test_mode = grib_filter_test.test_mode
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)


class grib_filter_test(unittest.TestCase):
    test_mode = True
    date = datetime(year=1990, month=1, day=1, hour=1)
    gg_file = "ICMGGECE3+199001.csv" if test_mode else "ICMGGECE3+199001"
    gg_path = {date: os.path.join(test_data_path, gg_file)}
    sh_file = "ICMSHECE3+199001.csv" if test_mode else "ICMSHECE3+199001"
    sh_path = {date: os.path.join(test_data_path, sh_file)}

    @staticmethod
    @with_setup(setup)
    def test_initialize():
        grib_filter.initialize(grib_filter_test.gg_path, grib_filter_test.sh_path, tmp_path)
        eq_(grib_filter.varsfreq[(133, 128, grib_file.hybrid_level_code, 9, cmor_source.ifs_grid.point)], 6)
        eq_(grib_filter.varsfreq[(133, 128, grib_file.pressure_level_Pa_code, 85000, cmor_source.ifs_grid.point)], 6)
        eq_(grib_filter.varsfreq[(164, 128, grib_file.surface_level_code, 0, cmor_source.ifs_grid.point)], 3)

    @staticmethod
    @with_setup(setup)
    def test_validate_tasks():
        grib_filter.initialize(grib_filter_test.gg_path, grib_filter_test.sh_path, tmp_path)
        ece2cmorlib.initialize()
        tgt1 = ece2cmorlib.get_cmor_target("clwvi", "CFday")
        src1 = cmor_source.ifs_source.read("79.128")
        tsk1 = cmor_task.cmor_task(src1, tgt1)
        tgt2 = ece2cmorlib.get_cmor_target("ua", "Amon")
        src2 = cmor_source.ifs_source.read("131.128")
        tsk2 = cmor_task.cmor_task(src2, tgt2)
        valid_tasks = grib_filter.validate_tasks([tsk1, tsk2])
        eq_(valid_tasks, [tsk1, tsk2])
        key1 = (79, 128, grib_file.surface_level_code, 0, cmor_source.ifs_grid.point)
        key2 = (131, 128, grib_file.pressure_level_Pa_code, 92500, cmor_source.ifs_grid.spec)
        eq_(grib_filter.varstasks[key1], [tsk1])
        eq_(grib_filter.varstasks[key2], [tsk2])
        ltype, plevs = cmor_target.get_z_axis(tgt2)
        levs = sorted([float(p) for p in plevs])
        levcheck = sorted([k[3] for k in grib_filter.varstasks if k[0] == 131])
        eq_(levs, levcheck)

    @staticmethod
    @with_setup(setup)
    def test_surf_var():
        grib_filter.initialize(grib_filter_test.gg_path, grib_filter_test.sh_path, tmp_path)
        ece2cmorlib.initialize()
        tgt = ece2cmorlib.get_cmor_target("clwvi", "CFday")
        src = cmor_source.ifs_source.read("79.128")
        tsk = cmor_task.cmor_task(src, tgt)
        grib_filter.execute([tsk])
        filepath = os.path.join(tmp_path, "79.128.1.3")
        ok_(os.path.isfile(filepath))
        ok_(getattr(tsk, cmor_task.filter_output_key), [filepath])
        with open(filepath) as fin:
            reader = grib_file.create_grib_file(fin)
            date, time = 0, 0
            while reader.read_next():
                param = reader.get_field(grib_file.param_key)
                eq_(param, 79)
                newdate = reader.get_field(grib_file.date_key)
                if date != 0 and newdate != date:
                    eq_(newdate, date + 1)
                    date = newdate
                newtime = reader.get_field(grib_file.time_key)
                eq_(newtime, (time + 300) % 2400)
                time = newtime
        os.remove(filepath)

    @staticmethod
    @with_setup(setup)
    def test_expr_var():
        grib_filter.initialize(grib_filter_test.gg_path, grib_filter_test.sh_path, tmp_path)
        ece2cmorlib.initialize()
        tgt = ece2cmorlib.get_cmor_target("sfcWind", "Amon")
        src = cmor_source.ifs_source.read("214.128", "sqrt(sqr(var165)+sqr(var166))")
        tsk = cmor_task.cmor_task(src, tgt)
        grib_filter.execute([tsk])
        filepath = os.path.join(tmp_path, "166.128.105_165.128.105.3")
        ok_(os.path.isfile(filepath))
        ok_(getattr(tsk, cmor_task.filter_output_key), [filepath])
        with open(filepath) as fin:
            reader = grib_file.create_grib_file(fin)
            date, time = 0, 0
            while reader.read_next():
                param = reader.get_field(grib_file.param_key)
                ok_(param in [165, 166])
                newdate = reader.get_field(grib_file.date_key)
                if date != 0 and newdate != date:
                    eq_(newdate, date + 1)
                    date = newdate
                newtime = reader.get_field(grib_file.time_key)
                if newtime != time:
                    eq_(newtime, (time + 300) % 2400)
                    time = newtime
        os.remove(filepath)

    @staticmethod
    @with_setup(setup)
    def test_pressure_var():
        grib_filter.initialize(grib_filter_test.gg_path, grib_filter_test.sh_path, tmp_path)
        ece2cmorlib.initialize()
        tgt = ece2cmorlib.get_cmor_target("ua", "Amon")
        src = cmor_source.ifs_source.read("131.128")
        tsk = cmor_task.cmor_task(src, tgt)
        grib_filter.execute([tsk])
        filepath = os.path.join(tmp_path, "131.128.210.6")
        ok_(os.path.isfile(filepath))
        ok_(getattr(tsk, cmor_task.filter_output_key), [filepath])
        with open(filepath) as fin:
            reader = grib_file.create_grib_file(fin)
            date, time = 0, 0
            while reader.read_next():
                param = reader.get_field(grib_file.param_key)
                eq_(param, 131)
                newdate = reader.get_field(grib_file.date_key)
                if date != 0 and newdate != date:
                    eq_(newdate, date + 1)
                    date = newdate
                newtime = reader.get_field(grib_file.time_key)
                if newtime != time:
                    eq_(newtime, (time + 600) % 2400)
                    time = newtime
        os.remove(filepath)
