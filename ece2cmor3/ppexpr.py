import logging
import re
import numexpr
from ece2cmor3 import cmor_source, ppmsg, ppop

log = logging.getLogger(__name__)


def fix_expr(expr):
    return re.sub('sqr\(', 'square(', expr)


class variable_expression(ppop.post_proc_operator):

    def __init__(self, expr):
        super(variable_expression, self).__init__()
        self.source = cmor_source.ifs_source.read(expr)
        self.numpy_expr = fix_expr(expr)
        self.local_dict = {v.to_var_string(): None for v in self.source.get_root_codes()}
        self.cached_properties = [ppmsg.message.datetime_key, ppmsg.message.resolution_key]

    def fill_cache(self, msg):
        vstr = msg.get_variable().code_.to_var_string()
        if vstr in self.local_dict:
            self.local_dict[vstr] = msg.get_values()
        if self.cache_is_full():
            self.values = numexpr.evaluate(self.numpy_expr, local_dict=self.local_dict)

    def cache_is_full(self):
        return super(variable_expression,self).cache_is_full() \
               and all([self.local_dict[k] is not None for k in self.local_dict])

    def clear_cache(self):
        for k in self.local_dict:
            self.local_dict[k] = None
