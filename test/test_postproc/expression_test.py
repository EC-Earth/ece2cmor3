import os
import unittest
from datetime import datetime, timedelta

import numpy
from nose.tools import ok_, eq_

from ece2cmor3 import grib_file, cmor_source
from ece2cmor3.postproc import expression, message


# Test utility function creating messages
def make_uv_messages(start_date, length, radius, size, nlevs=1):
    result = []
    time = start_date
    omega = 2 * numpy.pi / 3600
    props = {message.leveltype_key: grib_file.surface_level_code if nlevs == 1 else grib_file.hybrid_level_code,
             message.levellist_key: [0] if nlevs == 1 else range(1, nlevs + 1),
             message.resolution_key: 16}
    ucode = 165 if nlevs == 1 else 131
    vcode = 166 if nlevs == 1 else 132
    while time <= start_date + length:
        rands = numpy.random.rand(size) if nlevs == 1 else numpy.random.rand(size, nlevs)
        angles = 2 * numpy.pi * rands + omega * (time - start_date).total_seconds()
        bnds = (time, time)
        props[message.timebounds_key] = bnds
        props[message.datetime_key] = time
        udata = props.copy()
        udata[message.variable_key] = cmor_source.ifs_source(cmor_source.grib_code(ucode, 128))
        udata["values"] = radius * numpy.cos(angles)
        result.append(message.memory_message(**udata))
        vdata = props.copy()
        vdata[message.variable_key] = cmor_source.ifs_source(cmor_source.grib_code(vcode, 128))
        vdata["values"] = radius * numpy.sin(angles)
        result.append(message.memory_message(**vdata))
        time = time + timedelta(hours=3)
    return result


class expression_test(unittest.TestCase):

    @staticmethod
    def test_wind_speed():
        operator = expression.expression_operator("var214=sqrt(sqr(var165)+sqr(var166))")
        time = datetime(1990, 1, 1, 3, 0, 0)
        r = 12.34567
        msgs = make_uv_messages(time, timedelta(days=1), radius=r, size=10)
        i = 0
        for msg in msgs:
            i += 1
            operator.receive_msg(msg)
            if i % 2 == 0:
                ok_(operator.cache_is_full())
                new_msg = operator.create_msg()
                eq_(new_msg.get_variable().get_grib_code().var_id, 214)
                ok_(all(new_msg.get_values() - r < 1e-8))
                operator.clear_cache()
            else:
                ok_(not operator.cache_is_full())

    @staticmethod
    def test_wind_speed_3d():
        operator = expression.expression_operator("var214=sqrt(sqr(var131)+sqr(var132))")
        time = datetime(1990, 1, 1, 3, 0, 0)
        r = 12.34567
        msgs = make_uv_messages(time, timedelta(days=1), radius=r, size=10, nlevs=31)
        i = 0
        for msg in msgs:
            i += 1
            operator.receive_msg(msg)
            if i % 2 == 0:
                ok_(operator.cache_is_full())
                new_msg = operator.create_msg()
                eq_(new_msg.get_variable().get_grib_code().var_id, 214)
                ok_(all(new_msg.get_values().flatten() - r < 1e-8))
                operator.clear_cache()
            else:
                ok_(not operator.cache_is_full())

    @staticmethod
    def test_hurs_expr():
        operator = expression.expression_operator("var80=100.*exp(17.62*((var168-273.15)/(var168-30.03)-("
                                                  "var167-273.15)/(var167-30.03)))")
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMGGpl01+199001")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        while grbmsg.read_next():
            msg = message.grib_message(grbmsg)
            if msg.get_variable().get_grib_code().var_id in [167, 168]:
                operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        newmsg = operator.create_msg()
        ok_(all(newmsg.get_values().flatten() < 100.1))

    @staticmethod
    def test_huss_expr():
        operator = expression.expression_operator("var81=1./(1.+1.608*(var134*exp(-17.62*(var168-273.15)/("
                                                  "var168-30.03))/611.-1.))")
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMGGpl01+199001")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        while grbmsg.read_next():
            msg = message.grib_message(grbmsg)
            if msg.get_variable().get_grib_code().var_id in [134, 168]:
                operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        newmsg = operator.create_msg()
        ok_(all(newmsg.get_values().flatten() < 100.1))

    @staticmethod
    def test_tsl():
        operator = expression.expression_operator("var117=merge(var139,var170,var183,var236)")
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMGGpl01+199001")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        while grbmsg.read_next():
            msg = message.grib_message(grbmsg)
            if msg.get_variable().get_grib_code().var_id in [139, 170, 183, 236]:
                operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        newmsg = operator.create_msg()
        eq_(newmsg.get_values().shape[0], 4)

    @staticmethod
    def test_mrlsl():
        operator = expression.expression_operator("var118=merge(70*var39,210*var40,720*var41,1890*var42)")
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMGGpl01+199001")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        while grbmsg.read_next():
            msg = message.grib_message(grbmsg)
            if msg.get_variable().get_grib_code().var_id in [39, 40, 41, 42]:
                operator.receive_msg(msg)
        ok_(operator.cache_is_full())
        newmsg = operator.create_msg()
        eq_(newmsg.get_values().shape[0], 4)

    @staticmethod
    def test_hfdsn():
        operator = expression.expression_operator("var120=(var141>0)*(var146+var147+var176+var177)")
        grib_file.test_mode = False
        gg_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMGGpl01+199001")
        grbfile = grib_file.open_file(gg_path)
        grbmsg = grib_file.create_grib_file(grbfile)
        while grbmsg.read_next():
            msg = message.grib_message(grbmsg)
            if msg.get_variable().get_grib_code().var_id in [141, 146, 147, 176, 177]:
                operator.receive_msg(msg)
        ok_(operator.cache_is_full())
