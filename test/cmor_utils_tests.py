import logging
import unittest
import os
import datetime
from dateutil.relativedelta import relativedelta
from nose.tools import eq_,ok_,raises
from cmor_utils import make_time_intervals,find_ifs_output,get_ifs_date,find_nemo_output,get_nemo_interval,get_nemo_frequency,get_nemo_grid,group

logging.basicConfig(level=logging.DEBUG)

class utils_tests(unittest.TestCase):

    def test_group(self):
        t1=("a",3)
        t2=("b",4)
        t3=("c",6)
        t4=("d",11)
        d=group([t1,t2,t3,t4],lambda t: t[1]%2)
        eq_(d[0],[t2,t3])
        eq_(d[1],[t1,t4])

    def test_intervals_30days(self):
        t1=datetime.datetime(1999,12,31,23,45,20)
        t2=datetime.datetime(2003,8,29,12,0,0)
        intervals=make_time_intervals(t1,t2,datetime.timedelta(days=30))
        eq_(intervals[-1][1],t2)


    def test_intervals_month(self):
        t1=datetime.datetime(2000,1,1,23,45,20)
        t2=datetime.datetime(2003,8,29,12,0,0)
        intervals=make_time_intervals(t1,t2,relativedelta(months=+1))
        eq_(intervals[-1][0],datetime.datetime(2003,8,1,23,45,20))


    def test_find_ifs_output(self):
        ofiles=find_ifs_output(os.path.join(os.path.dirname(__file__),"test_data","ifs_dummy"))
        eq_(len(ofiles),3)
        ok_(os.path.join(os.path.dirname(__file__),"test_data","ifs_dummy","ICMGGGbla+003456") in ofiles)
        ok_(os.path.join(os.path.dirname(__file__),"test_data","ifs_dummy","ICMSHok+004321") in ofiles)


    def test_find_ifs_exp_output(self):
        ofiles=find_ifs_output(os.path.join(os.path.dirname(__file__),"test_data","ifs_dummy"),"ok")
        eq_(len(ofiles),1)
        ok_(os.path.join(os.path.dirname(__file__),"test_data","ifs_dummy","ICMSHok+004321") in ofiles)


    def test_ifs_output_date(self):
        ofile=os.path.join(os.path.dirname(__file__),"test_data","ICMGG+199011")
        eq_(get_ifs_date(ofile),datetime.date(1990,11,1))


    def test_find_nemo_output(self):
        ofiles=find_nemo_output(os.path.join(os.path.dirname(__file__),"test_data","nemo_dummy"))
        eq_(len(ofiles),2)
        ok_(os.path.join(os.path.dirname(__file__),"test_data","nemo_dummy","exp_1m_19991231_20000505_gridT.nc") in ofiles)
        ok_(os.path.join(os.path.dirname(__file__),"test_data","nemo_dummy","exp_1d_19991221_20000101_icemod.nc") in ofiles)


    def test_find_nemo_exp_output(self):
        ofiles=find_nemo_output(os.path.join(os.path.dirname(__file__),"test_data","nemo_dummy"),"exp")
        eq_(len(ofiles),2)
        ok_(os.path.join(os.path.dirname(__file__),"test_data","nemo_dummy","exp_1m_19991231_20000505_gridT.nc") in ofiles)
        ok_(os.path.join(os.path.dirname(__file__),"test_data","nemo_dummy","exp_1d_19991221_20000101_icemod.nc") in ofiles)


    def test_nemo_bad_output(self):
        ofiles=find_nemo_output(os.path.join(os.path.dirname(__file__),"test_data","nemo_dummy"),"bad")
        eq_(len(ofiles),0)


    def test_nemo_output_timestamps(self):
        ofiles=find_nemo_output(os.path.join(os.path.dirname(__file__),"test_data","nemo_dummy"),"exp")
        dates=[get_nemo_interval(f) for f in ofiles]
        starts=sorted([t[0] for t in dates])
        eq_([datetime.datetime(1999,12,21),datetime.datetime(1999,12,31)],starts)
        ends=sorted([t[1] for t in dates])
        eq_([datetime.datetime(2000,1,1),datetime.datetime(2000,5,5)],ends)

    def test_get_nemo_frequency(self):
        filepath=os.path.join(os.path.dirname(__file__),"my_exp_3h_19992131_20000102_icemod.nc")
        fstr=get_nemo_frequency(filepath,"my_exp")
        eq_(fstr,"3h")

    @raises(Exception)
    def test_bad_nemo_frequency(self):
        filepath=os.path.join(os.path.dirname(__file__),"my_exp_3h_19992131_20000102_icemod.nc")
        fstr=get_nemo_frequency(filepath,"exp")

    @raises(Exception)
    def test_bad_nemo_frequency2(self):
        filepath=os.path.join(os.path.dirname(__file__),"exp_3s_19992131_20000102_icemod.nc")
        fstr=get_nemo_frequency(filepath,"exp")

    @raises(Exception)
    def test_bad_nemo_frequency3(self):
        filepath=os.path.join(os.path.dirname(__file__),"exp_0d_19992131_20000102_icemod.nc")
        fstr=get_nemo_frequency(filepath,"exp")

    def test_get_nemo_grid(self):
        filepath=os.path.join(os.path.dirname(__file__),"my_exp_3h_19992131_20000102_icemod.nc")
        fstr=get_nemo_grid(filepath,"my_exp")
        eq_(fstr,"icemod")

    def test_get_nemo_grid2(self):
        filepath=os.path.join(os.path.dirname(__file__),"my_exp_3h_19992131_20000102_grid_T.nc")
        fstr=get_nemo_grid(filepath,"my_exp")
        eq_(fstr,"grid_T")

    @raises(Exception)
    def test_bad_nemo_grid(self):
        filepath=os.path.join(os.path.dirname(__file__),"my_exp_3h_19992131_20000102_grid_T.nc")
        fstr=get_nemo_grid(filepath,"exp")
        eq_(fstr,"grid_T")
