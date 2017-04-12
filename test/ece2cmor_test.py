import logging
import unittest
import os
from nose.tools import eq_,ok_,raises
import ece2cmorlib
import cmor_source
import cmor_task

logging.basicConfig(level=logging.DEBUG)

class ece2cmorlib_tests(unittest.TestCase):

    @staticmethod
    def init():
        conf=os.path.dirname(__file__)+"/test_data/cmor3_metadata.json"
        ece2cmorlib.initialize(metadata=conf)

    def test_initialize(self):
        ece2cmorlib_tests.init()
        ece2cmorlib.finalize()

    def test_lookup_target(self):
        ece2cmorlib_tests.init()
        tgt=ece2cmorlib.get_cmor_target("clwvi","CFday")
        ok_(tgt!=None,"CMOR target successfully created")
        ece2cmorlib.finalize()

    def test_create_task(self):
        ece2cmorlib_tests.init()
        tgt=ece2cmorlib.get_cmor_target("clwvi","CFday")
        src=cmor_source.ifs_source.read("79.128")
        tsk=cmor_task.cmor_task(src,tgt)
        ece2cmorlib.add_task(tsk)
        ok_(tsk in ece2cmorlib.tasks)
        ece2cmorlib.finalize()

    def test_duplicate_task(self):
        ece2cmorlib_tests.init()
        tgt=ece2cmorlib.get_cmor_target("clwvi","CFday")
        src1=cmor_source.ifs_source.read("49.128")
        tsk1=cmor_task.cmor_task(src1,tgt)
        ece2cmorlib.add_task(tsk1)
        src2=cmor_source.ifs_source.read("79.128")
        tsk2=cmor_task.cmor_task(src2,tgt)
        ece2cmorlib.add_task(tsk2)
        eq_(len(ece2cmorlib.tasks),1)
        ok_(tsk2 in ece2cmorlib.tasks)
        ece2cmorlib.finalize()
