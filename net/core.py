
"""
web module

TODO (web-header): fix the web header to fix google.com rendering JS problem using
                       alternate accept-char types

"""

import collections as _collections
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

from clay.env import is_idle as _is_idle, is_posix as _is_posix

CHUNK_CAP = int(1e6) # 1MB
DEFAULT_BROWSER = 'firefox'

# download links for testing
LINKS = {}
LINK_SIZES = list(str(n) + 'MB' for n in [1, 2, 5, 10, 20, 50, 100, 200, 512])
for n in LINK_SIZES:
    LINKS[n] = 'http://download.thinkbroadband.com/' + str(n) + '.zip'
del n
LINKS['1GB'] = 'http://download.thinkbroadband.com/1GB.zip'

EXAMPLE_URL = 'http://example.com'
TEST_LINK = 'https://minecraft.net/en-us/'
VALID_SCHEMES = ('file', 'ftp', 'http', 'https')
WEB_HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
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

        if 'http' not in uri:
            raise ValueError('uri must use the HTTP protocol')

        if title is None:
            title = WebDocument(uri).get_basename()[0]
        self.title = title

        self.uri = uri
        self.__init__(reload_on_set=self.reload_on_set)

        if self.reload_on_set and not _os.path.exists(self.title):
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
        depts = [item[:item.index('.')] for item in depts if '/' not in item and item.endswith('.html')]
        depts.sort()

        self.depts = depts
        self.MAX_LENGTH = max(map(len, depts))
        self.pages = pages

    def __print_columns(self, columns, width):
        for i, j in enumerate(columns):
            print(j, end=int(_math.ceil(_math.ceil(self.MAX_LENGTH / 8) - len(j) / 8)) * '\t')
            if i % width == width - 1:
                print()
        print() # flush output

    def get_departments(self):
        return self.depts

    def print_departments(self, legacy=False):
        if legacy:
            self.__print_columns(self.depts, 6)
        else:
            depts = self.depts[:]
            while len(depts) % 6 != 0:
                depts.append('')
            length = int(len(depts) / 6)
            one = depts[:length]
            two = depts[length: length * 2]
            three = depts[length * 2: length * 3]
            four = depts[length * 3: length * 4]
            five = depts[length * 4: length * 5]
            six = depts[length * 5:]

            zipped = []
            for i,j,k,l,m,n in zip(one, two, three, four, five, six):
                for item in (i,j,k,l,m,n):
                    zipped.append(item)

            self.__print_columns(zipped, 6)

    def query(self, text):
        message = None
        header = None # department header
        course_list = []
        parts = text.strip().lower().split()
        if len(parts) > 0 and parts[0] in self.depts: # if a valid department
            if parts[0] not in self.pages: # insert into cache
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
                                            'description': description if description else None,
                                            'instructor': instructor if instructor else None})
                    else:
                        message = 'course not found within ' + parts[0]
                    already_set = True
            else:
                header = self.pages[parts[0]].select('h1')[0].get_text()
            if not already_set:
                if len(found) > 0:
                    for f in found:
                        course_list.append({'title': f.get_text(),
                                            'description': None,
                                            'instructor': None})
                else:
                    message = 'course(s) not found'
        else: # invalid department
            message = 'enter a valid course id, ex. MATH 126'
        return {'message': message,
                'results': {'course_list': course_list,
                            'header': header}}

def file2uri(path):
    """Returns the web file URI for the given file path"""
    return 'file:///' + path.replace('\\', '/')

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
                if (location[:16] in x['href'] or x['href'].startswith('/')) and '#' not in x['href']:
                    links.append(x['href'])
            except:
                links.append(x)
        if internal:
            links = [link for link in links if '?' not in link]
    else:
        for x in raw_links:
            try:
                links.append(x['href'])
            except:
                links.append(x)
    return list(set(links)) # remove duplicates

def get_title(soup):
    """Returns the title from the given soup markup"""
    title = '[no title]'
    if soup.html is not None and soup.html.title is not None:
        title = soup.html.title.text
    return title

def get_vid(vid, vid_type='mp4'):
    """Downloads the given YouTube (tm) video id using yt-down.tk, no longer stable"""
    WebDocument('http://www.yt-down.tk/?mode={}&id={}'.format(vid_type, vid)) \
        .download(title='.'.join([vid, vid_type]))

class HtmlBuilder(object):

    INDENT = '    ' # 4 spaces

    def __init__(self):
        self.indent = 0
        self.__html = ''
        self.add_tag('html')
        self.add_tag('head')

    def add_raw(self, raw_html):
        self.__html += raw_html

    def add_nl(self):
        self.__html += '\n'

    def add_tag(self, tag, text='', self_closing=False, attrs={}):
        print('processing', tag, 'indent', self.indent)
        self.__html += HtmlBuilder.INDENT * self.indent + '<' + tag

        for attr in attrs:
            self.__html += ' ' + attr + '="' + attrs[attr] + '"'

        if self_closing:
            self.__html += ' /'
        else:
            self.indent += 1

        self.__html += '>'
        if text:
            self.__html += text
            self.close_tag(tag, has_text=True)
        self.add_nl()

    def close_tag(self, tag, has_text=False):
        self.indent -= 1
        if not has_text:
            self.__html += HtmlBuilder.INDENT * self.indent

        self.__html += '</' + tag + '>'
        if not has_text:
            self.add_nl()

        print('build', tag, 'now', self.indent)

    def build(self):
        return self.__html

class TagFinder(object):
    """Class TagFinder can be used to find and store elements
       from a given web page or markup"""

    def __init__(self, page):
        """Initalizes this TagFinder object"""
        self.request = None
        if isinstance(page, bytes):
            self.src = page
        elif _os.path.exists(page):
            with open(page, 'rb') as fp:
                self.src = fp.read()
        else:
            betterheaders = WEB_HDRS.copy()
            self.request = _requests.get(page, headers=betterheaders)
            if not self.request.content.startswith(b'<'):
                betterheaders.pop('Accept-Encoding')
                self.request = _requests.get(page, headers=betterheaders)
            self.src = self.request.content
        self.page = page
        self.soup = _BS(self.src, 'html.parser')

    def find(self, tag, method='find_all'):
        self.__found = eval('self.soup.{}("{}")'.format(method, tag))
        if len(self.__found) == 0:
            print('No tags matching "{}" found'.format(tag))
        return self.__found

    def show(self, attribute='text', file=_sys.stdout):
        print('Tags:', file=file)
        for i in self.__found:
            try:
                if attribute == 'text':
                    print(i.get_text(), file=file)
                elif attribute == 'string':
                    print(i.string, file=file)
                else:
                    print(i[attribute], file=file)
            except KeyError as e:
                print('Key', e, 'for', i, 'not found')
        if len(self.__found) == 0:
            print('None', file=file)

    def store_request(self, filename):
        assert isinstance(self.src, bytes)
        with open(filename, 'wb') as fp:
            fp.write(self.src)

    def store_tags(self, filename, inner='text'):
        try:
            with open(filename, 'w') as fp:
                self.show(inner=inner, file=fp)
            if _os.path.exists(filename):
                print('TagFinder store successful')
        except Exception as e:
            print('TagFinder store failed: {}'.format(e))

class UrlBuilder(object):
    """Can be used to build formatted URLs"""

    def __init__(self, base_url):
        """Initializes this UrlBuilder"""
        self.base_url = base_url
        self.reset()

    def __repr__(self):
        """Returns the string representation of this UrlBuilder"""
        return 'UrlBuilder(base_url={},\n'.format(self.base_url) \
            + ' ' * 4 + 'url={})'.format(self.__url)

    def append_segments(self, *paths):
        """Appends the given path segments to the URL"""
        # if joining the URL with the first path segment yeilds two '/'s
        if self.__url.endswith('/') and paths[0].startswith('/'):
            paths = list(paths) # allow for mutability
            paths[0] = paths[0][1:] # remove the / not part of the base URL
        # if joining the URL or the first path segment yeilds no '/'s
        elif not self.__url.endswith('/') and not paths[0].startswith('/'):
            self.__url += '/' # add one /
        self.__url += '/'.join(paths)
        return self

    def with_query_params(self, params):
        """Adds the given query params key-value pairs to the URL"""
        return self.with_query_string(urllib.parse.urlencode(params))

    def with_query_string(self, string):
        """Adds the given query string to the URL"""
        # if URL is the same as the base and only scheme separators exist
        if self.__url == self.base_url and self.__url.count('/') == 2:
            # suffix with / before adding query params
            self.__url += '/'
        # add separator if query params already exist,
        # otherwise add query params start symbol
        self.__url += '&' if '?' in self.__url else '?'
        self.__url += string
        return self

    def reset(self):
        """Resets the URL to the base URL"""
        self.__url = self.base_url

    def build(self):
        """Builds the URL string for this UrlBuilder"""
        return self.__url

class WeatherPollenApiUrlBuilder(UrlBuilder):

    def __init__(self):
        super(WeatherPollenApiUrlBuilder, self).__init__('https://api.weather.com/v2/indices/pollen/daypart/7day')
        self.base_url = self.with_query_params({'apiKey': '6532d6454b8aa370768e63d6ba5a832e',
            'format': 'json',
            'language': 'en-US'}).build()

    def with_geocode(self, lat, lon):
        """Adds the geocode latitude and longitude param to the URL"""
        return self.reset() or self.with_query_params({'geocode': str(lat) + ',' + str(lon)})

class WebDocument(object):

    """Can be used to work with files and URIs hosted on the web"""

    def __init__(self, uri=None):
        self.set_uri(uri)
        self.set_query(None)

    def __repr__(self):
        return 'WebDocument(uri=%s)' % self.__raw_uri

    def download(self, title='', full_title=False, destination='.',
                 log_name='webdoc-dl.log', return_speed=False,
                 headers=WEB_HDRS):
        """Downloads data from the document uri and logs revelant
           information in this directory"""

        # http://stackoverflow.com/a/16696317/5645103

        from clay.shell.core import set_title

        url = self.__raw_uri
        errors = False
        if log_name:
            if _is_posix():
                log_path = _os.path.join(r'/home/clay/Desktop', log_name)
            else:
                log_path = _os.path.join(r'C:\Python37\Lib\site-packages\clay\logs', log_name)
        current = _os.getcwd()
        _os.chdir(destination) # better file handling
        print('CWD:', _os.getcwd())

        if title: # if title already set
            query = None
        else:
            title, query = self.get_basename(full=full_title)

        # append internal query to query if not empty
        if self.__query is not None:
            if query is None:
                query = self.__query
            else:
                query += '&' + '&'.join((key + '=' + val for key, val in self.__query.items()))

        fp = open(title, 'wb')
        print('Retrieving "{}"...\n    Title: {}\n    Query: {}'.format(url, title, query))
        try:
            print('    Size :', end=' ')
            if '.' not in title or 'htm' in title or 'php' in title: # small file types (pages)
                response = _requests.get(url, params=query, headers=headers)
                if response.status_code != 200:
                    raise _requests.exceptions.InvalidURL('{}, status code {}'.format(response.reason, response.status_code))
                before = _time.time() # start timer
                size = len(response.text)
                print(size, 'bytes')
                fp.write(response.text.encode('utf-8'))
                fp.close()
            else: # larger file types
                response = _requests.get(url, params=query, headers=headers, stream=True)
                if response.status_code != 200:
                    raise _requests.exceptions.InvalidURL('{}, status code {}'.format(response.reason, response.status_code))
                before = _time.time() # start timer
                size = int(response.headers.get('content-length'))
                chunk = size // 100
                if chunk > CHUNK_CAP: # place chunk cap on files >1MB
                    chunk = CHUNK_CAP # 1MB
                print(size, 'bytes')
                print('Writing to file in chunks of {} bytes...'.format(chunk))
                actual = 0
                try:
                    for chunk in response.iter_content(chunk_size=chunk):
                        if len(chunk) == 0: break
                        fp.write(chunk)
                        actual += len(chunk)
                        percent = int(actual / size * 100)
                        if _is_idle():
                            if percent % 5 == 0: # print percent every multiple of 5
                                print('{}%'.format(percent), end=' ', flush=True)
                        else:
                            set_title('{}% ({}/{})'.format(percent, actual, size))
                except Exception as e:
                    print(e)
                finally:
                    fp.close()
        except Exception as e:
            print('\n' + str(e))
            log_string = url + ' failed\n'
            errors = True
        else:
            taken = _time.time() - before
            print('\nComplete. Took {}s'.format(round(taken, 2)))
            if not _is_idle():
                set_title('Downloaded {}'.format(title))
            log_string = '[{}] {} of {} bytes @ {}\n'.format(url, title, size, _dt.datetime.today())
        finally:
            if not fp.closed:
                fp.close()
        if log_name:
            with open(log_path, 'a+') as lp:
                lp.write(log_string)
        else:
            print(log_string.strip())
        _os.chdir(current) # better file handling
        if return_speed and not errors:
            return round(size / taken, 2)

    def get_basename(self, full=False):
        """Returns the basename and query of this document's `uri`"""
        url_query = self.__uri.query if self.__uri.query else None
        title = _os.path.basename(self.__uri.path)
        add_ext = not any(ext in title for ext in ('htm', 'aspx', 'php')) and len(title) < 2

        if len(title) < 2: # if title is '' or '/'
            title = 'index'
            add_ext = True
        if full:
            title = self.__uri.netloc + self.__uri.path.replace('/', '.')
        if add_ext:
            title += '.html'
        title = urllib.parse.unquote_plus(title)
        return title, url_query

    def get_html(self, headers=None):
        """Returns the binary response from this document's `uri`"""
        if headers is not None:
            if not hasattr(headers, 'keys'):
                raise TypeError('headers must derive from type dict')
            # remove user-agent and accept-encoding to ensure html is returned
            # for JS rendered pages
            headers = headers.copy()
            for header in ('User-Agent', 'Accept-Encoding'):
                if header in headers:
                    headers.pop(header)
        fread = _requests.get(self.__raw_uri, params=self.__query, headers=headers)
        return fread.content

    def get_response(self):
        """Returns the response from this document's `uri`"""
        request = urllib.request.Request(self.__raw_uri, headers=WEB_HDRS)
        response = urllib.request.urlopen(request)
        return response.read()

    def get_title(self, headers=None):
        from clay.net.core import get_title
        soup = _BS(self.get_html(headers=headers), 'html.parser')
        return get_title(soup)

    @property
    def query(self):
        return self.__query

    @property
    def uri(self):
        return self.__uri

    @property
    def raw_uri(self):
        return self.__raw_uri

    def launch(self, browser=DEFAULT_BROWSER):
        """Opens this document's `uri` in your favorite browser"""
        if _is_posix():
            _call(['google-chrome', self.uri], shell=True)
        else:
            _call(['start', browser, self.__raw_uri.replace('&', '^&')], shell=True)

    def set_query(self, query):
        """Sets the internal query to the given dictionary"""
        if query is not None and not isinstance(query, dict):
            raise TypeError('query must be of type dict or none')
        self.__query = query

    def set_uri(self, uri):
        """Sets the uri to the given string. Raises ValueError
           if the uri scheme is not supported"""
        if uri is not None:
            if not isinstance(uri, str):
                raise TypeError('uri must be of type str')
            elif not any(uri.startswith(scheme) for scheme in VALID_SCHEMES):
                raise ValueError('uri must have a file, ftp, or http[s] scheme')
        self.__raw_uri = uri
        self.__uri = urllib.parse.urlsplit(uri)

    def size(self):
        """Returns the size of this document in bytes"""
        response = _requests.head(self.__raw_uri, headers=WEB_HDRS)
        if 'Content-Length' in response.headers:
            size = int(response.headers['Content-Length'])
        else:
            size = len(_requests.get(self.__raw_uri, headers=WEB_HDRS).content)
        return size

class WundergroundUrlBuilder(UrlBuilder):

    def __init__(self):
        super(WundergroundUrlBuilder, self).__init__('https://www.wunderground.com/health/us/')

    def with_location(self, state, city, station):
        self.url = self.base_url + '/'.join((state, city, station))
        return self

    def to_string(self):
        return self.url

class PollenUrlBuilderFactory(object):

    def __init__(self):
        self.__weather = WeatherPollenApiUrlBuilder()
        self.__wunderground = WundergroundUrlBuilder()

    @property
    def weather(self):
        return self.__weather

    @property
    def wunderground(self):
        return self.__wunderground

class PollenApiClient(object):

    """Class PollenApiClient can be used to retrieve and store information about
       the pollen forecast from The Weather Channel (tm) and Wunderground (tm)"""

    URL_FACTORY = PollenUrlBuilderFactory()

    MAX_REQUESTS = 4
    SOURCE_SPAN = {'weather text': 7, 'weather values': 7, 'wu poll': 4}
    SOURCE_URLS = {98105: {'weather values': URL_FACTORY.weather.with_geocode(47.654003, -122.309166).build(),
                           'wu poll': URL_FACTORY.wunderground \
                                .with_location('wa', 'seattle', 'KWASEATT446') \
                                .with_query_params({'cm_ven': 'localwx_modpollen'}) \
                                .build()},
                   98684: {'weather values': URL_FACTORY.weather.with_geocode(45.639816, -122.497902).build(),
                           'wu poll': URL_FACTORY.wunderground \
                                .with_location('wa', 'camas', 'KWACAMAS42') \
                                .with_query_params({'cm_ven': 'localwx_modpollen'}) \
                                .build()}}

    for url in SOURCE_URLS:
        # weather text and values use the same endpoint
        SOURCE_URLS[url]['weather text'] = SOURCE_URLS[url]['weather values']
    del url # remove from scope
    TYPES = ('grass', 'ragweed', 'tree')

    def __init__(self, source, zipcode, print_sources=True):
        """Initializes this PollenApiClient object using the given source and
           zipcode. Builds the database when all inputs are valid."""
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
        if source not in PollenApiClient.SOURCE_SPAN.keys():
            raise ValueError('source must be one from [{}]'.format(", ".join(PollenApiClient.SOURCE_SPAN.keys())))

    def __verify_zipcode(self, zipcode):
        if zipcode not in PollenApiClient.SOURCE_URLS.keys() or zipcode < 0 or zipcode > 99501:
            raise ZipCodeNotFoundException(zipcode)

    def __get_markup(self, uri):
        """Retrieves the markup with up to 4 max tries. Returns empty
           markup if web requests fail"""

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
        """Sets the source for this PollenApiClient object. Requires `build` to be called to update data"""
        self.__verify_source(source)
        self.uri = PollenApiClient.SOURCE_URLS[self.zipcode][source]
        self.source = source
        self.__date_built = None

    def set_zipcode(self, zipcode):
        """Sets the zipcode for this PollenApiClient object. Requires `build` to be called to update data"""
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
        """Returns True if this client has built the database, otherwise False"""
        return self.date_built is not None

class ZipCodeNotFoundException(Exception):
    def __init__(self, zipcode, *args, **kwargs):
        super(ZipCodeNotFoundException, self).__init__(repr(self), *args, **kwargs)
        self.zipcode = zipcode

    def __repr__(self):
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

    import traceback

    from clay.settings import DOCS_DIR
    from clay.tests import testif

    cc = CourseCatalogUW()
    testif('UW course catalog queries general course correctly',
        cc.query('cse 14'),
        {'message': None,
         'results': {'course_list':
             [{'title': 'CSE 142 Computer Programming I (4) NW, QSR',
               'description': None, 'instructor': None},
              {'title': 'CSE 143 Computer Programming II (5) NW, QSR',
               'description': None, 'instructor': None}],
         'header': None}})
    testif('UW course catalog queries specific course correctly',
        cc.query('cse 142'),
        {'message': None,
         'results': {'course_list':
            [{'title': 'CSE 142 Computer Programming I (4) NW, QSR',
              'description': 'Basic programming-in-the-small abilities '
                  'and concepts including procedural programming (methods, '
                  'parameters, return, values), basic control structures '
                  '(sequence, if/else, for loop, while loop), file processing, '
                  'arrays, and an introduction to defining objects. Intended '
                  'for students without prior programming experience. Offered: '
                  'AWSpS.',
              'instructor': None}],
         'header': None}})

    with open('logs/net-core-find-anchors.log', 'w') as fa_log:
        print('ANCHORS', file=fa_log)
        print(find_anchors(TEST_LINK, internal=False), file=fa_log)

    we1 = TagFinder('https://thebestschools.org/rankings/20-best-music-conservatories-u-s/')
    testif('best music school list contains 21 elements', len(we1.find('h3')), 21)
    we2 = TagFinder(TEST_LINK)
    we2.find('a')
    with open('logs/net-core-tagfinder.log', 'w') as tf_log:
        we2.show(attribute='href', file=tf_log)

    print()
    expected_url = 'http://example.com/?key=value'
    for test_url in ('http://example.com/', EXAMPLE_URL):
        url_builder = UrlBuilder(test_url)
        url_builder.with_query_string('key=value')
        testif('UrlBuilder adds query string correctly', url_builder.build(), expected_url)
    expected_url = 'http://example.com/path/segment'
    for test_url in ('http://example.com/', EXAMPLE_URL):
        url_builder = UrlBuilder(test_url)
        for test_path in ('path', '/path'):
            url_builder.reset()
            url_builder.append_segments(test_path, 'segment')
            testif('UrlBuilder adds path segments correctly', url_builder.build(), expected_url)
    print(url_builder) # test the string representation
    testif('UrlBuilder resets URL to base correctly',
        url_builder.reset() or url_builder.build(),
        EXAMPLE_URL)

    print()
    testif('webdoc sets uri correctly for empty uri',
        WebDocument().raw_uri, None)
    for scheme in VALID_SCHEMES:
        testif('webdoc sets uri correctly for valid uri ({})'.format(scheme),
            WebDocument(scheme).raw_uri, scheme)
    testif('webdoc raises exception for invalid uri scheme',
        lambda: WebDocument('test'), None, raises=ValueError)
    print(WebDocument(LINKS['2MB']) \
        .download(
            destination=DOCS_DIR,
            return_speed=True),
        'bytes per second')
    print()
    testif('webdoc returns basename and query',
        WebDocument('https://www.minecraft.net/change-language?next=/en/')
            .get_basename(full=False),
        ('change-language', 'next=/en/'))
    testif('webdoc returns full name and no query',
        WebDocument(LINKS['1MB']).get_basename(full=True),
        ('download.thinkbroadband.com.1MB.zip', None))
    testif('webdoc returns correct website html title',
        WebDocument(EXAMPLE_URL).get_title(),
        'Example Domain')
    testif('webdoc returns correct YouTube html title',
        WebDocument('https://www.youtube.com/watch?v=LUjTvPy_UAg').get_title(),
        'I tracked every minute of my life for 3 months. - YouTube')
    testif('webdoc get_html ignores user-agent and accept-encoding headers',
        WebDocument('https://www.youtube.com/watch?v=LUjTvPy_UAg').get_title(headers=WEB_HDRS),
        'I tracked every minute of my life for 3 months. - YouTube')
    testif('webdoc get_html throws TypeError for invalid headers type',
        lambda: WebDocument().get_html(['invalid', 'headers', 'type']), None, raises=TypeError)
    testif('webdoc returns correct basename with no query',
        WebDocument(TEST_LINK).get_basename(),
        ('index.html', None))

    p = PollenApiClient('weather text', 98684)
    with open('logs/net-core-pollen.log', 'w') as pollen_log:
        try:
            p.print_db(file=pollen_log)
            p.set_source('weather values')
            p.set_zipcode(98105)
            p.build()
            p.print_db(file=pollen_log)
        except Exception:
            traceback.print_exc()

    testif('pollen throws exception for invalid source', \
        lambda: p.set_source('invalid source'), None, raises=ValueError)
    testif('pollen throws exception for invalid zipcode', \
        lambda: p.set_zipcode(97132), None, raises=ZipCodeNotFoundException)
