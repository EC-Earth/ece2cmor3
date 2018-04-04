import os
import unittest

from nose.tools import ok_, eq_

from ece2cmor3 import grib_file
from ece2cmor3.postproc import message, grids


class grids_test(unittest.TestCase):

    @staticmethod
    def test_grid_shapes():
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMGGpl01+199001")
        sh_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMSHpl01+199001")
        gg_file, sh_file = grib_file.open_file(gg_path), grib_file.open_file(sh_path)
        ggf, shf = grib_file.create_grib_file(gg_file), grib_file.create_grib_file(sh_file)
        ggf.read_next()
        shf.read_next()
        gg_msg, sh_msg = message.grib_message(ggf), message.grib_message(shf)
        operator = grids.grid_remap_operator()
        operator.receive_msg(gg_msg)
        ok_(operator.cache_is_full())
        gg_values = operator.create_msg().get_values()
        operator.receive_msg(sh_msg)
        ok_(operator.cache_is_full())
        sh_values = operator.create_msg().get_values()
        eq_(gg_values.shape, sh_values.shape)
