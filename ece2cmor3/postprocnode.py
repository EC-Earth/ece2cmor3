import logging

import numpy

# Log object.
log = logging.getLogger(__name__)


class message(object):
    keys = ["variable", "datetime", "leveltype", "levels"]

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
        if key == message.keys[0]:
            return self.get_variable()
        if key == message.keys[1]:
            return self.get_timestamp()
        if key == message.keys[2]:
            return self.get_level_type()
        if key == message.keys[3]:
            return self.get_levels()
        log.error("Key %s not a valid key for message properties" % key)
        return None


class mem_message(message):

    def __init__(self, source, timestamp, levels, level_type, values):
        super(mem_message, self).__init__()
        self.timestamp = timestamp
        self.levels = levels
        self.level_type = level_type
        self.source = source
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


class post_proc_node(object):

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
                if msg.get_field(key) != self.property_cache[key]:
                    log.error("Message property %s changed within coherent cache" % key)
                    return False
            else:
                self.property_cache[key] = msg.get_field(key)
        return self.fill_cache(msg)

    def create_message(self):
        return mem_message(source=self.property_cache["variable"],
                           timestamp=self.property_cache["datetime"],
                           level_type=self.property_cache["leveltype"],
                           levels=self.property_cache["levels"],
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


class level_integrator_node(post_proc_node):

    def __init__(self, levels, level_type):
        super(level_integrator_node, self).__init__()
        self.levels = levels
        self.level_type = level_type
        self.values = [None] * len(levels)
        self.coherency_keys = ["variable", "datetime"]

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


class time_integrator_node(post_proc_node):
    linear_mean_operator = 1
    block_mean_operator = 2
    min_operator = 3
    max_operator = 4

    def __init__(self, operator, interval):
        super(time_integrator_node, self).__init__()
        self.operator = operator
        self.interval = interval
        self.values = None
        self.previous_values = None
        self.previous_timestamp = None
        self.coherency_keys = ["variable", "leveltype", "levels"]

    def fill_cache(self, msg):
        if self.values is None:
            self.values = msg.get_values()
            if self.operator == self.linear_mean_operator:
                self.previous_values = self.values
            self.previous_timestamp = msg.get_timestamp()
            return
        self.full_cache = msg.get_timestamp() #TODO: make generic
        if self.operator == self.linear_mean_operator:
            dt = (msg.get_timestamp() - self.previous_timestamp).seconds()
            self.values += 0.5 * (self.previous_values + msg.get_values()) * dt
            self.previous_values = msg.get_values()
            self.previous_timestamp = msg.get_timestamp()
        if self.operator == self.block_mean_operator:
            dt = (msg.get_timestamp() - self.previous_timestamp).seconds()
            self.values += msg.get_values() * dt
            self.previous_timestamp = msg.get_timestamp()
        if self.operator == self.min_operator:
            self.values = numpy.minimum(self.values, msg.get_values())
        if self.operator == self.max_operator:
            self.values = numpy.maximum(self.values, msg.get_values())
