import logging
import unittest
import os
from nose.tools import eq_,ok_,raises
import ece2cmor
import cmor_source
import cmor_task

logging.basicConfig(level=logging.DEBUG)

class ece2cmor_tests(unittest.TestCase):

    @staticmethod
    def init():
        path=os.path.dirname(ece2cmor.__file__)+"/../../input/cmip6/cmip6-cmor-tables/Tables/CMIP6"
        conf=os.path.dirname(__file__)+"/test_data/cmor3_metadata.json"
        abspath=os.path.abspath(path)
        ece2cmor.initialize(path,conf)

    def test_initialize(self):
        ece2cmor_tests.init()

    def test_lookup_target(self):
        ece2cmor_tests.init()
        tgt=ece2cmor.get_cmor_target("clwvi","cfDay")
        ok_(tgt!=None,"CMOR target successfully created")

    def test_create_task(self):
        ece2cmor_tests.init()
        tgt=ece2cmor.get_cmor_target("clwvi","cfDay")
        src=cmor_source.ifs_source.read("79.128")
        tsk=cmor_task.cmor_task(src,tgt)
        ece2cmor.add_task(tsk)
        ok_(tsk in ece2cmor.get_tasks())

    def test_duplicate_task(self):
        ece2cmor_tests.init()
        tgt=ece2cmor.get_cmor_target("clwvi","cfDay")
        src1=cmor_source.ifs_source.read("49.128")
        tsk1=cmor_task.cmor_task(src1,tgt)
        ece2cmor.add_task(tsk1)
        src2=cmor_source.ifs_source.read("79.128")
        tsk2=cmor_task.cmor_task(src2,tgt)
        ece2cmor.add_task(tsk2)
        eq_(len(ece2cmor.get_tasks()),1)
        ok_(tsk2 in ece2cmor.get_tasks())

    def test_valid_ifs_path(self):
        here=os.path.dirname(__file__)
        ece2cmor.set_ifs_dir(os.path.join(here,"test_data","ifs_dummy"))

    @raises(Exception)
    def test_invalid_ifs_path(self):
        here=os.path.dirname(__file__)
        ece2cmor.set_ifs_dir(os.path.join(here,"test_data","nonexistent"))

    def test_valid_nemo_path(self):
        here=os.path.dirname(__file__)
        ece2cmor.set_nemo_dir(os.path.join(here,"test_data","nemo_dummy"))

    @raises(Exception)
    def test_invalid_nemo_path(self):
        here=os.path.dirname(__file__)
        ece2cmor.set_nemo_dir(os.path.join(here,"test_data","nonexistent"))
