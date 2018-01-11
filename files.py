"""
File functions, supports NT and unix-based kernels

"""

import os as _os
import requests as _requests
import traceback as _traceback
import urllib.request, urllib.error, urllib.parse

from clay import WEB_HDR as _WEB_HDR
from clay.shell import ssdExists as _ssdExists

def appendfile(filename, string=str()):
    """Appends line to a file, not prefaced with a new line"""
    while not(string):
        string = input('line: ')
    with open(filename, 'ab') as fp:
        try:
            f.write(string.encode('utf8')) # for str
        except:
            f.write(string) # for binary

def countchar(filename, char):
    """Returns the count occurence of char in filename"""
    with open(filename) as fp:
        fcount = fp.read().count(char)
    return fcount

def countwords(filename):
    """Returns the count number of words in file given filename"""
    with open(filename) as fp:
        fcount = len(fp.read().split())
    return fcount

def fix_quotes(filename):
    """Replaces UTF-8 quotes with ANSI ones"""
    try:
        fp = open(filename,'rb+')
        fread = fp.read()
        fp.seek(0)
        fread = fread.replace(b'\xe2\x80', b'')
        for i in (b'\x93', b'\x94', b'\x9c', b'\x9d'):
            fread = fread.replace(i, b'"')
        fp.write(fread)
        fp.truncate() # adds str terminator
        print('FixQuotes complete')
    except Exception as e:
        print('Error:', e)
    finally:
        fp.close()

def get_content(filename, binary=False):
    """Returns file content"""
    mode = 'r'
    if binary:
        mode += 'b'
    if not(_os.path.exists(filename)):
        raise FileNotFoundError()
    with open(filename, mode) as fp:
        fread = fp.read()
    return fread

def get_size(name):
    """Returns the size of a file or uri"""
    from requests import head
    if _os.path.exists(name):
        size = _os.path.getsize(name)
    else:
        if _os.path.basename(name):
            try:
                response = head(name, headers=_WEB_HDR)
                size = int(response.headers['Content-Length'])
            except Exception as e:
                _traceback.print_exc()
                size = 0
        else:
            raise Exception('Basename not found. Need an absolute url path')
    return size

def parsefile(filename, delim='\n', mode='r'):
    """Parses a file by it's delimiter and returns the list"""
    with open(filename, mode) as fp:
        spl = fp.read().split(delim)
    return spl

def printfile(filename):
    """Prints the binary contents to the given file"""
    with open(filename, 'rb') as fp:
        print(fp.read())

def save(text, name='text.txt'):
    """Saves the given text to file with version numbering"""
    SP = _os.path.splitext(name)
    x = 0
    name = _save_helper(SP, x)
    while _os.path.exists(name):
        x += 1
        name = _save_helper(SP, x)
    with open(name, 'w') as fp:
        fp.write(str(text))
    return name

def _save_helper(SP, x):
    """Helps `save` with finding a valide name for a file"""
    return '{}{:03d}{}'.format(SP[0], x, SP[-1])
        
def switch_lf(filename):
    """Switches the linefeed type from a unix-based machine to Windows and vice versa and overwrites the file"""
    with open(filename, 'rb') as fp:
        fread = fp.read()
        to_unix = False
        if b'\r' in fread:
            to_unix = True
    with open(filename, 'wb') as fp:
        if to_unix:
            fwrite = fread.replace(b'\r', b'')
        else:
            fwrite = fread.replace(b'\n', b'\r\n')
        fp.write(fwrite)
    if to_unix:
        print('Converted to lf')
    else:
        print('Converted to crlf')

def _tr_base(filename, old, new):
    """Helps `text_replace` rename a particular file
    http://stackoverflow.com/questions/6648493/open-file-for-both-reading-and-writing"""
    try:
        fp = open(filename, 'rb+')
        fread = fp.read()
        fp.seek(0)
        fp.write(fread.replace(old, new))
        fp.truncate() # add NULL terminator
        print('text_replace on "{}" complete'.format(filename))
    except Exception as e:
        print('Error:', e)
    finally:
        fp.close()

def text_replace(name, old, new, recurse=False, ext=str()):
    """Replaces `name` with binary string params `old` and `new`"""
    from clay.files import _tr_base
    if recurse:
        sure = eval(input('Replace all "{1}" in "{0}" with "{2}" (True/False)? '.format(name, old, new)))

        if sure:
            for root, dirs, files in _os.walk(name):
                for f in files:
                    try:
                        fp = open(_os.path.join(root, f), 'rb')
                        if old in fp.read() and f.endswith(ext):
                            _tr_base(_os.path.join(root, f), old, new)
                    except Exception as e:
                        raise e
                    finally:
                        fp.close()
            print('Done')
        else:
            print('Aborted')

    else:
        _tr_base(name, old, new)

if __name__ == '__main__':
    print('Expects basename not to exist')
    try:
        print(get_size('http://www.google.com/'))
    except Exception as e:
        _traceback.print_exc()
    from clay.web import LINKS as _LINKS
    print('Expects basename to exist')
    print(get_size(_LINKS['1MB']))
