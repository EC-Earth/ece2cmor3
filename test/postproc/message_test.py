import logging
import unittest

import os
from nose.tools import ok_, eq_
from datetime import datetime, timedelta
from ece2cmor3 import cmor_source, grib_file
from ece2cmor3.postproc import message

logging.basicConfig(level=logging.DEBUG)


class pp_message_test(unittest.TestCase):

    @staticmethod
    def test_get_field():
        varid = 131
        tabid = 128
        timestamp = datetime(1990, 1, 1, 4, 30, 22)
        timebounds = (timestamp - timedelta(days=1), timestamp + timedelta(days=1))
        levtype = 100
        levlist = [85000, 5000, 450]
        code = cmor_source.grib_code(varid, tabid)
        source = cmor_source.ifs_source(code)
        resolution = 256
        msg = message.memory_message(variable=source, timestamp=timestamp, timebounds=timebounds, levels=levlist,
                                     leveltype=levtype, resolution=resolution, values=None)
        eq_(msg.get_field(message.variable_key).get_root_codes(), [code])
        eq_(msg.get_field(message.datetime_key), timestamp)
        eq_(msg.get_field(message.timebounds_key), timebounds)
        eq_(msg.get_field(message.leveltype_key), levtype)
        eq_(msg.get_field(message.levellist_key), levlist)
        eq_(msg.get_field(message.resolution_key), resolution)

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
        msg = message.memory_message(variable=source, timestamp=timestamp, timebounds=(), levels=levlist,
                                     leveltype=levtype, resolution=resolution, values=None)
        ok_(msg.get_field("nonexisting_key") is None)

    @staticmethod
    def test_csv_message():
        grib_file.test_mode = True
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMGGECE3+199001.csv")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        grbmsg.read_next()
        msg = message.grib_message(grbmsg)
        eq_(msg.get_field(message.variable_key).get_root_codes()[0].var_id, 8)
        eq_(msg.get_field(message.variable_key).get_root_codes()[0].tab_id, 128)
        eq_(msg.get_field(message.datetime_key), datetime(1990, 1, 1, 3, 0, 0))
        eq_(msg.get_field(message.leveltype_key), 1)
        eq_(msg.get_field(message.levellist_key), [0])

    @staticmethod
    def test_grib_message():
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMGGpl01+199001")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        grbmsg.read_next()
        msg = message.grib_message(grbmsg)
        eq_(msg.get_field(message.variable_key).get_root_codes()[0].var_id, 8)
        eq_(msg.get_field(message.variable_key).get_root_codes()[0].tab_id, 128)
        eq_(msg.get_field(message.datetime_key), datetime(1990, 1, 1, 3, 0, 0))
        eq_(msg.get_field(message.leveltype_key), 1)
        eq_(msg.get_field(message.levellist_key), [0])

    @staticmethod
    def test_grib_resolution():
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMGGpl01+199001")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        grbmsg.read_next()
        msg = message.grib_message(grbmsg)
        ok_(not msg.is_spectral())
        eq_(msg.get_resolution(), 128)

    @staticmethod
    def test_grib_truncation():
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMSHpl01+199001")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        grbmsg.read_next()
        msg = message.grib_message(grbmsg)
        ok_(msg.is_spectral())
        eq_(msg.get_resolution(), 128)
