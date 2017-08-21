"""
File operations. Supports NT and linux-based kernels
"""

import os as _os
import requests as _requests
import traceback as _traceback
import urllib.request, urllib.error, urllib.parse

from pack import WEB_HDR as _WEB_HDR

def appendfile(filename, line=str()):
    """Appends line to a file"""
    while not(line):
        line = input('line: ')
    with open(filename, 'ab') as fp:
        try:
            f.write(line.encode('utf8')) # for str
        except:
            f.write(line) # for binary

def countchar(filename, char):
    """Count occurence of char in filename"""
    with open(filename) as fp:
        fcount = fp.read().count(char)
    return fcount

def countwords(filename):
    """Count number of words in file given filename"""
    with open(filename) as fp:
        fcount = len(fp.read().split())
    return fcount

def fix_quotes(filename):
    """Fix UTF-8 quotes to ANSI"""
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
    """Get file content"""
    mode = 'r'
    if binary:
        mode += 'b'
    if not(_os.path.exists(filename)):
        raise FileNotFoundError()
    with open(filename, mode) as fp:
        fread = fp.read()
    return fread

def get_size(name):
    """Get the size of a file or url"""
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

def parsefile(filename, delim='\n'):
    """Parse a file by it's delimiter"""
    with open(filename, 'r') as fp:
        spl = fp.read().split(delim)
    return spl

def printfile(filename):
    with open(filename) as fp:
        print(fp.read())

def save(text, name='text.txt'):
    """Save to file with file numbering"""
    from os.path import exists
    SP = name.split('.')
    x = 1
    while True:
        name = SP[0]+str(x)+''.join(SP[1:-1])+'.'+SP[-1]
        if not exists(name):
            break
        x += 1
    with open(name,'w') as s:
        s.write(str(text))
    return name
        
def switch_lf(filename):
    """Switch versions of linefeed from a UNIX machine to Windows and vice versa"""
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
    """http://stackoverflow.com/questions/6648493/open-file-for-both-reading-and-writing"""
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

def text_replace(name, old, new, recurse=False):
    from pack.fileops import _tr_base
    if recurse:
        sure = eval(input('Replace all "{1}" in "{0}" with "{2}" (True/False)? '.format(name, old, new)))

        if sure:
            for root, dirs, files in _os.walk(name):
                for f in files:
                    fp = open(_os.path.join(root, f), 'rb')
                    if old in fp.read():
                        _tr_base(_os.path.join(root, f), old, new)
                    fp.close()
            print('Done')
        else:
            print('Aborted')

    else:
        _tr_base(name, old, new)

if __name__ == '__main__':
    print('Expect basename not to exist')
    try:
        print(get_size('http://www.google.com/'))
    except Exception as e:
        _traceback.print_exc()
    from pack.web import LINK as _LINK
    print('Expect basename to exist')
    print(get_size(_LINK))
