import os
import unittest

from nose.tools import ok_

from ece2cmor3 import cmor_target, cmor_source, cmor_task
from ece2cmor3.postproc import factory, zlevels


def get_table_path(tab_id=None):
    directory = os.path.join(os.path.dirname(cmor_target.__file__), "resources", "tables")
    return os.path.join(directory, "CMIP6_" + tab_id + ".json") if tab_id else directory


class expression_test(unittest.TestCase):

    @staticmethod
    def test_omit_level_operator():
        targets = cmor_target.create_targets(get_table_path(), "CMIP6")
        source = cmor_source.ifs_source.create(79, 128)
        target = [t for t in targets if t.variable == "clwvi" and t.table == "CFday"][0]
        task = cmor_task.cmor_task(source, target)
        level_operator = factory.create_level_operator(task)
        ok_(level_operator is None)

    @staticmethod
    def test_create_level_operator():
        targets = cmor_target.create_targets(get_table_path(), "CMIP6")
        source = cmor_source.ifs_source.create(130, 128)
        target = [t for t in targets if t.variable == "ta" and t.table == "Amon"][0]
        task = cmor_task.cmor_task(source, target)
        level_operator = factory.create_level_operator(task)
        ok_(isinstance(level_operator, zlevels.level_aggregator))
