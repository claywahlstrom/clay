
"""
web module

TODO: fix the web header to fix google.com JS rendering problem with accept-char

"""

import os as _os
from subprocess import call as _call
import sys as _sys
import urllib.request, urllib.error, urllib.parse

import requests as _requests
from bs4 import BeautifulSoup as _BS

from clay.shell import getDocsFolder as _getDocsFolder, isIdle as _isIdle, isUnix as _isUnix

CHUNK_CAP = 1e6 # 1MB

# download links for testing
LINKS = dict()
LINK_SIZES = list(map(lambda n: str(n) + 'MB', [1, 2, 5, 10, 20, 50, 100, 200, 512]))
for n in LINK_SIZES:
    LINKS[n] = 'http://download.thinkbroadband.com/' + str(n) + '.zip'
LINKS['1GB'] = 'http://download.thinkbroadband.com/1GB.zip'

TEST_LINK = 'https://minecraft.net/en-us/'

WEB_HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
           #'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept': 'text/html,text/plain,application/xhtml+xml,application/xml,application/json;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Charset': 'Windows-1252,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'en-US,en;q=0.8;q=0.5',
           'Connection': 'keep-alive'}

class Cache(object):
    """Class Cache can be used to manage file caching on your local machine,
       accepts one uri. The caching system will use the local version of
       the file if it exists. Otherwise it will be downloaded from the server.

       The main advantage is saving time by eliminating downloads

    """

    def __init__(self, uri, alt_title=None):
        """Initializes a new Cache object using the given uri"""

        from clay.web import get_basename as _get_basename

        self.uri = uri

        if alt_title is None:
            self.title = _get_basename(uri)[0]
        else:
            self.title = alt_title

        if not(_os.path.exists(self.title)):
            self.store()

    def exists(self):
        """Returns a boolean of whether the file exists"""
        return _os.path.exists(self.title)
        
    def _get_content(self):
        """Returns the content of this cached file"""
        assert self.exists()
        with open(self.title, 'rb') as fp:
            fread = fp.read()
        return fread

    def length(self):
        """Returns the length of the byte file"""
        return len(self._get_content())

    def load(self):
        """Returns binary content from self.title"""
        print('Loading from cache "{}"...'.format(self.title), end=' ')
        cont = self._get_content()
        print('Done')
        return cont

    def reload(self):
        """Alias for `store`, but easier to remember for humans
           Commonly performed outside of a script"""
        print('Performing a cache reload for "{}"...'.format(self.title))
        self.store()

    def store(self):
        """Stores binary content of the requested uri, returns None"""
        print('Storing into cache "{}"...'.format(self.title), end=' ')
        with open(self.title, 'wb') as fp:
            fp.write(_requests.get(self.uri).content)
        print('Done')

def download(url, title=str(), full_title=False,
             destination='.', log_name='dl_log.txt', speed=False):
    """Downloads data from the given url and logs the relevant information
    in the same directory"""

    # http://stackoverflow.com/a/16696317/5645103

    assert type(url) == str, 'Lists not supported'

    import datetime as dt
    from time import time

    from clay.shell import set_title
    from clay.web import get_basename

    flag = False
    if log_name:
        log_path = _os.path.join(destination, log_name)
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
            response = _requests.get(url, params=query, headers=WEB_HDR)
            before = time() # start timer
            size = len(response.text)
            print(size, 'bytes')
            fp.write(response.text.encode('utf-8'))
            fp.close()
        else:
            response = _requests.get(url, params=query, headers=WEB_HDR, stream=True) # previously urllib.request.urlopen(urllib.request.Request(url, headers=WEB_HDR))
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
        print('\n'+type(e).__name__, e.args)
        log_string = url+' failed\n'
        flag = True
    else:
        taken = time() - before
        print('\ntook {}s'.format(taken))
        if not(_isIdle() or _isUnix()):
            set_title('Completed {}'.format(title))
        log_string = '{} on {} of {} bytes [{}]\n'.format(title, dt.datetime.today(), size, url)
        print('Complete\n')
    finally:
        if not(fp.closed):
            fpInitializes.close()
    if log_name:
        with open(log_path,'a+') as lp:
            lp.write(log_string)
    else:
        print(log_string.strip())
    _os.chdir(current) # better file handling
    if speed and not(flag):
        return size / taken

class Elements(object):
    """Class Elements can find and store elements from a given web page or markup"""

    def __init__(self, page=None, element=None, method='find_all', use_local=False):
        """Initalizes a new Elements object"""
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
            betterheaders = WEB_HDR.copy()
            self.request = _requests.get(page, headers=betterheaders)
            if not(self.request.content.startswith(b'<')):
                betterheaders.pop('Accept-Encoding')
                self.request = _requests.get(page, headers=betterheaders)
            self.src = self.request.content
        self.page = page
        self.soup = _BS(self.src, 'html.parser')
        self.element = element
        self.method = method

    def find_elements(self):
        self.__found = eval('self.soup.{}("{}")'.format(self.method, self.element))
        if not(self.__found):
            print('No elements found')

    def get_found(self):
        return self.__found

    def set_element(self, element):
        self.element = element

    def show(self, attribute='text', file=_sys.stdout):
        print('Elements for', self.page + ':', file=file)
        for i in self.get_found():
            try:
                if attribute == 'text':
                    print(i.getText(), file=file)
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
    """Extracts links from a location. Accepts filename or url"""
    if 'http' in location:
        fread = _requests.get(location, params=query).content#headers=WEB_HDR, params=query).content
    else:
        with open(location,'r') as bc:
            fread = bc.read()
    soup = _BS(fread, 'html.parser')
    raw_links = soup.find_all('a')
    links = list()
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

def get_file_uri(path):
    """Returns the web file uri for the given path"""
    return 'file:///' + path.replace('\\', '/')

def get_file(uri):
    """Returns the response from the given `uri`"""
    response = urllib.request.urlopen(urllib.request.Request(url, headers=WEB_HDR))
    return response.read()

def get_html(uri, query=None, headers=True):
    """Returns the binary response from the given `uri`"""
    if query is not None:
        assert type(query) == dict
    if headers:
        fread = _requests.get(uri, params=query, headers=WEB_HDR)
    else:
        fread = _requests.get(uri, params=query)
    text = fread.text.encode('utf-8')
    return text

def get_mp3(link, title=str()):
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
    from clay.files import download
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

if __name__ == '__main__':
    print(download(LINKS['2MB'], destination=_getDocsFolder(), speed=True), 'bytes per second')
    print(get_basename('https://www.minecraft.net/change-language?next=/en/', full=False))
    print(get_basename(LINKS['1MB'], full=True))
    print(get_title(TEST_LINK))
    print(get_basename(TEST_LINK))
    print('title from markup:', get_title(TEST_LINK))
    we1 = Elements('https://thebestschools.org/rankings/20-best-music-conservatories-u-s/', 'h3')
    we1.find_elements()
    we1.show()
    we2 = Elements()
    we2.find_elements()
    we2.show(attribute='href')
    print('ANCHORS')
    print(find_anchors(TEST_LINK, internal=False))

