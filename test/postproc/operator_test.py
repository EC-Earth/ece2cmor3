import logging
import unittest
from datetime import datetime
from nose.tools import ok_, eq_
from ece2cmor3 import grib_file, cmor_source
from ece2cmor3.postproc import message, operator

logging.basicConfig(level=logging.DEBUG)


# Test utility class summing last 10 values
class pp_sum_operator(operator.operator_base):

    def __init__(self, interval=10):
        super(pp_sum_operator, self).__init__()
        self.counter = 0
        self.interval = interval

    def fill_cache(self, msg):
        if self.values is None:
            self.values = msg.get_values()
        else:
            self.values += msg.get_values()
        self.counter += 1
        return True

    def clear_cache(self):
        self.values, self.counter = None, 0

    def cache_is_full(self):
        return self.counter == self.interval


# Test utility class multiplying single value
class pp_mult_operator(operator.operator_base):
    def __init__(self, factor=0.5):
        super(pp_mult_operator, self).__init__()
        self.factor = factor

    def fill_cache(self, msg):
        self.values = self.factor * msg.get_values()
        return True


# Test utility function creating messages
def make_msg(code, time, level_index, values):
    data = {message.variable_key: cmor_source.ifs_source(code=cmor_source.grib_code(code, 128)),
            message.datetime_key: time,
            message.timebounds_key: (time, time),
            message.leveltype_key: grib_file.hybrid_level_code,
            message.levellist_key: [level_index],
            message.resolution_key: 512,
            "values": values}
    return message.memory_message(**data)


class post_proc_operator_test(unittest.TestCase):

    @staticmethod
    def test_start_with_empty_cache():
        operator_1 = pp_sum_operator()
        operator_2 = pp_mult_operator()
        ok_(operator_1.cache_is_empty)
        ok_(operator_2.cache_is_empty)

    @staticmethod
    def test_receive_msg():
        operator = pp_sum_operator()
        operator.cached_properties = [message.variable_key, message.leveltype_key, message.levellist_key]
        time = datetime(1990, 1, 1, 6, 0, 0)
        operator.receive_msg(make_msg(130, time, 90, values=285.87))
        eq_(operator.property_cache,
            {message.variable_key: cmor_source.ifs_source(cmor_source.grib_code(130, 128)),
             message.leveltype_key: grib_file.hybrid_level_code,
             message.levellist_key: [90]})
        operator.receive_msg(make_msg(130, time, 90, values=214.13))
        eq_(operator.values, 500.)
        operator.receive_msg(make_msg(131, time, 90, values=-6.5))
        eq_(operator.values, 500.)

    @staticmethod
    def test_create_msg():
        operator = pp_sum_operator()
        operator.cached_properties = [message.variable_key,
                                      message.leveltype_key,
                                      message.levellist_key,
                                      message.datetime_key,
                                      message.timebounds_key,
                                      message.resolution_key]
        time = datetime(1990, 1, 1, 6, 0, 0)
        operator.receive_msg(make_msg(130, time, 90, values=285.87))
        operator.receive_msg(make_msg(130, time, 90, values=214.13))
        msg = operator.create_msg()
        eq_(msg.get_variable(), cmor_source.ifs_source(cmor_source.grib_code(130, 128)))
        eq_(msg.get_levels(), [90])
        eq_(msg.get_values(), 500.)

    @staticmethod
    def test_transfer_msg():
        operator_1, operator_2, operator_3 = pp_mult_operator(factor=2.0), pp_sum_operator(
            interval=8), pp_mult_operator(factor=0.3)
        operator_2.targets.append(operator_3)
        operator_1.targets.append(operator_2)
        result = 0
        time = datetime(1990, 1, 1, 6, 0, 0)
        for i in range(8):
            val = 273.5 + i
            result += 2.0 * val
            operator_1.receive_msg(make_msg(130, time, 90, values=val))
            if i < 7:
                ok_(operator_3.cache_is_empty())
        ok_(operator_3.cache_is_full())
        final_msg = operator_3.create_msg()
        eq_(final_msg.get_values(), 0.3 * result)
