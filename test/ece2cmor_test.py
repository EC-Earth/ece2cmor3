import logging
import unittest

from ece2cmor3 import ece2cmorlib, cmor_source, cmor_task

logging.basicConfig(level=logging.DEBUG)


class ece2cmorlib_tests(unittest.TestCase):

    @staticmethod
    def test_init():
        ece2cmorlib.initialize()

    @staticmethod
    def test_initialize():
        ece2cmorlib.initialize()
        ece2cmorlib.finalize()

    @staticmethod
    def test_lookup_target():
        ece2cmorlib.initialize()
        tgt = ece2cmorlib.get_cmor_target("clwvi", "CFday")
        assert tgt is not None
        ece2cmorlib.finalize()

    @staticmethod
    def test_create_task():
        ece2cmorlib.initialize()
        tgt = ece2cmorlib.get_cmor_target("clwvi", "CFday")
        src = cmor_source.ifs_source.read("79.128")
        tsk = cmor_task.cmor_task(src, tgt)
        ece2cmorlib.add_task(tsk)
        assert tsk in ece2cmorlib.tasks
        ece2cmorlib.finalize()

    @staticmethod
    def test_duplicate_task():
        ece2cmorlib.initialize()
        tgt = ece2cmorlib.get_cmor_target("clwvi", "CFday")
        src1 = cmor_source.ifs_source.read("49.128")
        tsk1 = cmor_task.cmor_task(src1, tgt)
        ece2cmorlib.add_task(tsk1)
        src2 = cmor_source.ifs_source.read("79.128")
        tsk2 = cmor_task.cmor_task(src2, tgt)
        ece2cmorlib.add_task(tsk2)
        assert len(ece2cmorlib.tasks) == 1
        assert tsk2 in ece2cmorlib.tasks
        ece2cmorlib.finalize()
