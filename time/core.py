
"""
time module

"""

import datetime as _dt
from statistics import mean as _mean
import time as _time

from clay.time.base import BaseDateTimeRange

MONTHS = ['january', 'february', 'march',
          'april', 'may', 'june', 'july',
          'august', 'september', 'october',
          'november', 'december']

class datetime(_dt.datetime):
    """Provides extension methods to the datetime.datetime object"""

    def round(self, minutes=0, seconds=0):
        """
        Rounds this datetime to the given number of nearest minutes and seconds.
        Returns self to allow for chaining

        """
        if seconds != 0:
            # if halfway or more
            if self.second % seconds >= seconds / 2:
                # round up
                self += _dt.timedelta(seconds=seconds - self.second % seconds)
            else:
                # round down
                self -= _dt.timedelta(seconds=self.second)

        if minutes != 0:
            # if halfway or more
            if self.minute % minutes >= minutes / 2:
                # round up
                self += _dt.timedelta(seconds=(minutes - self.minute % minutes) * 60)
            else:
                # round down
                self -= _dt.timedelta(seconds=self.minute % minutes * 60)

        return self

def get_next_hour(date=_dt.datetime.now()):
    """Returns the given datetime with the next hour and no total seconds"""
    return (date + _dt.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

def get_time_struct():
    """Returns the local time as struct object"""
    return _time.localtime(_time.time())

def get_time_until(year, month, day):
    """
    Returns the timedelta object from today until the given year, month, day

    """
    return _dt.datetime(year, month, day) - _dt.datetime.today()

class ReadingTimer(object):

    """Used to track reading rates"""

    def __init__(self, pages=0, current_page=0, precision=2):
        """Initializes this reading timer"""
        self.pages = pages
        self.current_page = current_page
        self.precision = precision
        self.start_time = 0
        self.times = []
        self.__paused = True

    def average_time(self):
        """Returns the average time in seconds per page"""
        if len(self.times) == 0:
            return 0
        return round(_mean(self.times), self.precision) # 2 for 0.

    def divmod_string(self):
        """Returns the string of the modulus division of average time"""
        dm = divmod(self.average_time(), 60)
        return ', '.join(map(str, map(lambda t: round(t, self.precision), dm)))

    def elapsed(self):
        """Returns the elapsed time since the start"""
        return _time.time() - self.start_time

    def human_report_projected(self):
        """Returns the human report projected time left to finish"""
        sec_left = self.seconds_left()
        if sec_left < 60:
            projected = str(round(sec_left, 2)) + ' seconds'
        else:
            projected = str(round(sec_left / 60, 2)) + ' minutes'
        return projected + ' left'

    def human_report_total(self):
        """Returns the human report total time"""
        total_sec = self.seconds_total()
        if total_sec < 60:
            total = str(round(total_sec, 2)) + ' TOTAL seconds'
        else:
            total = str(round(total_sec / 60, 2)) + ' TOTAL minutes'
        return total

    def is_paused(self):
        """Returns True if the reading timer is paused, False otherwise"""
        return self.__paused

    def pages_left(self):
        """Returns the number of pages left to read"""
        return self.pages - self.current_page

    def pause(self):
        """Pauses the reading timer"""
        self.__paused_time = _time.time()
        self.__paused = True

    def resume(self):
        """Resumes the reading timer"""
        self.start_time += _time.time() - self.__paused_time
        self.__paused = False

    def seconds_left(self):
        """Returns the number of seconds left to finish"""
        return self.average_time() * self.pages_left()

    def seconds_total(self):
        """Returns the number of total seconds"""
        return self.average_time() * self.pages

    def start(self):
        """Starts the reading timer"""
        self.start_time = _time.time()
        self.__paused = False

    def turn_page(self, forward=True):
        """Turns the page in the given direction (optional)"""
        # complete time-sensitive operations first
        self.times.append(round(self.elapsed(), self.precision))
        self.start()
        if forward:
            self.current_page += 1
        else:
            self.current_page -= 1

def round_nearest(hours, interval=0.5):
    """Rounds the given hours to the nearest interval-hour"""
    if interval <= 0:
        raise ValueError('interval must be greater than zero')
    return round(hours / interval) * interval

class TimeRange(BaseDateTimeRange):

    """Stores a range of dates for easy comparison"""

    def __repr__(self, now=_dt.time()) -> str:
        """Returns the string representation for this DateRange"""
        if self.start is None and self.end is None:
            return 'All Time'

        if self.start is None:
            string = 'Beginning'
        elif self.start == now:
            string = 'Now'
        else:
            string = str(self.start)

        if self.end == now:
            if self.start == now:
                return string
            else:
                return string + ' - Now'
        elif self.end is None:
            string += ' - Continuous'
        else:
            string += ' - ' + str(self.end)
        return string

if __name__ == '__main__':

    from clay.tests import testif, testraises
    from clay.utils import qualify

    testif('datetime rounds seconds down',
       datetime(2000, 1, 1, 0, 0, 2).round(seconds=5),
       _dt.datetime(2000, 1, 1, 0, 0, 0))

    testif('datetime rounds seconds up',
        datetime(2000, 1, 1, 0, 0, 4).round(seconds=5),
       _dt.datetime(2000, 1, 1, 0, 0, 5))

    testif('datetime rounds minutes down',
        datetime(2000, 1, 1, 0, 9).round(minutes=20),
       _dt.datetime(2000, 1, 1, 0, 0))

    testif('datetime rounds minutes up',
        datetime(2000, 1, 1, 0, 10).round(minutes=20),
       _dt.datetime(2000, 1, 1, 0, 20))

    testif('datetime rounds minutes down near hour',
        datetime(2000, 1, 1, 0, 45).round(minutes=20),
       _dt.datetime(2000, 1, 1, 0, 40))

    testif('datetime rounds minutes up near hour',
        datetime(2000, 1, 1, 0, 50).round(minutes=20),
       _dt.datetime(2000, 1, 1, 1, 0))

    get_next_date_tests = [
        (
            _dt.datetime(2021, 7, 21, 0, 0, 24, 627),
            _dt.datetime(2021, 7, 21, 1, 0, 0, 0)
        ),
        (
            _dt.datetime(2021, 7, 21, 0, 1, 37, 145525),
            _dt.datetime(2021, 7, 21, 1, 0, 0, 0)
        ),
        (
            _dt.datetime(2021, 7, 21, 0, 59, 42, 236125),
            _dt.datetime(2021, 7, 21, 1, 0, 0, 0)
        ),
        (
            _dt.datetime(2021, 7, 21, 1, 1, 28, 983788),
            _dt.datetime(2021, 7, 21, 2, 0, 0, 0)
        )
    ]

    for get_next_date_test in get_next_date_tests:
        date = get_next_date_test[0]
        testif('returns correct date (date: {})'.format(date),
            get_next_hour(date),
            get_next_date_test[1],
            name=qualify(get_next_hour))

    print('birthday', get_time_until(2019, 11, 6))
    print('exams over', get_time_until(2018, 12, 13))

    print(get_time_struct())

    testraises('interval is zero',
        lambda: round_nearest(1, 0),
        ValueError,
        name=qualify(round_nearest))
    testraises('interval is less than zero',
        lambda: round_nearest(1, -1),
        ValueError,
        name=qualify(round_nearest))

    for quarter_hour_test in [(0.1, 0.1), (0.2, 0.25), (0.3, 0.25), (0.4, 0.5)]:
        testif('rounds to nearest interval (interval: 0.25, datarow: {})'.format(quarter_hour_test[0]),
            round_nearest(quarter_hour_test[0], quarter_hour_test[1]),
            quarter_hour_test[1],
            name=qualify(round_nearest))

    nearest_half_hour_tests = [
        (0.2, 0),
        (0.3, 0.5),
        (0.5, 0.5),
        (0.7, 0.5),
        (0.8, 1.0),
        (1.62, 1.5)
    ]

    for half_hour_test in nearest_half_hour_tests:
        testif('rounds to nearest interval (interval: 0.5, datarow: {})'.format(half_hour_test[0]),
            round_nearest(half_hour_test[0]),
            half_hour_test[1],
            name=qualify(round_nearest))
