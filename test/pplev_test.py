import logging
import unittest
import numpy
from nose.tools import ok_,eq_
from ece2cmor3 import ppmsg, pplevels, grib_file

logging.basicConfig(level=logging.DEBUG)

# Test utility function creating messages
def make_msg(code, date, time, level_index, level_type, values):
    grbmsg = {grib_file.param_key : code, grib_file.date_key: date, grib_file.time_key: time,
              grib_file.levtype_key: level_type, grib_file.level_key: level_index, "values": values}
    return ppmsg.grib_message(grbmsg)

class levels_aggregator_test(unittest.TestCase):

    def test_nonmatching_levtype(self):
        operator = pplevels.level_aggregator(level_type=100, levels=[100000, 85000, 50000, 10000, 5000])
        msg = make_msg(130, 19900101, 300, 85000, 100, 273.5)
        operator.receive_msg(msg)
        msg = make_msg(130, 19900101, 300, 88, 99, 273.6)
        ok_(not operator.receive_msg(msg))

    def test_nonmatching_levels(self):
        operator = pplevels.level_aggregator(level_type=100, levels=[100000, 85000, 50000, 10000, 5000])
        msg = make_msg(130, 19900101, 300, 85000, 100, 273.5)
        operator.receive_msg(msg)
        msg = make_msg(130, 19900101, 300, 51000, 100, 273.6)
        eq_(operator.values,[None, 273.5, None, None, None])

    def test_matching_levels(self):
        plevs = [100000, 85000, 50000, 10000, 5000]
        operator = pplevels.level_aggregator(level_type=100, levels=plevs)
        for i in [3, 0, 4, 2, 1]:
            msg = make_msg(130, 19900101, 300, plevs[i], 100, numpy.array([273.5 - i,273.5 + i]))
            ok_(not operator.cache_is_full())
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        msg = operator.create_msg()
        v = msg.get_values()
        eq_((5, 2), v.shape)
        ok_(all(v[:, 0] + v[:, 1] == numpy.repeat(2 * v[0, 0], 5)))
