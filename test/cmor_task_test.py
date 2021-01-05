import logging
import unittest

import pytest

from ece2cmor3 import cmor_source
from ece2cmor3 import cmor_target
from ece2cmor3 import cmor_task

logging.basicConfig(level=logging.DEBUG)


class cmor_task_tests(unittest.TestCase):

    @staticmethod
    def test_invalid_source():
        src = "invalid"
        tgt = cmor_target.cmor_target("huss", "Amon")
        with pytest.raises(Exception, match=r"Invalid source*"):
            task = cmor_task.cmor_task(src, tgt)

    @staticmethod
    def test_invalid_target():
        src = cmor_source.ifs_source.read("81.128")
        tgt = "invalid"
        with pytest.raises(Exception, match=r"Invalid target*"):
            task = cmor_task.cmor_task(src, tgt)

    @staticmethod
    def test_constructor():
        src = cmor_source.ifs_source.read("79.128")
        tgt = cmor_target.cmor_target("clwvi", "Amon")
        task = cmor_task.cmor_task(src, tgt)
        assert task.source == src
        assert task.target == tgt
