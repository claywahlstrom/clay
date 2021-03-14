
"""
Runtime environment settings

"""

import os as _os
import sys as _sys

def is_idle():
    """Returns True if the script is running within IDLE, False otherwise"""
    return 'idlelib' in _sys.modules

def is_powershell():
    """Returns True if the script is running within PowerShell, False otherwise"""
    # per mklement0 via https://stackoverflow.com/a/55598796/5645103
    return is_win32() and len(_os.getenv('PSModulePath', '').split(_os.pathsep)) >= 3

def is_launcher():
    """
    Returns True if the script is running within the Python launcher (python.exe),
    False otherwise

    """
    return not is_idle() and (_sys.argv[0] == 'python.exe' or not _sys.argv[0].startswith('.'))

def is_posix():
    """
    Returns True if the script is running within a Posix machine,
    False otherwise

    """
    return any(_sys.platform.startswith(x) for x in ('linux', 'darwin')) # darwin for macOS

def is_win32():
    """Returns True if the script is running within a win32 machine, False otherwise"""
    return _sys.platform == 'win32'
