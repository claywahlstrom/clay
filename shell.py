
"""
shell: commands that can be used to manage your system or retrieve information

"""

import os as _os
import subprocess as _subprocess
import sys as _sys
import time as _time

# import a temporary version of isUnix to allow for constant declarations
from clay import _isUnix, HOME_DIR as _HOME_DIR

FILTERED_ARGS = list(filter(lambda name: not(name in ('python', 'python.exe')), _sys.argv))

FLASK_APP = 'app.py' # common name for Flask web apps

TIMEOUT_CMD = 'sleep ' if _isUnix() else 'timeout '

TRASH = _os.path.join(_HOME_DIR, 'Desktop', 'TRASH')

cd = _os.chdir # def

def clear():
    """Clears the screen"""
    if isIdle():
        print('\n'*40)
    elif _isUnix():
        _os.system('clear')
    else:
        _os.system('cls')

def chext(filepath, ext):
    """Changes file extension of the given file to `ext`"""
    new = '.'.join(_os.path.splitext(filepath)[:-1]+[ext]) # split into chunks and add list to name
    try:
        _os.rename(filepath, new)
        print('Ext changed')
    except Exception as e:
        print('Failed rename:', e)

def copy(src, dst):
    """Copies the source item to destination using shutil.copy"""
    print('Copying "{}" to "{}"...'.format(src, dst), end=' ')
    from shutil import copy as cp
    try:
        cp(src, dst)
        succeed = True
        print()
    except Exception as e:
        print(e)
        succeed = False
    if isIdle():
        if succeed:
            print('Complete')
        else:
            print('Failed')

# for linux users
cp = copy # def

# for nt users
cwd = _os.getcwd # def
# for linux users
pwd = _os.getcwd # def

def filemanager(directory=_os.curdir):
    """Opens the file manager to the specified directory"""
    if _isUnix(): # This should work for most systems
        fm_name = 'xdg-open'
    else:
        fm_name = 'explorer'
    _os.system('{} "{}"'.format(fm_name, directory))

def getDocsFolder():
    """Returns the location of the documents folder for this computer.
    Assumes a similar filesystem naming convention to work."""
    from clay.shell import ssdExists as _ssdExists
    if _ssdExists():
        return r'E:\Docs'
    else:
        return _os.path.join(_os.environ['HOME'], 'Documents')

def isIdle():
    """Returns true if the script is running within IDLE,
       false otherwise"""
    return 'idlelib' in _sys.modules

def isPowershell():
    """Returns true if the script is running within PowerShell,
       false otherwise"""
    return len(_sys.argv[0]) > 0 and (not((':' in _sys.argv[0])) or _sys.argv[0].startswith('.'))

def isUnix():
    """Returns true if the script is running within a Unix
       machine, false otherwise"""
    return any(_sys.platform.startswith(x) for x in ('linux', 'darwin')) # darwin for macOS

class JavaCompiler(object):
    """Class Java can be used to compile Java(tm) source files to bytecode"""
    
    SRC_EXT = '.java'
    
    def __init__(self, classes=None, directory=_os.curdir):
        """Initializes the compiler. Default for classes is all in the given
           directory or expects a list or tuple, otherwise and ValueError is thrown"""
        if classes is not None and (type(classes) != list or type(classes) != tuple):
            raise ValueError('`classes` must be an iterable')
        self.classes = classes
        self.directory = directory

    def set_path(self, directory):
        self.directory = directory
        
    def compile(self, flags='g Xlint:unchecked', exclude=None):
        """Compiles the source files in this directory with the given flags
           (debugging info included by default) and excludes any files
           containing the given string `exclude`"""
        from clay.shell import lsgrep
        if self.classes is None:
            self.classes = (_os.path.splitext(x)[0] for x in lsgrep(JavaCompiler.SRC_EXT, self.directory))
        if exclude is not None and len(exclude) > 0:
            self.classes = [x for x in self.classes if not(exclude in x)]
        if len(flags) > 0:
            opt_str = '-' + ' -'.join(flags.split()) + ' '
        else:
            opt_str = str()
        for src in self.classes:
            jname = src + JavaCompiler.SRC_EXT
            jclass = src + '.class'
            if not(_os.path.exists(jname)):
                print(src, 'doesn\'t exist, skipping...')
                continue
            jstat = _os.stat(jname).st_mtime
            try:
                jcomp = _os.stat(jclass).st_mtime
            except:
                jcomp = 0 # file doesn't exist

            if jstat - jcomp >= 5: # if edited more than five seconds ago
                print('Compiling:', src)
                _os.system('javac ' + opt_str + jname)

def ls(directory=_os.curdir, shell=False):
    """Returns the listing of contents for the given `directory`.
    If `shell` is true, then the MS-DOS style is printed and nothing is returned
    """
    if shell:
        print(_subprocess.check_output(['dir', directory],
                                       shell=True).decode('utf8', errors='ignore'))
    else:
        return _os.listdir(directory)

def lsgrep(regex, directory=_os.curdir, fullpath=True):
    """Finds and returns all files containing `regex` (string or list)
    sing re.findall"""
    listing = _os.listdir(directory)
    if type(regex) == list:
        results = list()
        for x in listing:
            if all(len(findall(char, x)) > 0 for char in regex):
                results.append(x)
    else:
        from re import findall
        results = [x for x in listing if findall(regex, x)]
    results = [_os.path.join(directory, x) if fullpath else x for x in results]
    return results

from os import mkdir # def
md = _os.mkdir # def

from shutil import move as mv # def

def notify(e, seconds=2.25):
    print(e)
    _time.sleep(seconds)

def pause(consoleonly=False):
    """Pauses the console execution"""
    if (isIdle() or isUnix()) and not(consoleonly):
        input('Press enter to continue . . . ')
    elif not(isIdle()):
        _subprocess.call('pause', shell=True)

def ren(src, dst, directory=_os.curdir, recurse=False):
    """Renames src to dst, or with recurse=True...
    Rename all items with old to new using str.replace(old,new)"""
    if recurse:
        print('Replacing all "{}" with "{}"...'.format(src, dst))
        x = 0
        for file in filter(lambda name: src in name, _os.listdir(directory)):
            try:
                _os.rename(file, file.replace(src, dst))
                x += 1
            except:
                print("Couldn't rename", src)
        print('{} item(s) renamed'.format(x))
    else:
        try:
            _os.rename(src, dst)
            print('"{}" renamed to "{}"'.format(src, dst))
        except Exception as e:
            print('Error:', e)

def rm(name_or_criteria, directory=_os.curdir, recurse=False, prompt=True):
    """Moves a file/folder to the TRASH, or with recurse...
    Recursive version rm, Optional prompting"""

    from clay.shell import rm_item

    if not(_os.path.exists(TRASH)):
        _os.mkdir(TRASH)

    if recurse:
        sure = not(prompt)
        if prompt:
            sure = input('Are you sure you want to delete all containing "{}" in "{}"? '.format(criteria, directory))
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
        # reverse any changes if something went wrong
        move(new_path, name)

def rm_from_trash(target):
    """Removes the given target from the `shell` trash"""
    rms = {'win32': ('del', 'rmdir /s'),
           'linux': ('rm', 'rm -r')}

    if _os.path.isfile(target):
        i = 0
    else:
        i = 1

    if _isUnix():
        key = 'linux'
    else:
        key = 'win32'
    _os.system('{} "{}"'.format(rms[key][i], target))

def set_title(title=_os.path.basename(FILTERED_ARGS[0]), add=str(),
              args=False, flask_default_name=True):
    """Sets the title of the current shell instance. Default is the modules name
    You can use your own additional text or use the command-line arguments"""
    name = title
    if name == FLASK_APP:
        add = _os.path.split(_os.path.dirname(_os.path.abspath(FILTERED_ARGS[0])))[-1]
    if args and len(FILTERED_ARGS) > 1:
        name += ' ' + ' '.join(FILTERED_ARGS[1:])
    if add:
        name += ' - {}'.format(add)
    name = name.replace('<', '^<').replace('>', '^>')
    if isIdle() or isUnix():
        print('set title -> {}'.format(name))
    else:
        _os.system('title ' + name)

def ssdExists():
    """Returns true if the solid state drive location 'E:\Docs' exists,
    otherwise false"""
    return _os.path.exists(r'E:\Docs')

def start(program):
    """Starts a given program"""
    try:
        command = str()
        if not(_isUnix()):
            command += 'start '
        _os.system(command + program)
    except Exception as e:
        print("Oops, couldn't start:", e)

def timeout(seconds, hidden=False):
    """Waits for the specified time in seconds"""
    if _isIdle():
        if not(hidden):
            print('Waiting for ' + seconds + '...')
        _time.sleep(seconds)
    else:
        command = TIMEOUT_CMD + str(seconds)
        if hidden:
            command += ' >nul'
        _os.system(command)
