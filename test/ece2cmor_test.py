import logging
import unittest
import os
from nose.tools import eq_,ok_,raises
import ece2cmor

logging.basicConfig(level=logging.DEBUG)

class ece2cmor_tests(unittest.TestCase):

    def test_initialize(self):
        path=os.path.dirname(ece2cmor.__file__)+"../../../input/cmip6/cmip6-cmor-tables/Tables"
        conf="test_data/cmor3_metadata.json"
        abspath=os.path.abspath(path)
        ece2cmor.initialize(path,conf)
