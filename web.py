
"""
web module

TODO (Pollen): allow multiple zipcodes for the given sources
                 - retrieve each api link
                 - use zip codes to lookup the dictionary of url sources
TODO (web-header): fix the web header to fix google.com rendering JS problem using
                       accept-char types

"""

import datetime as _dt
import json as _json
import math as _math
import os as _os
import re as _re
import requests as _requests
from subprocess import call as _call
import sys as _sys
import urllib.request, urllib.error, urllib.parse

import requests as _requests
from bs4 import BeautifulSoup as _BS

from clay.shell import \
    get_docs_folder as _get_docs_folder, \
    isIdle as _isIdle, \
    isUnix as _isUnix

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

class CachedFile(object):
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

        from clay.web import get_basename as _get_basename

        if title is None:
            title = _get_basename(uri)[0]
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
        DEPTS = [item['href'] for item in pages['list'].select('a')]
        DEPTS = [item[:item.index('.')] for item in DEPTS if not('/' in item) and item.endswith('.html')]
        DEPTS.sort()

        self.DEPTS = DEPTS
        self.MAX_LENGTH = max(map(len, DEPTS))
        self.pages = pages

    def get_departments(self):
        return self.DEPTS

    def print_departments(self):
        for i, j in enumerate(self.DEPTS):
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
        if len(parts) > 0 and parts[0] in self.DEPTS: # if a valid department
            if not(parts[0] in self.pages): # insert into cache
                link = CourseCatalogUW.CATALOG_URI + parts[0] + '.html'
                self.pages[parts[0]] = _BS(_requests.get(link).content, 'html.parser')
            already_set = False
            found = self.pages[parts[0]].select('p b') # get all class elements
            if len(parts) == 2:
                if len(parts[1]) != 3 or '-' in parts[1]: # if not specific class
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
                    name_prefix = parts[0]
                    # configure custom prefixes
                    if name_prefix == 'musensem':
                        name_prefix = 'musen'

                    found = self.pages[parts[0]].find('a', attrs={'name': name_prefix + parts[1]})
                    if found is not None:
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

class CRUDRepository(object):

    def __init__(self, file, pk):
        """Initializes this CRUD repository under the given file
           using the given primary key"""
        self.file = file
        self.pk = pk
        self.db = None
        self.default_model = None
        self.__has_read = False

    def __ensure_connected(self):
        if not(self.__has_read):
            raise RuntimeError('database has not been read')

    def __ensure_exists(self, pk):
        if not(self.db is None or pk in self.db):
            self.db[pk] = self.get_default_model().to_dict()

    def create_if_not_exists(self, pk):
        self.__ensure_connected()
        self.__ensure_exists(pk)

    def get_default_model(self):
        return self.default_model

    def read(self):
        if not(_os.path.exists(self.file)):
            self.db = {} # dict
            self.write()
        with open(self.file) as fp:
            self.db = _json.load(fp)
        if self.db is not None:
            self.__has_read = True

    def delete(self, pk):
        self.__ensure_connected()
        if pk in self.db:
            self.db.pop(pk)
            self.write()
            print('user entry for pk', pk, 'removed')
        else:
            print('user pk not found')

    def set_default_model(self, model):
        self.default_model = model

    def update(self, pk, model):
        self.__ensure_connected()
        self.__ensure_exists(pk)

        for attr in model.get_attributes():
            self.db[pk][attr] = getattr(model, attr)

        print('pk', pk, 'updated')

        self.write()

    def update_prop(self, pk, prop, value):
        self.__ensure_connected()
        self.__ensure_exists(pk)
        self.db[pk][prop] = value

    def write(self):
        self.__ensure_connected()
        with open(self.file, 'w') as fp:
            _json.dump(self.db, fp)
        print('database written')

def download(url, title='', full_title=False,
             destination='.', log_name='dl_log.txt', speed=False):
    """Downloads data from the given url and logs the relevant information
       in this package's directory"""

    # http://stackoverflow.com/a/16696317/5645103

    assert type(url) == str, 'Lists not supported'

    import datetime as dt
    from time import time

    from clay.shell import set_title
    from clay.web import get_basename

    flag = False
    if log_name:
        log_path = _os.path.join(r'C:\Python37\Lib\site-packages\clay', log_name)
    current = _os.getcwd()
    _os.chdir(destination) # better file handling
    print('curdir', _os.getcwd())

    if title: # if title already set
        query = None
    else:
        title, query = get_basename(url, full=full_title)
    fp = open(title, 'wb')
    print('Retrieving "{}"...\ntitle {}\nquery {}...'.format(url, title, query))
    try:
        print('size', end=' ')
        if not('.' in title) or 'htm' in title or 'php' in title:
            response = _requests.get(url, params=query, headers=WEB_HDRS)
            if response.status_code != 200:
                raise _requests.exceptions.InvalidURL(f'{response.reason}, status code {response.status_code}')
            before = time() # start timer
            size = len(response.text)
            print(size, 'bytes')
            fp.write(response.text.encode('utf-8'))
            fp.close()
        else:
            response = _requests.get(url, params=query, headers=WEB_HDRS, stream=True) # previously urllib.request.urlopen(urllib.request.Request(url, headers=WEB_HDRS))
            if response.status_code != 200:
                raise _requests.exceptions.InvalidURL(f'{response.reason}, status code {response.status_code}')
            before = time() # start timer
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
                    if _isIdle() or _isUnix():
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
        taken = time() - before
        print('\ntook {}s'.format(taken))
        if not(_isIdle() or _isUnix()):
            set_title('Completed {}'.format(title))
        log_string = '{} {} of {} bytes @ {}\n'.format('[' + url + ']', title, size, dt.datetime.today())
        print('Complete\n')
    finally:
        if not(fp.closed):
            fp.close()
    if log_name:
        with open(log_path, 'a+') as lp:
            lp.write(log_string)
    else:
        print(log_string.strip())
    _os.chdir(current) # better file handling
    if speed and not(flag):
        return size / taken

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
        if not(self.__found):
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
           php      = determines whether references with query params are included
    """

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
    return links

def get_basename(uri, full=False, show=False):
    """Returns the basename and query of the specified uri"""
    if '?' in uri:
        url, query = uri.split('?')
    else:
        url, query = uri, None
    title = _os.path.basename(url)
    add_ext = True
    if any(ext in title for ext in ('htm', 'aspx', 'php')) or len(_os.path.basename(title)) > 0:
        add_ext = False

    if full:
        title = url.replace('://', '_').replace('/', '_')
    if not(title):
        title = 'index'
    if add_ext:
        title += '.html'
    title = urllib.parse.unquote_plus(title)
    if show:
        print('Title', title)
    return title, query

def get_uri(path):
    """Returns the web file uri for the given path"""
    return 'file:///' + path.replace('\\', '/')

def get_file(uri):
    """Returns the response from the given `uri`"""
    response = urllib.request.urlopen(urllib.request.Request(url, headers=WEB_HDRS))
    return response.read()

def get_html(uri, query=None, headers=True):
    """Returns the binary response from the given `uri`"""
    if query is not None:
        assert type(query) == dict
    if headers:
        fread = _requests.get(uri, params=query, headers=WEB_HDRS)
    else:
        fread = _requests.get(uri, params=query)
    text = fread.text.encode('utf-8')
    return text

def get_mp3(link, title=''):
    """Downloads the given link from mp3juices.cc"""
    from clay.web import download
    if not(title):
        title = link[link.index('=') + 1:] + '.mp3'
    download(link, title=title)

def get_title(uri_or_soup):
    """Returns the title from the markup"""
    if type(uri_or_soup) == str:
        uri = uri_or_soup
        soup = _BS(_requests.get(uri).content, 'html.parser')
    else:
        soup = uri_or_soup
    return soup.html.title.text

def get_vid(vid, vid_type='mp4'):
    """Downloads the given YouTube (tm) video id using yt-down.tk, no longer stable"""
    from clay.web import download
    download('http://www.yt-down.tk/?mode={}&id={}'.format(vid_type, vid), title='.'.join([vid, vid_type]))

def launch(uri, browser='firefox'):
    """Opens the given uri (string or list) in your favorite browser"""
    if type(uri) == str:
        uri = [uri]
    if type(uri) == list:
        for link in uri:
            if _isUnix():
                _call(['google-chrome', link], shell=True)
            else:
                _call(['start', browser, link.replace('&', '^&')], shell=True)

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

class UserRepository(CRUDRepository):
    def __init__(self, primary_key, file='users'):
        super(UserRepository, self).__init__(file, primary_key)

class ZipCodeNotFoundException(Exception):
    def __init__(self, zipcode, *args, **kwargs):
        super(ZipCodeNotFoundException, self).__init__(repr(self), *args, **kwargs)
        self.zipcode = zipcode

    def __repr__(self):
        zipcodes = ", ".join(map(str, Pollen.SOURCE_URLS.keys()))
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
    print(download(LINKS['2MB'], destination=_get_docs_folder(), speed=True), 'bytes per second')
    print(get_basename('https://www.minecraft.net/change-language?next=/en/', full=False))
    print(get_basename(LINKS['1MB'], full=True))
    print(get_title(TEST_LINK))
    print(get_basename(TEST_LINK))
    print('title from markup:', get_title(TEST_LINK))
    we1 = Elements('https://thebestschools.org/rankings/20-best-music-conservatories-u-s/', 'h3')
    we1.find()
    we1.show()
    we2 = Elements()
    we2.find()
    we2.show(attribute='href')
    print('ANCHORS')
    print(find_anchors(TEST_LINK, internal=False))

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

