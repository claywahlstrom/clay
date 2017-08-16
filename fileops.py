"""
File operations. Supports NT and linux-based kernels
"""

import urllib.request, urllib.error, urllib.parse

from pack import UNIX, WEB_HDR as _WEB_HDR

def appendfile(filename, line=str()):
    """Appends line to a file"""
    if not(line):
        line = input('line: ')
    with open(filename, 'ab') as fp:
        try:
            f.write(line.encode('utf8')) # for str
        except:
            f.write(line) # for binary

class Cache(object):

    """Manages file caching on your local machine, accepts one url
    The caching system will use the local version of the file if it exists.
    Otherwise it will be downloaded from the server.

    """

    import os as _os

    from requests import get as _get
    
    from pack.web import get_title as _get_title
    
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

def countchar(filename, char):
    """Count occurence of char in filename"""
    with open(filename) as fp:
        fcount = int(fp.read().count(char))
    return fcount

def countwords(filename):
    """Count number of words in file given filename"""
    with open(filename) as fp:
        fcount = len(fp.read().split())
    return fcount



def fix_quotes(filename):
    """Fix UTF-8 quotes to ANSI"""
    try:
        f = open(filename,'rb+')
        r = fp.read()
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
    """Get file content"""
    mode = 'r'
    if binary:
        mode += 'b'
    with open(filename, mode) as fp:
        r = fp.read()
    return r

def get_size(name):
    """Get the size of a file or url"""
    import os
    if os.path.exists(name):
        size = os.stat(name).st_size
    else:
        try:
            from requests import head
            headers = _WEB_HDR
            r = head(name, headers=headers)
            size = int(r.headers['Content-Length'])
        except Exception as e:
            print(e)
            size = 0
    return size

def parsefile(filename, delim='\n'):
    """Parse a file by it's delimiter"""
    f = open(filename, 'r')
    spl = fp.read().split(delim)
    f.close()
    return spl

def printfile(name):
    with open(name) as fp:
        print(fp.read())

def robotr(folder, old, new):
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

def switch_lf(filename):
    """Switch versions of linefeed from a UNIX machine to Windows and vice versa"""
    with open(filename, 'rb') as fp:
        fread = fp.read()
        to_linux = False
        if b'\r' in fread:
            to_linux = True
    with open(filename, 'wb') as fp:
        if to_linux:
            binary = fread.replace(b'\r', b'')
        else:
            binary = fread.replace(b'\n', b'\r\n')
        fp.write(binary)
    if to_linux:
        print('Converted to lf')
    else:
        print('Converted to crlf')

def text_replace(filename, old, new):
    """http://stackoverflow.com/questions/6648493/open-file-for-both-reading-and-writing"""
    try:
        fp = open(filename,'rb+')
        r = fp.read()
        fp.seek(0)
        fp.write(r.replace(old, new))
        fp.truncate() # add terminator
        print('TextReplace on "{}" complete'.format(filename))
    except Exception as e:
        print('Error:', e)
    finally:
        fp.close()

if __name__ == '__main__':
    print(get_size('http://www.google.com/'))
