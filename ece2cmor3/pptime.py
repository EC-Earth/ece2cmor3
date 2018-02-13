import logging
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import numpy
from ece2cmor3 import ppmsg, ppop

log = logging.getLogger(__name__)

class time_integrator_node(ppop.post_proc_operator):

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
        self.coherency_keys = [ppmsg.message.variable_key, ppmsg.message.leveltype_key, ppmsg.message.level_key]

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
        start = self.start_date - self.interval
        end = self.start_date
        middle = start + timedelta(seconds=int((end - start)/total_seconds()/2))
        msg = ppmsg.memory_message(source=self.property_cache["variable"],
                                   timestamp=middle,
                                   level_type=self.property_cache["leveltype"],
                                   levels=self.property_cache["levels"],
                                   values=self.values)
        setattr(msg, "timebnd_left", start)
        setattr(msg, "timebnd_right", end)
        return msg
