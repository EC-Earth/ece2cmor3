import unittest

from datetime import datetime

from ece2cmor3 import grib_file, ece2cmorlib, cmor_source
from nose.tools import ok_, eq_, with_setup

from ece2cmor3.postproc import cmorize, message


# Test utility function creating messages
def make_msg(code, time, level_type, values):
    data = {message.variable_key: cmor_source.ifs_source(code=cmor_source.grib_code(code, 128)),
            message.datetime_key: time,
            message.timebounds_key: (time, time),
            message.leveltype_key: level_type,
            message.levellist_key: range(91) if level_type == grib_file.hybrid_level_code else [0],
            message.resolution_key: 256,
            "values": values}
    return message.memory_message(**data)


def setup():
    ece2cmorlib.initialize()


class cmorize_test(unittest.TestCase):

    @staticmethod
    @with_setup(setup)
    def test_receive_store_var():
        task = [t for t in ece2cmorlib.tasks if (t.target.table, t.target.variable) == ("CFday", "ta")][0]
        op = cmorize.cmor_operator(task, chunk_size=1, store_var_key=(134, 128, grib_file.surface_level_code, 0))
        time = datetime(1990, 1, 1, 6, 0, 0)
        op.receive_msg(make_msg(130, time, grib_file.hybrid_level_code, values=0.0))
        ok_(not op.cache_is_full())
        op.receive_store_var(make_msg(134, time, grib_file.surface_level_code, values=10.000))
        ok_(op.cache_is_full())
