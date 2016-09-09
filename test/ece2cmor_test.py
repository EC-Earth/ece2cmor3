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
        conf="test_data/cmor3_metadata.json"
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
        ece2cmor.add_task(cmor_task.cmor_task(src,tgt))
