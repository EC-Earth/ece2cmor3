import logging
import unittest
import os
from dateutil.relativedelta import relativedelta
from nose.tools import eq_,ok_
import cmor_target

logging.basicConfig(level=logging.DEBUG)

def get_table_path(tab_id = None):
    directory = os.path.join(os.path.dirname(cmor_target.__file__),"resources","tables")
    return os.path.join(directory,"CMIP6_" + tab_id + ".json") if tab_id else directory

class cmor_target_tests(unittest.TestCase):

    def test_get_table_id(self):
        fname="dir1/dir2/dir3/CMIP6_Omon.json"
        tid=cmor_target.get_table_id(fname,"CMIP6")
        eq_("Omon",tid)

    def test_make_Omon_vars(self):
        abspath=get_table_path("Omon")
        targets=cmor_target.create_targets(abspath,"CMIP6")
        ok_(len(targets)>0)
        toss=[t for t in targets if t.variable=="tos"]
        eq_(len(toss),1)
        tos=toss[0]
        eq_(tos.frequency,"mon")
        eq_(tos.units,"degC")
        eq_(tos.dimensions,"longitude latitude time")

    def test_make_CMIP6_vars(self):
        abspath=get_table_path()
        targets=cmor_target.create_targets(abspath,"CMIP6")
        ok_(len(targets)>0)
        toss=[t for t in targets if t.variable=="tos"]
        eq_(len(toss),3)
        tosfreqs=[v.frequency for v in toss]
        ok_("mon" in tosfreqs)
        ok_("day" in tosfreqs)

    def test_cell_measures(self):
        abspath=get_table_path()
        targets=cmor_target.create_targets(abspath,"CMIP6")
        tasmin = [t for t in targets if t.table == "day" and t.variable == "tasmin"][0]
        ok_(hasattr(tasmin,"time_operator"))
        ok_(getattr(tasmin,"time_operator"),"minimum")
