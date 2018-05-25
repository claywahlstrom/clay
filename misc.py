
"""
misc: content that doesn't have a separate module

"""

import datetime as _dt
import json as _json
import math as _math
import time as _time

from bs4 import BeautifulSoup as _BeautifulSoup
import requests as _requests

from clay.shell import isUnix as _isUnix
from clay.web import WEB_HDR as _WEB_HDR

def human_hex(dec):
    """Converts decimal values to human readable hex.
       Mainly used in engineering class"""
    return hex(dec)[2:]

def map_args(function, iterable, *args, **kwargs):
    """Maps iterable to a function with arguments/keywords. 
       Dynamic types can be used"""
    return type(iterable)(function(x, *args, **kwargs) for x in iterable)

def map_args_test_function(x, y=2, z=3):
    return x + y + z
    
class Pollen(object):

    """Class Pollen can be used to retrieve and store information about
       the pollen forecast from The Weather Channel (tm) and Wunderground (tm)"""

    LAYERS = ('grass', 'ragweed', 'tree')
    MAX_TRIES = 4
    SOURCES = ('weather', 'wu poll', 'wu 7day')
    WUNDERDAYS = (0, 4, 7)
    WEATHER_QUERY = ':4:US'

    def __init__(self, source, zipcode=98105, print_sources=True):
        """Constructs a new Pollen object using the given source and zipcode"""
        assert source in Pollen.SOURCES
        self.wu_days = Pollen.WUNDERDAYS[Pollen.SOURCES.index(source)]
        self.zipcode = zipcode
        self.print_sources = print_sources
        self.source = source
        self.setzipcode(zipcode)
        self.build()

    def setzipcode(self, zipcode):
        """Sets the zipcode for this Pollen"""
        if self.source == Pollen.SOURCES[0]:
            self.uri = 'https://weather.com/forecast/allergy/l/' + str(zipcode)
        elif self.source == Pollen.SOURCES[1]:
            self.uri = 'https://www.wunderground.com/health/us/wa/seattle/KWASEATT446?cm_ven=localwx_modpollen'
        else:
            self.uri = 'https://api.weather.com/v2/indices/pollen/daypart/7day?apiKey=6532d6454b8aa370768e63d6ba5a832e&geocode=47.654003%2C-122.309166&format=json&language=en-US'
        self.zipcode = zipcode

    def _get_markup(self, uri):
        """Retrieves the markup with up to 4 max tries"""
        if self.source == Pollen.SOURCES[0]:
            params = _WEB_HDR
        else:
            params = dict()
        req = _requests.get(uri, params=params)
        retried = False
        tries = 1
        if req.status_code != 200:
            print('Retrying Pollen request', end='')
        while req.status_code != 200 and tries <= Pollen.MAX_TRIES:
            print('.', end='')
            _time.sleep(1.0)
            req = _requests.get(uri, params=params)
            tries += 1
        if tries > 1:
            print()
        return req.content

    def build(self, weather_query=True):
        """Builds and populates the pollen record database"""
        if self.source == Pollen.SOURCES[0] and weather_query:
            self.uri += self.WEATHER_QUERY
        markup = self._get_markup(self.uri)

        page = _BeautifulSoup(markup, 'html.parser')

        if self.source == Pollen.SOURCES[0]:
            found = page.select('button > div')
            records = dict()
            if len(found) > 0:
                for elm in found:
                    divs = elm.select('div')
                    records[divs[0].getText()] = divs[-1].getText()
        elif self.source == Pollen.SOURCES[1]:
            j = page.select('.count')
            records = {i: j[i].getText() for i in range(self.wu_days)} # or class .status
        else:
            js = _json.loads(markup)
            base = js['pollenForecast12hour']
            stored = list(base[layer + 'PollenIndex'] for layer in Pollen.LAYERS)
            lzt = list(zip(*stored))
            records = {i / 2: lzt[i] for i in range(len(lzt))}
            
        if len(records) == 0:
            if self.source == Pollen.SOURCES[0]:
                self.build(weather_query=not(weather_query))
            else:
                records = {i: 'null' for i in range(self.wu_days)['null']}
        self.src = page
        self.records = records

    def printall(self):
        """Prints all of the records information in a table format"""
        print('Pollen data for', self.zipcode)
        for i, j in self.records.items():
            print('{:>{}}: {}'.format(i, len('Tonight'), j))

    def get_day(self, day):
        """Returns the value in the records for the given day"""
        data = None
        if self.wu_days > 0 and day + 1 <= self.wu_days:
            # updates afternoon forecasts for today only (floor of cos of day)
            day += 0.5 * _math.floor(_math.cos(day)) * _math.floor(_dt.datetime.now().hour / 12)
            if type(self.records[day]) == str:
                data = self.records[day].title()
            else:
                data = self.records[day]
        else:
            date = str((_dt.date.today() + _dt.timedelta(days=day)).day)
            for dong in self.records:
                if dong.endswith(' ' + date):
                    data = self.records[dong]
                    break # not the best style but saves runtime
        if data is not None and self.print_sources:
            print('[{}] day={}'.format(self.source, day))
        return data

    def get_today(self):
        """Returns the type of pollen for today"""
        if self.source == Pollen.SOURCES[0]:
            if 'Tonight' in self.records:
                return self.records['Tonight']
            elif 'Today' in self.records:
                return self.records['Today']
        return self.get_day(0)

    def get_tomorrow(self):
        """Returns the type of pollen forecasted for tomorrow"""
        return self.get_day(1)

if __name__ == '__main__':

    print(human_hex(2700))
    print(map_args(map_args_test_function, (1, 4, 16, 25), z = 4))

    p = Pollen(2, zipcode=97132)
    p.printall()
    p.setzipcode(98105)
    p.build()
    p.printall()
