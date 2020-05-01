
"""
Runtime environment settings

"""

import sys as _sys

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
