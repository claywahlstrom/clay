"""
File operations. Supports NT and linux-based kernels
"""

import urllib.request, urllib.error, urllib.parse

from pack import LINUX

LINK = 'http://download.thinkbroadband.com/1MB.zip'

HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.60 Safari/537.36',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'Windows-1252,utf-8;q=0.7,*;q=0.3',
       "Accept-Encoding": "gzip, deflate, br",
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def appendfile(filename, line=str()):
    """Appends line to a file"""
    if not(line):
        line = input('line: ')
    with open(filename,'ab') as f:
        try:
            f.write(line.encode('utf8')) # for str
        except:
            f.write(line) # for binary

def countchar(filename, char):
    """Count occurence of char in filename"""
    with open(filename) as f:
        fcount = int(f.read().count(char))
    return fcount

def countwords(filename):
    """Count number of words in file given filename"""
    with open(filename) as f:
        fcount = len(f.read().split())
    return fcount

def download(url, title=str(), full_title=False, destination='.', speed=False, log='DL_log.txt'):
    """Downloads a url and logs information appropriately"""
    # http://stackoverflow.com/a/16696317/5645103

    assert type(url) == str, 'Lists not supported'

    from datetime import datetime
    import os # for less pack dependencies
    import sys
    from time import time

    import requests
    
    from pack.fileops import get_title

    flag = False
    if log:
        logloc = destination+'/'+log
    current = os.getcwd()
    os.chdir(destination) # better file handling
    print('curdir', os.getcwd())

    if not title:
        title, query = get_title(url, full_title)
    else:
        query = None
    f = open(title, 'wb')
    print('Retrieving "{}"...\ntitle {}\nquery {}...'.format(url, title, query))
    try:
        print('size', end=' ')
        if not('.' in title) or 'htm' in title or 'php' in title:
            response = requests.get(url, params=query, headers=HDR)
            before = time() # start timer
            size = len(response.text)
            print(size, 'bytes')
            f.write(response.text.encode('utf-8'))
            f.close()
        else:
            response = requests.get(url, params=query, headers=HDR, stream=True)# previously urllib.request.urlopen(urllib.request.Request(url, headers=HDR))
            before = time() # start timer
            size = int(response.headers.get('content-length'))
            CHUNK = size//100
            if CHUNK > 1000000: # place chunk cap on files >1MB
                CHUNK = 100000 # 0.1MB
            print(size, 'bytes')
            print("Writing to file in chunks of {} bytes...".format(CHUNK))
            actual = 0
            try:
                for chunk in response.iter_content(chunk_size=CHUNK):
                    if not chunk: break
                    f.write(chunk)
                    actual += len(chunk)
                    percent = int((actual/size)*100)
                    if 'idlelib' in sys.modules or LINUX:
                        if percent % 5 == 0: # if multiple of 5 reached...
                            print('{}%'.format(percent), end=' ', flush=True)
                    else:
                        os.system('title {}% {}/{}'.format(percent, actual, size))
            except Exception as e:
                print(e)
            finally:
                f.close()
    except Exception as e:
        print('\n'+type(e).__name__, e.args)
        logging = url+' failed\n'
        flag = True
    else:
        taken = time() - before
        print('\ntook {}s'.format(taken))
        if not('idlelib' in sys.modules or LINUX):
            os.system('title Completed {}'.format(title))
        logging = '{} on {} of {} bytes\n'.format(url, datetime.today(), size)
        print('Complete\n')
    finally:
        if not f.closed:
            f.close()
    if log:
        with open(logloc,'a+') as L:
            L.write(logging)
    else:
        print(logging.strip())
    os.chdir(current) # better file handling
    if speed and not(flag):
        return size/taken

def find_href(location, query={}, internal=True, php=False):
    """Extract links. Accepts filename or url"""
    from bs4 import BeautifulSoup as bs
    if not('://' in location):
        with open(location,'r') as bc:
            Read = bc.read()
    else:
        from requests import get
        Read = get(location, headers=HDR, params=query).content
    soup = bs(Read, 'html.parser')
    raw_links = soup.find_all('a')
    print(raw_links)
    if php or internal:
        links = [x['href'] for x in raw_links if (location[:16] in x['href'] or x['href'].startswith('/')) and not('#' in x['href'])]
        if internal:
            links = [link for link in links if not('?' in link)]
    else:
        links = [link['href'] for link in raw_links]
    return links

def FixQuotes(filename):
    try:
        f = open(filename,'rb+')
        r = f.read()
        f.seek(0)
        r = r.replace(b'\xe2\x80', b'')
        for i in (b'\x93', b'\x94', b'\x9c', b'\x9d'):
            r = r.replace(i, b'"')
        f.write(r)
        f.truncate() # adds str terminator
        print('FixQuotes complete')
    except Exception as e:
        print('Error:', e)
    finally:
        f.close()

def get_content(filename, binary=False):
    mode = 'r'
    if binary:
        mode += 'b'
    with open(filename, mode) as f:
        r = f.read()
    return r

def get_file(url):
    """Read response from files"""
    response = urllib.request.urlopen(urllib.request.Request(url, headers=HDR))
    return response.read()

def get_html(page, query=None):
    """Read binary response from webpage"""
    if query is not None:
        assert type(query) == dict
    import requests
    r = requests.get(page, params=query, headers=HDR)
    t = r.text.encode('utf-8')
    return t

def get_size(url):
    response = urllib.request.urlopen(urllib.request.Request(url, headers=HDR))
    return int(response.info()["Content-Length"])

def get_title(url, full=False):
    if '?' in url:
        nurl, query = url.split('?')
    else:
        nurl, query = url, None
    title = nurl.split('/')[-1]
    ext = True
    if ('htm' in title) or ('aspx' in title) or ('php' in title) or ('.' in title and url.count('/') > 2):
        ext = False

    if full:
        title = nurl.replace('://', '_').replace('/', '_')
    if not(title):
        title = 'index'
    if ext:
        title += '.html'
    title = urllib.parse.unquote_plus(title)
    #print('Title', title)
    return title, query

def get_mp3(link, title=str()):
    """Download mp3juice.cc links"""
    from pack.fileops import download
    if not(title):
        title = link[link.index('=')+1:]+'.mp3'
    download(link, title=title)

def get_vid(v, vid_type='mp4'):
    """Download using yt-down.tk"""
    from pack.fileops import download
    download('http://www.yt-down.tk/?mode={}&id={}'.format(vid_type, v), title='.'.join([v, vid_type]))

def parsefile(filename, delim='\n'):
    """Parse a file by it's delimiter"""
    f = open(filename, 'r')
    spl = f.read().split(delim)
    f.close()
    return spl

def printfile(name):
    with open(name) as f:
        print(f.read())

def RoboTR(folder, old, new):
    sure = eval(input('Replace all "{1}" in "{0}" with "{2}" (True/False)? '.format(folder, old, new)))

    if sure:
        from os import walk, sep
        from pack.fileops import TextReplace
        for root, dirs, files in walk(folder):
            for f in files:
                fp = open(root+sep+f, 'rb')
                if old in fp.read():
                    TextReplace(root+sep+f, old, new)
                fp.close()
        print('Done')
    else:
        print('Aborted')

def TextReplace(filename, old, new):
    """http://stackoverflow.com/questions/6648493/open-file-for-both-reading-and-writing"""
    try:
        f = open(filename,'rb+')
        r = f.read()
        f.seek(0)
        f.write(r.replace(old, new))
        f.truncate() # add terminator
        print('TextReplace on "{}" complete'.format(filename))
    except Exception as e:
        print('Error:', e)
    finally:
        f.close()

class Cache(object):

    """Manages file caching on your local machine, accepts one url
    The caching system will use the local version of the file if it exists.
    Otherwise it will be downloaded from the server.

    """

    import os as _os

    from requests import get as _get
    
    from pack.fileops import get_title as _get_title
    
    def __init__(self, url, alt_title=None):
        self.url = url
        self.title = Cache._get_title(url)[0]
        self.exists = True
        if not alt_title is None:
            self.title = alt_title
        if not(Cache._os.path.exists(self.title)):
            self.exists = False
            self.store()
    def load(self):
        """Return binary content from self.title"""
        print('Loading cache...')
        with open(self.title, 'rb') as fp:
            r = fp.read()
        return r
    def reload(self):
        self.store()
    def store(self):
        """Store binary content of requested url, returns None"""
        print('Storing cache...')
        with open(self.title, 'wb') as fp:
            fp.write(Cache._get(self.url).content)


if __name__ == '__main__':
    get_title('https://www.minecraft.net/change-language?next=/en/', full=False)
    get_title('http://www.google.com/')
    get_title('http://www.google.com')
    get_title(LINK, full=True)
    download(LINK, destination=r'E:\Docs')
