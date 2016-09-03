import logging
import unittest
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from nose.tools import eq_,ok_
from cmorutils import make_time_intervals,find_ifs_output,get_ifs_steps

logging.basicConfig(level=logging.DEBUG)

class TestTimeIntervals(unittest.TestCase):

    def test1(self):
        t1=datetime(1999,12,31,23,45,20)
        t2=datetime(2003,8,29,12,0,0)
        intervals=make_time_intervals(t1,t2,timedelta(days=30))
        eq_(intervals[-1][1],t2)


    def test2(self):
        t1=datetime(2000,1,1,23,45,20)
        t2=datetime(2003,8,29,12,0,0)
        intervals=make_time_intervals(t1,t2,relativedelta(months=+1))
        eq_(intervals[-1][0],datetime(2003,8,1,23,45,20))

    def test3(self):
        ofiles=find_ifs_output('./test_data')
        eq_(len(ofiles),2)
        ok_('./test_data/ICMGGGbla+003456' in ofiles)
        ok_('./test_data/ICMSHok+004321' in ofiles)

    def test4(self):
        ofiles=find_ifs_output('./test_data','ok')
        eq_(len(ofiles),1)
        ok_('./test_data/ICMSHok+004321' in ofiles)

    def test4(self):
        ofiles=find_ifs_output('./test_data','Gbla')
        eq_(len(ofiles),1)
        eq_(get_ifs_steps(ofiles[0]),3456)
