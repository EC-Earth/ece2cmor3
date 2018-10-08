import logging
import os
import unittest

import nose.tools

import test_utils
from ece2cmor3 import cmor_source, cmor_target, cmor_task, ifs2cmor, postproc

logging.basicConfig(level=logging.DEBUG)
ifs2cmor.ifs_gridpoint_file_ = "ICMGG+199003"

ifs2cmor.ifs_spectral_file_ = "ICMSH+199003"


class ifs2cmor_tests(unittest.TestCase):

    @staticmethod
    def test_initialize():
        pass

    @staticmethod
    def test_execute():
        pass

    @staticmethod
    def test_mask_tasks():
        pass

    @staticmethod
    def test_cleanup():
        pass


