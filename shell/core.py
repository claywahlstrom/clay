
"""
shell: commands that can be used to manage your system or
       retrieve information about it

"""

import os as _os
import string as _string
import subprocess as _subprocess
import sys as _sys
import time as _time

def is_dev_env():
    """Returns true if the script is running within the
       developer's environment, false otherwise"""
    return _os.path.exists(r'E:\Docs')

def is_idle():
    """Returns true if the script is running within IDLE,
       false otherwise"""
    return 'idlelib' in _sys.modules

def is_powershell():
    """Returns true if the script is running within PowerShell,
       false otherwise"""
    return not is_idle() and not is_launcher()

def is_launcher():
    """Returns true if the script is running within the Python launcher (python.exe),
       false otherwise"""
    return not is_idle() and (_sys.argv[0] == 'python.exe' or not _sys.argv[0].startswith('.'))

def is_unix():
    """Returns true if the script is running within a Unix machine,
       false otherwise"""
    return any(_sys.platform.startswith(x) for x in ('linux', 'darwin')) # darwin for macOS

FLASK_APP = 'app.py' # a common name for Flask web apps

HOME_DIR = _os.environ['HOME'] if is_unix() else _os.environ['USERPROFILE']

RUNTIME_ARGS = _sys.argv
if len(RUNTIME_ARGS[0]) == 0:
    RUNTIME_ARGS[0] = 'python.exe'

TIMEOUT_CMD = 'sleep ' if is_unix() else 'timeout '

TRASH = _os.path.join(HOME_DIR, 'Desktop', 'clay-trash')

cd = _os.chdir # alias

def clear():
    """Clears the console window"""
    if is_idle():
        print('\n' * 40)
    elif is_unix():
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

def file_manager(directory=_os.curdir):
    """Opens the system file manager to the specified directory"""
    from clay.shell.core import is_unix
    if is_unix():
        fm_name = 'xdg-open' # This should work for most systems
    else:
        fm_name = 'explorer'
    _os.system('{} "{}"'.format(fm_name, directory))

def get_disk_drives():
    """Returns a list of drive root paths that are available
       on this machine.

       Ex. ['CSSS-9928', 'sda', ...] or ['C:\\', 'D:\\', ...]

    """
    drives = []
    if is_unix():
        for folder in _os.listdir('/dev'):
            if folder.startswith('sd'):
                drives.append(folder)
        user_media = _os.path.join('/media/', _os.environ['USER'])
        if _os.path.exists(user_media):
            drives += _os.listdir(user_media)
    else:
        for letter in _string.ascii_uppercase:
            if _os.path.exists(letter + ':\\'):
                drives.append(letter + ':\\')
    return sorted(drives)

def get_docs_folder():
    """Returns the location of the documents folder for this computer."""
    from clay.shell.core import get_disk_drives
    if 'E:\\' in get_disk_drives():
        return r'E:\Docs'
    else:
        return _os.path.join(HOME_DIR, 'Documents')

class Compiler(object):

    def __init__(self, compiler_name, src_ext, dst_ext, sources=None, directory=_os.curdir):
        """Initializes the compiler. Default for classes is all in the given
           directory or expects a list or tuple, otherwise and ValueError is thrown"""
        if sources is not None and type(sources) not in (list, tuple):
            raise TypeError('sources must be an iterable')
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
        from clay.shell.core import lsgrep
        _os.chdir(self.directory)
        sources = self.sources
        if sources is None:
            sources = [_os.path.splitext(x)[0] for x in lsgrep(self.src_ext, self.directory, recurse=recurse)]
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

def locate_script():
    """Locates and changes to the current script\'s directory"""
    dir_name = _os.path.dirname(RUNTIME_ARGS[0])
    if dir_name:
        _os.chdir(dir_name)

ls = _os.listdir # alias

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

def lsshell(directory=_os.curdir):
    """Prints the long listing format of the given directory"""
    if is_unix():
        command = 'ls -al'
    else:
        command = 'dir'
    print(_subprocess.check_output([command, directory],
                                    shell=True).decode('utf8', errors='ignore'))

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

def ren(src, dst):
    """Renames src to dst and prints the status of the operation"""
    try:
        _os.rename(src, dst)
        print('Renamed "{}" to "{}"'.format(src, dst))
    except Exception as e:
        print('Error:', e)

def ren_all(old, new, directory=_os.curdir):
    """Renames all items containing old string with the new string"""
    print('Renaming all files containing "{}" with "{}"...'.format(old, new))
    x = 0
    for file in filter(lambda name: old in name, _os.listdir(directory)):
        try:
            print(' ' * 4, end='')
            file = _os.path.join(directory, file)
            ren(file, file.replace(old, new))
            x += 1
        except:
            print("Couldn't rename", old)
    print('Renamed {} item(s)'.format(x))

def rm_all(criteria, directory=_os.curdir, prompt=True):
    """Moves all files of the given criteria to to the trash"""
    if prompt:
        sure = input('Are you sure you want to delete all files' + \
                     'containing "{}" in "{}"? '.format(criteria, directory))
    else:
        sure = 'Yes'

    x = 0
    if sure.lower() in ('1', 'yes'):
        print('Deleting all w/ "{}"...'.format(criteria))
        for name in filter(lambda name: criteria.lower() in name.lower(),
                           _os.listdir(directory)):
            rm(_os.path.join(directory, name))
            x += 1
    print('Deleted {} item(s)'.format(x))

def rm_target(target):
    """Removes the given target from the file system"""
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

def rm(target):
    """Moves an item from the given target to the `shell` trash"""

    target = _os.path.abspath(target)
    if not _os.path.exists(target):
        raise FileNotFoundError(target)

    from shutil import move
    import uuid

    MAX_FILE_NAME_LENGTH = 230

    if not _os.path.exists(TRASH):
        _os.mkdir(TRASH)

    src_dir = _os.path.dirname(target)
    dir_info = src_dir.lower().replace('\\', '.').replace(':', '.') # make path safe

    base_name = _os.path.basename(target)
    item_name, item_ext = _os.path.splitext(base_name)

    new_name = '{} {} ({}){}'.format(str(uuid.uuid4()), item_name, dir_info, item_ext)
    # prevent file name overflow errors by shrinking the dir name
    while len(new_name) > MAX_FILE_NAME_LENGTH:
        dir_info = dir_info[len(new_name) - MAX_FILE_NAME_LENGTH:].strip('.')
        new_name = '{} {} ({}){}'.format(str(uuid.uuid4()), item_name, dir_info, item_ext)

    dst_path = _os.path.join(TRASH, new_name)
    move(target, dst_path) # move the item to the trash
    print('Deleted "{}"'.format(target))

def set_title(title=_os.path.basename(RUNTIME_ARGS[0]), add='', args=False,
              flask_default_name=True):
    """Sets the title of the current shell instance. Default is
       the modules name. You can use your own additional text or
       use the command-line arguments"""
    if title == FLASK_APP:
        add = _os.path.split(_os.path.dirname(_os.path.abspath(RUNTIME_ARGS[0])))[-1]
    if args and len(RUNTIME_ARGS) > 1:
        title += ' ' + ' '.join(RUNTIME_ARGS[1:])
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
    if type(seconds) != int:
        raise TypeError('seconds must be of type int')
    if seconds < 0:
        raise ValueError('seconds must be >= 0')

    if is_idle() or seconds > 99999:
        if not(hidden):
            print('Waiting for', seconds, 'seconds...', end='')
        _time.sleep(seconds)
        if not(hidden):
            print()
    else:
        command = TIMEOUT_CMD + str(seconds)
        if hidden and not is_unix():
            command += ' >nul'
        if not hidden and is_unix():
            print('Waiting for', seconds, 'seconds...', end='', flush=True)
        _os.system(command)
        if not hidden and is_unix():
            print()

if __name__ == '__main__':
    if is_dev_env():
        # only test on developer's machine due to paths
        jc = JavaCompiler(directory=r'E:\Docs\Clay\Tech\Software\java\gravity')
        jc.compile(exclude=['-', 'unused'])

    # used to test if pause runs correctly
    # is_unix = lambda: True
    # is_idle = lambda: True
    pause()
    pause(shell_only=True)
