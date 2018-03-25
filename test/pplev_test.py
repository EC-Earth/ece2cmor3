import logging
import unittest

import numpy
from datetime import datetime
from nose.tools import ok_, eq_

from ece2cmor3 import ppmsg, pplevels, cmor_source

logging.basicConfig(level=logging.DEBUG)


# Test utility function creating messages
def make_msg(code, time, level_index, level_type, values):
    data = {ppmsg.message.variable_key: cmor_source.ifs_source(code=cmor_source.grib_code(code, 128)),
            ppmsg.message.datetime_key: time,
            ppmsg.message.timebounds_key: (time, time),
            ppmsg.message.leveltype_key: level_type,
            ppmsg.message.levellist_key: [level_index],
            ppmsg.message.resolution_key: 512,
            "values": values}
    return ppmsg.memory_message(**data)


class levels_aggregator_test(unittest.TestCase):

    @staticmethod
    def test_nonmatching_levtype():
        operator = pplevels.level_aggregator(level_type=100, levels=[100000, 85000, 50000, 10000, 5000])
        time = datetime(1990, 1, 1, 3, 0, 0)
        msg = make_msg(130, time, 85000, 100, 273.5)
        operator.receive_msg(msg)
        msg = make_msg(130, time, 88, 99, 273.6)
        ok_(not operator.receive_msg(msg))

    @staticmethod
    def test_nonmatching_levels():
        operator = pplevels.level_aggregator(level_type=100, levels=[100000, 85000, 50000, 10000, 5000])
        time = datetime(1990, 1, 1, 3, 0, 0)
        msg = make_msg(130, time, 85000, 100, 273.5)
        operator.receive_msg(msg)
        msg = make_msg(130, time, 51000, 100, 273.6)
        operator.receive_msg(msg)
        eq_(operator.values, [None, 273.5, None, None, None])

    @staticmethod
    def test_matching_levels():
        plevs = [100000, 85000, 50000, 10000, 5000]
        operator = pplevels.level_aggregator(level_type=100, levels=plevs)
        time = datetime(1990, 1, 1, 3, 0, 0)
        for i in [3, 0, 4, 2, 1]:
            msg = make_msg(130, time, plevs[i], 100, numpy.array([273.5 - i, 273.5 + i]))
            ok_(not operator.cache_is_full())
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        msg = operator.create_msg()
        v = msg.get_values()
        eq_((5, 2), v.shape)
        ok_(all(v[:, 0] + v[:, 1] == numpy.repeat(2 * v[0, 0], 5)))
