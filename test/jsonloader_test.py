import os
import logging
import unittest
from nose.tools import eq_,ok_,raises
import jsonloader
import ece2cmor
import cmor_source
import cmor_task

logging.basicConfig(level=logging.DEBUG)

configfile = os.path.join(os.path.dirname(__file__),"test_data","cmor3_metadata.json")

class namloader_test(unittest.TestCase):

    def test_load_clt(self):
        ece2cmor.initialize(configfile)
        try:
            jsonloader.load_targets({"3hr":["clt"]})
            eq_(len(ece2cmor.tasks),1)
            src = ece2cmor.tasks[0].source
            eq_(src.get_grib_code().var_id,164)
        finally:
            ece2cmor.finalize()
    def test_load_avars(self):
        ece2cmor.initialize(configfile)
        try:
            jsonloader.load_targets({"3hr":["clt","uas","vas"],"Amon":["vas","tas"]})
            eq_(len(ece2cmor.tasks),5)
            eq_(2,len([t.source.get_grib_code().var_id for t in ece2cmor.tasks if t.target.variable == "vas"]))
        finally:
            ece2cmor.finalize()

    def test_load_ovars(self):
        ece2cmor.initialize(configfile)
        try:
            jsonloader.load_targets({"Omon":["tossq","so","thetao"],"Oday":["sos"]})
            eq_(len(ece2cmor.tasks),4)
        finally:
            ece2cmor.finalize()

    def test_load_oavars(self):
        ece2cmor.initialize(configfile)
        try:
            jsonloader.load_targets({"3hr":["clt","uas"],"Amon":["vas","tas"],"Omon":["tossq"]})
            eq_(len(ece2cmor.tasks),5)
            eq_(4,len([t for t in ece2cmor.tasks if isinstance(t.source,cmor_source.ifs_source)]))
            eq_(1,len([t for t in ece2cmor.tasks if isinstance(t.source,cmor_source.nemo_source)]))
        finally:
            ece2cmor.finalize()

    def test_load_unit_conv(self):
        ece2cmor.initialize(configfile)
        try:
            jsonloader.load_targets({"Amon":["prc","rsus","zg"]})
            eq_(len(ece2cmor.tasks),3)
            prctask = [t for t in ece2cmor.tasks if t.target.variable == "prc"][0]
            rsustask = [t for t in ece2cmor.tasks if t.target.variable == "rsus"][0]
            zgtask = [t for t in ece2cmor.tasks if t.target.variable == "zg"][0]
            eq_("vol2flux",getattr(prctask,cmor_task.conversion_key))
            eq_("cum2inst",getattr(rsustask,cmor_task.conversion_key))
            eq_("pot2alt",getattr(zgtask,cmor_task.conversion_key))
        finally:
            ece2cmor.finalize()

    def test_load_expressions(self):
        ece2cmor.initialize(configfile)
        try:
            jsonloader.load_targets({"day":["sfcWindmax"]})
            eq_("var214=sqrt(sqr(var165)+sqr(var166))",getattr(ece2cmor.tasks[0].source,"expr"))
        finally:
            ece2cmor.finalize()
