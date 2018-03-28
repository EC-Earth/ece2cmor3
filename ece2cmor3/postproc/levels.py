import logging
import tempfile
import os
import numpy

from ece2cmor3 import grib_file
from ece2cmor3.postproc import message, operator

log = logging.getLogger(__name__)

num_levels = 0
pv_array = None
a_coefs, b_coefs = None, None


def get_pv_array(gribfile):
    global num_levels, pv_array, a_coefs, b_coefs
    if pv_array is not None:
        return
    pv = gribfile.try_get_field("pv")
    if pv is None:
        return
    L = len(pv) / 2
    if num_levels == 0:
        num_levels = L - 1
    a_coefs = pv[0:num_levels]
    b_coefs = pv[L:L + num_levels]


class level_aggregator(operator.operator_base):

    def __init__(self, level_type, levels, mem_cache=True):
        super(level_aggregator, self).__init__()
        self.levels = levels
        self.level_type = level_type
        self.mem_cache = mem_cache
        self.values = None if levels is None else [None] * len(levels)
        self.cached_properties = [message.variable_key, message.resolution_key, message.datetime_key,
                                  message.timebounds_key]

    def accept_msg(self, msg):
        return msg.get_level_type() == self.level_type

    def fill_cache(self, msg):
        if self.level_type == grib_file.hybrid_level_code and self.levels is None:
            self.levels = range(1, num_levels + 1)
            self.values = [None] * num_levels
        leveltype = msg.get_level_type()
        if leveltype != self.level_type:
            return False
        i = 0
        for level in msg.get_levels():
            level_value = level
            if self.level_type == grib_file.pressure_level_code:
                level_value = float(100 * level)
            elif self.level_type == grib_file.height_level_code:
                level_value = float(level)
            if level_value not in self.levels:
                continue
            index = self.levels.index(level_value)
            if self.values[index] is not None:
                log.warning(
                    "Overwriting level %d for variable %s" % (level, self.property_cache.get("variable", "unknown")))
            if self.mem_cache:
                if len(msg.get_levels()) > 1:  # Shouldn't normally happen...
                    self.values[index] = msg.get_values()[i, :]
                else:
                    self.values[index] = msg.get_values()
            else:
                f = tempfile.NamedTemporaryFile(delete=False)
                numpy.save(f, msg.get_values())
                self.values[index] = f.name
                f.close()

        return True

    def print_state(self):
        super(level_aggregator, self).print_state()
        print "level type:", self.level_type
        print "requested levels:", self.levels
        print "filled levels:", [self.levels[i] for i in range(len(self.values)) if self.values[i] is not None]

    def clear_cache(self):
        self.values = None if self.levels is None else [None] * len(self.levels)

    def create_msg(self):
        if not self.mem_cache:
            files = [open(f, 'r') for f in self.values]
            vals = numpy.stack([numpy.load(f) for f in files])
            for f in files:
                f.close()
                os.remove(f.name)
        else:
            vals = numpy.stack(self.values)
        return message.memory_message(variable=self.property_cache[message.variable_key],
                                      timestamp=self.property_cache[message.datetime_key],
                                      timebounds=self.property_cache[message.timebounds_key],
                                      leveltype=self.level_type,
                                      levels=self.levels,
                                      resolution=self.property_cache[message.resolution_key],
                                      values=vals)

    def cache_is_full(self):
        return self.values is not None and all(v is not None for v in self.values)

    def cache_is_empty(self):
        return self.values is None or all(v is None for v in self.values)
