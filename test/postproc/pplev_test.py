import logging
import unittest

import numpy
from datetime import datetime
from nose.tools import ok_, eq_

from ece2cmor3 import cmor_source
from ece2cmor3.postproc import message, levels

logging.basicConfig(level=logging.DEBUG)


# Test utility function creating messages
def make_msg(code, time, level_index, level_type, values):
    data = {message.message_base.variable_key: cmor_source.ifs_source(code=cmor_source.grib_code(code, 128)),
            message.message_base.datetime_key: time,
            message.message_base.timebounds_key: (time, time),
            message.message_base.leveltype_key: level_type,
            message.message_base.levellist_key: [level_index],
            message.message_base.resolution_key: 512,
            "values": values}
    return message.memory_message(**data)


class levels_aggregator_test(unittest.TestCase):

    @staticmethod
    def test_nonmatching_levtype():
        operator = levels.level_aggregator(level_type=100, levels=[100000, 85000, 50000, 10000, 5000])
        time = datetime(1990, 1, 1, 3, 0, 0)
        msg = make_msg(130, time, 850., 100, 273.5)
        operator.receive_msg(msg)
        msg = make_msg(130, time, 88, 99, 273.6)
        ok_(not operator.receive_msg(msg))

    @staticmethod
    def test_nonmatching_levels():
        operator = levels.level_aggregator(level_type=100, levels=[100000, 85000, 50000, 10000, 5000])
        time = datetime(1990, 1, 1, 3, 0, 0)
        msg = make_msg(130, time, 850., 100, 273.5)
        operator.receive_msg(msg)
        msg = make_msg(130, time, 510., 100, 273.6)
        operator.receive_msg(msg)
        eq_(operator.values, [None, 273.5, None, None, None])

    @staticmethod
    def test_matching_levels():
        plevs = [100000, 85000, 50000, 10000, 5000]
        operator = levels.level_aggregator(level_type=100, levels=plevs)
        time = datetime(1990, 1, 1, 3, 0, 0)
        for i in [3, 0, 4, 2, 1]:
            msg = make_msg(130, time, plevs[i]/100., 100, numpy.array([273.5 - i, 273.5 + i]))
            ok_(not operator.cache_is_full())
            operator.receive_msg(msg)
        operator.print_state()
        ok_(operator.cache_is_full())
        msg = operator.create_msg()
        v = msg.get_values()
        eq_((5, 2), v.shape)
        ok_(all(v[:, 0] + v[:, 1] == numpy.repeat(2 * v[0, 0], 5)))
