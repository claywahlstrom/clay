"""
web module

need to fix the web header to fix google accept char problems


"""

import os as _os
from subprocess import call as _call
import sys as _sys
import urllib.request, urllib.error, urllib.parse

import requests as _requests
from bs4 import BeautifulSoup as _BS

from clay import UNIX as _UNIX

# data vars
from clay import WEB_HDR

CHUNK_CAP = 1000000 # 1MB

# downloadable links
LINKS = dict()
LINK_SIZES = map(lambda n: str(n) + 'MB', [1, 2, 5, 10, 20, 50, 100, 200, 512])
for n in LINK_SIZES:
    LINKS[n] = 'http://download.thinkbroadband.com/' + str(n) + '.zip'
LINKS['1GB'] = 'http://download.thinkbroadband.com/1GB.zip'

TEST_LINK = 'https://minecraft.net/en-us/'

class Cache:

    """Manages file caching on your local machine, accepts one uri
    The caching system will use the local version of the file if it exists.
    Otherwise it will be downloaded from the server.

    The main advantage is saving time by eliminating downloads

    """

    def __init__(self, uri, alt_title=None):

        from clay.web import get_basename as _get_basename

        self.uri = uri

        if alt_title is None:
            self.title = _get_basename(uri)[0]
        else:
            self.title = alt_title

        if not(_os.path.exists(self.title)):
            self.store()

    def exists(self):
        """Return a boolean of whether the file exists"""
        return _os.path.exists(self.title)

    def load(self):
        """Return binary content from self.title"""
        print('Loading cache "{}"...'.format(self.title))
        with open(self.title, 'rb') as fp:
            fread = fp.read()
        return fread

    def reload(self):
        """Alias for `store`, but easier to remember for humans
        Commonly performed outside of a script
        """
        print('Performing a cache reload...')
        self.store()

    def store(self):
        """Store binary content of requested uri, returns None"""
        print('Storing cache "{}"...'.format(self.title))
        with open(self.title, 'wb') as fp:
            fp.write(_requests.get(self.uri).content)

def download(url, title=str(), full_title=False, destination='.', log_name='dl_log.txt', speed=False):
    """Downloads a url and logs the relevant information"""

    # http://stackoverflow.com/a/16696317/5645103

    assert type(url) == str, 'Lists not supported'

    import datetime as dt
    import sys
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
                    if 'idlelib' in sys.modules or _UNIX:
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
        if not('idlelib' in sys.modules or _UNIX):
            set_title('Completed {}'.format(title))
        log_string = '{} on {} of {} bytes [{}]\n'.format(title, dt.datetime.today(), size, url)
        print('Complete\n')
    finally:
        if not(fp.closed):
            fp.close()
    if log_name:
        with open(log_path,'a+') as lp:
            lp.write(log_string)
    else:
        print(log_string.strip())
    _os.chdir(current) # better file handling
    if speed and not(flag):
        return size / taken

def find_anchors(location, query={}, internal=True, php=False):
    """Extract links from a location. Accepts filename or url"""
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
    """Return the basename and query of the specified uri"""
    if '?' in uri:
        url, query = uri.split('?')
    else:
        url, query = uri, None
    title = _os.path.basename(url)
    add_ext = True
    if [x for x in ['htm', 'aspx', 'php'] if x in title] or _os.path.basename(title):
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
    return 'file:///' + path.replace('\\', '/')

def get_file(url):
    """Read response from files"""
    response = urllib.request.urlopen(urllib.request.Request(url, headers=WEB_HDR))
    return response.read()

def get_html(page, query=None, headers=True):
    """Read binary response from webpage"""
    if query is not None:
        assert type(query) == dict
    if headers:
        fread = _requests.get(page, params=query, headers=WEB_HDR)
    else:
        fread = _requests.get(page, params=query)
    text = fread.text.encode('utf-8')
    return text

def get_mp3(link, title=str()):
    """Download mp3juice.cc links"""
    from clay.web import download
    if not(title):
        title = link[link.index('=') + 1:] + '.mp3'
    download(link, title=title)

def get_title(uri_or_soup):
    """Return the title from the markup"""
    if type(uri_or_soup) == str:
        uri = uri_or_soup
        soup = _BS(_requests.get(uri).content, 'html.parser')
    else:
        soup = uri_or_soup
    return soup.html.title.text

def get_vid(v, vid_type='mp4'):
    """Download using yt-down.tk"""
    from clay.fileops import download
    download('http://www.yt-down.tk/?mode={}&id={}'.format(vid_type, v), title='.'.join([v, vid_type]))

def openweb(uri, browser='firefox'):
    """Open pages in web browsers. "url" can be a list of urls"""
    if type(uri) == str:
        uri = [uri]
    if type(uri) == list:
        for link in uri:
            if _UNIX:
                _call(['google-chrome', link], shell=True)
            else:
                _call(['start', browser, link.replace('&', '^&')], shell=True)

class Elements:
    def __init__(self, page=None, element=None, method='find_all', reload_local=False):
        if page is None and element is None:
            page = TEST_LINK
            element = 'link'
        self.request = None
        if type(page) == bytes:
            self.src = page
        elif _os.path.exists(page) and not(reload_local):
            with open(page, 'rb') as fp:
                self.src = fp.read()
        else:
            self.request = _requests.get(page, headers=WEB_HDR)
            self.src = self.request.content
        self.soup = _BS(self.src, 'html.parser')
        self.element = element
        self.method = method

    def find_element(self):
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
                if attribute in ('string', 'text'):
                    print(eval('i.{}'.format(attribute)), file=file)
                else:
                    print(eval('i["{}"]'.format(attribute)), file=file)
            except KeyError as e:
                print('Key', e, 'for', i, 'not found')

    def store(self, filename, inner='text'):
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

if __name__ == '__main__':
    print(download(LINKS['1MB'], destination=r'E:\Docs', speed=True), 'bytes per second')
    print(get_basename('https://www.minecraft.net/change-language?next=/en/', full=False))
    print(get_basename(LINKS['1MB'], full=True))
    print(get_title(TEST_LINK))
    print(get_basename(TEST_LINK))
    print('title from markup:', get_title(TEST_LINK))
    we = Elements()
    we.find_element()
    we.show(attribute='href')
    print('ANCHORS')
    print(find_anchors(TEST_LINK, internal=False))

