
"""
Net APIs

"""

import collections as _collections
import datetime as _dt
import json as _json
import re as _re
import sys as _sys
import time as _time

from bs4 import BeautifulSoup as _BS
import requests as _requests

from clay.models import Abstract as _Abstract
from clay.net import settings as net_settings
from clay.net.core import select_text, WebDocument
from clay.net.sockets import LOCALHOST as _LOCALHOST
from clay.utils import SortableDict

DEF_COUNTRY = 'usa'
DEF_CITY    = 'vancouver'

TAD_URL_BASE = 'https://www.timeanddate.com/astronomy'

class BaseSocketApiClient(_Abstract):

    """Used to create a socket API client"""

    def __init__(self, ip_addr, port, use_ssl=False):
        """Initializes this socket API client"""
        self.raise_if_base(BaseSocketApiClient)
        self.__ip_addr = ip_addr
        self.__port = port
        self.__use_ssl = use_ssl

    @property
    def ip_addr(self):
        """The socket IP address"""
        return self.__ip_addr

    @property
    def port(self):
        """The socket port"""
        return self.__port

    @property
    def use_ssl(self):
        """Whether or not to use SSL"""
        return self.__use_ssl

    @property
    def url(self):
        """The URL of the socket API"""
        return 'http{}://{}:{}'.format('s' if self.use_ssl else '',
            self.ip_addr,
            self.port)

class BaseLocalhostApiClient(BaseSocketApiClient):

    """Used to create a localhost API client"""

    def __init__(self, port, ip_addr=_LOCALHOST, use_ssl=False):
        """Initializes this localhost API client"""
        self.raise_if_base(BaseLocalhostApiClient)
        super().__init__(ip_addr, port, use_ssl=use_ssl)

class NationalTodayApiClient:

    """Used to get data from nationaltoday.com(tm)"""

    def __init__(self) -> None:
        """Initializes this national today API client"""
        pass

    def get_today(self) -> list:
        """Gets the list of holidays for today"""
        req = _requests.get('https://nationaltoday.com/what-is-today/')
        return self._get_mappings(req.content)

    def get_tomorrow(self) -> list:
        """Gets the list of holidays for tomorrow"""
        req = _requests.get('https://nationaltoday.com/what-is-tomorrow/')
        return self._get_mappings(req.content)

    def _get_mappings(self, request_content: bytes) -> dict:
        """Gets a mapping of holidays to links using the request content"""
        soup = _BS(request_content, 'html.parser')
        titles = select_text(soup, 'h3[class="holiday-title"]')
        links = [element.attrs.get('href') for element in soup.select('.day-card .title-box a')]

        mappings = SortableDict()
        for title, link in zip(titles, links):
            mappings[title.strip()] = link.strip()
        mappings.sort(key=lambda title: title.lower())
        return mappings

class PollenApiClient(object):

    """
    Class PollenApiClient can be used to retrieve and store information about
    the pollen forecast from The Weather Channel (tm) and Wunderground (tm)

    """

    MAX_REQUESTS = 4
    SOURCE_SPAN = {'weather text': 7, 'weather values': 7, 'wu poll': 4}
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
        """
        Raises `ZipCodeInvalidError` if the zipcode is invalid.
        Raises `ZipCodeNotSupportedError` if the zipcode is not supported.

        """
        if zipcode < 0 or zipcode > 99501 or len(str(zipcode)) != 5:
            raise ZipCodeInvalidError(zipcode)
        elif zipcode not in net_settings.pollen_source_urls:
            raise ZipCodeNotSupportedError(zipcode)

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
        self.uri = net_settings.pollen_source_urls[self.zipcode][source]
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

class SunTimesApiClient(object):
    """
    An API client for collecting sun times information from timeanddate.com (c)
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
        """Initializes this API client"""
        self.country = country
        self.city = city
        self.dynamic = dynamic
        self.build()

    def __repr__(self):
        """Returns the string representation of this API client"""
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(country=%s, city=%s, dynamic=%s)' % \
            (self.__class__.__name__,
            self.country, self.city,
            self.dynamic)

    def build(self):
        """
        Collects sun data and creates the following fields:
            req  = request response
            cont = web request content
            soup = `bs4` soup object
            data = list of data scraped

        """
        import textwrap as _textwrap
        from bs4 import BeautifulSoup as _BS
        import requests as _requests
        url = '/'.join([TAD_URL_BASE, self.country, self.city])
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
            print('A SunTimesApiClient instance made a request to:')
            print(' ' * 4 + url)
            print('which caused the folloing error:')
            print(_textwrap.indent(_textwrap.fill(str(e)), ' ' * 4))
            req = object()
            cont = ''
            soup = _BS(cont, 'html.parser')
            scraped = ['offline'] * SunTimesApiClient.COLS * 2

        # parse the data into rows
        data = []
        for i in range(0, len(scraped), SunTimesApiClient.COLS):
            data.append(scraped[i: i + SunTimesApiClient.COLS])

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
        """Checks the date last built and rebuilds if dynamic and not same-day"""
        if _dt.date.today() != self.__date and self.dynamic:
            self.rebuild()

    def __check_valid(self, day):
        """
        Raises `ValueError` if the given day is less than 0 or
        greater than the data range

        """
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
        """Returns any important info such as daylight savings time messages"""
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

class ZipCodeInvalidError(Exception):

    """Raised when a zipcode is invalid"""

    def __init__(self, zipcode, *args, **kwargs):
        self.zipcode = zipcode
        super().__init__(repr(self), *args, **kwargs)

    def __repr__(self):
        """Returns the string representation"""
        return str(self.zipcode)

class ZipCodeNotSupportedError(Exception):

    """Raised when a zipcode is not supported"""

    def __init__(self, zipcode, *args, **kwargs):
        self.zipcode = zipcode
        super().__init__(repr(self), *args, **kwargs)

    def __repr__(self):
        """Returns the string representation"""
        zipcodes = ', '.join(map(str, net_settings.pollen_source_urls.keys()))
        plural = zipcodes.count(',') > 0
        string = '{} is not supported. The only zipcode'.format(self.zipcode)
        if plural:
            string += 's'
        string += ' currently supported for PollenApiClient '
        if plural:
            string += 'are'
        else:
            string += 'is'
        string += ' ' + zipcodes
        return string

class YtVidApiClient:

    """API client for data on Youtube(tm) videos"""

    def __init__(self, vid_id: str) -> None:
        """Initializes this API client"""
        self.vid_id = vid_id
        self._soup = WebDocument('https://youtube.com/watch?v=' + self.vid_id).get_soup()
        self._duration = None
        self._title = None
        self._channel_name = None
        self._view_count = None
        self._publish_date = None
        self._short_desc = None
        self._long_desc = None

    def _get_metadata(self, node, selection: str) -> str:
        string = '[not avail.]'
        if node is not None:
            strings = node.select(selection)
            if len(strings) > 0:
                string = strings[0]['content']
        return string

    def get_duration(self) -> str:
        """Returns the duration for this video"""
        if self._duration is not None:
            return self._duration
        content = self._get_metadata(self._soup.html.head, 'meta[itemprop=duration]')
        found = _re.findall('(\d+)M(\d+)S', content)
        m, s = found[0] if len(found) > 0 else ('0', '0')
        m_int, s_int = int(m), int(s)
        h_int = 0
        while m_int > 60:
            h_int += 1
            m_int -= 60
        self._duration = '{:0>2d}:{:0>2d}:{:0>2d}'.format(h_int, m_int, s_int)
        return self._duration

    def get_title(self) -> str:
        """Returns the title for this video"""
        if self._title is not None:
            return self._title
        self._title = self._get_metadata(self._soup.html.head, 'meta[itemprop=name]')
        return self._title

    def get_channel_name(self) -> str:
        """Returns the channel name for this video"""
        if self._channel_name is not None:
            return self._channel_name
        self._channel_name = self._get_metadata(self._soup.html.head, 'link[itemprop=name]')
        return self._channel_name

    def get_view_count(self) -> int:
        """Returns the view count for this video"""
        if self._view_count is not None:
            return self._view_count
        self._view_count = int(self._get_metadata(self._soup.html.head, 'meta[itemprop=interactionCount]'))
        return self._view_count

    def get_publish_date(self) -> str:
        """Returns the publish date for this video"""
        if self._publish_date is not None:
            return self._publish_date
        self._publish_date = self._get_metadata(self._soup.html.head, 'meta[itemprop=datePublished]')
        return self._publish_date

    def get_short_desc(self) -> str:
        """Returns the short description for this video"""
        if self._short_desc is not None:
            return self._short_desc
        self._short_desc = self._get_metadata(self._soup.html.head, 'meta[name=description]')
        return self._short_desc

    def get_long_desc(self) -> str:
        """Returns the long description for this video"""
        if self._long_desc is not None:
            return self._long_desc
        text = self._soup.html.body.select('script')[0].getText()
        start = text[text.index('shortDescription') + len('shortDescription": '):]
        end = start[:start.index('","')]

        replaces = {
            'â\x9e\x94': '=>',
            '\\n': '\n',
            'â': '-',
            '\\"': '"',
            '\\u0026': '&',
        }

        for old, new in replaces.items():
            end = end.replace(old, new)

        self._long_desc = end
        return self._long_desc

    # TODO: expand to gather macro markers
    # body script key name: macroMarkersListItemRenderer

if __name__ == '__main__':

    import os
    import traceback

    from clay import settings
    from clay.tests import testif, testraises
    from clay.utils import qualify

    national_today_client = NationalTodayApiClient()
    print('holidays today:', national_today_client.get_today())
    print('holidays tomorrow:', national_today_client.get_tomorrow())

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
    testraises('zipcode invalid (zipcode: -1234)',
        lambda: p.set_zipcode(-1234),
        ZipCodeInvalidError,
        name=qualify(PollenApiClient.set_zipcode))
    testraises('zipcode invalid (zipcode: 1234)',
        lambda: p.set_zipcode(1234),
        ZipCodeInvalidError,
        name=qualify(PollenApiClient.set_zipcode))
    testraises('zipcode invalid (zipcode: 99502)',
        lambda: p.set_zipcode(99502),
        ZipCodeInvalidError,
        name=qualify(PollenApiClient.set_zipcode))
    testraises('zipcode not supported',
        lambda: p.set_zipcode(97132),
        ZipCodeNotSupportedError,
        name=qualify(PollenApiClient.set_zipcode))

    sun = SunTimesApiClient()
    print('sunset tonight is', sun.get_sunset())

    yt_vid = YtVidApiClient('0HoogBke26M')
    testif('returns correct video duration',
        yt_vid.get_duration(),
        '00:03:22',
        name=qualify(YtVidApiClient.get_duration))
    testif('returns correct video title',
        yt_vid.get_title(),
        'T-Rex Entry Scene (Jurassic Park) ● 8K HDR ● DTS X',
        name=qualify(YtVidApiClient.get_title))
    testif('returns correct video channel name',
        yt_vid.get_channel_name(),
        '4K Clips And Trailers',
        name=qualify(YtVidApiClient.get_channel_name))
    testif('returns correct video view count',
        yt_vid.get_view_count() > 4.1e6,
        True,
        name=qualify(YtVidApiClient.get_view_count))
    testif('returns correct video publish date',
        yt_vid.get_publish_date(),
        '2020-08-24',
        name=qualify(YtVidApiClient.get_publish_date))
    testif('returns correct video short description',
        yt_vid.get_short_desc(),
        'Play, save & stream 4K movie videos free on PC with 5KPlayer: ' + \
        'https://www.5kplayer.com/video-music-player/index.htm?ttref=20714' + \
        '-----------------------I DO NO...',
        name=qualify(YtVidApiClient.get_short_desc))
    testif('returns correct video long description',
        yt_vid.get_long_desc(),
        'Play, save & stream 4K movie videos free on PC with 5KPlayer: \n' + \
        'https://www.5kplayer.com/video-music-player/index.htm?ttref=20714\n' + \
        '\n' + \
        '-----------------------\n' + \
        'I DO NOT OWN THIS CLIP\n' + \
        'All rights owned by Universal Pictures\n' + \
        'https://www.youtube.com/universalpictures',
        name=qualify(YtVidApiClient.get_long_desc))
