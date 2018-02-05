import logging
import unittest

import os

from ece2cmor3 import grib_filter, grib, ece2cmorlib, cmor_source, cmor_task, cmor_target
from nose.tools import eq_, ok_

logging.basicConfig(level=logging.DEBUG)

test_data_path = os.path.join(os.path.dirname(__file__), "test_data", "ifs", "001")
tmp_path = os.path.join(os.path.dirname(__file__), "tmp")


class grib_filter_test(unittest.TestCase):

    @staticmethod
    def test_initialize():
        gg_path = os.path.join(test_data_path, "ICMGGECE3+199001")
        sh_path = os.path.join(test_data_path, "ICMSHECE3+199001")
        grib_filter.initialize(gg_path, sh_path, tmp_path)
        ok_((133, 128, grib.hybrid_level_code, 9) in grib_filter.varsfreq)
        eq_(grib_filter.varsfreq[(133, 128, grib.hybrid_level_code, 9)], 6)
        ok_((133, 128, grib.pressure_level_code, 85000) in grib_filter.varsfreq)
        eq_(grib_filter.varsfreq[(133, 128, grib.pressure_level_code, 85000)], 6)
        ok_((164, 128, grib.surface_level_code, 0) in grib_filter.varsfreq)
        eq_(grib_filter.varsfreq[(164, 128, grib.surface_level_code, 0)], 3)

    @staticmethod
    def test_validate_tasks():
        gg_path = os.path.join(test_data_path, "ICMGGECE3+199001")
        sh_path = os.path.join(test_data_path, "ICMSHECE3+199001")
        grib_filter.initialize(gg_path, sh_path, tmp_path)
        ece2cmorlib.initialize()
        tgt1 = ece2cmorlib.get_cmor_target("clwvi", "CFday")
        src1 = cmor_source.ifs_source.read("79.128")
        tsk1 = cmor_task.cmor_task(src1, tgt1)
        tgt2 = ece2cmorlib.get_cmor_target("ua", "Amon")
        src2 = cmor_source.ifs_source.read("131.128")
        tsk2 = cmor_task.cmor_task(src2, tgt2)
        valid_tasks = grib_filter.validate_tasks([tsk1, tsk2])
        eq_(valid_tasks, [tsk1, tsk2])
        key1 = (79, 128, grib.surface_level_code, 0.)
        key2 = (131, 128, grib.pressure_level_code, 92500.)
        eq_(grib_filter.varstasks[key1], [tsk1])
        eq_(grib_filter.varstasks[key2], [tsk2])
        ltype, plevs = cmor_target.get_z_axis(tgt2)
        levs = sorted([float(p) for p in plevs])
        levcheck = sorted([k[3] for k in grib_filter.varstasks if k[0] == 131])
        eq_(levs, levcheck)

#    @unittest.skip("Hanging indefinitely")
    def test_execute_tasks(self):
        gg_path = os.path.join(test_data_path, "ICMGGECE3+199001")
        sh_path = os.path.join(test_data_path, "ICMSHECE3+199001")
        grib_filter.initialize(gg_path, sh_path, tmp_path)
        ece2cmorlib.initialize()
        tgt1 = ece2cmorlib.get_cmor_target("clwvi", "CFday")
        src1 = cmor_source.ifs_source.read("79.128")
        tsk1 = cmor_task.cmor_task(src1, tgt1)
        tgt2 = ece2cmorlib.get_cmor_target("ua", "Amon")
        src2 = cmor_source.ifs_source.read("131.128")
        tsk2 = cmor_task.cmor_task(src2, tgt2)
        grib_filter.execute([tsk1, tsk2], 1)

