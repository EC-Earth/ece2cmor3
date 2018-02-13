import logging
import unittest
from nose.tools import ok_,eq_
from datetime import datetime
from ece2cmor3 import cmor_source,ppmsg,grib_file

logging.basicConfig(level=logging.DEBUG)

class pp_message_test(unittest.TestCase):

    def test_get_field(self):
        varid = 131
        tabid = 128
        timestamp = datetime(1990,1,1,4,30,22)
        levtype = 100
        levlist = [85000,5000,450]
        code = cmor_source.grib_code(varid,tabid)
        source = cmor_source.ifs_source(code)
        msg = ppmsg.memory_message(source, timestamp, levels=levlist, leveltype=levtype, values=None)
        eq_(msg.get_field(ppmsg.message.variable_key).get_root_codes(),[code])
        eq_(msg.get_field(ppmsg.message.datetime_key),timestamp)
        eq_(msg.get_field(ppmsg.message.leveltype_key),levtype)
        eq_(msg.get_field(ppmsg.message.levellist_key),levlist)

    def test_get_undefined_field(self):
        varid = 131
        tabid = 128
        timestamp = datetime(1990,1,1,4,30,22)
        levtype = 100
        levlist = [85000,5000,450]
        code = cmor_source.grib_code(varid,tabid)
        source = cmor_source.ifs_source(code)
        msg = ppmsg.memory_message(source, timestamp, levels=levlist, leveltype=levtype, values=None)
        ok_(msg.get_field("nonexisting_key") is None)

    def test_grib_message(self):
        varid = 131
        tabid = 128
        timestamp = datetime(1990,1,1,4,30)
        date,time = 19900101,430
        levtype = 100
        levlist = [85000]
        grbmsg = {grib_file.param_key : 131,
                  grib_file.date_key: date,
                  grib_file.time_key: time,
                  grib_file.levtype_key: levtype,
                  grib_file.level_key: levlist[0]}
        msg = ppmsg.grib_message(grbmsg)
        eq_(msg.get_field(ppmsg.message.variable_key).get_root_codes()[0].var_id,varid)
        eq_(msg.get_field(ppmsg.message.variable_key).get_root_codes()[0].tab_id,tabid)
        eq_(msg.get_field(ppmsg.message.datetime_key),timestamp)
        eq_(msg.get_field(ppmsg.message.leveltype_key),levtype)
        eq_(msg.get_field(ppmsg.message.levellist_key),levlist)
