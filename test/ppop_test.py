import logging
import unittest
from nose.tools import ok_,eq_
from ece2cmor3 import ppop, ppmsg, grib_file

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
        self.full_cache = (self.counter == self.interval)

    def clear_cache(self):
        self.values, self.counter = None, 0

# Test utility class multiplying single value
class pp_mult_operator(ppop.post_proc_operator):
    def __init__(self,factor = 0.5):
        super(pp_mult_operator, self).__init__()
        self.factor = factor

    def fill_cache(self,msg):
        self.values = self.factor * msg.get_values()
        self.full_cache = True

    def clear_cache(self):
        self.values, self.counter = None, False

# Test utility function creating messages
def make_msg(code, date, time, level_index, values):
    grbmsg = {grib_file.param_key : code, grib_file.date_key: date, grib_file.time_key: time,
              grib_file.levtype_key: 99, grib_file.level_key: level_index, "values": values}
    return ppmsg.grib_message(grbmsg)


class post_proc_operator_test(unittest.TestCase):

    def test_collect(self):
        operator = pp_sum_operator()
        operator.coherency_keys = [ppmsg.message.variable_key,ppmsg.message.leveltype_key,ppmsg.message.levellist_key]
        operator.collect(make_msg(130, 19900101, 600, 90, values=285.87))
        operator.collect(make_msg(130, 19900101, 600, 90, values=214.13))
        eq_(operator.values, 500.)
        operator.collect(make_msg(131, 19900101, 600, 90, values=-6.5))
        eq_(operator.values, 500.)
