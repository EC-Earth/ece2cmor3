import logging
import unittest

import os

from ece2cmor3 import grib_filter, grib
from nose.tools import eq_, ok_

logging.basicConfig(level=logging.DEBUG)

test_data_path = os.path.join(os.path.dirname(__file__), "test_data", "ifs", "001")
tmp_path = os.path.join(os.path.dirname(__file__), "tmp")


class grib_filter_test(unittest.TestCase):

    def test_initialize(self):
        gg_path = os.path.join(test_data_path, "ICMGGECE3+199001")
        sh_path = os.path.join(test_data_path, "ICMSHECE3+199001")
        grib_filter.initialize(gg_path, sh_path, tmp_path)
        ok_((133, 128, grib.hybrid_level_code, 9) in grib_filter.varsfreq)
        eq_(grib_filter.varsfreq[(133, 128, grib.hybrid_level_code, 9)], 6)
        ok_((133, 128, grib.pressure_level_code, 850) in grib_filter.varsfreq)
        eq_(grib_filter.varsfreq[(133, 128, grib.pressure_level_code, 850)], 6)
        ok_((164, 128, grib.surface_level_code, 0) in grib_filter.varsfreq)
        eq_(grib_filter.varsfreq[(164, 128, grib.surface_level_code, 0)], 3)

    def test_execute(self):
        pass
