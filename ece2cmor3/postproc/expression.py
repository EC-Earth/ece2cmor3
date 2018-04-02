import logging
import re
import numexpr
from ece2cmor3 import cmor_source, grib_file
from ece2cmor3.postproc import message, operator

log = logging.getLogger(__name__)


def fix_expr(expr):
    pattern = re.compile('sqr\( ( [^})]* ) \)', re.VERBOSE)
    return pattern.sub(r'(\1)**2', expr.split('=', 1)[-1].strip())


class expression_operator(operator.operator_base):

    def __init__(self, expr):
        super(expression_operator, self).__init__()
        self.source = cmor_source.ifs_source.read(expr)
        self.numpy_expr = fix_expr(expr)
        self.local_dict = {v.to_var_string(): None for v in self.source.get_root_codes()}
        self.cached_properties = [message.datetime_key, message.timebounds_key,
                                  message.resolution_key]

    def fill_cache(self, msg):
        vstr = msg.get_variable().code_.to_var_string()
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
        self.values = numexpr.evaluate(self.numpy_expr, local_dict=self.local_dict)
        # TODO: what about 3D derived variables?
        return message.memory_message(variable=self.source,
                                      timestamp=self.property_cache[message.datetime_key],
                                      timebounds=self.property_cache[message.timebounds_key],
                                      leveltype=grib_file.surface_level_code,
                                      levels=[0],
                                      resolution=self.property_cache[message.resolution_key],
                                      values=self.values)
