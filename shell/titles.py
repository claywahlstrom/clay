
"""
titles: Module for inspecting window titles on Windows

"""

import re as _re
import time as _time
import ctypes as _ctypes

from clay.env import is_posix as _is_posix

if _is_posix():
    raise NotImplementedError('titles can only be used on Windows')

_EnumWindows = _ctypes.windll.user32.EnumWindows
_EnumWindowsProc = _ctypes.WINFUNCTYPE(_ctypes.c_bool, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))
_GetWindowTextW = _ctypes.windll.user32.GetWindowTextW
_GetWindowTextLengthW = _ctypes.windll.user32.GetWindowTextLengthW
_IsWindowVisible = _ctypes.windll.user32.IsWindowVisible

def _foreach_window(hwnd, lParam):
    """Callback func for the EnumWindowsProc"""
    if _IsWindowVisible(hwnd):
        length = _GetWindowTextLengthW(hwnd)
        buff = _ctypes.create_unicode_buffer(length + 1)
        _GetWindowTextW(hwnd, buff, length + 1)
        titles.append(buff.value)
    return True

def get_titles():
    """Returns a list of active window titles"""
    global titles
    titles = []
    _EnumWindows(_EnumWindowsProc(_foreach_window), 0)
    while '' in titles: # remove blank entries
        titles.remove('')
    return titles

class WindowHandler(object):
    """Class WindowHandler can be used to find Window titles by their name"""

    def __init__(self, query, regex=False):
        """
        Initializes a new WindowHandler with the given query and whether
        the query is regex or not

        """
        self.query = query
        self.regex = regex
        self.__names = ()

    def fetch_names(self):
        """Returns a list of all of the window handle names"""
        titles = get_titles()
        if self.regex:
            names = tuple(query for title in titles for query in _re.findall(self.query, title))
        else:
            names = tuple(title for title in titles if self.query in title)
        self.__names = names

    def wait(self):
        """Waits until a window with this query is active, retries every 1.0 second interval"""
        self.fetch_names()
        if not self.is_active:
            print('Waiting for a new window')
            while not self.is_active:
                _time.sleep(1.0)
                self.fetch_names()

    @property
    def is_active(self):
        """Returns True if this window handle query is active, False otherwise"""
        return any(self.names)

    @property
    def names(self):
        """Returns the names found for this window handle's query"""
        return self.__names

    @property
    def first(self):
        """Returns the first window handle name"""
        return self.names[0]

    @property
    def last(self):
        """Returns the last window handle name"""
        return self.names[-1]

if __name__ == '__main__':

    wh = WindowHandler('.*Python.*', regex=True)
    wh.fetch_names()
    print('current windows:', wh.names)
