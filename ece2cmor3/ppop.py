import logging
from ece2cmor3 import ppmsg

# Post-processing operator abstract base class

log = logging.getLogger(__name__)

class post_proc_operator(object):

    def __init__(self):

        self.values = None
        self.source = None
        self.targets = []
        self.full_cache = False
        self.coherency_keys = []
        self.property_cache = {}

    def collect(self, msg):
        for key in self.coherency_keys:
            if key in self.property_cache:
                if not msg.get_field(key) == self.property_cache[key]:
                    log.error("Message property %s changed within coherent cache" % key)
                    return False
            else:
                self.property_cache[key] = msg.get_field(key)
        return self.fill_cache(msg)

    def create_message(self):
        return memory_message(source=self.property_cache[ppmsg.message.variable_key],
                              timestamp=self.property_cache[ppmsg.message.datetime_key],
                              level_type=self.property_cache[ppmsg.message.leveltype_key],
                              levels=self.property_cache[ppmsg.message.levellist_key],
                              values=self.values)

    def fill_cache(self, msg):
        log.error("Collection method not implemented in abstract base class %s" % type(self))

    def clear_cache(self):
        log.warning("Clear cache method not implemented in abstract base class %s" % type(self))

    def push(self):
        if self.full_cache:
            for target in self.targets:
                target.collect(self.create_message())
                target.push()
            self.property_cache = {}
            self.clear_cache()
