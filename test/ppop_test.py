import logging
import unittest
from nose.tools import ok_,eq_
from ece2cmor3 import ppop, ppmsg, grib_file, cmor_source

logging.basicConfig(level=logging.DEBUG)

# Test utility class summing last 10 values
class pp_sum_operator(ppop.post_proc_operator):

    def __init__(self, interval = 10):
        super(pp_sum_operator, self).__init__()
        self.counter = 0
        self.interval = interval

    def fill_cache(self, msg):
        if(self.values is None):
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
class pp_mult_operator(ppop.post_proc_operator):
    def __init__(self,factor = 0.5):
        super(pp_mult_operator, self).__init__()
        self.factor = factor

    def fill_cache(self,msg):
        self.values = self.factor * msg.get_values()
        return True

# Test utility function creating messages
def make_msg(code, date, time, level_index, values):
    grbmsg = {grib_file.param_key : code, grib_file.date_key: date, grib_file.time_key: time,
              grib_file.levtype_key: 99, grib_file.level_key: level_index, "values": values}
    return ppmsg.grib_message(grbmsg)


class post_proc_operator_test(unittest.TestCase):

    def test_start_with_empty_cache(self):
        operator_1 = pp_sum_operator()
        operator_2 = pp_mult_operator()
        ok_(operator_1.cache_is_empty)
        ok_(operator_2.cache_is_empty)

    def test_receive_msg(self):
        operator = pp_sum_operator()
        operator.cached_properties = [ppmsg.message.variable_key,ppmsg.message.leveltype_key,ppmsg.message.levellist_key]
        operator.receive_msg(make_msg(130, 19900101, 600, 90, values=285.87))
        eq_(operator.property_cache,{ppmsg.message.variable_key : cmor_source.ifs_source(cmor_source.grib_code(130,128)),
                                     ppmsg.message.leveltype_key : 99,
                                     ppmsg.message.levellist_key : [90]})
        operator.receive_msg(make_msg(130, 19900101, 600, 90, values=214.13))
        eq_(operator.values, 500.)
        operator.receive_msg(make_msg(131, 19900101, 600, 90, values=-6.5))
        eq_(operator.values, 500.)

    def test_create_msg(self):
        operator = pp_sum_operator()
        operator.cached_properties = [ppmsg.message.variable_key,
                                      ppmsg.message.leveltype_key,
                                      ppmsg.message.levellist_key,
                                      ppmsg.message.datetime_key]
        operator.receive_msg(make_msg(130, 19900101, 600, 90, values=285.87))
        operator.receive_msg(make_msg(130, 19900101, 600, 90, values=214.13))
        msg = operator.create_msg()
        eq_(msg.get_variable(),cmor_source.ifs_source(cmor_source.grib_code(130,128)))
        eq_(msg.get_levels(),[90])
        eq_(msg.get_level_type(),99)
        eq_(msg.get_values(),500.)

    def test_transfer_msg(self):
        operator_1,operator_2,operator_3 = pp_mult_operator(factor = 2.0),pp_sum_operator(interval = 8),pp_mult_operator(factor = 0.3)
        operator_2.targets.append(operator_3)
        operator_1.targets.append(operator_2)
        result = 0
        for i in range(8):
            val = 273.5 + i
            result += 2.0 * val
            operator_1.receive_msg(make_msg(130, 19900101, 600, 90, values=val))
            if i < 7:
                ok_(operator_3.cache_is_empty())
        ok_(operator_3.cache_is_full())
        final_msg = operator_3.create_msg()
        eq_(final_msg.get_values(),0.3 * result)
