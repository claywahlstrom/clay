"""
Shell commands uses Python to manage your system
"""

import os
import subprocess
import sys

from clay import UNIX, HOME_DIR


if UNIX:
    TIMEOUT_CMD = 'sleep '
else:
    TIMEOUT_CMD = 'timeout '

TRASH = os.path.join(HOME_DIR, 'Desktop', 'TRASH')
if not(os.path.exists(TRASH)):
    os.mkdir(TRASH)
    print('Trash made')

cd = os.chdir # def

def cls():
    """Clear the screen"""
    if 'idlelib' in sys.modules:
        print('\n'*40)
    elif UNIX:
        os.system('clear')
    else:
        os.system('cls')

def chext(filepath, ext):
    """Change file extension"""
    new = '.'.join(os.path.splitext(filepath)[:-1]+[ext]) # split into chunks and add list to name
    try:
        os.rename(filepath, new)
        print('Ext changed')
    except:
        print('Failed rename')

def copy(src, dst):
    """Copy source item to destination using shutil.copy"""
    print('Copying "{}" to "{}"...'.format(src, dst))
    from shutil import copy as cp
    try:
        cp(src, dst)
        succeed = True
    except Exception as e:
        print(e)
        succeed = False
    if 'idlelib' in sys.modules:
        if succeed:
            print('Item copied')
        else:
            print('Copy failed')

# nt users
cwd = os.getcwd # def
# linux users
pwd = os.getcwd # def

def filemanager(directory=os.curdir):
    """Open the file manager to the specified directory"""
    if UNIX: # This should work...
        os.system('xdg-open "{}"'.format(directory))
    else:
        os.system('explorer "{}"'.format(directory))

def ls(directory=os.curdir, shell=False):
    """List contents of the current directory. Use 'cmd' style for Command Prompt's 'dir'"""
    if shell:
        print(subprocess.check_output(['dir', directory], shell=True).decode('utf8', errors='ignore'))
    else:
        return os.listdir(directory)

def lsgrep(regex, directory=os.curdir):
    """Find all files containing "regex" using re.findall. Returns list"""
    from re import findall
    listing = os.listdir(directory)
    if type(regex) == list:
        results = list()
        for x in listing:
            if eval(' and '.join(['findall("{}", "{}")'.format(char, x) for char in regex])):
                results.append(x)
    else:
        results = [x for x in listing if findall(regex, x)]
    return results

from os import mkdir # def

from shutil import move as mv # def

def pause(consoleonly=False):
    """Pause the script"""
    if ('idlelib' in sys.modules or UNIX) and not(consoleonly):
        input('Press enter to continue . . . ')
    elif not('idlelib' in sys.modules):
        subprocess.call('pause', shell=True)

def ren(src, dst, directory=os.curdir, recurse=False):
    """Rename src to dst, or with recurse=True...
    Rename all items with old to new using str.replace(old,new)"""
    if recurse:
        print('Replacing all "{}" with "{}"...'.format(src, dst))
        x = 0
        for file in filter(lambda name: src in name, os.listdir(directory)):
            try:
                os.rename(file, file.replace(src, dst))
                x += 1
            except:
                print("Couldn't rename", src)
        print('{} item(s) renamed'.format(x))
    else:
        try:
            os.rename(src, dst)
            print('"{}" renamed to "{}"'.format(src, dst))
        except Exception as e:
            print('Error:', e)

def rm(name_or_criteria, directory=os.curdir, recurse=False, prompt=True):
    """Move a file/folder to the TRASH, or with recurse...
    Recursive version rm, Optional prompting"""
    from shutil import move

    from clay.shellcmds import rm_from_trash

    if recurse:
        if prompt:
            sure = input('Are you sure you want to delete all containing "{}" in "{}"? '.format(criteria, directory))
        else:
            sure = True
        x = 0
        if sure:
            criteria = name_or_criteria
            print('Deleting all w/ "{}"...'.format(criteria))
            for name in filter(lambda name: criteria.lower() in name.lower(), os.listdir(directory)):
                try:
                    target = os.path.join(TRASH, name)
                    if os.path.exists(target):
                        print('Exists in TRASH, deleting...')
                        rm_from_trash(target)
                    move(os.path.join(directory, name), TRASH)
                    x += 1
                except:
                    pass
        print('{} item(s) deleted'.format(x))
    else:
        name = name_or_criteria
        try:
            target = os.path.join(TRASH, name)
            if os.path.exists(target):
                print('Exists in TRASH, deleting...')
                rm_from_trash(target)
            move(os.path.join(directory, name), TRASH)
            print('"{}" deleted'.format(name))
        except Exception as e:
            print(e)

def rm_from_trash(target):
    win32_rm = ['del', 'rmdir /s']
    linux_rm = ['rm', 'rm -r']

    i = 0
    if not(os.path.isfile(target)):
        i = 1

    if UNIX:
        os.system('{} "{}"'.format(linux_rm[i], target))
    else:
        os.system('{} "{}"'.format(win32_rm[i], target))

def set_title(title=os.path.basename(list(filter(lambda name: not('python' == name), sys.argv))[0]), add=str(), args=False):
    """Customize the window title. Default is through sys.argv.
    You can use additional text to follow and full for additional sys.argv's"""
    name = title
    if args:
        name += ' ' + ' '.join(list(filter(lambda name: not('python' == name), sys.argv))[1:])
    if add:
        name += ' - {}'.format(add)
    name = name.replace('<', '^<').replace('>', '^>')
    if 'idlelib' in sys.modules or UNIX:
        print('set title -> {}'.format(name))
    else:
        os.system('title ' + name)

def start(program):
    """Start a program"""
    try:
        if UNIX:
            os.system(program)
        else:
            os.system('start {}'.format(program))
    except Exception as e:
        print("Oops, couln't start:", e)

def timeout(seconds, hide=False):
    """Wait for the specified time. Optional visibility"""
    command = TIMEOUT_CMD + str(seconds)
    if hide:
        command += ' >nul'
    try:
        os.system(command)
    except:
        print('\nTimeout skipped')

