"""
Shell commands uses Python to manage your system
"""

import os
import subprocess
import sys

from pack import LINUX

if LINUX:
    TRASH = r'/home/clayton/Desktop/TRASH'
    TIMEOUT_CMD = 'sleep '
else:
    TRASH = r'C:\Python35\Lib\site-packages\TRASH'
    TIMEOUT_CMD = 'timeout '

if not(os.path.exists(TRASH)):
    os.mkdir(TRASH)
    print('Trash made')

cd = os.chdir # def

def cls():
    """Clear the screen"""
    if 'idlelib' in sys.modules:
        print('\n'*40)
    elif LINUX:
        os.system('clear')
    else:
        os.system('cls')

def chext(filepath, ext):
    """Change file extension"""
    new = '.'.join(os.path.splitext(filepath)[0]+[ext]) # split into chunks and add list to name
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
    if LINUX: # This should work...
        os.system('xdg-open "{}"'.format(directory))
    else:
        os.system('explorer "{}"'.format(directory))

explorer = filemanager # laziness to change incompatible programs 

def ls(directory=os.curdir, shell=False):
    """List contents of the current directory. Use 'cmd' style for Command Prompt's 'dir'"""
    if shell:
        print(subprocess.check_output(['dir', directory], shell=True).decode('utf8', errors='ignore'))
    else:
        return os.listdir(directory)

def lsgrep(chars, directory=os.curdir):
    """Find all files containing "chars" using re.findall. Returns list"""
    from re import findall
    listing = os.listdir(directory)
    if type(chars) == list:
        results = list()
        for x in listing:
            if eval(' and '.join(['findall("{}", "{}")'.format(char, x) for char in chars])):
                results.append(x)
    else:
        results = [x for x in listing if findall(chars, x)]
    return results

from os import mkdir # def

from shutil import move as mv # def

def pause():
    """Pause the script"""
    if 'idlelib' in sys.modules or LINUX:
        input('Press enter to continue . . . ')
    else:
        subprocess.call('pause', shell=True)

def ren(src, dst):
    """Rename src to dst"""
    try:
        os.rename(src, dst)
        print('"{}" renamed to "{}"'.format(src, dst))
    except Exception as e:
        print('Error:', e)

def rm(file, directory=os.curdir):
    """Move a file/folder to the TRASH"""
    from shutil import move

    from pack.shellcmds import rm_from_trash

    try:
        target = os.path.join(TRASH, file)
        if os.path.exists(target):
            print('Exists in TRASH, deleting...')
            rm_from_trash(target)
        move(os.path.join(directory, file), TRASH)
        print('"{}" deleted'.format(file))
    except Exception as e:
        print(e)

def rm_from_trash(target):
    win32_rm = ['del', 'rmdir /s']
    linux_rm = ['rm', 'rm -r']

    i = 0
    if not(os.path.isfile(target)):
        i = 1

    if LINUX:
        os.system('{} "{}"'.format(linux_rm[i], target))
    else:
        os.system('{} "{}"'.format(win32_rm[i], target))

def roboren(old=None, new=None, directory=os.curdir):
    """Rename all items with old to new using str.replace(old,new)"""
    if old == None:
        old = input('Enter old string: ')
    if new == None:
        new = input('Enter new string: ')
    print('Replacing "{}" with "{}"...'.format(old, new))
    x = 0
    for file in filter(lambda name: old in name, os.listdir(directory)):
        try:
            os.rename(file, file.replace(old, new))
            x += 1
        except:
            print("Couldn't rename")
    print('{} item(s) renamed'.format(x))

def roborm(criteria, prompt=True, directory=os.curdir):
    """Recursive version of pack.ShellCmds.rm, Optional prompting"""
    from shutil import move
    if prompt:
        sure = input('Are you sure you want to delete all containing "{}" in "{}"? '.format(criteria, directory))
    else:
        sure = True
    x = 0
    if sure:
        print('Deleting all w/ "{}"...'.format(criteria))
        for file in filter(lambda name: criteria.lower() in name.lower(), os.listdir(directory)):
            try:
                move(os.path.join(directory, file), TRASH)
                x += 1
            except:
                pass
    print('{} item(s) deleted'.format(x))

def set_title(title=os.path.basename(list(filter(lambda name: not('python' == name), sys.argv))[0]), add=str(), args=False):
    """Customize the window title. Default is through sys.argv.
    You can use additional text to follow and full for additional sys.argv's"""
    name = title
    if args:
        name += ' ' + ' '.join(list(filter(lambda name: not('python' == name), sys.argv))[1:])
    if add:
        name += ' - {}'.format(add)
    name = name.replace('<', '^<').replace('>', '^>')
    if 'idlelib' in sys.modules or LINUX:
        print('set title -> {}'.format(name[6:]))
    else:
        os.system('title ' + name)

def start(program):
    """Start a program"""
    try:
        if LINUX:
            os.system(program)
        else:
            os.system('start {}'.format(program))
    except Exception as e:
        print("Oops, couln't start:", e)

def timeout(seconds, hide=False):
    """Wait for specified time. Optional visibility"""
    command = TIMEOUT_CMD + str(seconds)
    if hide:
        command += ' >nul'
    try:
        os.system(command)
    except:
        print('\nTimeout skipped')

