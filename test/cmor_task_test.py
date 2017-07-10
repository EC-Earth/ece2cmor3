import logging
import unittest
import os
from nose.tools import eq_,ok_,raises
from ece2cmor3 import cmor_source
from ece2cmor3 import cmor_target
from ece2cmor3 import cmor_task

logging.basicConfig(level=logging.DEBUG)

class cmor_task_tests(unittest.TestCase):

    @raises(Exception)
    def test_invalid_source(self):
        src="invalid"
        tgt=cmor_target.cmor_target("huss","Amon")
        task=cmor_task.cmor_task(src,tgt)

    @raises(Exception)
    def test_invalid_target(self):
        src=cmor_source.ifs_source("81.128")
        tgt="invalid"
        task=cmor_task.cmor_task(src,tgt)

    @raises(Exception)
    def test_constructor(self):
        src=cmor_source.ifs_source.read("79.128")
        tgt=cmor_target.cmor_target("clwvi","Amon")
        task=cmor_task.cmor_task(src,tgt)
        eq_(task.source,src)
        eq_(task.target,tgt)
