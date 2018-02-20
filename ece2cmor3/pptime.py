import logging
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import numpy
from ece2cmor3 import ppmsg, ppop

log = logging.getLogger(__name__)


class time_filter(ppop.post_proc_operator):

    def __init__(self, period):
        super(time_filter, self).__init__()
        self.period = period
        self.timestamp = None
        self.cached_properties = [ppmsg.message.variable_key, ppmsg.message.leveltype_key, ppmsg.message.levellist_key]

    def fill_cache(self, msg):
        t = msg.get_timestamp()
        self.timestamp = t
        tnext = t + self.period
        dthrs = (tnext - t).total_seconds() / 3600
        if t.hour % int(round(dthrs)) == 0:
            self.values = msg.get_values()
            return True
        else:
            self.values = None
            return False

    def create_msg(self):
        return ppmsg.memory_message(source=self.property_cache["variable"],
                                    timestamp=self.timestamp,
                                    leveltype=self.property_cache["leveltype"],
                                    levels=self.property_cache["levels"],
                                    values=self.values)


class time_aggregator(ppop.post_proc_operator):
    linear_mean_operator = 1
    block_left_operator = 2
    block_right_operator = 3
    min_operator = 4
    max_operator = 5

    def __init__(self, operator, interval):
        super(time_aggregator, self).__init__()
        self.operator = operator
        self.interval = interval
        self.previous_values = None
        self.previous_timestamp = None
        self.remainder = None
        self.start_date = None
        self.full_cache = False
        self.cached_properties = [ppmsg.message.variable_key, ppmsg.message.leveltype_key, ppmsg.message.levellist_key]

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
                self.values = numpy.zeros(msg.get_values().shape, msg.get_values().dtype)
                self.previous_values = numpy.copy(msg.get_values())

            self.start_date = msg.get_timestamp()
            self.previous_timestamp = msg.get_timestamp()
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
                    self.remainder = msg.get_values() * (delta_right / norm_right)
                elif self.operator == self.block_right_operator:
                    self.values += msg.get_values() * (delta_left / norm_left)
                    self.remainder = msg.get_values() * (delta_right / norm_right)
                elif self.operator == self.linear_mean_operator:
                    delta_tot = delta_left + delta_right
                    a1 = 0.5 * delta_left * (delta_right / delta_tot + 1) / norm_left
                    a2 = 0.5 * delta_left * delta_left / (delta_tot * norm_left)
                    b1 = 0.5 * delta_right * delta_right / (delta_tot * norm_right)
                    b2 = 0.5 * delta_right * (delta_left / delta_tot + 1) / norm_right
                    self.values += (a1 * self.previous_values + a2 * msg.get_values())
                    self.remainder = (b1 * self.previous_values + b2 * msg.get_values())
                self.previous_values = numpy.copy(msg.get_values())
                self.start_date = new_start_date
            else:
                if self.remainder is not None:
                    self.values = self.remainder
                    self.remainder = None
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
                    rhs = self.previous_values if self.values is None else self.values
                    self.values = numpy.minimum(rhs, msg.get_values())
                elif self.operator == self.max_operator:
                    rhs = self.previous_values if self.values is None else self.values
                    self.values = numpy.maximum(rhs, msg.get_values())
                else:
                    raise Exception("Unknown averaging operator")
            self.previous_timestamp = timestamp

    def clear_cache(self):
        self.values = None
        self.full_cache = False

    def cache_is_full(self):
        return self.full_cache

    def create_msg(self):
        start = self.start_date - self.interval
        end = self.start_date
        middle = start + timedelta(seconds=int((end - start).total_seconds() / 2))
        msg = ppmsg.memory_message(source=self.property_cache["variable"],
                                   timestamp=middle,
                                   leveltype=self.property_cache["leveltype"],
                                   levels=self.property_cache["levels"],
                                   values=self.values)
        setattr(msg, "timebnd_left", start)
        setattr(msg, "timebnd_right", end)
        return msg
