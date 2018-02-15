import logging
from ece2cmor3 import ppmsg

# Post-processing operator abstract base class

log = logging.getLogger(__name__)


class post_proc_operator(object):

    def __init__(self):

        self.values = None
        self.targets = []
        self.cached_properties = [ppmsg.message.variable_key,
                                  ppmsg.message.datetime_key,
                                  ppmsg.message.leveltype_key,
                                  ppmsg.message.levellist_key]
        self.property_cache = {}

    def receive_msg(self, msg):
        if self.cache_is_full():
            self.clear_cache()
        if self.cache_is_empty():
            self.property_cache = {}
        for key in self.cached_properties:
            if key in self.property_cache:
                if not msg.get_field(key) == self.property_cache[key]:
                    log.error("Message property %s changed within filling cache" % key)
                    return False
            else:
                self.property_cache[key] = msg.get_field(key)
        self.fill_cache(msg)
        if self.cache_is_full():
            msg = self.create_msg()
            for target in self.targets:
                target.receive_msg(msg)

    def create_msg(self):
        return ppmsg.memory_message(source=self.property_cache[ppmsg.message.variable_key],
                                    timestamp=self.property_cache[ppmsg.message.datetime_key],
                                    leveltype=self.property_cache[ppmsg.message.leveltype_key],
                                    levels=self.property_cache[ppmsg.message.levellist_key],
                                    values=self.values)

    def fill_cache(self, msg):
        self.values = msg.get_values()
        return self.values is not None

    def clear_cache(self):
        self.values = None

    def cache_is_full(self):
        return self.values is not None

    def cache_is_empty(self):
        return self.values is None
