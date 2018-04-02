import unittest
from datetime import datetime, timedelta

import numpy
from nose.tools import ok_, eq_

from ece2cmor3 import grib_file, cmor_source
from ece2cmor3.postproc import expression, message


# Test utility function creating messages
def make_uv_messages(start_date, length, radius, size):
    result = []
    time = start_date
    omega = 2*numpy.pi / 3600
    while time <= start_date + length:
        angles = 2*numpy.pi * numpy.random.rand(size) + omega * (time - start_date).total_seconds()
        uvals = radius * numpy.cos(angles)
        vvals = radius * numpy.sin(angles)
        bnds = (time, time)
        udata = {message.variable_key: cmor_source.ifs_source(cmor_source.grib_code(165, 128)),
                 message.datetime_key: time,
                 message.timebounds_key: bnds,
                 message.leveltype_key: grib_file.surface_level_code,
                 message.levellist_key: [0],
                 message.resolution_key: 16,
                 "values": uvals}
        result.append(message.memory_message(**udata))
        vdata = {message.variable_key: cmor_source.ifs_source(cmor_source.grib_code(166, 128)),
                 message.datetime_key: time,
                 message.timebounds_key: bnds,
                 message.leveltype_key: grib_file.surface_level_code,
                 message.levellist_key: [0],
                 message.resolution_key: 16,
                 "values": vvals}
        result.append(message.memory_message(**vdata))
        time = time + timedelta(hours=3)
    return result


class expression_test(unittest.TestCase):

    @staticmethod
    def test_wind_speed():
        operator = expression.expression_operator("var214=sqrt(sqr(var165)+sqr(var166))")
        time = datetime(1990, 1, 1, 3, 0, 0)
        r = 12.34567
        msgs = make_uv_messages(time, timedelta(days=1), radius=r, size=10)
        i = 0
        for msg in msgs:
            i += 1
            operator.receive_msg(msg)
            if i % 2 == 0:
                print operator.local_dict
                ok_(operator.cache_is_full())
                new_msg = operator.create_msg()
                eq_(new_msg.get_variable().get_grib_code().var_id, 214)
                print new_msg.get_values()
                ok_(all(new_msg.get_values() - r  < 1e-8))
                operator.clear_cache()
            else:
                ok_(not operator.cache_is_full())
