import csv
import os

# Vertical axes codes
import pygrib
import random

import numpy

surface_level_code = 1
hybrid_level_code = 109
pressure_level_code = 100
height_level_code = 105
depth_level_code = 111
pv_level_code = 108

surface_level_string = "sfc"
hybrid_level_string = "ml"
pressure_level_string = "pl"
height_level_string = "105"
depth_level_string = "111"
pv_level_string = "pv"

# Key names
date_key = "dataDate"
time_key = "dataTime"
param_key = "paramId"
levtype_key = "indicatorOfTypeOfLevel"
level_key = "level"
spherical_harmonics_key = "sphericalHarmonics"
truncation_key = "J"
resolution_key = "N"
values_key = "values"

test_mode = False


# Factory method for file stream
def open_file(filepath):
    if test_mode:
        return open(filepath)
    else:
        return pygrib.open(filepath)


# Factory method
def create_grib_file(file_object_):
    if test_mode:
        return csv_grib_mock(file_object_)
    else:
        return pygrib_api(file_object_)


# Interface for grib file object
class grib_file(object):

    def __init__(self, file_object_):
        self.file_object = file_object_

    def read_next(self):
        pass

    def read_previous(self):
        pass

    def write(self, file_object_):
        pass

    def set_field(self, name, value):
        pass

    def get_field(self, name):
        pass

    def try_get_field(self, name):
        pass

    def release(self):
        pass

    def eof(self):
        pass


# pygrib api implementation of grib file interface
class pygrib_api(grib_file):
    level_mapping = {surface_level_string: surface_level_code,
                     hybrid_level_string: hybrid_level_code,
                     pressure_level_string: pressure_level_code,
                     height_level_string: height_level_code,
                     depth_level_string: depth_level_code,
                     pv_level_string: pv_level_code}

    def __init__(self, file_object_):
        super(pygrib_api, self).__init__(file_object_)
        self.message = None
        os.environ["GRIB_API_PYTHON_NO_TYPE_CHECKS"] = "1"

    def read_next(self):
        self.message = self.file_object.readline()
        return self.message is not None

    def read_previous(self):
        self.message = self.file_object.seek(-1, 1)
        return self.message is not None

    def write(self, file_object_):
        file_object_.write(self.message.tostring())

    def set_field(self, name, value):
        self.message[name] = value

    def get_field(self, name):
        if name == levtype_key:
            level_type_string = str(self.message[name])
            return pygrib_api.level_mapping.get(level_type_string, self.message[name])
        return self.message[name]

    def try_get_field(self, name):
        if name in self.message.keys():
            return self.get_field(name)
        return None

    def release(self):
        pass

    def eof(self):
        return self.message is None


# CSV header-only implementation of grib file interface for testing purposes
class csv_grib_mock(grib_file):
    columns = [date_key, time_key, param_key, levtype_key, level_key]

    def __init__(self, file_object_):
        super(csv_grib_mock, self).__init__(file_object_)
        self.row = []
        self.reader = csv.reader(file_object_, delimiter=',')
        self.read_next()

    def read_next(self):
        self.row = next(self.reader, None)
        return self.row is not None

    def read_previous(self):
        self.row = self.reader.seek(-1, 1)
        return self.row is not None

    def write(self, file_object_):
        writer = csv.writer(file_object_)
        writer.writerow(self.row)

    def set_field(self, name, value):
        self.row[csv_grib_mock.columns.index(name)] = value

    def get_field(self, name):
        if name in [resolution_key, truncation_key]:
            return 1
        if name == spherical_harmonics_key:
            return 0
        if name == values_key:
            return numpy.array([random.random()])
        return int(self.row[csv_grib_mock.columns.index(name)])

    def try_get_field(self, name):
        if name in [resolution_key, truncation_key]:
            return 1
        if name == spherical_harmonics_key:
            return 0
        if name == values_key:
            return numpy.array([random.random()])
        if name in self.columns:
            return self.get_field(name)
        return None

    def release(self):
        self.row = []

    def eof(self):
        return self.row is None
