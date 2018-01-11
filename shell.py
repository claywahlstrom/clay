"""
Shell uses shell-like commands in Python to manage your system

"""

import os as _os
import subprocess as _subprocess
import sys as _sys
import time as _time

from clay import isUnix as _isUnix, HOME_DIR as _HOME_DIR

if _isUnix():
    TIMEOUT_CMD = 'sleep '
else:
    TIMEOUT_CMD = 'timeout '

TRASH = _os.path.join(_HOME_DIR, 'Desktop', 'TRASH')

cd = _os.chdir # def

def clear():
    """Clears the screen"""
    if 'idlelib' in _sys.modules:
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
    print('Copying "{}" to "{}"...'.format(src, dst))
    from shutil import copy as cp
    try:
        cp(src, dst)
        succeed = True
    except Exception as e:
        print(e)
        succeed = False
    if 'idlelib' in _sys.modules:
        if succeed:
            print('Item copied')
        else:
            print('Copy failed')

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
    from clay.shell import ssdExists as _ssdExists
    if _ssdExists():
        return r'E:\Docs'
    else:
        return r'C:\Users\Clayton\Documents'

def ls(directory=_os.curdir, shell=False):
    """Returns the listing of contents for the given `directory`.
    If `shell` is true, then the MS-DOS style is printed and noting returned
    """
    if shell:
        print(_subprocess.check_output(['dir', directory], shell=True).decode('utf8', errors='ignore'))
    else:
        return _os.listdir(directory)

def lsgrep(regex, directory=_os.curdir):
    """Finds and returns all files containing `regex` (string or list)
    sing re.findall"""
    listing = _os.listdir(directory)
    if type(regex) == list:
        results = list()
        for x in listing:
            if eval(' and '.join(['findall("{}", "{}")'.format(char, x) for char in regex])):
                results.append(x)
    else:
        from re import findall
        results = [x for x in listing if findall(regex, x)]
    return results

from os import mkdir # def
md = _os.mkdir # def

from shutil import move as mv # def

def notify(e, seconds=2.25):
    print(e)
    _time.sleep(seconds)

def pause(consoleonly=False):
    """Pauses the console execution"""
    if ('idlelib' in _sys.modules or _isUnix()) and not(consoleonly):
        input('Press enter to continue . . . ')
    elif not('idlelib' in _sys.modules):
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
            for name in filter(lambda name: criteria.lower() in name.lower(), _os.listdir(directory)):
                rm_item(directory, name)
                x += 1
        print('{} item(s) deleted'.format(x))
    else:
        name = name_or_criteria
        rm_item(directory, name)
        
def rm_item(directory, name):
    """Moves an item from the given directory with its name including its
    path neutral version of its origin. Helps `rm` accomplish its task"""
    from shutil import move
    from clay.shell import rm_from_trash
    print('name', name)
    try:
        target = _os.path.join(directory, name)
        src_dir = _os.path.dirname(_os.path.abspath(name))
        dir_info = src_dir.lower().replace('\\', '.').replace(':', '.')
        new_name = '.'.join((dir_info, name))
        new_path = _os.path.join(directory, new_name)
        dst_path = _os.path.join(TRASH, new_name)
        # print('dir_info', dir_info)
        # print('new_name', new_name)
        # print('new_path', new_path)
        # print('dst_path', dst_path)
        move(target, new_name)
        if _os.path.exists(dst_path):
            # print(name, 'exists in TRASH, deleting...')
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

def set_title(title=_os.path.basename(list(filter(lambda name: not('python' == name), _sys.argv))[0]), add=str(), args=False):
    """Customizes the window title. Default is the modules name
    You can use your own additional text or use the command-line arguments"""
    name = title
    if args:
        name += ' ' + ' '.join(list(filter(lambda name: not('python' == name), _sys.argv))[1:])
    if add:
        name += ' - {}'.format(add)
    name = name.replace('<', '^<').replace('>', '^>')
    if 'idlelib' in _sys.modules or _isUnix():
        print('set title -> {}'.format(name))
    else:
        _os.system('title ' + name)

def ssdExists():
    return _os.path.exists(r'E:\Docs')

def start(program):
    """Starts a given program"""
    try:
        if _isUnix():
            _os.system(program)
        else:
            _os.system('start {}'.format(program))
    except Exception as e:
        print("Oops, couln't start:", e)

def timeout(seconds, hidden=False):
    """Waits for the specified time in seconds"""
    if 'idlelib' in _sys.modules:
        if not(hidden):
            print('Waiting for ' + seconds + '...')
        _time.sleep(seconds)
    else:
        command = TIMEOUT_CMD + str(seconds)
        if hidden:
            command += ' >nul'
        try:
            _os.system(command)
        except:
            print('\nTimeout skipped')
