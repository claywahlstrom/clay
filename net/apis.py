
"""
Net APIs

"""

import collections as _collections
import datetime as _dt
import json as _json
import sys as _sys
import time as _time

from bs4 import BeautifulSoup as _BS
import requests as _requests

from clay.models import Abstract as _Abstract
from clay.net.builders import WundergroundUrlBuilder, UrlBuilder
from clay.net.sockets import LOCALHOST as _LOCALHOST

class BaseSocketApiClient(_Abstract):

    """Used to create a socket API client"""

    def __init__(self, ip_addr, port):
        """Initializes this socket API client"""
        self.raise_if_base(BaseSocketApiClient)
        self.__ip_addr = ip_addr
        self.__port = port

    @property
    def ip_addr(self):
        """The socket IP address"""
        return self.__ip_addr

    @property
    def port(self):
        """The socket port"""
        return self.__port

    @property
    def url(self):
        """The URL of the socket API"""
        return 'http://{}:{}'.format(self.ip_addr, self.port)

class BaseLocalhostApiClient(BaseSocketApiClient):

    """Used to create a localhost API client"""

    def __init__(self, port):
        """Initializes this localhost API client"""
        self.raise_if_base(BaseLocalhostApiClient)
        super().__init__(_LOCALHOST, port)

class WeatherPollenApiUrlBuilder(UrlBuilder):

    """Used to build URLs for the Weather.com(tm) pollen API"""

    def __init__(self):
        """Initializes this builder"""
        super().__init__('https://api.weather.com/v2/indices/pollen/daypart/7day')
        self.base_url = self.with_query_params({
            'apiKey': '6532d6454b8aa370768e63d6ba5a832e',
            'format': 'json',
            'language': 'en-US'
        }).build()

    def with_geocode(self, lat, lon):
        """Adds the geocode latitude and longitude param to the URL"""
        return self.reset() or self.with_query_params({'geocode': str(lat) + ',' + str(lon)})

class PollenUrlBuilderFactory(object):

    """Used to allow access to the pollen URL builders"""

    def __init__(self):
        """Initializes thie pollen URL builder factory"""
        self.__weather = WeatherPollenApiUrlBuilder()
        self.__wunderground = WundergroundUrlBuilder()

    @property
    def weather(self):
        """Returns the Weather.com(tm) URL builder"""
        return self.__weather

    @property
    def wunderground(self):
        """Returns the Wunderground(tm) URL builder"""
        return self.__wunderground

class PollenApiClient(object):

    """
    Class PollenApiClient can be used to retrieve and store information about
    the pollen forecast from The Weather Channel (tm) and Wunderground (tm)

    """

    URL_FACTORY = PollenUrlBuilderFactory()

    MAX_REQUESTS = 4
    SOURCE_SPAN = {'weather text': 7, 'weather values': 7, 'wu poll': 4}
    SOURCE_URLS = {
        98105: {
            'weather values': URL_FACTORY.weather.with_geocode(47.654003, -122.309166).build(),
            'wu poll': URL_FACTORY.wunderground \
                .with_location('wa', 'seattle', 'KWASEATT446') \
                .with_query_params({'cm_ven': 'localwx_modpollen'}) \
                .build()
        },
        98684: {
            'weather values': URL_FACTORY.weather.with_geocode(45.639816, -122.497902).build(),
            'wu poll': URL_FACTORY.wunderground \
                .with_location('wa', 'vancouver', 'KWAVANCO547') \
                .with_query_params({'cm_ven': 'localwx_modpollen'}) \
                .build()
        }
    }

    for url in SOURCE_URLS:
        # weather text and values use the same endpoint
        SOURCE_URLS[url]['weather text'] = SOURCE_URLS[url]['weather values']
    del url # remove from scope
    TYPES = ('grass', 'ragweed', 'tree')

    def __init__(self, source, zipcode, print_sources=True):
        """
        Initializes this PollenApiClient object using the given source and
        zipcode. Builds the database when all inputs are valid.

        """
        self.zipcode = zipcode
        self.source = source
        self.set_zipcode(zipcode)
        self.print_sources = print_sources
        self.__date_built = None
        self.build()

    def __repr__(self):
        """Returns the string representation of this PollenApiClient instance"""
        return 'PollenApiClient(source={{{}}}, zipcode={}, print_sources={})' \
            .format(self.source, self.zipcode, self.print_sources)

    def __check_built(self):
        """Throws a RuntimeError if this PollenApiClient instance has not been built"""
        if not self.has_built:
            raise RuntimeError('PollenApiClient must be built after zipcode or source has been changed')

    def __verify_source(self, source):
        """Raises `ValueError` if the source is invalid"""
        if source not in PollenApiClient.SOURCE_SPAN.keys():
            raise ValueError('source must be one from [{}]'.format(", ".join(PollenApiClient.SOURCE_SPAN.keys())))

    def __verify_zipcode(self, zipcode):
        """Raises `ZipCodeNotFoundException` if the zipcode is invalid"""
        if zipcode not in PollenApiClient.SOURCE_URLS.keys() or zipcode < 0 or zipcode > 99501:
            raise ZipCodeNotFoundError(zipcode)

    def __get_markup(self, uri):
        """
        Retrieves the markup with up to 4 max tries. Returns empty
        markup if web requests fail

        """

        unsuccessful = True
        tries = 0
        while unsuccessful and tries < PollenApiClient.MAX_REQUESTS:
            try:
                print('Requesting "{}" for zipcode {}...'.format(self.source, self.zipcode))
                req = _requests.get(uri)
                unsuccessful = False
            except Exception as e:
                if tries == 0:
                    print('Retrying PollenApiClient request', end='', flush=True)
                else:
                    print('.', end='', flush=True)
            _time.sleep(1.0)
            tries += 1

        if tries > 1:
            print() # flush newline to stdout
            return b''

        return req.content

    def build(self):
        """Builds and populates the pollen client database"""

        markup = self.__get_markup(self.uri)

        if markup:
            self.soup = _BS(markup, 'html.parser')

            if self.source.startswith('weather'):
                js = _json.loads(markup.decode('latin-1'))
                base = js['pollenForecast12hour']
                # weather report type is Index for values and Category for text
                report_type = 'Index' if self.source == 'weather values' else 'Category'
                stored = list(base[layer + 'Pollen' + report_type] for layer in PollenApiClient.TYPES)
                lzt = list(zip(*stored)) # zips each layer to their corresponding value
                db = _collections.OrderedDict()
                for i in range(len(lzt)):
                    db[i / 2] = lzt[i]
            else: # self.source == 'wu poll'
                j = self.soup.select('.count') # or class .status
                db = _collections.OrderedDict()
                for i in range(PollenApiClient.SOURCE_SPAN[self.source]):
                    db[i] = j[i].get_text()
            if len(db) == 0:
                # populate database with empty values
                db = _collections.OrderedDict({i: 'null' for i in range(PollenApiClient.SOURCE_SPAN[self.source])})
        else:
            # populate the database with the most general structure of data
            # current generalization: weather values [0.0, 0.5, ...]
            db = {i / 2: 'null' for i in range(2 * PollenApiClient.SOURCE_SPAN[self.source])}
            self.soup = None

        self.__db = db
        self.__date_built = _dt.datetime.today()

    def get_day(self, day):
        """Returns the value in the database for the given day"""
        self.__check_built()

        data = None

        if self.source == 'wu poll':
            data = self.db[int(day)].title()
        else:
            data = self.db[day]

        if data is not None and self.print_sources:
            print('{{source={}, day={}}}'.format(self.source, day))

        return data

    def get_today(self):
        """Returns the pollen data for today"""
        # if built before noon and is currently afternoon
        if self.has_built and self.date_built.hour < 12 \
                and _dt.datetime.today().hour >= 12:
            # report the afternoon data
            return self.get_day(0.5)
        else:
            # report the current data
            return self.get_day(0)

    def get_tomorrow(self):
        """Returns the pollen data forecasted for tomorrow"""
        return self.get_day(1) # checks for valid db in get_day

    def print_db(self, file=_sys.stdout):
        """Prints all of the db information in a table format"""
        self.__check_built()
        print('Pollen data for', self.zipcode, file=file)
        for i, j in self.db.items():
            print('{:>4}: {}'.format(i, j), file=file)

    def set_source(self, source):
        """
        Sets the source for this PollenApiClient object.
        Requires `build` to be called to update data

        """
        self.__verify_source(source)
        self.uri = PollenApiClient.SOURCE_URLS[self.zipcode][source]
        self.source = source
        self.__date_built = None

    def set_zipcode(self, zipcode):
        """
        Sets the zipcode for this PollenApiClient object.
        Requires `build` to be called to update data

        """
        self.__verify_zipcode(zipcode)
        self.zipcode = zipcode
        self.set_source(self.source) # ensures data is updated if the method is 'weather text'

    @property
    def db(self):
        """This PollenApiClient's database"""
        return self.__db

    @property
    def date_built(self):
        """Returns the last date the database is built"""
        return self.__date_built

    @property
    def has_built(self):
        """Returns True if this client has built the database, False otherwise"""
        return self.date_built is not None

class ZipCodeNotFoundError(Exception):

    """Raised when a zipcode is invalid (not found)"""

    def __init__(self, zipcode, *args, **kwargs):
        super().__init__(repr(self), *args, **kwargs)
        self.zipcode = zipcode

    def __repr__(self):
        """Returns the string representation"""
        zipcodes = ', '.join(map(str, PollenApiClient.SOURCE_URLS.keys()))
        plural = zipcodes.count(',') > 0
        string = 'The only zipcode'
        if plural:
            string += 's'
        string += ' currently supported for PollenApiClient '
        if plural:
            string += 'are'
        else:
            string += 'is'
        string += ' ' + zipcodes
        return string

if __name__ == '__main__':

    import os
    import traceback

    from clay import settings
    from clay.tests import testraises
    from clay.utils import qualify

    p = PollenApiClient('weather text', 98684)
    with open(os.path.join(settings.LOGS_DIR, 'net-core-pollen.log'), 'w') as pollen_log:
        try:
            p.print_db(file=pollen_log)
            p.set_source('weather values')
            p.set_zipcode(98105)
            p.build()
            p.print_db(file=pollen_log)
        except Exception:
            traceback.print_exc()

    testraises('source invalid',
        lambda: p.set_source('invalid source'),
        ValueError,
        name=qualify(PollenApiClient.set_source))
    testraises('zipcode invalid',
        lambda: p.set_zipcode(97132),
        ZipCodeNotFoundError,
        name=qualify(PollenApiClient.set_zipcode))
