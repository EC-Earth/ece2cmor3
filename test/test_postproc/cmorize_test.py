from datetime import datetime, timedelta

import numpy
import os
import unittest
from nose.tools import ok_, with_setup

from ece2cmor3 import grib_file, ece2cmorlib, cmor_source, taskloader
from ece2cmor3.postproc import cmorize, message, zlevels

nlats = 10


# Test utility function creating messages
def make_msg(code, time, level_type, mean, dt=timedelta(hours=3)):
    if level_type == grib_file.hybrid_level_code:
        vals = numpy.random.rand(zlevels.num_levels, nlats, 2 * nlats) * (0.1 * mean) + mean
    elif level_type == grib_file.surface_level_code:
        vals = numpy.random.rand(nlats, 2 * nlats) * (0.1 * mean) + mean
    else:
        raise ValueError("Unsupported level type: %d" % level_type)
    data = {message.variable_key: cmor_source.ifs_source(code=cmor_source.grib_code(code, 128)),
            message.datetime_key: time,
            message.leveltype_key: level_type,
            message.levellist_key: range(zlevels.num_levels) if level_type == grib_file.hybrid_level_code else [0],
            message.resolution_key: nlats ** 2,
            message.timebounds_key: [time - dt, time + dt],
            "values": vals}
    return message.memory_message(**data)


def setup():
    ece2cmorlib.initialize()
    cmorize.table_root = os.path.join(ece2cmorlib.table_dir, ece2cmorlib.prefix)
    sh_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ifs", "ICMSHpl01+199001")
    grib_file.test_mode = False
    with grib_file.open_file(sh_path) as grbfile:
        grbmsg = grib_file.create_grib_file(grbfile)
        while grbmsg.read_next():
            message.grib_message(grbmsg)
            zlevels.get_pv_array(grbmsg)
            if zlevels.num_levels:
                break


class cmorize_test(unittest.TestCase):

    store_var_key = (134, 128, grib_file.surface_level_code, 0)

    @staticmethod
    @with_setup(setup)
    def test_chunking():
        taskloader.load_targets({"day": ["tas"]})
        task = [t for t in ece2cmorlib.tasks if (t.target.variable, t.target.table) == ("tas", "day")][0]
        setattr(task, "output_freq", 3)
        op = cmorize.cmor_operator(task, chunk_size=3)
        time = datetime(1990, 1, 1, 12, 0, 0)
        op.receive_msg(make_msg(task.source.get_grib_code().var_id, time, grib_file.surface_level_code, mean=290.,
                                dt=timedelta(hours=12)))
        ok_(not op.cache_is_full())
        time = datetime(1990, 1, 2, 12, 0, 0)
        op.receive_msg(make_msg(task.source.get_grib_code().var_id, time, grib_file.surface_level_code, mean=290.,
                                dt=timedelta(hours=12)))
        ok_(not op.cache_is_full())
        time = datetime(1990, 1, 3, 12, 0, 0)
        op.receive_msg(make_msg(task.source.get_grib_code().var_id, time, grib_file.surface_level_code, mean=290.,
                                dt=timedelta(hours=12)))
        ok_(op.cache_is_full())

    @staticmethod
    @with_setup(setup)
    def test_receive_store_var():
        taskloader.load_targets({"CFday": ["ta"]})
        task = [t for t in ece2cmorlib.tasks if (t.target.variable, t.target.table) == ("ta", "CFday")][0]
        setattr(task, "output_freq", 6)
        op = cmorize.cmor_operator(task, chunk_size=1, store_var_key=cmorize_test.store_var_key)
        time = datetime(1990, 1, 1, 6, 0, 0)
        op.receive_msg(make_msg(task.source.get_grib_code().var_id, time, grib_file.hybrid_level_code, mean=290.))
        ok_(not op.cache_is_full())
        op.receive_store_var(make_msg(134, time, grib_file.surface_level_code, mean=100000.))
        ok_(op.cache_is_full())

    @staticmethod
    @with_setup(setup)
    def test_receive_store_var_twice():
        taskloader.load_targets({"CFday": ["ua", "va"]})
        utask = [t for t in ece2cmorlib.tasks if (t.target.variable, t.target.table) == ("ua", "CFday")][0]
        vtask = [t for t in ece2cmorlib.tasks if (t.target.variable, t.target.table) == ("va", "CFday")][0]
        setattr(utask, "output_freq", 6)
        setattr(vtask, "output_freq", 6)
        uop = cmorize.cmor_operator(utask, chunk_size=1, store_var_key=cmorize_test.store_var_key)
        vop = cmorize.cmor_operator(vtask, chunk_size=1, store_var_key=cmorize_test.store_var_key)
        time = datetime(1990, 1, 1, 6, 0, 0)
        uop.receive_msg(make_msg(utask.source.get_grib_code().var_id, time, grib_file.hybrid_level_code, mean=2.9))
        ok_(not uop.cache_is_full())
        psmsg = make_msg(134, time, grib_file.surface_level_code, mean=100000.)
        uop.receive_store_var(psmsg)
        vop.receive_store_var(psmsg)
        ok_(uop.cache_is_full())
        ok_(not vop.cache_is_full())
        vop.receive_msg(make_msg(vtask.source.get_grib_code().var_id, time, grib_file.hybrid_level_code, mean=-1.1))
        ok_(vop.cache_is_full())