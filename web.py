
"""
web module

TODO (web-header): fix the web header to fix google.com rendering JS problem using
                       alternate accept-char types

"""

import datetime as _dt
import json as _json
import math as _math
import os as _os
import re as _re
import requests as _requests
from subprocess import call as _call
import sys as _sys
import time as _time
import urllib.request, urllib.error, urllib.parse

import requests as _requests
from bs4 import BeautifulSoup as _BS

from clay.shell import \
    get_docs_folder as _get_docs_folder, \
    is_idle as _is_idle, \
    is_unix as _is_unix

CHUNK_CAP = int(1e6) # 1MB

# download links for testing
LINKS = {}
LINK_SIZES = list(map(lambda n: str(n) + 'MB', [1, 2, 5, 10, 20, 50, 100, 200, 512]))
for n in LINK_SIZES:
    LINKS[n] = 'http://download.thinkbroadband.com/' + str(n) + '.zip'
LINKS['1GB'] = 'http://download.thinkbroadband.com/1GB.zip'

TEST_LINK = 'https://minecraft.net/en-us/'

WEB_HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
           #'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept': 'text/html,text/plain,application/xhtml+xml,application/xml,application/_json;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Charset': 'Windows-1252,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'en-US,en;q=0.8;q=0.5',
           'Connection': 'keep-alive'}

class CacheableFile(object):
    """Class Cache can be used to manage file caching on your local machine,
       accepts one uri. The caching system will use the local version of
       the file if it exists. Otherwise it will be downloaded from the server.

       The main advantage is saving time by eliminating downloads

    """

    def __init__(self, reload_on_set=False):
        """Initializes a new Cache object"""
        self.reloaded = False
        self.reload_on_set = reload_on_set
        self.remote_content = None

    def exists(self):
        """Returns a boolean of whether the file exists"""
        return _os.path.exists(self.title)

    def get_local(self):
        """Returns the content of the local cached file"""
        assert self.exists()
        with open(self.title, 'rb') as fp:
            fread = fp.read()
        return fread

    def get_remote(self):
        """Returns the content of the remote file. Stores a copy
           in this object for future reloads to reduce bandwidth."""
        self.remote_content = _requests.get(self.uri).content
        return self.remote_content

    def get_title(self):
        return self.title

    def is_updated(self):
        """Returns True if the cached file has the same
           length as the remote file, False otherwise"""
        return len(self.get_local()) == len(self.get_remote())

    def length(self):
        """Returns the length of the locally cached byte file"""
        return len(self.get_local())

    def load(self):
        """Returns binary content from self.title"""
        print('Loading cached file "{}"...'.format(self.title), end=' ')
        cont = self.get_local()
        print('Done')
        return cont

    def reload(self):
        """Alias for `store`, but easier to remember for humans
           Commonly performed outside of a script"""
        print('Performing a cache reload for "{}"...'.format(self.title))
        self.store()

    def set(self, uri, title=None):
        """Sets the cache to point to the given uri with the optional title"""

        if not('http' in uri):
            raise ValueError('invalid uri')

        if title is None:
            title = WebDocument(uri).get_basename()[0]
        self.title = title

        self.uri = uri
        self.__init__(reload_on_set=self.reload_on_set)

        if self.reload_on_set and not(_os.path.exists(self.title)):
            self.store()

    def store(self):
        """Writes the binary content of the requested uri to the disk.
           Writes and erases the remote content copy if it exists."""
        print('Storing cached file "{}"...'.format(self.title), end=' ')
        with open(self.title, 'wb') as fp:
            if self.remote_content is not None:
                fp.write(self.remote_content)
                self.remote_content = None
            else:
                fp.write(self.get_remote())
        print('Done')
        self.reloaded = True

class CourseCatalogUW(object):

    """This class can be used to lookup courses by their ID
       on the University of Washington's Course Catalog.

       Query:
           CEE for a list of all classes in the department
           AES 1-25 or PHYS 12 or PHIL 1 for a narrowed listing
           MATH 126 for a description of the course

       Casing is ignored

    """

    CATALOG_URI = 'https://www.washington.edu/students/crscat/'

    def __init__(self):
        pages = {}

        pages['list'] = _BS(_requests.get(CourseCatalogUW.CATALOG_URI).content, 'html.parser')
        depts = [item['href'] for item in pages['list'].select('a')]
        depts = [item[:item.index('.')] for item in depts if not('/' in item) and item.endswith('.html')]
        depts.sort()

        self.depts = depts
        self.MAX_LENGTH = max(map(len, depts))
        self.pages = pages

    def get_departments(self):
        return self.depts

    def print_departments(self):
        for i, j in enumerate(self.depts):
            if i % 6 != 0:
                print(j, end=int(_math.ceil(_math.ceil(self.MAX_LENGTH / 8) - len(j) / 8)) * '\t')
            else:
                print()
        print() # flush output

    def query(self, text):
        message = None
        header = None # department header
        course_list = []
        parts = text.strip().lower().split()
        if len(parts) > 0 and parts[0] in self.depts: # if a valid department
            if not(parts[0] in self.pages): # insert into cache
                link = CourseCatalogUW.CATALOG_URI + parts[0] + '.html'
                self.pages[parts[0]] = _BS(_requests.get(link).content, 'html.parser')
            already_set = False
            found = self.pages[parts[0]].select('p b') # get all class elements
            if len(parts) == 2:
                if len(parts[1]) < 3 or '-' in parts[1]: # if not specific class
                    levels = list(map(int, parts[1].split('-')))
                    # remove spaces for oddly named titles and departments
                    numbers = [int(_re.findall('\d+', item.get_text().lower().replace(' ', ''))[0]) for item in found]
                    for i, level in enumerate(levels):
                        while len(str(levels[i])) < 3:
                            levels[i] *= 10
                    temp = []
                    for i, number in enumerate(numbers): # previous: any(str(number).startswith(str(level)) for level in levels) or
                        if len(levels) > 1 and (number >= levels[0] and number <= levels[-1] or \
                            (levels[0] > levels[-1] and number <= levels[0] and number >= levels[-1])) or \
                            str(number).startswith(str(parts[1])): # no range specifed clause
                            temp.append(found[i])
                    found = temp[:]
                    if levels[0] > levels[-1]:  # sorts backwards queries in descending order
                        found = sorted(found, key=lambda x: x.get_text(), reverse=True)
                else: # if full course name given

                    found = [anchor for anchor in self.pages[parts[0]].select('a[name^=""]') \
                        if anchor.has_attr('name') and len(anchor['name']) > 0 and \
                            anchor['name'].endswith(parts[1])]
                    
                    if len(found) > 0:
                        found = found[0]
                        instructor = ''
                        if found.p.i is not None:
                            instructor = found.p.i.get_text().strip()
                            found.p.i.decompose() # remove the instructor
                        if found.p.a is not None:
                            found.p.a.decompose() # remove the MyPlan link
                        title = found.p.b.get_text()
                        description = found.p.get_text().replace(title, '')
                        course_list.append({'title': title,
                                            'description': description if len(description) > 0 else None,
                                            'instructor': instructor if len(instructor) > 0 else None})
                    else:
                        message = 'course not found'
                    already_set = True
            else:
                header = self.pages[parts[0]].select('h1')[0].get_text()
            if not(already_set):
                if len(found) > 0:
                    course_list = [f.get_text() for f in found]
                else:
                    message = 'course(s) not found'
        else: # invalid department
            message = 'enter a valid course id, ex. MATH 126'
        return {'message': message,
                'results': {'course_list': course_list,
                            'header': header}}

class Elements(object):
    """Class Elements can be used to find and store elements
       from a given web page or markup"""

    def __init__(self, page=None, element=None, method='find_all', use_local=False):
        """Initalizes this Elements object"""
        if page is None and element is None:
            page = TEST_LINK
            element = 'link'
        self.request = None
        if type(page) == bytes:
            self.src = page
        elif _os.path.exists(page) and not(use_local):
            with open(page, 'rb') as fp:
                self.src = fp.read()
        else:
            betterheaders = WEB_HDRS.copy()
            self.request = _requests.get(page, headers=betterheaders)
            if not(self.request.content.startswith(b'<')):
                betterheaders.pop('Accept-Encoding')
                self.request = _requests.get(page, headers=betterheaders)
            self.src = self.request.content
        self.page = page
        self.soup = _BS(self.src, 'html.parser')
        self.element = element
        self.method = method

    def find(self):
        self.__found = eval('self.soup.{}("{}")'.format(self.method, self.element))
        if len(self.__found) == 0:
            print('No elements found')

    def get_found(self):
        return self.__found

    def set_element(self, element):
        self.element = element

    def show(self, attribute='text', file=_sys.stdout):
        print('Elements:', file=file)
        for i in self.get_found():
            try:
                if attribute == 'text':
                    print(i.get_text(), file=file)
                elif attribute == 'string':
                    print(i.string, file=file)
                else:
                    print(i[attribute], file=file)
            except KeyError as e:
                print('Key', e, 'for', i, 'not found')

    def store_elements(self, filename, inner='text'):
        with open(filename, 'w') as fp:
            self.show(inner=inner, file=fp)
        if _os.path.exists(filename):
            print('Elements stored successfully')
        else:
            print('Something went wrong')

    def store_request(self, filename):
        assert type(self.src) == bytes
        with open(filename, 'wb') as fp:
            fp.write(self.src)

def find_anchors(location, query={}, internal=True, php=False):
    """Returns anchor references from a location (file name or uri)
           query    = query params sent in the request
           internal = uses internal site referenes if True
           php      = determines whether references with query params are included"""

    if 'http' in location:
        fread = _requests.get(location, params=query).content#headers=WEB_HDRS, params=query).content
    else:
        with open(location,'r') as bc:
            fread = bc.read()
    soup = _BS(fread, 'html.parser')
    raw_links = soup.find_all('a')
    links = []
    if php or internal:
        for x in raw_links:
            try:
                if (location[:16] in x['href'] or x['href'].startswith('/')) and not('#' in x['href']):
                    links.append(x['href'])
            except:
                links.append(x)
        if internal:
            links = [link for link in links if not('?' in link)]
    else:
        for x in raw_links:
            try:
                links.append(x['href'])
            except:
                links.append(x)
    return list(set(links)) # remove duplicates

def get_uri(path):
    """Returns the web file URI for the given file path"""
    return 'file:///' + path.replace('\\', '/')

def get_title(uri_or_soup):
    """Returns the title from the markup"""
    if type(uri_or_soup) == str:
        soup = _BS(_requests.get(uri_or_soup).content, 'html.parser')
    else:
        soup = uri_or_soup
    return soup.html.title.text

def get_vid(vid, vid_type='mp4'):
    """Downloads the given YouTube (tm) video id using yt-down.tk, no longer stable"""
    WebDocument('http://www.yt-down.tk/?mode={}&id={}'.format(vid_type, vid)) \
        .download(title='.'.join([vid, vid_type]))

class HtmlBuilder(object):

    INDENT = '    ' # 4 spaces
    
    def __init__(self):
        self.indent = 0
        self.builder = ''
        self.add_tag('html')
        self.add_tag('head')

    def add_nl(self):
        self.builder += '\n'

    def add_tag(self, tag, text='', self_closing=False, attrs={}):
        print('processing', tag, 'indent', self.indent)
        self.builder += HtmlBuilder.INDENT * self.indent + '<' + tag

        for attr in attrs:
            self.builder += ' ' + attr + '="' + attrs[attr] + '"'

        if self_closing:
            self.builder += ' /'
        else:
            self.indent += 1
  
        self.builder += '>'
        if len(text) > 0:
            self.builder += text
            self.close_tag(tag, has_text=True)
        self.add_nl()

    def close_tag(self, tag, has_text=False):
        self.indent -= 1
        if not(has_text):
            self.builder += HtmlBuilder.INDENT * self.indent

        self.builder += '</' + tag + '>'
        if not(has_text):
            self.add_nl()
           
        print('build', tag, 'now', self.indent)
        
    def to_string(self):
        return self.builder

class UrlBuilder(object):

    def __init__(self, base):
        self.url = base

    def with_query_params(self, params):
        if '?' in self.url: # already exists
            self.url += '&'
        else: # does not exist
            self.url += '?'
        self.url += urllib.parse.urlencode(params)
        return self
        
    def to_string(self):
        return self.url

class WeatherUrlBuilder(UrlBuilder):

    def __init__(self):
        super(WeatherUrlBuilder, self).__init__('https://api.weather.com/v2/indices/pollen/daypart/7day')
        self.with_query_params({'apiKey': '6532d6454b8aa370768e63d6ba5a832e',
            'format': 'json',
            'language': 'en-US'})

    def with_geocode(self, lat, lon):
        self.url += '&' + urllib.parse.urlencode({'geocode': str(lat) + ',' + str(lon)})
        return self

class WebDocument(object):

    """Can be used to work with files and URIs hosted on the web"""

    def __init__(self, uri):
        self.set_uri(uri)

    def __repr__(self):
        return 'WebDocument(uri=%s)' % self.uri

    def download(self, title='', full_title=False, destination='.',
                 log_name='dl_log.txt', return_speed=False):
        """Downloads data from the given url and logs the relevant information
           in this package's directory"""

        # http://stackoverflow.com/a/16696317/5645103

        from clay.shell import set_title

        url = self.uri
        flag = False
        if log_name:
            log_path = _os.path.join(r'C:\Python37\Lib\site-packages\clay', log_name)
        current = _os.getcwd()
        _os.chdir(destination) # better file handling
        print('curdir', _os.getcwd())

        if len(title) > 0: # if title already set
            query = None
        else:
            title, query = self.get_basename(full=full_title)
        fp = open(title, 'wb')
        print('Retrieving "{}"...\ntitle {}\nquery {}...'.format(url, title, query))
        try:
            print('size', end=' ')
            if not('.' in title) or 'htm' in title or 'php' in title: # small file types (pages)
                response = _requests.get(url, params=query, headers=WEB_HDRS)
                if response.status_code != 200:
                    raise _requests.exceptions.InvalidURL(f'{response.reason}, status code {response.status_code}')
                before = _time.time() # start timer
                size = len(response.text)
                print(size, 'bytes')
                fp.write(response.text.encode('utf-8'))
                fp.close()
            else: # larger file types
                response = _requests.get(url, params=query, headers=WEB_HDRS, stream=True) # previously urllib.request.urlopen(urllib.request.Request(url, headers=WEB_HDRS))
                if response.status_code != 200:
                    raise _requests.exceptions.InvalidURL(f'{response.reason}, status code {response.status_code}')
                before = _time.time() # start timer
                size = int(response.headers.get('content-length'))
                chunk = size // 100
                if chunk > CHUNK_CAP: # place chunk cap on files >1MB
                    chunk = CHUNK_CAP # 1MB
                print(size, 'bytes')
                print("Writing to file in chunks of {} bytes...".format(chunk))
                actual = 0
                try:
                    for chunk in response.iter_content(chunk_size=chunk):
                        if len(chunk) == 0: break
                        fp.write(chunk)
                        actual += len(chunk)
                        percent = int(actual / size * 100)
                        if _is_idle() or _is_unix():
                            if percent % 5 == 0: # if multiple of 5 reached...
                                print('{}%'.format(percent), end=' ', flush=True)
                        else:
                            set_title('{}% {}/{}'.format(percent, actual, size))
                except Exception as e:
                    print(e)
                finally:
                    fp.close()
        except Exception as e:
            print('\n' + str(e))
            log_string = url+' failed\n'
            flag = True
        else:
            taken = _time.time() - before
            print(f'\nComplete. Took {round(taken, 5)}s')
            if not(_is_idle() or _is_unix()):
                set_title(f'Completed {title}')
            log_string = f'[{url}] {title} of {size} bytes @ {_dt.datetime.today()}\n'
        finally:
            if not(fp.closed):
                fp.close()
        if log_name:
            with open(log_path, 'a+') as lp:
                lp.write(log_string)
        else:
            print(log_string.strip())
        _os.chdir(current) # better file handling
        if return_speed and not(flag):
            return round(size / taken, 5)

    def get_basename(self, full=False):
        """Returns the basename and query of this document's `uri`"""
        url_split = urllib.parse.urlsplit(self.uri)
        query = url_split.query if len(url_split.query) > 0 else None
        title = _os.path.basename(url_split.path)
        add_ext = not(any(ext in title for ext in ('htm', 'aspx', 'php'))) and len(title) < 2
        
        if len(title) < 2: # if title is '' or '/'
            title = 'index'
            add_ext = True
        if full:
            title = '.'.join((url_split.netloc, title))
        if add_ext:
            title += '.html'
        title = urllib.parse.unquote_plus(title)
        return title, query

    def get_html(self, query=None, headers=True):
        """Returns the binary response from this document's `uri`"""
        if query is not None:
            assert type(query) == dict
        if headers:
            fread = _requests.get(self.uri, params=query, headers=WEB_HDRS)
        else:
            fread = _requests.get(self.uri, params=query)
        return fread.text.encode('utf-8')

    def get_mp3(self, title=''):
        """Downloads the this document's `uri` from mp3juices.cc"""
        if len(title) == 0:
            title = _os.path.basename(self.uri) + '.mp3'
        self.download(link, title=title)

    def get_response(self):
        """Returns the response from this document's `uri`"""
        request = urllib.request.Request(self.url, headers=WEB_HDRS)
        response = urllib.request.urlopen(request)
        return response.read()

    def get_uri(self):
        return self.uri
    
    def launch(self, browser='firefox'):
        """Opens this document's `uri` in your favorite browser"""
        if _is_unix():
            _call(['google-chrome', self.uri], shell=True)
        else:
            _call(['start', browser, self.uri.replace('&', '^&')], shell=True)

    def set_uri(self, uri):
        self.uri = uri

class WundergroundUrlBuilder(UrlBuilder):

    def __init__(self):
        super(WundergroundUrlBuilder, self).__init__('https://www.wunderground.com/health/us/')
        
    def with_location(self, state, city, station):
        self.url += '/'.join((state, city, station))
        self.with_query_params({'cm_ven': 'localwx_modpollen'})
        return self
        
    def to_string(self):
        return self.url

class PollenUrlBuilderFactory(object):

    def __init__(self):
        self.weather = WeatherUrlBuilder()
        self.wunderground = WundergroundUrlBuilder()
        
class Pollen(object):

    """Class Pollen can be used to retrieve and store information about
       the pollen forecast from The Weather Channel (tm) and Wunderground (tm)"""

    URL_FACTORY = PollenUrlBuilderFactory()

    MAX_REQUESTS = 4
    SOURCE_SPAN = {'weather text': 7, 'weather values': 7, 'wu poll': 4}
    SOURCE_URLS = {98105: {'weather values': URL_FACTORY.weather.with_geocode(47.654003, -122.309166).to_string(),
                           'wu poll': URL_FACTORY.wunderground.with_location('wa', 'seattle', 'WASEATT446').to_string()},
                   98684: {'weather values': URL_FACTORY.weather.with_geocode(45.639816, -122.497902).to_string(),
                           'wu poll': URL_FACTORY.wunderground.with_location('wa', 'camas', 'KWACAMAS42').to_string()}}
    for url in SOURCE_URLS:
        SOURCE_URLS[url]['weather text'] = 'https://weather.com/forecast/allergy/l/'
    TYPES = ('grass', 'ragweed', 'tree')
    WEATHER_QUERY_PARAMS = ':4:US'

    def __init__(self, source, zipcode=98105, print_sources=True):
        """Constructs a new Pollen object using the given source and zipcode"""
        self.zipcode = zipcode
        self.print_sources = print_sources
        self.source = source
        self.set_zipcode(zipcode)
        self.__has_built = False
        self.build()

    def __repr__(self):
        """Returns the string representation of this Pollen instance"""
        return f'Pollen(source={{{self.source}}}, zipcode={self.zipcode}, print_sources={self.print_sources})'

    def __check_built(self):
        """Throws a RuntimeError if this Pollen instance has not been built"""
        if not(self.__has_built):
            raise RuntimeError('Pollen must be build after zipcode or source has been changed')

    def __verify_source(self, source):
        if not(source in Pollen.SOURCE_SPAN.keys()):
            raise ValueError(f'source must be one from [{", ".join(Pollen.SOURCE_SPAN.keys())}]')

    def __verify_zipcode(self, zipcode):
        if (self.source != 'weather text' and not(zipcode in Pollen.SOURCE_URLS.keys())) or \
            not(zipcode in Pollen.SOURCE_URLS.keys()) or zipcode < 0 or zipcode > 99501:
            raise ZipCodeNotFoundException(zipcode)

    def __get_markup(self, uri):
        """Retrieves the markup with up to 4 max tries"""
        if self.source == 'weather text':
            params = WEB_HDRS
        else:
            params = {}
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

    def build(self, add_weather_query=True):
        """Builds and populates the pollen record database"""
        uri = self.uri
        if self.source == 'weather text' and add_weather_query:
            uri += self.WEATHER_QUERY_PARAMS

        markup = self.__get_markup(uri)

        page = _BS(markup, 'html.parser')

        if self.source == 'weather text':
            found = page.select('button > div')
            db = {}
            if len(found) > 0:
                for elm in found:
                    divs = elm.select('div')
                    db[divs[0].get_text()] = divs[-1].get_text()
        elif self.source == 'weather values':
            js = _json.loads(markup)
            base = js['pollenForecast12hour']
            stored = list(base[layer + 'PollenIndex'] for layer in Pollen.TYPES)
            lzt = list(zip(*stored))
            db = {i / 2: lzt[i] for i in range(len(lzt))}
        else: # wu poll
            j = page.select('.count') # or class .status
            db = {i: j[i].get_text() for i in range(Pollen.SOURCE_SPAN[self.source])}
        if len(db) == 0:
            if self.source == 'weather text':
                self.build(add_weather_query=not(add_weather_query)) # retry using the alternate query
            else:
                db = {i: 'null' for i in range(Pollen.SOURCE_SPAN[self.source])['null']}
        self.src = page
        self.db = db
        self.__has_built = True

    def get_day(self, day):
        """Returns the value in the db for the given day"""
        self.__check_built()
        data = None
        if self.source == 'weather text':
            date = str((_dt.date.today() + _dt.timedelta(days=day)).day)
            for dong in self.db:
                if dong.endswith(' ' + date):
                    data = self.db[dong]
                    break # not the best style but saves runtime
        else:
            # updates afternoon forecasts for today only (floor of cos of day)
            day += 0.5 * _math.floor(_math.cos(day)) * _math.floor(_dt.datetime.now().hour / 12)
            if type(self.db[day]) == str:
                data = self.db[int(day)].title()
            else:
                data = self.db[day]
        if data is not None and self.print_sources:
            print('[{}] day={}'.format(self.source, day))
        return data

    def get_today(self):
        """Returns the type of pollen for today"""
        self.__check_built()
        if self.source == 'weather text':
            if 'Tonight' in self.db:
                return self.db['Tonight']
            elif 'Today' in self.db:
                return self.db['Today']
        return self.get_day(0)

    def get_tomorrow(self):
        """Returns the type of pollen forecasted for tomorrow"""
        return self.get_day(1) # checks for valid db in get_day

    def print_db(self):
        """Prints all of the db information in a table format"""
        self.__check_built()
        print('Pollen data for', self.zipcode)
        for i, j in self.db.items():
            print('{:>{}}: {}'.format(i, len('Tonight'), j))

    def set_source(self, source):
        """Sets the source for this Pollen object. Requires `build` to be called to update data"""
        self.__verify_source(source)
        self.uri = Pollen.SOURCE_URLS[self.zipcode][source]
        if source == 'weather text':
            self.uri += str(self.zipcode)
        self.source = source
        self.__has_built = False

    def set_zipcode(self, zipcode):
        """Sets the zipcode for this Pollen object. Requires `build` to be called to update data"""
        self.__verify_zipcode(zipcode)
        self.zipcode = zipcode
        self.set_source(self.source) # ensures data is updated if the method is 'weather text'

class ZipCodeNotFoundException(Exception):
    def __init__(self, zipcode, *args, **kwargs):
        super(ZipCodeNotFoundException, self).__init__(repr(self), *args, **kwargs)
        self.zipcode = zipcode

    def __repr__(self):
        zipcodes = ', '.join(map(str, Pollen.SOURCE_URLS.keys()))
        plural = zipcodes.count(',') > 0
        string = 'The only zipcode'
        if plural:
            string += 's'
        string += ' currently supported for Pollen '
        if plural:
            string += 'are'
        else:
            string += 'is'
        string += ' ' + zipcodes
        return string

if __name__ == '__main__':

    from clay.tests import it

    print(WebDocument(LINKS['2MB']).download(destination=_get_docs_folder(), \
                                             return_speed=True), 'bytes per second')
    print()
    it('returns basename and query', \
        WebDocument('https://www.minecraft.net/change-language?next=/en/') \
            .get_basename(full=False), \
        ('change-language', 'next=/en/'))
    it('returns full name and no query', \
        WebDocument(LINKS['1MB']).get_basename(full=True), \
        ('download.thinkbroadband.com.1MB.zip', None))
    it('returns Official Minecraft site html title', get_title(TEST_LINK), 'Official site | Minecraft')
    it('returns index.html and no query', WebDocument(TEST_LINK).get_basename(), ('index.html', None))
    print()
    we1 = Elements('https://thebestschools.org/rankings/20-best-music-conservatories-u-s/', 'h3')
    we1.find()
    it('best music school list contains 21 elements', we1.get_found(), 21, len)
    we1.show()
    we2 = Elements()
    we2.find()
    we2.show(attribute='href')
    print()
    print('ANCHORS')
    print(find_anchors(TEST_LINK, internal=False))
    print()

    import traceback

    p = Pollen('weather text')
    p.print_db()
    p.set_source('weather values')
    p.set_zipcode(98105)
    p.build()
    p.print_db()

    print('The next two tests will throw exceptions.')
    try:
        p.set_source('wrong source')
    except Exception:
        exc_type, exc_value, exc_tb = _sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
    print()
    try:
        p.set_zipcode(97132)
    except Exception:
        exc_type, exc_value, exc_tb = _sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)

