import logging
import numexpr
import numpy
import re

from ece2cmor3 import cmor_source, grib_file
from ece2cmor3.postproc import message, operator

log = logging.getLogger(__name__)


def fix_expr(expr):
    pattern = re.compile('sqr\( ( [^})]* ) \)', re.VERBOSE)
    result = pattern.sub(r'(\1)**2', expr.split('=', 1)[-1].strip())
    if result.startswith("merge"):
        return [s.strip() for s in result[6:-1].split(',')]
    return result


class expression_operator(operator.operator_base):

    def __init__(self, expr, leveltype=grib_file.surface_level_code):
        super(expression_operator, self).__init__()
        self.source = cmor_source.ifs_source.read(expr)
        self.numpy_expr = fix_expr(expr)
        self.local_dict = {v.to_var_string(): None for v in self.source.get_root_codes()}
        self.cached_properties = [message.datetime_key, message.timebounds_key,
                                  message.resolution_key]
        self.level_type = leveltype
        if isinstance(self.numpy_expr, str):
            self.cached_properties.append(message.leveltype_key)
            self.cached_properties.append(message.levellist_key)

    def fill_cache(self, msg):
        vstr = msg.get_variable().code_.to_var_string()
        self.level_type = msg.get_level_type()
        if vstr in self.local_dict:
            self.local_dict[vstr] = msg.get_values()

    def cache_is_full(self):
        return not any([v is None for v in self.local_dict.values()])

    def cache_is_empty(self):
        return all([v is None for v in self.local_dict.values()])

    def clear_cache(self):
        for k in self.local_dict:
            self.local_dict[k] = None

    def create_msg(self):
        levtype = self.property_cache.get(message.leveltype_key, self.level_type)
        if message.levellist_key in self.cached_properties:
            self.values = numexpr.evaluate(self.numpy_expr, local_dict=self.local_dict)
            levels = self.property_cache[message.levellist_key]
        else:
            self.values = numpy.stack([numexpr.evaluate(e, local_dict=self.local_dict) for e in self.numpy_expr])
            levels = range(1, len(self.numpy_expr) + 1)
        return message.memory_message(variable=self.source,
                                      timestamp=self.property_cache[message.datetime_key],
                                      timebounds=self.property_cache[message.timebounds_key],
                                      leveltype=levtype,
                                      levels=levels,
                                      resolution=self.property_cache[message.resolution_key],
                                      values=self.values)
