import datetime
import logging
import math
import os
import shutil
import unittest

import cmor
import numpy
from nose.tools import eq_

import test_utils
from ece2cmor3 import nemo2cmor, cmor_source, cmor_target, cmor_task

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def circwave(t, j, i):
    return 15 * math.cos((i * i + j * j) / 1000. + 0.1 * t)


def circwave3d(t, z, j, i):
    return 15 * math.cos((i * i + j * j) / 1000. + 0.1 * t) * (z / 12)


def hypwave(t, j, i):
    return 0.001 * math.sin((i * i - j * j) / 1000. + 0.1 * t)


def get_table_path(tab_id=None):
    directory = os.path.join(os.path.dirname(cmor_target.__file__), "resources", "tables")
    return os.path.join(directory, "CMIP6_" + tab_id + ".json") if tab_id else directory


class nemo2cmor_tests(unittest.TestCase):

    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "test_data", "nemodata")
        if os.path.exists(self.data_dir):
            return
        os.mkdir(self.data_dir)
        dimx, dimy, dimz = 65, 75, 10
        opf = test_utils.nemo_output_factory()
        opf.make_grid(dimx, dimy, "grid_U", dimz)
        opf.set_timeframe(datetime.date(1990, 1, 1), datetime.date(1991, 1, 1), "1d")
        uto = {"name": "uto",
               "dims": 2,
               "function": circwave,
               "standard_name": "temperature_transport_x",
               "long_name": "Product of x-ward sea water velocity and temperature",
               "units": "m degC s-1"}
        uso = {"name": "uso",
               "dims": 2,
               "function": hypwave,
               "standard_name": "salinity_transport_x",
               "long_name": "Product of x-ward sea water velocity and salinity",
               "units": "kg m-2 s-1"}
        opf.write_variables(self.data_dir, "exp", [uto, uso])

        opf.make_grid(dimx, dimy, "grid_V", dimz)
        opf.set_timeframe(datetime.date(1990, 1, 1), datetime.date(1991, 1, 1), "1d")
        vto = {"name": "vto",
               "dims": 2,
               "function": circwave,
               "standard_name": "temperature_transport_y",
               "long_name": "Product of y-ward sea water velocity and temperature",
               "units": "m degC s-1"}
        vso = {"name": "vso",
               "dims": 2,
               "function": hypwave,
               "standard_name": "salinity_transport_y",
               "long_name": "Product of y-ward sea water velocity and salinity",
               "units": "kg m-2 s-1"}
        opf.write_variables(self.data_dir, "exp", [vto, vso])

        opf.make_grid(dimx, dimy, "grid_T", dimz)
        opf.set_timeframe(datetime.date(1990, 1, 1), datetime.date(1991, 1, 1), "1m")
        tos = {"name": "tos",
               "dims": 2,
               "function": circwave,
               "standard_name": "sea_surface_temperature",
               "long_name": "Sea surface temperature",
               "units": "degC"}
        to = {"name": "to",
              "dims": 3,
              "function": circwave3d,
              "standard_name": "sea_water_temperature",
              "long_name": "Sea water temperature",
              "units": "degC"}
        sos = {"name": "sos",
               "dims": 2,
               "function": hypwave,
               "standard_name": "sea_surface_salinity",
               "long_name": "Sea surface salinity",
               "units": "kg m-3"}
        opf.write_variables(self.data_dir, "exp", [tos, to, sos])

        opf.make_grid(dimx, dimy, "icemod")
        opf.set_timeframe(datetime.date(1990, 1, 1), datetime.date(1991, 1, 1), "6h")
        sit = {"name": "sit", "dims": 2, "function": circwave, "standard_name": "sea_ice_temperature",
               "long_name": "Sea ice temperature", "units": "degC"}
        opf.write_variables(self.data_dir, "exp", [sit])

    def tearDown(self):
        cmor_dir = os.path.join(os.getcwd(), "cmor")
        if os.path.exists(cmor_dir):
            try:
                shutil.rmtree(cmor_dir)
            except Exception as e:
                log.warning("Attempt to remove cmorized test data failed, reason: %s" % e.message)
        if os.path.exists(self.data_dir):
            try:
                shutil.rmtree(self.data_dir)
            except Exception as e:
                log.warning("Attempt to remove generated test data failed, reason: %s" % e.message)

    def test_cmor_single_task(self):
        tab_dir = get_table_path()
        conf_path = os.path.join(os.path.dirname(nemo2cmor.__file__), "resources", "metadata-template.json")
        cmor.setup(tab_dir)
        cmor.dataset_json(conf_path)
        nemo2cmor.initialize(self.data_dir, "exp", os.path.join(tab_dir, "CMIP6"), datetime.datetime(1990, 3, 1))
        src = cmor_source.netcdf_source("tos", "nemo")
        tgt = cmor_target.cmor_target("tos", "Omon")
        setattr(tgt, "frequency", "mon")
        setattr(tgt, "dimensions", "longitude latitude time")
        setattr(tgt, "time_operator", ["mean"])
        tgt.dims = 2
        tsk = cmor_task.cmor_task(src, tgt)
        nemo2cmor.execute([tsk])
        nemo2cmor.finalize()
        cmor.close()

    @staticmethod
    def test_create_grid():
        dim = 1000
        lons = numpy.fromfunction(lambda i, j: (i * 360 + 0.5) / (0.5 * (dim + j) + 2), (dim, dim), dtype=numpy.float64)
        lats = numpy.fromfunction(lambda i, j: (j * 180 + 0.5) / (0.5 * (dim + i) + 2) - 90, (dim, dim),
                                  dtype=numpy.float64)

        grid = nemo2cmor.nemo_grid("lat-lon", lons, lats)

        p1 = (grid.vertex_lons[0, 0, 0], grid.vertex_lats[0, 0, 0])
        p2 = (grid.vertex_lons[0, 0, 1], grid.vertex_lats[0, 0, 1])
        p3 = (grid.vertex_lons[0, 0, 2], grid.vertex_lats[0, 0, 2])
        p4 = (grid.vertex_lons[0, 0, 3], grid.vertex_lats[0, 0, 3])

        eq_(p2[0], p3[0])
        eq_(p1[1], p2[1])
        eq_(p3[1], p4[1])

    def test_init_nemo2cmor(self):
        tab_dir = get_table_path()
        conf_path = os.path.join(os.path.dirname(nemo2cmor.__file__), "resources", "metadata-template.json")
        cmor.setup(tab_dir)
        cmor.dataset_json(conf_path)
        nemo2cmor.initialize(self.data_dir, "exp", os.path.join(tab_dir, "CMIP6"), datetime.datetime(1990, 3, 1))
        nemo2cmor.finalize()
        cmor.close()

    def test_cmor_single_task3d(self):
        tab_dir = get_table_path()
        conf_path = os.path.join(os.path.dirname(nemo2cmor.__file__), "resources", "metadata-template.json")
        cmor.setup(tab_dir)
        cmor.dataset_json(conf_path)
        nemo2cmor.initialize(self.data_dir, "exp", os.path.join(tab_dir, "CMIP6"), datetime.datetime(1990, 3, 1))
        src = cmor_source.netcdf_source("to", "nemo")
        tgt = cmor_target.cmor_target("thetao", "Omon")
        setattr(tgt, "frequency", "mon")
        setattr(tgt, "dimensions", "longitude latitude olevel time")
        setattr(tgt, "time_operator", ["mean"])
        tgt.dims = 3
        tsk = cmor_task.cmor_task(src, tgt)
        nemo2cmor.execute([tsk])
        nemo2cmor.finalize()
        cmor.close()
