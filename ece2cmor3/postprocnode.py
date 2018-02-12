import logging
# Log object.
from datetime import timedelta

import numpy
from dateutil.relativedelta import relativedelta

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
    block_left_operator = 2
    block_right_operator = 3
    min_operator = 4
    max_operator = 5

    def __init__(self, operator, interval):
        super(time_integrator_node, self).__init__()
        self.operator = operator
        self.interval = interval
        self.values = None
        self.previous_values = None
        self.previous_timestamp = None
        self.start_date = None
        self.coherency_keys = ["variable", "leveltype", "levels"]

    @staticmethod
    def next_step(start, stop, resolution):
        if resolution in [timedelta(hours=1), relativedelta(hours=1)]:
            return start.hour != stop.hour
        if resolution in [timedelta(days=1), relativedelta(days=1)]:
            return start.day != stop.day
        if resolution == relativedelta(months=1):
            return start.month != stop.month
        if resolution == relativedelta(years=1):
            return start.year != stop.year
        return False

    def fill_cache(self, msg):
        # First time:
        if self.start_date is None:
            if self.operator in [self.min_operator, self.max_operator]:
                self.values = numpy.copy(msg.get_values())
            else:
                self.previous_values = numpy.copy(msg.get_values())

            self.start_date = msg.get_timestamp()
        else:
            timestamp = msg.get_timestamp()
            if self.next_step(self.start_date, timestamp, self.interval):
                self.full_cache = True
                new_start_date = self.start_date + self.interval
                delta_left = (new_start_date - self.previous_timestamp).total_seconds()
                delta_right = (timestamp - new_start_date).total_seconds()
                norm_left = (new_start_date - self.start_date).total_seconds()
                norm_right = ((new_start_date + self.interval) - new_start_date).total_seconds()
                if self.operator == self.block_left_operator:
                    self.values += self.previous_values * (delta_left / norm_left)
                    self.previous_values = msg.get_values() * (delta_right / norm_right)
                elif self.operator == self.block_right_operator:
                    self.values += msg.get_values() * (delta_left / norm_left)
                    self.previous_values = msg.get_values() * (delta_right / norm_right)
                elif self.operator == self.linear_mean_operator:
                    delta_tot = delta_left + delta_right
                    a1 = 0.5 * delta_left * (delta_right / delta_tot + 1) / norm_left
                    a2 = 0.5 * delta_left * delta_left / (delta_tot * norm_left)
                    b1 = 0.5 * delta_right * delta_right / (delta_tot * norm_right)
                    b2 = 0.5 * delta_right * (delta_left / delta_tot + 1) / norm_right
                    self.values += (a1 * self.previous_values + a2 * msg.get_values())
                    self.previous_values = (b1 * self.previous_values + b2 * msg.get_values())
                else:
                    self.previous_values = numpy.copy(msg.get_values())
                self.start_date = new_start_date
                self.previous_timestamp = timestamp
                return
            elif self.values is None:
                self.values = self.previous_values
                self.previous_values = numpy.copy(msg.get_values())
            else:
                future_start_date = self.start_date + self.interval
                delta_t = (timestamp - self.previous_timestamp).total_seconds() / \
                          (future_start_date - self.start_date).total_seconds()
                if self.operator == self.block_left_operator:
                    self.values += self.previous_values * delta_t
                    self.previous_values = numpy.copy(msg.get_values())
                elif self.operator == self.block_right_operator:
                    self.values += msg.get_values() * delta_t
                    self.previous_values = numpy.copy(msg.get_values())
                elif self.operator == self.linear_mean_operator:
                    self.values += 0.5 * delta_t * (self.previous_values + msg.get_values())
                    self.previous_values = numpy.copy(msg.get_values())
                elif self.operator == self.min_operator:
                    self.values = numpy.minimum(self.values, msg.get_values())
                elif self.operator == self.max_operator:
                    self.values = numpy.maximum(self.values, msg.get_values())
                else:
                    raise Exception("Unknown averaging operator")

    def clear_cache(self):
        if self.values is not None:
            del self.values
            self.values = None

    def create_message(self):
        msg = super(time_integrator_node, self).create_message()
        setattr(msg, "timebnd_left", self.start_date - self.interval)
        setattr(msg, "timebnd_right", self.start_date)
        setattr(msg, "time_center", self.start_date - self.interval/2)
        return msg
