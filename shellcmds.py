"""
Shell commands uses Python to control your system
"""

import os
import subprocess
import sys
#import shutil

from pack import LINUX

if LINUX:
    TRASH = r'/home/clayton/Desktop/TRASH'
else:
    TRASH = r'C:\Python35\Lib\site-packages\TRASH'

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

def contains(chars=list(), directory=os.curdir):
    """Find all files containing "chars" using re.findall. Returns list"""
    assert 3 > len(chars) > 0
    from re import findall
    listing = os.listdir(directory)
    results = [x for x in listing for char in chars if findall(chars[0], x) and findall(chars[-1], x)]
    return results

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
# LINUX users
pwd = os.getcwd # def

def explorer(directory=os.curdir):
    """Open File Explorer to the specified directory"""
    os.system('explorer "{}"'.format(directory))
    
def ls(directory=os.curdir, cmd=False):
    """List contents of the current directory. Use 'cmd' style for Command Prompt's 'dir'"""
    if cmd:
        print(subprocess.check_output(['dir', directory], shell=True).decode('utf8', errors='ignore'))
    else:
        return os.listdir(directory)

from os import mkdir # def

from shutil import move as mv # def

def pause():
    """Pause the script"""
    if 'idlelib' in sys.modules:
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

def rm(f, directory=os.curdir):
    """Move a file/folder to the TRASH"""
    from shutil import move
    target = os.path.join(TRASH, f)
    try:
        if os.path.exists(target):
            print('Exists in TRASH, deleting...')
            if os.path.isfile(target):
                os.system('del "%s"' % target)
            else:
                os.system('rmdir /s "%s"' % target)
        move(r'{}\{}'.format(directory, f), TRASH)
        print('"{}" deleted'.format(f))
    except Exception as e:
        print(e)

def roboren(old=None, new=None, directory=os.curdir):
    """Rename all items with old to new using str.replace(old,new)"""
    if old == None:
        old = input('Enter old string: ')
    if new == None:
        new = input('Enter new string: ')
    print('Replacing "{}" with "{}"...'.format(old, new))
    x = 0
    for f in filter(lambda name: old in name, os.listdir(directory)):
        try:
            os.rename(f, f.replace(old, new))
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
        for f in filter(lambda name: criteria.lower() in name.lower(), os.listdir(directory)):
            try:
                move(r'{}\{}'.format(directory, f), TRASH)
                x += 1
            except:
                pass
    print('{} item(s) deleted'.format(x))

def set_title(title=os.path.basename(list(filter(lambda name: not('python' == name), sys.argv))[0]), add=str(), args=False):
    """Customize the window title. Default is through sys.argv.
    You can use additional text to follow and full for additional sys.argv's"""
    command = 'title {}'.format(title)
    if args:
        command += ' ' + ' '.join(list(filter(lambda name: not('python' == name), sys.argv))[1:])
    if add:
        command += ' - {}'.format(add)
    command = command.replace('<', '^<').replace('>', '^>')
    if 'idlelib' in sys.modules or LINUX:
        print('set title -> {}'.format(command[6:]))
    else:
        os.system(command)

def start(program):
    """Start a program"""
    try:
        os.system('start {}'.format(program))
    except Exception as e:
        print("Oops, couln't start:", e)
        
def timeout(seconds, visible=True):
    """Wait for specified time. Optional visibility"""
    if LINUX:
        command = 'ping -c {} www.google.com'.format(seconds * 2)
    else:
        command = 'timeout {}'.format(seconds)
    if not(visible):
        command += ' >nul'
    try:
        os.system(command)
    except:
        print('\nTimeout skipped')

