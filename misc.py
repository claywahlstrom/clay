
"""
misc: content that doesn't have a separate module

TODO (Pollen): allow multiple zipcodes for the given sources
                 - retrieve each api link
                 - use zip codes to lookup the dictionary of url sources

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

def map_args_test(x, y=2, z=3):
    """A test function for the map_args function. Returns the sum of x, y, z"""
    return x + y + z
    
class Pollen(object):

    """Class Pollen can be used to retrieve and store information about
       the pollen forecast from The Weather Channel (tm) and Wunderground (tm)"""

    MAX_REQUESTS = 4
    SOURCE_SPAN = {'weather text': 7, 'weather values': 7, 'wu poll': 4}
    SOURCE_URLS = {98105: {'weather text': 'https://weather.com/forecast/allergy/l/',
                           'weather values': 'https://api.weather.com/v2/indices/pollen/daypart/7day?apiKey=6532d6454b8aa370768e63d6ba5a832e&geocode=47.654003%2C-122.309166&format=json&language=en-US',
                           'wu poll': 'https://www.wunderground.com/health/us/wa/seattle/KWASEATT446?cm_ven=localwx_modpollen'},
                   98684: {'weather text': 'https://weather.com/forecast/allergy/l/',
                           'weather values': 'https://api.weather.com/v2/indices/pollen/daypart/7day?apiKey=6532d6454b8aa370768e63d6ba5a832e&geocode=45.639816%2C-122.497902&format=json&language=en-US',
                           'wu poll': 'https://www.wunderground.com/health/us/wa/camas/KWACAMAS42?cm_ven=localwx_modpollen'}}
    TYPES = ('grass', 'ragweed', 'tree')
    WEATHER_QUERY_PARAMS = ':4:US'

    def __init__(self, source, zipcode=98105, print_sources=True):
        """Constructs a new Pollen object using the given source and zipcode"""
        self.zipcode = zipcode
        self.print_sources = print_sources
        self.source = source
        self.setsource(source)
        self.setzipcode(zipcode)
        self.build()

    def setzipcode(self, zipcode):
        """Sets the zipcode for this Pollen object. Requires `build` to be called to update data"""
        if self.source != 'weather text' and not(zipcode in Pollen.SOURCE_URLS.keys()):
            raise ValueError('only zipcode(s) {} are supported for values or Wunderground'.format(', '.join(SOURCE_URLS.keys())))
        assert zipcode >= 0 and zipcode <= 99501 # valid US zipcode
        self.zipcode = zipcode
        self.setsource(self.source)
        
    def setsource(self, source):
        """Sets the source for this Pollen object. Requires `build` to be called to update data"""
        assert source in Pollen.SOURCE_SPAN.keys()
        self.uri = Pollen.SOURCE_URLS[self.zipcode][source]
        if source == 'weather text':
            self.uri += str(self.zipcode)
        self.source = source

    def _get_markup(self, uri):
        """Retrieves the markup with up to 4 max tries"""
        if self.source == 'weather text':
            params = _WEB_HDR
        else:
            params = dict()
        req = _requests.get(uri, params=params)
        retried = False
        tries = 1
        if req.status_code != 200:
            print('Retrying Pollen request', end='')
        while req.status_code != 200 and tries <= Pollen.MAX_REQUESTS:
            print('.', end='')
            _time.sleep(1.0)
            req = _requests.get(uri, params=params)
            tries += 1
        if tries > 1:
            print()
        return req.content

    def build(self, weather_query=True):
        """Builds and populates the pollen record database"""
        uri = self.uri
        if self.source == 'weather text' and weather_query:
            uri += self.WEATHER_QUERY_PARAMS
        markup = self._get_markup(uri)

        page = _BeautifulSoup(markup, 'html.parser')

        if self.source == 'weather text':
            found = page.select('button > div')
            records = dict()
            if len(found) > 0:
                for elm in found:
                    divs = elm.select('div')
                    records[divs[0].getText()] = divs[-1].getText()
        elif self.source == 'weather values':
            js = _json.loads(markup)
            base = js['pollenForecast12hour']
            stored = list(base[layer + 'PollenIndex'] for layer in Pollen.TYPES)
            lzt = list(zip(*stored))
            records = {i / 2: lzt[i] for i in range(len(lzt))}
        else:
            j = page.select('.count') # or class .status
            records = {i: j[i].getText() for i in range(Pollen.SOURCE_SPAN[self.source])}
        if len(records) == 0:
            if self.source == 'weather text':
                self.build(weather_query=not(weather_query))
            else:
                records = {i: 'null' for i in range(Pollen.SOURCE_SPAN[self.source])['null']}
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
        if self.source == 'weather text':
            date = str((_dt.date.today() + _dt.timedelta(days=day)).day)
            for dong in self.records:
                if dong.endswith(' ' + date):
                    data = self.records[dong]
                    break # not the best style but saves runtime
        else:
            # updates afternoon forecasts for today only (floor of cos of day)
            day += 0.5 * _math.floor(_math.cos(day)) * _math.floor(_dt.datetime.now().hour / 12)
            if type(self.records[day]) == str:
                data = self.records[int(day)].title()
            else:
                data = self.records[day]
        if data is not None and self.print_sources:
            print('[{}] day={}'.format(self.source, day))
        return data

    def get_today(self):
        """Returns the type of pollen for today"""
        if self.source == 'weather text':
            if 'Tonight' in self.records:
                return self.records['Tonight']
            elif 'Today' in self.records:
                return self.records['Today']
        return self.get_day(0)

    def get_tomorrow(self):
        """Returns the type of pollen forecasted for tomorrow"""
        return self.get_day(1)

if __name__ == '__main__':

    print('human hex for 2700', human_hex(2700))
    print('map args on test function', map_args(map_args_test, (1, 4, 16, 25), z = 4))

    p = Pollen('weather text', zipcode=97132)
    p.printall()
    p.setsource('weather values')
    p.setzipcode(98105)
    p.build()
    p.printall()
    
    # other unit tests
    # for i in Pollen.SOURCE_SPAN.keys():
        # p.setsource(i)
        # p.build()
        # p.printall()
