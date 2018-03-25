import logging
import unittest

from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy
from nose.tools import ok_, eq_
from ece2cmor3 import ppmsg, pptime, grib_file

logging.basicConfig(level=logging.DEBUG)


def linear_up(t0, t, x0, x):
    return x0 + x * (t - t0).total_seconds() / (3600 * 24)


def linear_down(t0, t, x0, x):
    return x0 - x * (t - t0).total_seconds() / (3600 * 24)


def sine(t0, t, x0, x):
    return x0 + x * numpy.math.sin(2 * numpy.math.pi * (t - t0).total_seconds() / (3600 * 24))


# Test utility function creating messages
def make_msgs(code, start_date, length, interval, level_index, level_type, amplitude, start_value, func):
    result = []
    time = start_date
    while time <= start_date + length:
        value = func(start_date, time, start_value, amplitude)
        bnds = (time - length/2,time + length/2)
        data = {ppmsg.message.variable_key: code,
                ppmsg.message.datetime_key: time,
                ppmsg.message.timebounds_key: bnds,
                ppmsg.message.leveltype_key: level_type,
                ppmsg.message.levellist_key: [level_index],
                ppmsg.message.resolution_key: 512,
                "values": value}
        result.append(ppmsg.memory_message(**data))
        time = time + interval
    return result


class time_aggregator_test(unittest.TestCase):

    @staticmethod
    def test_block_left_daymean():
        operator = pptime.time_aggregator(pptime.time_aggregator.block_left_operator, interval=relativedelta(days=1))
        msgs = make_msgs(165, datetime(1990, 1, 1), relativedelta(days=1), relativedelta(hours=3), 0, 1, 2.5,
                         numpy.array([1.0, -1.0]), linear_up)
        for msg in msgs:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        average = sum([m.get_values() for m in msgs[:-1]]) / (len(msgs) - 1)
        ok_(all(operator.create_msg().get_values() == average))
        operator.clear_cache()
        msgs2 = make_msgs(165, datetime(1990, 1, 2, 3), relativedelta(hours=21), relativedelta(hours=3), 0, 1, 3.5,
                          numpy.array([3.0, 2.0]), linear_up)
        for msg in msgs2:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        average = sum([m.get_values() for m in [msgs[-1]] + msgs2[:-1]]) / len(msgs2)
        ok_(all(operator.create_msg().get_values() == average))

    @staticmethod
    def test_block_left_daymean2():
        operator = pptime.time_aggregator(pptime.time_aggregator.block_left_operator, interval=relativedelta(days=1))
        msgs = make_msgs(165, datetime(1990, 1, 1), relativedelta(days=1), relativedelta(hours=3), 0, 1, 2.5,
                         numpy.array([1.0, -1.0]), sine)
        for msg in msgs:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        average = sum([m.get_values() for m in msgs[:-1]]) / (len(msgs) - 1)
        ok_(all(operator.create_msg().get_values() == average))
        operator.clear_cache()
        msgs2 = make_msgs(165, datetime(1990, 1, 2, 3), relativedelta(hours=21), relativedelta(hours=3), 0, 1, 3.5,
                          numpy.array([3.0, 2.0]), linear_down)
        for msg in msgs2:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        average = sum([m.get_values() for m in [msgs[-1]] + msgs2[:-1]]) / len(msgs2)
        ok_(all(operator.create_msg().get_values() == average))

    @staticmethod
    def test_block_right_daymean():
        operator = pptime.time_aggregator(pptime.time_aggregator.block_right_operator, interval=relativedelta(days=1))
        msgs = make_msgs(165, datetime(1990, 1, 1), relativedelta(days=1), relativedelta(hours=3), 0, 1, 2.5,
                         numpy.array([1.0, -1.0]), linear_up)
        for msg in msgs:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        average = sum([m.get_values() for m in msgs[1:]]) / (len(msgs) - 1)
        ok_(all(operator.create_msg().get_values() == average))
        operator.clear_cache()
        msgs2 = make_msgs(165, datetime(1990, 1, 2, 3), relativedelta(hours=21), relativedelta(hours=3), 0, 1, 3.5,
                          numpy.array([3.0, 2.0]), linear_up)
        for msg in msgs2:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        average = sum([m.get_values() for m in msgs2]) / len(msgs2)
        ok_(all(operator.create_msg().get_values() == average))

    @staticmethod
    def test_block_right_daymean2():
        operator = pptime.time_aggregator(pptime.time_aggregator.block_right_operator, interval=relativedelta(days=1))
        msgs = make_msgs(165, datetime(1990, 1, 1), relativedelta(days=1), relativedelta(hours=3), 0, 1, 2.5,
                         numpy.array([1.0, -1.0]), sine)
        for msg in msgs:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        average = sum([m.get_values() for m in msgs[1:]]) / (len(msgs) - 1)
        ok_(all(operator.create_msg().get_values() == average))
        operator.clear_cache()
        msgs2 = make_msgs(165, datetime(1990, 1, 2, 3), relativedelta(hours=21), relativedelta(hours=3), 0, 1, 3.5,
                          numpy.array([3.0, 2.0]), linear_down)
        for msg in msgs2:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        average = sum([m.get_values() for m in msgs2]) / len(msgs2)
        ok_(all(operator.create_msg().get_values() == average))

    @staticmethod
    def test_linear_daymean():
        operator = pptime.time_aggregator(pptime.time_aggregator.linear_mean_operator, interval=relativedelta(days=1))
        msgs = make_msgs(165, datetime(1990, 1, 1), relativedelta(days=1), relativedelta(hours=3), 0, 1, 2.5,
                         numpy.array([1.0, -1.0]), linear_up)
        for msg in msgs:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        average = sum([m.get_values() for m in msgs]) / (len(msgs) - 1) \
                  - 0.5 * (msgs[0].get_values() + msgs[-1].get_values()) / (len(msgs) - 1)
        ok_(all(operator.create_msg().get_values() == average))
        operator.clear_cache()
        msgs2 = make_msgs(165, datetime(1990, 1, 2, 3), relativedelta(hours=21), relativedelta(hours=3), 0, 1, 3.5,
                          numpy.array([5.0, 3.0]), linear_up)
        for msg in msgs2:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        average = sum([m.get_values() for m in [msgs[-1]] + msgs2[:]]) / (len(msgs2)) \
                  - 0.5 * (msgs[-1].get_values() + msgs2[-1].get_values()) / len(msgs2)
        ok_(all(operator.create_msg().get_values() == average))

    @staticmethod
    def test_linear_daymean2():
        operator = pptime.time_aggregator(pptime.time_aggregator.linear_mean_operator, interval=relativedelta(days=1))
        msgs = make_msgs(165, datetime(1990, 1, 1), relativedelta(days=1), relativedelta(hours=3), 0, 1, 2.5,
                         numpy.array([1.0, -1.0]), linear_down)
        for msg in msgs:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        average = sum([m.get_values() for m in msgs]) / (len(msgs) - 1) \
                  - 0.5 * (msgs[0].get_values() + msgs[-1].get_values()) / (len(msgs) - 1)
        ok_(all(numpy.abs(operator.create_msg().get_values() - average) < 1e-8))
        operator.clear_cache()
        msgs2 = make_msgs(165, datetime(1990, 1, 2, 3), relativedelta(hours=21), relativedelta(hours=3), 0, 1, 3.5,
                          numpy.array([5.0, 3.0]), sine)
        for msg in msgs2:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        average = sum([m.get_values() for m in [msgs[-1]] + msgs2[:]]) / (len(msgs2)) \
                  - 0.5 * (msgs[-1].get_values() + msgs2[-1].get_values()) / len(msgs2)
        ok_(all(numpy.abs(operator.create_msg().get_values() - average) < 1e-8))

    @staticmethod
    def test_daymin():
        operator = pptime.time_aggregator(pptime.time_aggregator.min_operator, interval=relativedelta(days=1))
        msgs = make_msgs(165, datetime(1990, 1, 1), relativedelta(days=1), relativedelta(hours=3), 0, 1, 2.5,
                         numpy.array([2.0, 3.0]), linear_down)
        for msg in msgs:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        minvals = msgs[-2].get_values()
        ok_(all(operator.create_msg().get_values() == minvals))
        operator.clear_cache()
        msgs2 = make_msgs(165, datetime(1990, 1, 2, 3), relativedelta(hours=21), relativedelta(hours=3), 0, 1, 3.5,
                          numpy.array([0.0, 1.0]), linear_up)
        for msg in msgs2:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        minvals = msgs[-1].get_values()
        ok_(all(operator.create_msg().get_values() == minvals))

    @staticmethod
    def test_daymax():
        operator = pptime.time_aggregator(pptime.time_aggregator.max_operator, interval=relativedelta(days=1))
        msgs = make_msgs(165, datetime(1990, 1, 1), relativedelta(days=1), relativedelta(hours=3), 0, 1, 2.5,
                         numpy.array([20.0, 30.0]), linear_down)
        for msg in msgs:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        maxvals = msgs[0].get_values()
        ok_(all(operator.create_msg().get_values() == maxvals))
        operator.clear_cache()
        msgs2 = make_msgs(165, datetime(1990, 1, 2, 3), relativedelta(hours=21), relativedelta(hours=3), 0, 1, 3.5,
                          numpy.array([20.0, 30.0]), linear_up)
        for msg in msgs2:
            operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        maxvals = msgs2[-2].get_values()
        ok_(all(operator.create_msg().get_values() == maxvals))
