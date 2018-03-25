import logging
import unittest
from nose.tools import ok_, eq_
from datetime import datetime, timedelta
from ece2cmor3 import cmor_source, ppmsg, grib_file

logging.basicConfig(level=logging.DEBUG)


class pp_message_test(unittest.TestCase):

    @staticmethod
    def test_get_field():
        varid = 131
        tabid = 128
        timestamp = datetime(1990, 1, 1, 4, 30, 22)
        timebounds = (timestamp - timedelta(days=1),timestamp + timedelta(days=1))
        levtype = 100
        levlist = [85000, 5000, 450]
        code = cmor_source.grib_code(varid, tabid)
        source = cmor_source.ifs_source(code)
        resolution = 256
        msg = ppmsg.memory_message(variable=source, timestamp=timestamp, timebounds=timebounds, levels=levlist,
                                   leveltype=levtype, resolution=resolution, values=None)
        eq_(msg.get_field(ppmsg.message.variable_key).get_root_codes(), [code])
        eq_(msg.get_field(ppmsg.message.datetime_key), timestamp)
        eq_(msg.get_field(ppmsg.message.timebounds_key), timebounds)
        eq_(msg.get_field(ppmsg.message.leveltype_key), levtype)
        eq_(msg.get_field(ppmsg.message.levellist_key), levlist)
        eq_(msg.get_field(ppmsg.message.resolution_key), resolution)

    @staticmethod
    def test_get_undefined_field():
        varid = 131
        tabid = 128
        timestamp = datetime(1990, 1, 1, 4, 30, 22)
        levtype = 100
        levlist = [85000, 5000, 450]
        resolution = 512
        code = cmor_source.grib_code(varid, tabid)
        source = cmor_source.ifs_source(code)
        msg = ppmsg.memory_message(variable=source, timestamp=timestamp, timebounds=(), levels=levlist,
                                   leveltype=levtype, resolution=resolution, values=None)
        ok_(msg.get_field("nonexisting_key") is None)

    @staticmethod
    # TODO: Fix this
    def test_grib_message():
        varid = 131
        tabid = 128
        timestamp = datetime(1990, 1, 1, 4, 30)
        date, time = 19900101, 430
        levtype = 100
        levlist = [85000]
        value = 3.14
        grbmsg = {grib_file.param_key: 131,
                  grib_file.date_key: date,
                  grib_file.time_key: time,
                  grib_file.levtype_key: levtype,
                  grib_file.level_key: levlist[0],
                  "values": value}
        msg = ppmsg.grib_message(grbmsg)
        eq_(msg.get_field(ppmsg.message.variable_key).get_root_codes()[0].var_id, varid)
        eq_(msg.get_field(ppmsg.message.variable_key).get_root_codes()[0].tab_id, tabid)
        eq_(msg.get_field(ppmsg.message.datetime_key), timestamp)
        eq_(msg.get_field(ppmsg.message.leveltype_key), levtype)
        eq_(msg.get_field(ppmsg.message.levellist_key), levlist)
        eq_(msg.get_values(), value)
