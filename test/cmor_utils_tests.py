import logging
import unittest
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from nose.tools import eq_,ok_
from cmor_utils import make_time_intervals,find_ifs_output,get_ifs_steps,find_nemo_output,get_nemo_interval

logging.basicConfig(level=logging.DEBUG)

class utils_tests(unittest.TestCase):

    def test_intervals_30days(self):
        t1=datetime(1999,12,31,23,45,20)
        t2=datetime(2003,8,29,12,0,0)
        intervals=make_time_intervals(t1,t2,timedelta(days=30))
        eq_(intervals[-1][1],t2)


    def test_intervals_month(self):
        t1=datetime(2000,1,1,23,45,20)
        t2=datetime(2003,8,29,12,0,0)
        intervals=make_time_intervals(t1,t2,relativedelta(months=+1))
        eq_(intervals[-1][0],datetime(2003,8,1,23,45,20))


    def test_find_ifs_output(self):
        ofiles=find_ifs_output("./test_data/ifs_dummy")
        eq_(len(ofiles),2)
        ok_("./test_data/ifs_dummy/ICMGGGbla+003456" in ofiles)
        ok_("./test_data/ifs_dummy/ICMSHok+004321" in ofiles)


    def test_find_ifs_exp_output(self):
        ofiles=find_ifs_output("./test_data/ifs_dummy","ok")
        eq_(len(ofiles),1)
        ok_("./test_data/ifs_dummy/ICMSHok+004321" in ofiles)


    def test_ifs_output_timestamps(self):
        ofiles=find_ifs_output("./test_data/ifs_dummy","Gbla")
        eq_(len(ofiles),1)
        eq_(get_ifs_steps(ofiles[0]),3456)


    def test_find_nemo_output(self):
        ofiles=find_nemo_output("./test_data/nemo_dummy")
        eq_(len(ofiles),2)
        ok_("./test_data/nemo_dummy/exp_1m_19991231_20000505_gridT.nc" in ofiles)
        ok_("./test_data/nemo_dummy/exp_1d_19991221_20000101_icemod.nc" in ofiles)


    def test_find_nemo_exp_output(self):
        ofiles=find_nemo_output("./test_data/nemo_dummy","exp")
        eq_(len(ofiles),2)
        ok_("./test_data/nemo_dummy/exp_1m_19991231_20000505_gridT.nc" in ofiles)
        ok_("./test_data/nemo_dummy/exp_1d_19991221_20000101_icemod.nc" in ofiles)


    def test_nemo_bad_output(self):
        ofiles=find_nemo_output("./test_data/nemo_dummy","bad")
        eq_(len(ofiles),0)


    def test_nemo_output_timestamps(self):
        ofiles=find_nemo_output("./test_data/nemo_dummy","exp")
        dates=[get_nemo_interval(f) for f in ofiles]
        starts=sorted([t[0] for t in dates])
        eq_([datetime(1999,12,21),datetime(1999,12,31)],starts)
        ends=sorted([t[1] for t in dates])
        eq_([datetime(2000,1,1),datetime(2000,5,5)],ends)
