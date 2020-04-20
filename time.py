
"""
time module

"""

import datetime as _dt
from statistics import mean as _mean
import time as _time

DEF_COUNTRY = 'usa'
DEF_CITY    = 'vancouver'

MONTHS = ['january', 'february', 'march',
          'april', 'may', 'june', 'july',
          'august', 'september', 'october',
          'november', 'december']

TAD_BASE = 'https://www.timeanddate.com/astronomy' # astronomy or sun url base

class datetime(_dt.datetime):
    """Provides extension methods to the datetime.datetime object"""

    def round(self, minutes=0, seconds=0):
        """Rounds this datetime to the given number of nearest minutes and seconds.
           Returns self to allow for chaining"""
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

def get_time_struct():
    """Returns the local time as struct object"""
    return _time.localtime(_time.time())

def get_time_until(year, month, day):
    """Returns the timedelta object from today until the
       given year, month, day"""
    return _dt.datetime(year, month, day) - _dt.datetime.today()

class ReadingTimer(object):

    def __init__(self, pages=0, current_page=0, precision=2):
        self.pages = pages
        self.current_page = current_page
        self.precision = precision
        self.start_time = 0
        self.times = []
        self.__paused = True

    def average_time(self):
        if len(self.times) == 0:
            return 0
        return round(_mean(self.times), self.precision) # 2 for 0.

    def divmod_string(self):
        dm = divmod(self.average_time(), 60)
        return ', '.join(map(str, map(lambda t: round(t, self.precision), dm)))

    def elapsed(self):
        return _time.time() - self.start_time

    def human_report_projected(self):
        sec_left = self.seconds_left()
        if sec_left < 60:
            projected = str(round(sec_left, 2)) + ' seconds'
        else:
            projected = str(round(sec_left / 60, 2)) + ' minutes'
        return projected + ' left'

    def human_report_total(self):
        total_sec = self.seconds_total()
        if total_sec < 60:
            total = str(round(total_sec, 2)) + ' TOTAL seconds'
        else:
            total = str(round(total_sec / 60, 2)) + ' TOTAL minutes'
        return total

    def is_paused(self):
        return self.__paused

    def pages_left(self):
        return self.pages - self.current_page

    def pause(self):
        self.__paused_time = _time.time()
        self.__paused = True

    def resume(self):
        self.start_time += _time.time() - self.__paused_time
        self.__paused = False

    def seconds_left(self):
        return self.average_time() * self.pages_left()

    def seconds_total(self):
        return self.average_time() * self.pages

    def start(self):
        self.start_time = _time.time()
        self.__paused = False

    def turn_page(self, forward=True):
        # complete time-sensitive operations first
        self.times.append(round(self.elapsed(), self.precision))
        self.start()
        if forward:
            self.current_page += 1
        else:
            self.current_page -= 1

class SunTimes(object):
    """A class for storing sun data collected from timeanddate.com (c)
       in the following form:

           Rise/Set     |     Daylength       |   Solar Noon
       Sunrise | Sunset | Length | Difference | Time | Million Miles

       Countries with more than one occurence of a city require state abbrev.s,
       such as Portland, OR, and Portland, ME:
           city -> portland-or
           city -> portland-me

    """

    COLS = 6

    def __init__(self, country=DEF_COUNTRY, city=DEF_CITY, dynamic=False):
        self.country = country
        self.city = city
        self.dynamic = dynamic
        self.build()

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(country=%s, city=%s, dynamic=%s)' % (self.__class__.__name__,
                                                        self.country, self.city,
                                                        self.dynamic)

    def build(self):
        """Collects sun data and creates the following fields:
               req  = request response
               cont = web request content
               soup = `bs4` soup object
               data = list of data scraped

        """
        import textwrap as _textwrap
        from bs4 import BeautifulSoup as _BS
        import requests as _requests
        url = '/'.join([TAD_BASE, self.country, self.city])
        message = None
        try:
            req = _requests.get(url)
            if req.status_code != 200:
                raise Exception('request unsuccessful, used url: %s' % url)
            cont = req.content
            soup = _BS(cont, 'html.parser')
            scraped = [td.text for td in soup.select('#as-monthsun > tbody > tr > td')]
            # check for notes about daylight savings
            if scraped[0].startswith('Note'):
                message = scraped[0]
                print(message)
                scraped = scraped[1:]
        except Exception as e:
            print('A SunTimes instance made a request to:')
            print(' ' * 4 + url)
            print('which caused the folloing error:')
            print(_textwrap.indent(_textwrap.fill(str(e)), ' ' * 4))
            req = object()
            cont = ''
            soup = _BS(cont, 'html.parser')
            scraped = ['offline'] * SunTimes.COLS * 2

        # parse the data into rows
        data = []
        for i in range(0, len(scraped), SunTimes.COLS):
            data.append(scraped[i: i + SunTimes.COLS])

        # store relevant fields
        self.url     = url
        self.req     = req
        self.cont    = cont
        self.soup    = soup
        self.scraped = scraped
        self.data    = data
        self.message = message

        self.__date = _dt.date.today()

    def __check_date(self):
        if _dt.date.today() != self.__date and self.dynamic:
            self.rebuild()

    def __check_valid(self, day):
        if day < 0 or day >= len(self.data):
            raise ValueError('day must be from 0 to ' + str(len(self.data) - 1))

    def __validate(self, day):
        """Verifies that the requested day is valid and the data is up to date"""
        self.__check_valid(day)
        self.__check_date()

    def get_data(self):
        """Returns data retrieved and parsed from timeanddate.com (c)"""
        return self.data

    def get_message(self):
        """Prints out any important information such as daylight
           savings messages"""
        return self.message

    def get_sunrise(self, day=0):
        """Returns string of the sunrise time"""
        self.__validate(day)
        return self.data[day][0]

    def get_sunset(self, day=0):
        """Returns string of the sunset time"""
        self.__validate(day)
        return self.data[day][1]

    def get_solar_noon(self, day=0):
        """Returns string of the solar noon time"""
        self.__validate(day)
        return self.data[day][4]

    def rebuild(self):
        """An alias for building the relevant information. See `build`"""
        self.build()

if __name__ == '__main__':

    from clay.tests import testif

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

    print('birthday', get_time_until(2019, 11, 6))
    print('exams over', get_time_until(2018, 12, 13))

    print(get_time_struct())
    sun = SunTimes()
    print('sunset tonight is', sun.get_sunset())

