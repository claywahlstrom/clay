
"""
shell: commands that can be used to manage your system or
       retrieve information about it

"""

import inspect as _inspect
import os as _os
import string as _string
import subprocess as _subprocess
import sys as _sys
import time as _time

from clay import _is_unix

FLASK_APP = 'app.py' # a common name for Flask web apps

HOME_DIR = _os.environ['HOME'] if _is_unix() else _os.environ['USERPROFILE']

RUNTIME_ARGS = _sys.argv
if len(RUNTIME_ARGS[0]) == 0:
    RUNTIME_ARGS[0] = 'python.exe'

TIMEOUT_CMD = 'sleep ' if _is_unix() else 'timeout '

TRASH = _os.path.join(HOME_DIR, 'Desktop', 'TRASH')

cd = _os.chdir # alias

def clear():
    """Clears the console window"""
    if is_idle():
        print('\n' * 40)
    elif _is_unix():
        _os.system('clear')
    else:
        _os.system('cls')

def chext(filepath, ext):
    """Changes file extension of the given file to `ext`"""
    new = '.'.join(_os.path.splitext(filepath)[:-1] + [ext]) # split into chunks and add list to name
    try:
        _os.rename(filepath, new)
        print('Ext changed')
    except Exception as e:
        print('Failed rename:', e)

def copy(src, dst):
    """Copies the source item to destination using shutil.copy"""
    print('Copying "{}" to "{}"...'.format(src, dst), end=' ')
    from shutil import copy as cp # avoids recursion
    try:
        cp(src, dst)
        succeed = True
        print()
    except Exception as e:
        print(e)
        succeed = False
    if is_idle():
        if succeed:
            print('Complete')
        else:
            print('Failed')

# for linux users
cp = copy # alias
cwd = _os.getcwd # alias
# for linux users
pwd = _os.getcwd # alias

class FileSizeReport(object):
    """A class for generating reports on file systems
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
        """Initializes this report using the given directory and stores
           the result in the string field"""
        self.directory = directory
        self.generate()
        self.string = '\n'.join(['{} | {}'.format(x, y) for x,y in self.report])

    def __repr__(self):
        """Prints the string representation of this report"""
        return self.string

    def generate(self):
        """Generates a report in the format (filename, filesize)"""
        report = []
        Walk = _os.walk(self.directory)

        for root, dirs, files in Walk:
            for file in files:
                filename = _os.path.join(root, file)
                report.append((filename, _os.stat(filename).st_size))
        self.report = report

    def parse(self):
        """Parses the string field and returns the original report"""
        splt = [x.split(' | ') for x in self.string.strip().split('\n')]
        lst = [(x, int(y.strip())) for x, y in splt]
        return lst

def file_manager(directory=_os.curdir):
    """Opens the system file manager to the specified directory"""
    from clay.shell import is_unix
    if is_unix():
        fm_name = 'xdg-open' # This should work for most systems
    else:
        fm_name = 'explorer'
    _os.system('{} "{}"'.format(fm_name, directory))

def get_disk_drives():
    """Returns a list of drive root paths that are available
       on this machine. Ex. ['C:\\', 'D:\\', ...]"""
    drives = []
    for letter in _string.ascii_uppercase:
        if _os.path.exists(letter + ':\\'):
            drives.append(letter + ':\\')
    return drives

def get_docs_folder():
    """Returns the location of the documents folder for this computer.
       Assumes a Windows-style filesystem to work."""
    from clay.shell import get_disk_drives
    if 'E:\\' in get_disk_drives():
        return r'E:\Docs'
    else:
        return _os.path.join(_os.environ['HOME'], 'Documents')

def is_idle():
    """Returns true if the script is running within IDLE,
       false otherwise"""
    return 'idlelib' in _sys.modules

def is_powershell():
    """Returns true if the script is running within PowerShell,
       false otherwise"""
    return len(_sys.argv[0]) > 0 and (not((':' in _sys.argv[0])) or _sys.argv[0].startswith('.'))

def is_unix():
    """Returns true if the script is running within a Unix machine,
       false otherwise"""
    return any(_sys.platform.startswith(x) for x in ('linux', 'darwin')) # darwin for macOS

class Compiler(object):

    def __init__(self, compiler_name, src_ext, dst_ext, sources=None, directory=_os.curdir):
        """Initializes the compiler. Default for classes is all in the given
           directory or expects a list or tuple, otherwise and ValueError is thrown"""
        if sources is not None and not(type(sources) in (list, tuple)):
            raise ValueError('`sources` must be an iterable')
        self.compiler_name = compiler_name
        self.src_ext = src_ext
        self.dst_ext = dst_ext
        self.sources = sources
        self.directory = directory
        self.flags = []

    def set_path(self, directory):
        """Sets the path of this compiler to the given directory"""
        self.directory = directory

    def add_flag(self, flag):
        self.flags.append(flag)

    def clear_flags(self):
        self.flags.clear()

    def compile(self, exclude=None, recurse=True, references=None, verbose=False):
        """Compiles the source files in this directory with this compiler's
           flags. Keyword parameters are as follows:
               exclude = None or list of strings to exclude
               recurse = boolean to indicate whether all files in this
                         compiler's path should be compiled
               references = None or list of refernces for C# sources
               verbose = boolean to indicate whether the system command
                         should be printed for each file

        """
        from clay.shell import lsgrep
        _os.chdir(self.directory)
        sources = self.sources
        if sources is None:
            sources = [_os.path.splitext(x)[0] for x in lsgrep(self.src_ext, self.directory, recurse=True)]
        if exclude is not None and len(exclude) > 0:
            sources = list(filter(lambda x: all(not(y in x) for y in exclude), sources))
        if len(self.flags) > 0:
            opt_str = '-' + ' -'.join(self.flags)
        else:
            opt_str = ''
        statechanged = False
        for src in sources:
            src_name = src + self.src_ext
            dst_name = src + self.dst_ext
            if not(_os.path.exists(src_name)):
                print(src, 'doesn\'t exist, skipping...')
                continue
            src_mtime = _os.stat(src_name).st_mtime
            if _os.path.exists(dst_name):
                dst_mtime = _os.stat(dst_name).st_mtime
            else:
                dst_mtime = 0 # file doesn't exist

            if src_mtime - dst_mtime >= 5: # if edited more than five seconds ago
                print('Compiling ({}):'.format(self.compiler_name), src)
                cmd = self.compiler_name
                if self.compiler_name == 'csc': # C# specific handling
                    if references is not None:
                        cmd += ' /r:' + ','.join(references)
                    cmd += ' /out:{} '.format(dst_name)
                cmd += '{} "{}"'.format(opt_str, src_name)
                if verbose:
                    print('cmd:', cmd)
                _os.system(cmd)
                statechanged = True
        if not(statechanged):
            print('Nothing new to compile in "{}" when recurse={}'.format(self.directory, recurse))

class CSharpCompiler(Compiler):

    def __init__(self, sources=None, directory=_os.curdir):
        super(CSharpCompiler, self).__init__('csc', '.cs', '.exe', sources, directory)
        self.add_flag('nologo')

class JavaCompiler(Compiler):
    """Class JavaCompiler can be used to compile Java(tm) source
       files to bytecode"""

    def __init__(self, sources=None, directory=_os.curdir):
        super(JavaCompiler, self).__init__('javac', '.java', '.class', sources, directory)
        self.add_flag('g')
        self.add_flag('Xlint:unchecked')

def ls(directory=_os.curdir, shell=False):
    """Returns the listing of contents for the given `directory`.
    If `shell` is true, then the MS-DOS style is printed and nothing is returned
    """
    if shell:
        print(_subprocess.check_output(['dir', directory],
                                       shell=True).decode('utf8', errors='ignore'))
    else:
        return _os.listdir(directory)

def lsgrep(regex, directory=_os.curdir, recurse=False):
    """Finds and returns all files containing `regex` (string or list) using re.findall"""
    import re
    if type(regex) == str:
        regex = [regex]
    results = []
    for root, dirs, files in _os.walk(directory):
        for x in files:
            if all(len(re.findall(char, x)) > 0 for char in regex):
                results.append(_os.path.join(root, x))
        if not(recurse):
            break
    return results

from os import mkdir # def
md = _os.mkdir # alias

from shutil import move as mv # alias

def notify(message, seconds=2.25):
    print(message)
    _time.sleep(seconds)

def pause(shell_only=False):
    """Pauses the console execution and prompts the user to continue"""
    if shell_only and is_idle():
        return
    print()
    input('Press enter to continue . . . ')

def ren(src, dst, directory=_os.curdir, recurse=False):
    """Renames src to dst. Renames all items in the current
       directory if recurse is True using str.replace(src, dst)"""

    if recurse:
        print('Replacing all "{}" with "{}"...'.format(src, dst))
        x = 0
        for file in filter(lambda name: src in name, _os.listdir(directory)):
            try:
                _os.rename(file, file.replace(src, dst))
                x += 1
            except:
                print("Couldn't rename", src)
        print('Renamed {} item(s)'.format(x))
    else:
        try:
            _os.rename(src, dst)
            print('Renamed "{}" to "{}"'.format(src, dst))
        except Exception as e:
            print('Error:', e)

def rm(name_or_criteria, directory=_os.curdir, recurse=False, prompt=True):
    """Moves a file/folder to the TRASH. Recursive version rm if recurse
       is True with optional prompting"""

    from clay.shell import rm_item

    if not(_os.path.exists(TRASH)):
        _os.mkdir(TRASH)

    if recurse:
        sure = not(prompt)
        if prompt:
            sure = input('Are you sure you want to delete all ' + \
                         'containing "{}" in "{}"? '.format(criteria, directory))
        x = 0
        if sure.lower() in ('1', 'yes'):
            criteria = name_or_criteria
            print('Deleting all w/ "{}"...'.format(criteria))
            for name in filter(lambda name: criteria.lower() in name.lower(),
                               _os.listdir(directory)):
                rm_item(directory, name)
                x += 1
        print('{} item(s) deleted'.format(x))
    else:
        name = name_or_criteria
        rm_item(directory, name)

def rm_item(directory, name):
    """Moves an item from the given directory with its name including its
       path neutral version of its origin. Helps `rm` accomplish its task"""

    DEBUG = False

    from shutil import move
    from clay.shell import rm_from_trash

    try:
        target = _os.path.join(directory, name)
        src_dir = _os.path.dirname(_os.path.abspath(name))
        dir_info = src_dir.lower().replace('\\', '.').replace(':', '.')
        new_name = '.'.join((dir_info, name))
        new_path = _os.path.join(directory, new_name)
        dst_path = _os.path.join(TRASH, new_name)
        if DEBUG:
            print('name', name)
            print('dir_info', dir_info)
            print('new_name', new_name)
            print('new_path', new_path)
            print('dst_path', dst_path)
        move(target, new_name)
        if _os.path.exists(dst_path):
            if DEBUG:
                print(name, 'exists in TRASH, deleting...')
            print('removing', dst_path)
            rm_from_trash(dst_path)
        move(new_path, TRASH)
        print('"{}" deleted'.format(target))
    except Exception as e:
        print(e)
        # rollback removal if something went wrong
        move(new_path, name)

def rm_from_trash(target):
    """Removes the given target from the `shell` trash"""
    rms = {'win32': ('del', 'rmdir /s'),
           'linux': ('rm', 'rm -r')}

    if _os.path.isfile(target):
        i = 0
    else:
        i = 1

    if is_unix():
        key = 'linux'
    else:
        key = 'win32'
    _os.system('{} "{}"'.format(rms[key][i], target))

def set_title(title=_os.path.basename(RUNTIME_ARGS[0]), add='', args=False,
              flask_default_name=True):
    """Sets the title of the current shell instance. Default is
       the modules name. You can use your own additional text or
       use the command-line arguments"""
    if title == FLASK_APP:
        add = _os.path.split(_os.path.dirname(_os.path.abspath(RUNTIME_ARGS[0])))[-1]
    if args:
        if len(RUNTIME_ARGS) > 1:
            name += ' ' + ' '.join(RUNTIME_ARGS[1:])
    if len(add) > 0:
        title += ' - '  + add
    if not(is_unix()):
        title = title.replace('<', '^<').replace('>', '^>')
    if is_idle():
        print('title -> ' + title)
    elif is_unix():
        _sys.stdout.write('\x1b]2;' + title + '\x07')
        _sys.stdout.flush()
    else: # is windows
        _os.system('title ' + title)

def start(program):
    """Starts a given program"""
    try:
        command = ''
        if not(is_unix()):
            command += 'start '
        _os.system(command + program)
    except Exception as e:
        print('Oops, could not start:', e)

def timeout(seconds, hidden=False):
    """Waits for the specified time in seconds"""
    if seconds < 0 or type(seconds) != int:
        raise ValueError('seconds must be >= and type int')
    if is_idle() or seconds > 99999:
        if not(hidden):
            print('Waiting for', seconds, 'seconds...', end='')
        _time.sleep(seconds)
        if not(hidden):
            print()
    else:
        command = TIMEOUT_CMD + str(seconds)
        if hidden:
            command += ' >nul'
        if is_unix():
            print('Waiting for', seconds, 'seconds...', end='', flush=True)
        _os.system(command)
        if is_unix():
            print()

if __name__ == '__main__':
    jc = JavaCompiler(directory=r'C:\Users\Clayton\Google Drive\UW Remote Work\Java Remote\gravity')
    jc.compile(exclude=['-', 'unused'])

    # used to test if pause runs correctly
    # is_unix = lambda: True
    # is_idle = lambda: True
    pause()
    pause(shell_only=True)
