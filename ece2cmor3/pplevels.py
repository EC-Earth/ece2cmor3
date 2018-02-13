import logging
from ece2cmor3 import ppmsg, ppop

log = logging.getLogger(__name__)

class level_integrator(ppop.post_proc_operator):

    def __init__(self, levels, level_type):
        super(level_integrator_node, self).__init__()
        self.levels = levels
        self.level_type = level_type
        self.values = [None] * len(levels)
        self.coherency_keys = [ppmsg.message.variable_key, ppmsg.message.datetime_key]

    def fill_cache(self, msg):
        leveltype = msg.get_level_type()
        if leveltype != self.level_type:
            return False
        i = 0
        for level in msg.get_levels():
            if level not in self.levels:
                continue
            index = self.levels.index(level)
            if self.values[index]:
                log.warning(
                    "Overwriting level %d for variable %s" % (level, self.property_cache.get("variable", "unknown")))
            if len(msg.get_levels()) > 1:  # Shouldn't normally happen...
                self.values[index] = msg.get_values()[i, :]
            else:
                self.values[index] = msg.get_values()
        self.full_cache = all(self.values)
        return True

    def clear_cache(self):
        del self.values
        self.values = [None] * len(self.levels)
        self.full_cache = False
