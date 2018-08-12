
"""
files: Common file operations done easier with Python

"""

import os as _os
import requests as _requests
import traceback as _traceback
import urllib.request, urllib.error, urllib.parse

from clay.web import WEB_HDR as _WEB_HDR

def appendfile(filename, string=str()):
    """Appends the string to the end of the given file.
       No new line is preceded"""
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
    """Returns the count of words in the given file"""
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

def get_size(name, local=True):
    """Returns the size of the given file or uri.
       Returns 0 if no size was found."""
    size = 0 # default if no size is found
    if _os.path.exists(name) and not(local):
        size = _os.path.getsize(name)
    else:
        if _os.path.basename(name) or not(local):
            response = _requests.head(name, headers=_WEB_HDR)
            if 'Content-Length' in response.headers:
                size = int(response.headers['Content-Length'])
            else:
                size = len(_requests.get(name, headers=_WEB_HDR).content)
        else:
            raise Exception('Basename not found. Need an absolute url path')
    return size

def parsefile(filename, delim='\n', mode='r'):
    """Parses a file by the given delimiter and returns the resulting list"""
    with open(filename, mode) as fp:
        spl = fp.read().split(delim)
    return spl

def printfile(filename):
    """Prints the binary contents of the given file"""
    with open(filename, 'rb') as fp:
        print(fp.read())

def save(text, name='saved_text.txt', use_epoch=True):
    """Saves the given text to the file with sequential numbering"""
    SP = _os.path.splitext(name)
    if use_epoch:
        name = '{}-{}{}'.format(SP[0], int(time.time()), SP[-1])
    else:
        x = 0
        name = _save_helper(SP, x)
        while _os.path.exists(name):
            x += 1
            name = _save_helper(SP, x)
    with open(name, 'w') as fp:
        fp.write(str(text))
    return name

def _save_helper(SP, x):
    """Returns a possible filename. Helps `save` with finding a
       valid name for a file"""
    return '{}-{:03d}{}'.format(SP[0], x, SP[-1])
        
def switch_lf(filename):
    """Switches the linefeed type from a unix-based machine to
       Windows and vice versa and overwrites the file"""
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
