import logging
import unittest
from datetime import datetime
from nose.tools import ok_, eq_
from ece2cmor3 import grib_file, cmor_source
from ece2cmor3.postproc import message, operator

logging.basicConfig(level=logging.DEBUG)


# Test utility class summing last 10 values
class sum_operator(operator.operator_base):

    def __init__(self, interval=10):
        super(sum_operator, self).__init__()
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
        return super(sum_operator, self).cache_is_full() and self.counter == self.interval


# Test utility class multiplying single value
class multiply_operator(operator.operator_base):
    def __init__(self, factor=0.5):
        super(multiply_operator, self).__init__()
        self.factor = factor

    def fill_cache(self, msg):
        self.values = self.factor * msg.get_values()
        return True


# Test utility class multiplying single value with mask
class masked_multiply_operator(operator.operator_base):
    def __init__(self, factor=0.5):
        super(masked_multiply_operator, self).__init__()
        self.mask_key = (172, 128, grib_file.hybrid_level_code, 22)
        self.factor = factor

    def fill_cache(self, msg):
        mask_factor = -1 if self.mask_values < 0.5 else 1
        self.values = mask_factor * self.factor * msg.get_values()
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
        operator_1 = sum_operator()
        operator_2 = multiply_operator()
        ok_(operator_1.cache_is_empty)
        ok_(operator_2.cache_is_empty)

    @staticmethod
    def test_receive_msg():
        op = sum_operator()
        op.cached_properties = [message.variable_key, message.leveltype_key, message.levellist_key]
        time = datetime(1990, 1, 1, 6, 0, 0)
        op.receive_msg(make_msg(130, time, 90, values=285.87))
        eq_(op.property_cache,
            {message.variable_key: cmor_source.ifs_source(cmor_source.grib_code(130, 128)),
             message.leveltype_key: grib_file.hybrid_level_code,
             message.levellist_key: [90]})
        op.receive_msg(make_msg(130, time, 90, values=214.13))
        eq_(op.values, 500.)
        op.receive_msg(make_msg(131, time, 90, values=-6.5))
        eq_(op.values, 500.)

    @staticmethod
    def test_fill_cache():
        op = sum_operator()
        op.cached_properties = [message.variable_key,
                                message.leveltype_key,
                                message.levellist_key,
                                message.datetime_key,
                                message.timebounds_key,
                                message.resolution_key]
        time = datetime(1990, 1, 1, 6, 0, 0)
        value = 0.
        tot_value = 0.
        for i in range(9):
            value += i * i
            tot_value += value
            op.receive_msg(make_msg(130, time, 90, values=value))
        ok_(not op.cache_is_full())
        value -= 10.
        tot_value += value
        op.receive_msg(make_msg(130, time, 90, values=value))
        ok_(op.cache_is_full())
        msg = op.create_msg()
        eq_(msg.get_variable(), cmor_source.ifs_source(cmor_source.grib_code(130, 128)))
        eq_(msg.get_levels(), [90])
        eq_(msg.get_values(), tot_value)

    @staticmethod
    def test_transfer_msg():
        op1, op2, op3 = multiply_operator(factor=2.0), sum_operator(interval=8), multiply_operator(factor=0.3)
        op2.targets.append(op3)
        op1.targets.append(op2)
        result = 0
        time = datetime(1990, 1, 1, 6, 0, 0)
        for i in range(8):
            val = 273.5 + i
            result += 2.0 * val
            op1.receive_msg(make_msg(130, time, 90, values=val))
            if i < 7:
                ok_(op3.cache_is_empty())
        ok_(op3.cache_is_full())
        final_msg = op3.create_msg()
        eq_(final_msg.get_values(), 0.3 * result)

    # @staticmethod
    # def test_receive_store_var():
    #     op = sum_operator()
    #     op.cached_properties = [message.variable_key,
    #                             message.leveltype_key,
    #                             message.levellist_key,
    #                             message.datetime_key,
    #                             message.timebounds_key,
    #                             message.resolution_key]
    #     op.store_var_key = (134, 128, grib_file.hybrid_level_code, 91)
    #     time = datetime(1990, 1, 1, 6, 0, 0)
    #     value = 0.
    #     tot_value = 0.
    #     for i in range(10):
    #         value += i * i
    #         tot_value += value
    #         op.receive_msg(make_msg(130, time, 90, values=value))
    #     ok_(not op.cache_is_full())
    #     op.receive_store_var(make_msg(134, time, 91, values=tot_value))
    #     ok_(op.cache_is_full())
    #
    # @staticmethod
    # def test_receive_mask():
    #     op1, op2, op3 = masked_multiply_operator(factor=2.0), sum_operator(interval=8), masked_multiply_operator(factor=0.3)
    #     op2.targets.append(op3)
    #     op1.targets.append(op2)
    #     result = 0
    #     time = datetime(1990, 1, 1, 6, 0, 0)
    #     op1.receive_mask(make_msg(170, time, 22, values=0.6))
    #     for i in range(8):
    #         val = 273.5 + i
    #         result += 2.0 * val
    #         op1.receive_msg(make_msg(130, time, 90, values=val))
    #     ok_(op1.cache_is_full())
    #     ok_(not op3.cache_is_full())
    #     op3.receive_mask(make_msg(170, time, 22, values=0.4))
    #     ok_(op3.cache_is_full())
    #     final_msg = op3.create_msg()
    #     eq_(final_msg.get_values(), - 0.3 * result)
