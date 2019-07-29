import logging
import unittest
import os
import datetime

import netCDF4
import numpy
from dateutil.relativedelta import relativedelta
from nose.tools import eq_, ok_, raises
from ece2cmor3.cmor_utils import make_time_intervals, find_ifs_output, get_ifs_date, find_nemo_output, get_nemo_grid, \
    group, num2num

logging.basicConfig(level=logging.DEBUG)


class utils_tests(unittest.TestCase):

    @staticmethod
    def test_group():
        t1 = ("a", 3)
        t2 = ("b", 4)
        t3 = ("c", 6)
        t4 = ("d", 11)
        d = group([t1, t2, t3, t4], lambda t: t[1] % 2)
        eq_(d[0], [t2, t3])
        eq_(d[1], [t1, t4])

    @staticmethod
    def test_intervals_30days():
        t1 = datetime.datetime(1999, 12, 31, 23, 45, 20)
        t2 = datetime.datetime(2003, 8, 29, 12, 0, 0)
        intervals = make_time_intervals(t1, t2, datetime.timedelta(days=30))
        eq_(intervals[-1][1], t2)

    @staticmethod
    def test_intervals_month():
        t1 = datetime.datetime(2000, 1, 1, 23, 45, 20)
        t2 = datetime.datetime(2003, 8, 29, 12, 0, 0)
        intervals = make_time_intervals(t1, t2, relativedelta(months=+1))
        eq_(intervals[-1][0], datetime.datetime(2003, 8, 1, 23, 45, 20))

    @staticmethod
    def test_find_ifs_output():
        ofiles = find_ifs_output(os.path.join(os.path.dirname(__file__), "test_data", "ifs_dummy"))
        eq_(len(ofiles), 3)
        ok_(os.path.join(os.path.dirname(__file__), "test_data", "ifs_dummy", "ICMGGGbla+003456") in ofiles)
        ok_(os.path.join(os.path.dirname(__file__), "test_data", "ifs_dummy", "ICMSHok+004321") in ofiles)

    @staticmethod
    def test_find_ifs_exp_output():
        ofiles = find_ifs_output(os.path.join(os.path.dirname(__file__), "test_data", "ifs_dummy"), "ok")
        eq_(len(ofiles), 1)
        ok_(os.path.join(os.path.dirname(__file__), "test_data", "ifs_dummy", "ICMSHok+004321") in ofiles)

    @staticmethod
    def test_ifs_output_date():
        ofile = os.path.join(os.path.dirname(__file__), "test_data", "ICMGG+199011")
        eq_(get_ifs_date(ofile), datetime.date(1990, 11, 1))

    @staticmethod
    def test_find_nemo_output():
        ofiles = find_nemo_output(os.path.join(os.path.dirname(__file__), "test_data", "nemo_dummy"))
        eq_(len(ofiles), 2)
        ok_(os.path.join(os.path.dirname(__file__), "test_data", "nemo_dummy",
                         "exp_1m_19991231_20000505_gridT.nc") in ofiles)
        ok_(os.path.join(os.path.dirname(__file__), "test_data", "nemo_dummy",
                         "exp_1d_19991221_20000101_icemod.nc") in ofiles)

    @staticmethod
    def test_find_nemo_exp_output():
        ofiles = find_nemo_output(os.path.join(os.path.dirname(__file__), "test_data", "nemo_dummy"), "exp")
        eq_(len(ofiles), 2)
        ok_(os.path.join(os.path.dirname(__file__), "test_data", "nemo_dummy",
                         "exp_1m_19991231_20000505_gridT.nc") in ofiles)
        ok_(os.path.join(os.path.dirname(__file__), "test_data", "nemo_dummy",
                         "exp_1d_19991221_20000101_icemod.nc") in ofiles)

    @staticmethod
    def test_nemo_bad_output():
        ofiles = find_nemo_output(os.path.join(os.path.dirname(__file__), "test_data", "nemo_dummy"), "bad")
        eq_(len(ofiles), 0)

    @staticmethod
    def test_get_nemo_grid():
        filepath = os.path.join(os.path.dirname(__file__), "my_exp_3h_19992131_20000102_icemod.nc")
        fstr = get_nemo_grid(filepath, "my_exp")
        eq_(fstr, "icemod")

    @staticmethod
    def test_get_nemo_grid2():
        filepath = os.path.join(os.path.dirname(__file__), "my_exp_3h_19992131_20000102_grid_T.nc")
        fstr = get_nemo_grid(filepath, "my_exp")
        eq_(fstr, "grid_T")

    @raises(Exception)
    def test_bad_nemo_grid(self):
        filepath = os.path.join(os.path.dirname(__file__), "my_exp_3h_19992131_20000102_grid_T.nc")
        fstr = get_nemo_grid(filepath, "exp")
        eq_(fstr, "grid_T")

    @staticmethod
    def test_num2num_gregorian():
        times = numpy.array([datetime.datetime(1849, 12, 15, 12, 30, 30), datetime.datetime(1850, 1, 1, 0, 0, 0),
                             datetime.datetime(1850, 2, 1, 15, 12, 0)])
        units = "days since " + str(datetime.datetime(1830, 6, 6, 12, 0, 0))
        calender = "gregorian"
        ref = datetime.datetime(1850, 1, 1, 0, 0, 0)
        nums = netCDF4.date2num(times, units, calender)
        new_times, new_units = num2num(nums, ref, units, calender)
        eq_(new_times[1], 0.)
        eq_(new_units, "days since " + str(ref))

    @staticmethod
    def test_num2num_proleptic_gregorian():
        times = numpy.array([datetime.datetime(1849, 12, 15, 12, 30, 30), datetime.datetime(1850, 1, 1, 0, 0, 0),
                             datetime.datetime(1850, 2, 1, 15, 12, 0)])
        units = "hours since " + str(datetime.datetime(1830, 6, 6, 12, 0, 0))
        calender = "gregorian"
        ref = datetime.datetime(1850, 1, 1, 0, 0, 0)
        nums = netCDF4.date2num(times, units, calender)
        new_times, new_units = num2num(nums, ref, units, calender)
        eq_(new_times[1], 0.)
        eq_(new_units, "hours since " + str(ref))

    @staticmethod
    def test_num2num_noleap():
        times = numpy.array([datetime.datetime(1849, 12, 15, 12, 30, 30), datetime.datetime(1850, 1, 1, 0, 0, 0),
                             datetime.datetime(1850, 2, 1, 15, 12, 0)])
        units = "days since " + str(datetime.datetime(1830, 6, 6, 12, 0, 0))
        calender = "noleap"
        ref = datetime.datetime(1850, 1, 1, 0, 0, 0)
        nums = netCDF4.date2num(times, units, calender)
        new_times, new_units = num2num(nums, ref, units, calender)
        eq_(new_times[1], 0.)
        eq_(new_units, "days since " + str(ref))

    @staticmethod
    def test_date2num_types():
        times = numpy.array([datetime.datetime(1849, 12, 15, 12, 30, 30), datetime.datetime(1850, 1, 1, 0, 0, 0),
                             datetime.datetime(1850, 2, 1, 15, 12, 0)])
        units = "days since " + str(datetime.datetime(1830, 6, 6, 12, 0, 0))
        calender = "gregorian"
        nums = netCDF4.date2num(times, units, calender)
        dates = netCDF4.num2date(nums, units, calender)
        ok_(isinstance(dates[0], datetime.datetime))
        calender = "noleap"
        nums = netCDF4.date2num(times, units, calender)
        dates = netCDF4.num2date(nums, units, calender)
        ok_(not isinstance(dates[0], datetime.datetime))
