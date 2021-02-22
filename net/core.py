
"""
Net module

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

from bs4 import BeautifulSoup as _BS
import requests as _requests

from clay.env import is_idle as _is_idle, is_posix as _is_posix
from clay import settings

# download links for testing
LINKS = {}
LINK_SIZES = list(str(n) + 'MB' for n in [1, 2, 5, 10, 20, 50, 100, 200, 512])
for n in LINK_SIZES:
    LINKS[n] = 'http://download.thinkbroadband.com/' + str(n) + '.zip'
del n
LINKS['1GB'] = 'http://download.thinkbroadband.com/1GB.zip'

EXAMPLE_URL = 'http://example.com'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Accept': 'text/html,text/plain,application/xhtml+xml,application/xml,application/_json;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Charset': 'Windows-1252,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.8;q=0.5',
    'Connection': 'keep-alive'
}
TEST_LINK = 'https://minecraft.net/en-us/'
VALID_SCHEMES = ('file', 'ftp', 'http', 'https')

class CacheableFile(object):
    """
    Used to manage file caching on your local machine, accepts one URI.
    The caching system will use the local version of the file if it exists.
    Otherwise it will be downloaded from the server on load.

    The main advantage is saving time by eliminating recurring downloads.

    """

    def __init__(self, uri, filename=None):
        """Initializes this cacheable file. Does not cache the file."""
        self.reloaded = False
        self.remote_content = None

        if not isinstance(uri, str):
            raise TypeError('uri must be of type string')
        elif not uri or 'http' not in uri:
            raise ValueError('uri must use the HTTP protocol')

        self.filename = filename or WebDocument(uri).get_basename()[0]
        self.uri = uri

    def exists(self):
        """Returns a boolean of whether the cacheable file exists"""
        return _os.path.exists(self.filename)

    def fetch_remote(self):
        """Returns the content of the remote file"""
        print('Fetching remote for "{}"...'.format(self.filename), end=' ', flush=True)
        content = _requests.get(self.uri).content
        print('Done')
        return content

    def get_cached_remote(self):
        """
        Returns the content of the remote file from memory.
        Uses a copy of the remote for future calls to save bandwidth.

        """
        if self.remote_content is None:
            self.remote_content = self.fetch_remote()
        return self.remote_content

    def is_updated(self):
        """
        Returns True if the cacheable file has the same length
        as the remote file, False otherwise. Returns early with
        False if the file does not exist on the disk.

        """
        if not self.exists():
            return False

        return len(self._get_local()) == len(self.fetch_remote())

    def length(self):
        """Returns the length of the locally cacheable byte file"""
        self.store_if_not_exists()
        return len(self._get_local())

    def load(self):
        """Returns binary content from the cacheable file. Stores if not exists"""
        self.store_if_not_exists()
        print('Loading cacheable file "{}"...'.format(self.filename), end=' ', flush=True)
        cont = self._get_local()
        print('Done')
        return cont

    def reload(self):
        """
        Alias for `store`, but easier to remember for humans.
        Commonly performed outside of a script

        """
        print('Performing a cache reload for "{}"...'.format(self.filename))
        self.remote_content = self.fetch_remote()
        self.store()

    def store_if_not_exists(self):
        """Stores the remote content if the filename does not already exist"""
        if not self.exists():
            self.store()

    def store(self):
        """
        Writes the binary content of the requested URI to the disk.

        """
        print('Storing cacheable file "{}"...'.format(self.filename), end=' ', flush=True)
        with open(self.filename, 'wb') as fp:
            fp.write(self.get_cached_remote())
        print('Done')
        self.reloaded = True

    def _get_local(self):
        """Returns the content of the local cacheable file"""
        assert self.exists()
        with open(self.filename, 'rb') as fp:
            fread = fp.read()
        return fread

class CourseCatalogUW(object):

    """
    This class can be used to lookup courses by their ID
    on the University of Washington's Course Catalog.

    Query:
        CEE for a list of all classes in the department
        AES 1-25 or PHYS 12 or PHIL 1 for a narrowed listing
        MATH 126 for a description of the course

    Casing is ignored

    """

    CATALOG_URI = 'https://www.washington.edu/students/crscat/'

    def __init__(self):
        """Initializes this course catalog"""
        pages = {}

        pages['list'] = _BS(_requests.get(CourseCatalogUW.CATALOG_URI).content, 'html.parser')
        depts = [item['href'] for item in pages['list'].select('a')]
        depts = [item[:item.index('.')] for item in depts if '/' not in item and item.endswith('.html')]
        depts.sort()

        self.depts = depts
        self.MAX_LENGTH = max(map(len, depts))
        self.pages = pages

    def __print_columns(self, columns, width):
        """Prints the column values as columns for this course catalog"""
        for i, j in enumerate(columns):
            print(j, end=int(_math.ceil(_math.ceil(self.MAX_LENGTH / 8) - len(j) / 8)) * '\t')
            if i % width == width - 1:
                print()
        print() # flush output

    def get_departments(self):
        """Returns the departments"""
        return self.depts

    def print_departments(self, legacy=False):
        """Prints the departments for all course levels"""
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
        """Returns a result dictionary containing a list of matching courses"""
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
                        course_list.append({
                            'title': title,
                            'description': description if description else None,
                            'instructor': instructor if instructor else None
                        })
                    else:
                        message = 'course not found within ' + parts[0]
                    already_set = True
            else:
                header = self.pages[parts[0]].select('h1')[0].get_text()
            if not already_set:
                if len(found) > 0:
                    for f in found:
                        course_list.append({
                            'title': f.get_text(),
                            'description': None,
                            'instructor': None
                        })
                else:
                    message = 'course(s) not found'
        else: # invalid department
            message = 'enter a valid course id, ex. MATH 126'
        return {
            'message': message,
            'results': {
                'course_list': course_list,
                'header': header
            }
        }

def encode_json(data) -> str:
    """Returns the JSON string representation of the given data"""
    encoder = _json.JSONEncoder()
    return encoder.encode(data)

def file2uri(path):
    """Returns the web file URI for the given file path"""
    return 'file:///' + path.replace('\\', '/')

def find_anchors(location, query={}, internal=True, php=False):
    """
    Returns anchor references from a location (file name or uri)
        query    = query params sent in the request
        internal = uses internal site referenes if True
        php      = determines whether references with query params are included

    """

    if 'http' in location:
        fread = _requests.get(location, params=query).content#headers=HEADERS, params=query).content
    else:
        with open(location,'r') as bc:
            fread = bc.read()
    soup = _BS(fread, 'html.parser')
    raw_links = soup.find_all('a')
    links = []
    if php or internal:
        for x in raw_links:
            try:
                if (location[:16] in x['href'] or x['href'].startswith('/')) and \
                    '#' not in x['href']:
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

    """Used to build HTML markup"""

    INDENT = '    ' # 4 spaces

    def __init__(self, debug=False):
        """Initializes this builder"""
        self.indent = 0
        self.__html = ''
        self.__debug = debug

    def init(self):
        """Initiates this builder with the doctype and opening html tag"""
        self.add_doctype()
        self.add_tag('html', attrs={'lang': 'en'})

    def add_raw(self, raw_html):
        """Adds the raw HTML to this builder"""
        self.__html += raw_html

    def add_doctype(self):
        """Adds the doctype declaration to this builder"""
        self.__html += '<!doctype html>\n'

    def add_charset(self, charset='utf-8'):
        """Adds the meta charset tag to this builder"""
        self.add_tag('meta', self_closing=True, attrs={'charset': charset})

    def add_nl(self):
        """Adds the newline character to this builder"""
        self.__html += '\n'

    def add_tag(self, tag, text='', self_closing=False, attrs={}):
        """Adds the tag with options to this builder"""
        if self.debug:
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
        """Closes the given tag and dedents if applicable"""
        self.indent -= 1
        if not has_text:
            self.__html += HtmlBuilder.INDENT * self.indent

        self.__html += '</' + tag + '>'
        if not has_text:
            self.add_nl()

        if self.debug:
            print('build', tag, 'now', self.indent)

    def build(self):
        """Builds the HTML markup for this builder"""
        return self.__html

    @property
    def debug(self):
        """Returns the debug setting for this builder"""
        return self.__debug

def parse_raw_headers(raw_headers: str) -> dict:
    """
    Parses the given headers string and returns the corresponding
    headers dictionary. Useful when working with developer tools in
    the browser

    """
    headers = {}
    for header in raw_headers.strip().split('\n'):
        key, value = header.split(': ')
        headers[key] = value
    return headers

class TagFinder(object):
    """
    Class TagFinder can be used to find and store elements
    from a given web page or markup

    """

    def __init__(self, page):
        """Initializes this tag finder"""
        self.request = None
        if isinstance(page, bytes):
            self.src = page
        elif _os.path.exists(page):
            with open(page, 'rb') as fp:
                self.src = fp.read()
        else:
            betterheaders = HEADERS.copy()
            self.request = _requests.get(page, headers=betterheaders)
            if not self.request.content.startswith(b'<'):
                betterheaders.pop('Accept-Encoding')
                self.request = _requests.get(page, headers=betterheaders)
            self.src = self.request.content
        self.page = page
        self.soup = _BS(self.src, 'html.parser')

    def find(self, tag, method='find_all'):
        """Returns a list of found tags for the given search method"""
        self.__found = eval('self.soup.{}("{}")'.format(method, tag))
        if len(self.__found) == 0:
            print('No tags matching "{}" found'.format(tag))
        return self.__found

    def show(self, attribute='text', file=_sys.stdout):
        """Prints the tags to the output file (default is stdout)"""
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
        """Stores the request contents to the given filename"""
        assert isinstance(self.src, bytes)
        with open(filename, 'wb') as fp:
            fp.write(self.src)

    def store_tags(self, filename, inner='text'):
        """Stores the delineated tags output to the given filename"""
        try:
            with open(filename, 'w') as fp:
                self.show(inner=inner, file=fp)
            if _os.path.exists(filename):
                print('TagFinder store successful')
        except Exception as e:
            print('TagFinder store failed: {}'.format(e))

class WebDocument(object):

    """Can be used to work with files and URIs hosted on the web"""

    def __init__(self, uri=None, bypass_js=False):
        """Initializes this web document"""
        self.set_uri(uri)
        self.set_query(None)
        self.bypass_js = bypass_js

    def __repr__(self):
        """Returns the string representation for this web document"""
        return 'WebDocument(uri=%s)' % self.__raw_uri

    def download(self, title='', full_title=False, destination='.',
            log_name='webdoc-dl.log', return_speed=False,
            headers=HEADERS):
        """
        Downloads data from the document uri and logs revelant
        information in this directory

        """

        # http://stackoverflow.com/a/16696317/5645103

        from clay.shell.core import set_title

        url = self.__raw_uri
        errors = False
        if log_name:
            if _is_posix():
                log_path = _os.path.join(r'/home/clay/Desktop', log_name)
            else:
                log_path = _os.path.join(settings.PACKAGE_DIR, 'logs', log_name)
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
            else:
                # handle larger file types
                response = _requests.get(url, params=query, headers=headers, stream=True)
                if response.status_code != 200:
                    raise _requests.exceptions.InvalidURL('{}, status code {}'.format(response.reason, response.status_code))

                # start timer
                before = _time.time()
                size = int(response.headers.get('content-length'))
                chunk = size // 100

                # place chunk cap on files
                if chunk > settings.DOWNLOAD_CHUNK_SIZE:
                    chunk = settings.DOWNLOAD_CHUNK_SIZE

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
            if not isinstance(headers, dict):
                raise TypeError('headers must derive from type dict')
            if self.bypass_js:
                # remove user-agent and accept-encoding to ensure html is returned
                # for JS rendered pages
                headers = headers.copy()
                if 'Accept-Encoding' in headers:
                    headers.pop('Accept-Encoding')
                if 'User-Agent' in headers:
                    headers.pop('User-Agent')

        req = self._perform_get_request(headers=headers)

        if (req.status_code < 200 or req.status_code >= 300) and \
                headers and 'Accept-Encoding' in headers:
            headers = headers.copy()
            headers.pop('Accept-Encoding')
            req = self._perform_get_request(headers=headers)

        return req.content

    def get_response(self):
        """Returns the response from this document's `uri`"""
        request = urllib.request.Request(self.__raw_uri, headers=HEADERS)
        response = urllib.request.urlopen(request)
        return response.read()

    def get_title(self, headers=None):
        """Returns the title of this web document"""
        from clay.net.core import get_title
        soup = _BS(self.get_html(headers=headers), 'html.parser')
        return get_title(soup)

    @property
    def query(self):
        """The query parameters"""
        return self.__query

    @property
    def uri(self):
        """The URI"""
        return self.__uri

    @property
    def raw_uri(self):
        """The URI with query parameters"""
        return self.__raw_uri

    def launch(self, browser=settings.DEFAULT_BROWSER):
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
        """
        Sets the uri to the given string. Raises ValueError
        if the uri scheme is not supported

        """
        if uri is not None:
            if not isinstance(uri, str):
                raise TypeError('uri must be of type str')
            elif not any(uri.startswith(scheme) for scheme in VALID_SCHEMES):
                raise ValueError('uri must have a file, ftp, or http[s] scheme')
        self.__raw_uri = uri
        self.__uri = urllib.parse.urlsplit(uri)

    def size(self):
        """Returns the size of this document in bytes"""
        response = _requests.head(self.__raw_uri, headers=HEADERS)
        if 'Content-Length' in response.headers:
            size = int(response.headers['Content-Length'])
        else:
            size = len(self._perform_get_request(headers=HEADERS).content)
        return size

    def _perform_get_request(self, headers=None):
        """Performs the GET request and returns the response"""
        return _requests.get(self.__raw_uri, params=self.__query, headers=headers)

if __name__ == '__main__':

    from clay.settings import DOCS_DIR, LOGS_DIR
    from clay.tests import testif, testraises
    from clay.utils import qualify

    testraises('URI is not a string',
        lambda: CacheableFile(None),
        TypeError,
        name=qualify(CacheableFile.__init__))
    testraises('URI is empty',
        lambda: CacheableFile(''),
        ValueError,
        name=qualify(CacheableFile.__init__))
    testraises('URI does not use HTTP scheme',
        lambda: CacheableFile('ftp://127.0.0.1'),
        ValueError,
        name=qualify(CacheableFile.__init__))

    cc = CourseCatalogUW()
    testif('UW course catalog queries general course correctly',
        cc.query('cse 14'),
        {
            'message': None,
            'results': {
                'course_list': [
                    {
                        'title': 'CSE 142 Computer Programming I (4) NW, QSR',
                        'description': None,
                        'instructor': None
                    },
                    {
                        'title': 'CSE 143 Computer Programming II (5) NW, QSR',
                        'description': None,
                        'instructor': None
                    }
                ],
               'header': None
            }
         })
    testif('UW course catalog queries specific course correctly',
        cc.query('cse 142'),
        {
            'message': None,
            'results': {
                'course_list': [
                    {
                        'title': 'CSE 142 Computer Programming I (4) NW, QSR',
                        'description': 'Basic programming-in-the-small abilities '
                        'and concepts including procedural programming (methods, '
                        'parameters, return, values), basic control structures '
                        '(sequence, if/else, for loop, while loop), file processing, '
                        'arrays, and an introduction to defining objects. Intended '
                        'for students without prior programming experience. Offered: '
                        'AWSpS.',
                        'instructor': None
                    }
                ],
                'header': None
            }
        })

    with open(_os.path.join(LOGS_DIR, 'net-core-find-anchors.log'), 'w') as fa_log:
        print('ANCHORS', file=fa_log)
        print(find_anchors(TEST_LINK, internal=False), file=fa_log)

    testif('Parses headers correctly',
        parse_raw_headers("""Host: example.com
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive"""),
        {
            'Host': 'example.com',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        },
        name=qualify(parse_raw_headers))

    we1 = TagFinder('https://thebestschools.org/rankings/20-best-music-conservatories-u-s/')
    testif('best music school list contains 21 elements', len(we1.find('h3')), 21)
    we2 = TagFinder(TEST_LINK)
    we2.find('a')
    with open(_os.path.join(LOGS_DIR, 'net-core-tagfinder.log'), 'w') as tf_log:
        we2.show(attribute='href', file=tf_log)

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
    # testif('webdoc returns correct YouTube html title',
    #     WebDocument('https://www.youtube.com/watch?v=LUjTvPy_UAg').get_title(),
    #     'I tracked every minute of my life for 3 months. - YouTube')
    testif('webdoc get_html ignores user-agent and accept-encoding headers when JS bypassed',
        WebDocument('https://www.youtube.com/watch?v=LUjTvPy_UAg', bypass_js=True).get_title(headers=HEADERS),
        'I tracked every minute of my life for 3 months. - YouTube')
    testif('webdoc get_html throws TypeError for invalid headers type',
        lambda: WebDocument().get_html(['invalid', 'headers', 'type']), None, raises=TypeError)
    testif('webdoc returns correct basename with no query',
        WebDocument(TEST_LINK).get_basename(),
        ('index.html', None))
