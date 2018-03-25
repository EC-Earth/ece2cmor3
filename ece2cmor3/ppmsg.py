import logging
from datetime import datetime
from ece2cmor3 import cmor_source, grib_file

# Defines messages on which the post-processing operations act

log = logging.getLogger(__name__)


class message(object):

    variable_key = "variable"
    datetime_key = "timestamp"
    timebounds_key = "timebounds"
    leveltype_key = "leveltype"
    levellist_key = "levels"
    resolution_key = "resolution"

    keys = [variable_key, datetime_key, timebounds_key, leveltype_key, levellist_key, resolution_key]

    def __init__(self):
        pass

    def get_variable(self):
        pass

    def get_timestamp(self):
        pass

    def get_time_bounds(self):
        pass

    def get_levels(self):
        pass

    def get_level_type(self):
        pass

    def get_values(self):
        pass

    def get_resolution(self):
        pass

    def is_spectral(self):
        pass

    def get_field(self, key):
        if key == self.variable_key:
            return self.get_variable()
        if key == self.datetime_key:
            return self.get_timestamp()
        if key == self.timebounds_key:
            return self.get_time_bounds()
        if key == self.leveltype_key:
            return self.get_level_type()
        if key == self.levellist_key:
            return self.get_levels()
        if key == self.resolution_key:
            return self.get_resolution()
        log.error("Key %s not a valid key for message properties" % key)
        return None


class memory_message(message):

    def __init__(self, **kwargs):
        super(memory_message, self).__init__()
        self.variable = kwargs[message.variable_key]
        self.timestamp = kwargs[message.datetime_key]
        self.time_bounds = kwargs[message.timebounds_key]
        self.levels = kwargs[message.levellist_key]
        self.level_type = kwargs[message.leveltype_key]
        self.resolution = kwargs[message.resolution_key]
        self.values = kwargs["values"]

    def get_variable(self):
        return self.variable

    def get_timestamp(self):
        return self.timestamp

    def get_time_bounds(self):
        return self.time_bounds

    def get_levels(self):
        return self.levels

    def get_level_type(self):
        return self.level_type

    def get_values(self):
        return self.values

    def get_resolution(self):
        return self.resolution

    def is_spectral(self):
        return self.variable.get_grib_code() in cmor_source.ifs_source.grib_codes_sh


class grib_message(message):

    def __init__(self, grbmsg_):
        super(grib_message, self).__init__()
        self.grbmsg = grbmsg_

    def get_variable(self):
        param = self.grbmsg.get_field(grib_file.param_key)
        code, table = param if param < 1000 else param % 1000, 128 if param < 1000 else param / 1000
        return cmor_source.ifs_source(cmor_source.grib_code(code, table))

    def get_timestamp(self):
        date, time = self.grbmsg.get_field(grib_file.date_key), self.grbmsg.get_field(grib_file.time_key)
        return datetime(year=date / 10000, month=(date % 10000) / 100, day=(date % 100),
                        hour=time / 100, minute=(time % 100))

    def get_time_bounds(self):
        return []

    def get_levels(self):
        return [self.grbmsg.get_field(grib_file.level_key)]

    def get_level_type(self):
        return self.grbmsg.get_field(grib_file.levtype_key)

    def get_values(self):
        return self.grbmsg.get_field("values")

    def get_resolution(self):
        if self.is_spectral():
            return (int(self.grbmsg.get_field("J")) + 1)/2
        return int(self.grbmsg.get_field("N"))

    def is_spectral(self):
        return int(self.grbmsg.get_field("sphericalHarmonics")) == 1
