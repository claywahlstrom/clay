
"""
Common file operations done easier with Python

"""

import os as _os
import time

from clay.libr import replace_smart_quotes

class ContentWatcher(object):

    """
    Class ContentWacther can be used to watch the modification
    time of a file, which correlates to a change in content

    """

    def __init__(self, filename):
        """Initializes this content watcher with the given file path"""
        self.set_path(filename)

    def get_mtime(self):
        """
        Returns the modified time for the content, returns 0
        if no file was found

        """
        if _os.path.exists(self.filename):
            return _os.stat(self.filename).st_mtime
        print(self.filename, 'does not exist')
        return 0

    def is_modified(self):
        """
        Returns True if the content has changed and resets the
        modification time, otherwise returns False and does not
        reset the modification time

        """
        new_time = self.get_mtime()
        if self.mtime == 0 or new_time != self.mtime:
            self.mtime = new_time
            return True
        return False

    def set_path(self, filename):
        """Sets the path of the content"""
        self.filename = filename
        self.mtime = 0

class File(object):

    """Class File can be used to access a file on the disk"""

    def __init__(self, name, create_if_not_exists=False):
        """Initializes this file"""
        self.name = name

        if not _os.path.exists(name):
            if create_if_not_exists:
                self.clear()
            else:
                raise FileNotFoundError(name)

    def append(self, string):
        """
        Appends the string to the end of this file.
        No new line is preceded

        """
        with open(self.name, 'ab') as fp:
            try:
                fp.write(string.encode('utf8')) # for non-binary strings
            except:
                fp.write(string) # for binary strings

    def clear(self):
        """Clears the content of this file"""
        with open(self.name, 'w') as fp:
            pass

    def get_char_count(self, char):
        """Returns the count occurrence of char in this file"""
        with open(self.name) as fp:
            fcount = fp.read().count(char)
        return fcount

    def get_content(self, binary=False):
        """Returns the content of this file"""
        mode = 'r'
        if binary:
            mode += 'b'
        with open(self.name, mode) as fp:
            fread = fp.read()
        return fread

    def get_word_count(self):
        """Returns the count of words in this file"""
        with open(self.name) as fp:
            fcount = len(fp.read().split())
        return fcount

    def parse(self, delim='\n', mode='r', strip=False):
        """Parses this by the given delimiter and returns the resulting list"""
        with open(self.name, mode) as fp:
            content = fp.read()
        if strip:
            content = content.strip()
        return content.split(delim)

    def print(self):
        """Prints the binary contents of this file"""
        with open(self.name, 'rb') as fp:
            print(fp.read())

    def remove_blank_lines(self):
        """
        Removes blank lines from this file and writes the new
        content to the disk

        """
        content = self.get_content(binary=True)
        while b'\r\n\r\n' in content or b'\n\n' in content:
            print('replacing')
            content = content.replace(b'\r\n\r\n', b'\r\n')
            content = content.replace(b'\n\n', b'\n')

        with open(self.name, 'wb') as fp:
            fp.write(content)

    def size(self):
        """Returns the size of this file"""
        return _os.path.getsize(self.name)

    def mtime(self):
        """Returns the modification time of this file"""
        return _os.stat(self.name).st_mtime

    def switch_lf(self):
        """
        Switches the linefeed type from a Posix machine to
        Windows and vice versa and overwrites this file

        """
        with open(self.name, 'rb') as fp:
            fread = fp.read()
            to_posix = False
            if b'\r' in fread:
                to_posix = True
        with open(self.name, 'wb') as fp:
            if to_posix:
                fwrite = fread.replace(b'\r', b'')
            else:
                fwrite = fread.replace(b'\n', b'\r\n')
            fp.write(fwrite)
        if to_posix:
            print('Converted to lf')
        else:
            print('Converted to crlf')

class FileSizeReport(object):
    """
    A class for generating reports on file systems

    An exmaple of output:

    .\align.py | 587
    .\badquotes.txt | 308
    .\boxes.py | 2027
    .\collections.py | 3391
    .\collections_test.txt | 1363
    ...

    TODO: file IO

    """

    def __init__(self, directory='.'):
        """
        Initializes this report using the given directory and stores
        the result in the string field

        """
        self.directory = directory
        self.report = self.generate()

    def __repr__(self):
        """Prints the string representation of this report"""
        return '\n'.join(['{} | {}'.format(x, y) for x,y in self.report.items()])

    def generate(self):
        """Generates a report of file names and their sizes"""
        report = {}
        Walk = _os.walk(self.directory)

        for root, dirs, files in Walk:
            for file in files:
                filename = _os.path.join(root, file)
                report[filename] = _os.stat(filename).st_size
        return report

    @staticmethod
    def parse(string):
        """Parses the given string and returns the corresponding report"""
        splt = [x.split(' | ') for x in string.strip().split('\n')]
        report = {x: int(y.strip()) for x, y in splt}
        return report

def fix_quotes(filename):
    """Replaces smart quotes with straight ones for the given filename"""
    fp = None
    try:
        fp = open(filename,'rb+')
        fread = fp.read()
        fp.seek(0)
        fread = replace_smart_quotes(fread)
        fp.write(fread)
        fp.truncate() # adds str terminator
        print('Quotes fixed')
    except Exception as e:
        print('Error:', e)
    finally:
        if fp: fp.close()

def _randomize_file(filename: str):
    """Helps randomize the given filename with random bytes"""
    # get file length
    length = _os.path.getsize(filename)
    # get random bytes
    rand = _os.urandom(length)
    print('Randomizing:', filename)
    # open file
    with open(filename, 'wb') as fp:
        # write random bytes
        fp.write(rand)

def randomize(filename_or_directory: str):
    """Recursively randomizes a file, or files in the given directory"""
    if _os.path.isdir(filename_or_directory):
        directory = filename_or_directory
        # otherwise, walk and randomize
        for root, dirs, files in _os.walk(directory):
            for file in files:
                _randomize_file(_os.path.join(root, file))
    else:
        filename = filename_or_directory
        _randomize_file(filename)

def save(text, name='saved-text.txt', append_epoch=True):
    """Saves the given text to the file with sequential numbering"""
    split_ext = _os.path.splitext(name)
    if append_epoch:
        name = '{}-{}{}'.format(split_ext[0], int(time.time()), split_ext[-1])
    else:
        x = 0
        name = _save_helper(split_ext, x)
        while _os.path.exists(name):
            x += 1
            name = _save_helper(split_ext, x)
    with open(name, 'w') as fp:
        fp.write(str(text))
    return name

def _save_helper(split_ext, x):
    """
    Returns a possible filename. Helps `save` with finding a
    valid name for a file

    """
    return '{}-{:03d}{}'.format(split_ext[0], x, split_ext[-1])

def replace_text(name, old, new, recurse=False, ext=''):
    """Replaces `name` with binary string params `old` and `new`"""
    from clay.files.core import _rt_helper
    if recurse:
        sure = eval(input('Replace all "{1}" in "{0}" with "{2}" (True/False)? '.format(name, old, new)))

        if sure:
            fp = None
            for root, dirs, files in _os.walk(name):
                for f in files:
                    try:
                        fp = open(_os.path.join(root, f), 'rb')
                        if old in fp.read() and f.endswith(ext):
                            _rt_helper(_os.path.join(root, f), old, new)
                    except Exception as e:
                        raise e
                    finally:
                        if fp: fp.close()
            print('Done')
        else:
            print('Aborted')

    else:
        _rt_helper(name, old, new)

def _rt_helper(filename, old, new):
    """
    Helps `replace_text` rename a single file
    http://stackoverflow.com/questions/6648493/open-file-for-both-reading-and-writing

    """
    fp = None
    try:
        fp = open(filename, 'rb+')
        fread = fp.read()
        fp.seek(0)
        fp.write(fread.replace(old, new))
        fp.truncate() # add a NULL terminator
        print('replace_text on "{}" complete'.format(filename))
    except Exception as e:
        print('Error:', e)
    finally:
        if fp: fp.close()

if __name__ == '__main__':

    from clay.tests import testif

    testif('File.size raises FileNotFoundError when file not found',
        lambda: File('http://www.google.com/').size(),
        None,
        raises=FileNotFoundError)
    testif('File.size returns type int when file found',
        type(File(__file__).size()),
        int)

    report = FileSizeReport(directory='.')
    print('File size report')
    print(report)
