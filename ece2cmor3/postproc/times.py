import logging
import numpy
import tempfile
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from ece2cmor3.postproc import message, operator

log = logging.getLogger(__name__)


class time_filter(operator.operator_base):

    def __init__(self, period):
        super(time_filter, self).__init__()
        self.period = period
        self.timestamp = None
        self.tnext, self.tprev = None, None
        self.cached_properties = [message.variable_key, message.leveltype_key,
                                  message.levellist_key, message.resolution_key]

    @staticmethod
    def is_linear():
        return True

    def fill_cache(self, msg):
        t = msg.get_timestamp()
        self.timestamp = t
        self.tnext = t + self.period
        dthrs = (self.tnext - t).total_seconds() / 3600
        if t.hour % int(round(dthrs)) == 0:
            self.values = msg.get_values()
            print "assigning values..."
            return True
        else:
            print "deleting values..."
            self.values = None
            return False

    def create_msg(self):
        return message.memory_message(variable=self.property_cache[message.variable_key],
                                      timestamp=self.timestamp,
                                      timebounds=[self.timestamp - self.period, self.timestamp],
                                      leveltype=self.property_cache[message.leveltype_key],
                                      levels=self.property_cache[message.levellist_key],
                                      resolution=self.property_cache[message.resolution_key],
                                      values=self.values)


class time_aggregator(operator.operator_base):
    linear_mean_operator = 1
    block_left_operator = 2
    block_right_operator = 3
    min_operator = 4
    max_operator = 5

    def __init__(self, operator_type, interval, filecache=True):
        super(time_aggregator, self).__init__()
        self.operator = operator_type
        self.interval = interval
        self.file_cache = filecache
        self.previous_values = None
        self.previous_timestamp = None
        self.remainder = None
        self.start_date = None
        self.full_cache = False
        self.cached_properties = [message.variable_key, message.leveltype_key,
                                  message.levellist_key, message.resolution_key]

    def is_linear(self):
        return self.operator in [time_aggregator.linear_mean_operator, time_aggregator.block_left_operator,
                                 time_aggregator.block_right_operator]

    @staticmethod
    def save_values(array):
        cache_file = tempfile.TemporaryFile()
        numpy.save(cache_file, array)
        return cache_file

    @staticmethod
    def mod_date(starttime, resolution):
        if resolution in [timedelta(days=1), relativedelta(days=1)]:
            return starttime.replace(hour=0, second=0, microsecond=0)
        if resolution == relativedelta(months=1):
            return starttime.replace(day=1, hour=0, second=0, microsecond=0)
        if resolution == relativedelta(years=1):
            return starttime.replace(month=1, day=1, hour=0, second=0, microsecond=0)
        return starttime.replace(second=0, microsecond=0)

    def set_values(self, values):
        self.values = self.save_values(values) if self.file_cache else values

    def get_values(self):
        if self.values is None:
            return None
        if self.file_cache:
            self.values.seek(0)
            return numpy.load(self.values)
        return self.values

    def set_previous_values(self, values):
        self.previous_values = self.save_values(values) if self.file_cache else values

    def get_previous_values(self):
        if self.previous_values is None:
            return None
        if self.file_cache:
            self.previous_values.seek(0)
            return numpy.load(self.previous_values)
        return self.previous_values

    def set_remainder(self, values):
        self.remainder = self.save_values(values) if self.file_cache else values

    def get_remainder(self):
        if self.remainder is None:
            return None
        if self.file_cache:
            self.remainder.seek(0)
            return numpy.load(self.remainder)
        return self.remainder

    def fill_cache(self, msg):
        # First time:
        if self.start_date is None:
            if self.operator in [self.min_operator, self.max_operator]:
                self.set_values(numpy.copy(msg.get_values()))
            else:
                timestamp = msg.get_timestamp()
                self.set_values(numpy.zeros(msg.get_values().shape, dtype=numpy.float64))
                self.set_previous_values(msg.get_values())
            self.start_date = msg.get_timestamp()
            self.previous_timestamp = msg.get_timestamp()
        else:
            timestamp = msg.get_timestamp()
            rounded_timestamp = self.mod_date(timestamp, self.interval)
            if rounded_timestamp != self.mod_date(self.start_date, self.interval):
                self.full_cache = True
                new_start_date = rounded_timestamp
                delta_left = (new_start_date - self.previous_timestamp).total_seconds()
                delta_right = (timestamp - new_start_date).total_seconds()
                norm_left = (new_start_date - self.start_date).total_seconds()
                norm_right = ((new_start_date + self.interval) - new_start_date).total_seconds()
                values = self.get_values()
                if self.operator == self.block_left_operator:
                    values += self.get_previous_values() * (delta_left / norm_left)
                    self.set_remainder(msg.get_values() * (delta_right / norm_right))
                elif self.operator == self.block_right_operator:
                    values += msg.get_values() * (delta_left / norm_left)
                    self.set_remainder(msg.get_values() * (delta_right / norm_right))
                elif self.operator == self.linear_mean_operator:
                    delta_tot = delta_left + delta_right
                    a1 = 0.5 * delta_left * (delta_right / delta_tot + 1) / norm_left
                    a2 = 0.5 * delta_left * delta_left / (delta_tot * norm_left)
                    b1 = 0.5 * delta_right * delta_right / (delta_tot * norm_right)
                    b2 = 0.5 * delta_right * (delta_left / delta_tot + 1) / norm_right
                    previous_values = self.get_previous_values()
                    values += (a1 * previous_values + a2 * msg.get_values())
                    self.set_remainder(b1 * previous_values + b2 * msg.get_values())
                self.set_values(values)
                self.set_previous_values(msg.get_values())
                self.start_date = new_start_date
            else:
                values = self.get_values()
                if self.remainder is not None:
                    values = self.get_remainder()
                    self.remainder = None
                future_start_date = self.mod_date(self.previous_timestamp, self.interval) + self.interval
                delta_t = (timestamp - self.previous_timestamp).total_seconds() / \
                          (future_start_date - self.start_date).total_seconds()
                if self.operator == self.block_left_operator:
                    values += self.get_previous_values() * delta_t
                    self.set_previous_values(msg.get_values())
                elif self.operator == self.block_right_operator:
                    values += msg.get_values() * delta_t
                    self.set_previous_values(msg.get_values())
                elif self.operator == self.linear_mean_operator:
                    values += 0.5 * delta_t * (self.get_previous_values() + msg.get_values())
                    self.set_previous_values(msg.get_values())
                elif self.operator == self.min_operator:
                    rhs = self.get_previous_values() if self.values is None else values
                    values = numpy.minimum(rhs, msg.get_values())
                elif self.operator == self.max_operator:
                    rhs = self.get_previous_values() if self.values is None else values
                    values = numpy.maximum(rhs, msg.get_values())
                else:
                    raise Exception("Unknown averaging operator")
                self.set_values(values)
            self.previous_timestamp = timestamp

    def clear_cache(self):
        self.values = None
        self.full_cache = False

    def cache_is_full(self):
        return self.full_cache and super(time_aggregator, self).cache_is_full()

    def create_msg(self):
        start = self.start_date - self.interval
        end = self.start_date
        middle = start + timedelta(seconds=int((end - start).total_seconds() / 2))
        msg = message.memory_message(variable=self.property_cache[message.variable_key],
                                     timestamp=middle,
                                     timebounds=[start, end],
                                     leveltype=self.property_cache[message.leveltype_key],
                                     levels=self.property_cache[message.levellist_key],
                                     resolution=self.property_cache[message.resolution_key],
                                     values=self.get_values())
        return msg
