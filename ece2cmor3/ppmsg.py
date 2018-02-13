import logging
from datetime import datetime
from ece2cmor3 import cmor_source, grib_file

# Defines messages on which the post-processing operations act

log = logging.getLogger(__name__)

class message(object):

    variable_key = "variable"
    datetime_key = "datetime"
    leveltype_key = "leveltype"
    levellist_key = "levels"

    keys = [variable_key, datetime_key, leveltype_key, levellist_key]

    def __init__(self):
        pass

    def get_variable(self):
        pass

    def get_timestamp(self):
        pass

    def get_levels(self):
        pass

    def get_level_type(self):
        pass

    def get_values(self):
        pass

    def get_field(self, key):
        if key == self.variable_key:
            return self.get_variable()
        if key == self.datetime_key:
            return self.get_timestamp()
        if key == self.leveltype_key:
            return self.get_level_type()
        if key == self.levellist_key:
            return self.get_levels()
        log.error("Key %s not a valid key for message properties" % key)
        return None


class memory_message(message):

    def __init__(self, source, timestamp, levels, leveltype, values):
        super(memory_message, self).__init__()
        self.source = source
        self.timestamp = timestamp
        self.levels = levels
        self.level_type = leveltype
        self.values = values

    def get_variable(self):
        return self.source

    def get_timestamp(self):
        return self.timestamp

    def get_levels(self):
        return self.levels

    def get_level_type(self):
        return self.level_type

    def get_values(self):
        return self.values


class grib_message(message):

    def __init__(self,grbmsg_):
        super(grib_message, self).__init__()
        self.grbmsg = grbmsg_

    def get_variable(self):
        param = self.grbmsg[grib_file.param_key]
        code,table = param if param < 1000 else param % 1000, 128 if param < 1000 else param / 1000
        return cmor_source.ifs_source(cmor_source.grib_code(code,table))

    def get_timestamp(self):
        date,time = self.grbmsg[grib_file.date_key],self.grbmsg[grib_file.time_key]
        yyyy = date/10**4
        day = (date % 10**4)/10**2
        return datetime(year=date/10000, month=(date % 10000)/100, day=(date % 100),
                        hour=time/100, minute=(time % 100))

    def get_levels(self):
        return [self.grbmsg[grib_file.level_key]]

    def get_level_type(self):
        return self.grbmsg[grib_file.levtype_key]
