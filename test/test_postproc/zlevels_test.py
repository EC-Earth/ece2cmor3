import logging
import os
import unittest

import numpy
from datetime import datetime
from nose.tools import ok_, eq_

from ece2cmor3 import cmor_source, grib_file
from ece2cmor3.postproc import message, zlevels

logging.basicConfig(level=logging.DEBUG)


# Test utility function creating messages
def make_msg(code, time, level_index, level_type, values):
    data = {message.variable_key: cmor_source.ifs_source(code=cmor_source.grib_code(code, 128)),
            message.datetime_key: time,
            message.timebounds_key: (time, time),
            message.leveltype_key: level_type,
            message.levellist_key: [level_index],
            message.resolution_key: 512,
            "values": values}
    return message.memory_message(**data)


class levels_aggregator_test(unittest.TestCase):

    @staticmethod
    def test_nonmatching_levtype():
        operator = zlevels.level_aggregator(level_type=grib_file.pressure_level_Pa_code,
                                            levels=[100000, 85000, 50000, 10000, 5000])
        time = datetime(1990, 1, 1, 3, 0, 0)
        msg = make_msg(130, time, 850., grib_file.pressure_level_hPa_code, 273.5)
        operator.receive_msg(msg)
        msg = make_msg(130, time, 88, 99, 273.6)
        ok_(not operator.receive_msg(msg))

    @staticmethod
    def test_nonmatching_levels():
        operator = zlevels.level_aggregator(level_type=grib_file.pressure_level_Pa_code,
                                            levels=[100000, 85000, 50000, 10000, 5000])
        time = datetime(1990, 1, 1, 3, 0, 0)
        msg = make_msg(130, time, 850., grib_file.pressure_level_hPa_code, 273.5)
        operator.receive_msg(msg)
        msg = make_msg(130, time, 510., grib_file.pressure_level_hPa_code, 273.6)
        operator.receive_msg(msg)
        eq_(operator.values, [None, 273.5, None, None, None])

    @staticmethod
    def test_matching_levels():
        plevs = [100000, 85000, 50000, 10000, 5000]
        operator = zlevels.level_aggregator(level_type=grib_file.pressure_level_Pa_code,
                                            levels=plevs)
        time = datetime(1990, 1, 1, 3, 0, 0)
        for i in [3, 0, 4, 2, 1]:
            msg = make_msg(130, time, plevs[i] / 100., grib_file.pressure_level_hPa_code,
                           numpy.array([273.5 - i, 273.5 + i]))
            ok_(not operator.cache_is_full())
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        msg = operator.create_msg()
        v = msg.get_values()
        eq_((5, 2), v.shape)
        ok_(all(v[:, 0] + v[:, 1] == numpy.repeat(2 * v[0, 0], 5)))

    @staticmethod
    def test_model_levels():
        operator = zlevels.level_aggregator(level_type=grib_file.hybrid_level_code, levels=None)
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMSHpl01+199001")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        test_values = None
        while grbmsg.read_next():
            msg = message.grib_message(grbmsg)
            zlevels.get_pv_array(grbmsg)
            if msg.get_variable().get_grib_code().var_id == 132 and \
                    msg.get_level_type() == grib_file.hybrid_level_code:
                if msg.get_levels() == [13]:
                    test_values = msg.get_values()
                operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        msg = operator.create_msg()
        eq_(msg.get_values().shape[0], 91)
        ok_(numpy.array_equal(msg.get_values()[12, :], test_values))

    @staticmethod
    def test_pressure_levels_hPa():
        plevs = [100000, 85000, 50000, 10000, 500]
        operator = zlevels.level_aggregator(level_type=grib_file.pressure_level_Pa_code, levels=plevs)
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMSHpl01+199001")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        test_values = None
        while grbmsg.read_next():
            msg = message.grib_message(grbmsg)
            zlevels.get_pv_array(grbmsg)
            if msg.get_variable().get_grib_code().var_id == 132 and \
                    msg.get_level_type() == grib_file.pressure_level_hPa_code:
                if msg.get_levels() == [100]:
                    test_values = msg.get_values()
                operator.receive_msg(msg)
                if operator.cache_is_full():
                    break
        ok_(operator.cache_is_full())
        msg = operator.create_msg()
        eq_(msg.get_values().shape[0], 5)
        ok_(numpy.array_equal(msg.get_values()[3, :], test_values))
        grbfile.close()

    @staticmethod
    def test_pressure_levels_Pa():
        plevs = [100000, 85000, 50000, 10000, 500, 40]
        operator = zlevels.level_aggregator(level_type=grib_file.pressure_level_Pa_code, levels=plevs)
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMSHpl01+199001")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        test_values = None
        while grbmsg.read_next():
            msg = message.grib_message(grbmsg)
            zlevels.get_pv_array(grbmsg)
            if msg.get_variable().get_grib_code().var_id == 131 and \
                    msg.get_level_type() in [grib_file.pressure_level_Pa_code, grib_file.pressure_level_hPa_code]:
                if msg.get_levels() == [40]:
                    test_values = msg.get_values()
                operator.receive_msg(msg)
                if operator.cache_is_full():
                    break
        operator.print_state()
        ok_(operator.cache_is_full())
        msg = operator.create_msg()
        eq_(msg.get_values().shape[0], 6)
        ok_(numpy.array_equal(msg.get_values()[5, :], test_values))
        grbfile.close()

    @staticmethod
    def test_pressure_level_units():
        plevs = [1000., 850., 500., 100., 5., 0.4]
        operator = zlevels.level_aggregator(level_type=grib_file.pressure_level_hPa_code, levels=plevs)
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMSHpl01+199001")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        test_values = None
        while grbmsg.read_next():
            msg = message.grib_message(grbmsg)
            zlevels.get_pv_array(grbmsg)
            if msg.get_variable().get_grib_code().var_id == 131 and \
                    msg.get_level_type() in [grib_file.pressure_level_Pa_code, grib_file.pressure_level_hPa_code]:
                if msg.get_levels() == [40]:
                    test_values = msg.get_values()
                operator.receive_msg(msg)
                if operator.cache_is_full():
                    break
        operator.print_state()
        ok_(operator.cache_is_full())
        msg = operator.create_msg()
        eq_(msg.get_values().shape[0], 6)
        ok_(numpy.array_equal(msg.get_values()[5, :], test_values))
        grbfile.close()
