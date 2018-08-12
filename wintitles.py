
import re as _re
import time as _time
import ctypes as _ctypes

EnumWindows = _ctypes.windll.user32.EnumWindows
EnumWindowsProc = _ctypes.WINFUNCTYPE(_ctypes.c_bool, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))
GetWindowTextW = _ctypes.windll.user32.GetWindowTextW
GetWindowTextLengthW = _ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = _ctypes.windll.user32.IsWindowVisible
 
def foreach_window(hwnd, lParam):
    """Callback func for the EnumWindowsProc"""
    if IsWindowVisible(hwnd):
        length = GetWindowTextLengthW(hwnd)
        buff = _ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buff, length + 1)
        titles.append(buff.value)
    return True

def get_wintitles():
    """Returns a list of active window titles"""
    global titles
    titles = []
    EnumWindows(EnumWindowsProc(foreach_window), 0)
    while str() in titles: # remove blank entries
        titles.remove(str())
    return titles

class WindowHandler(object):
    """Class WindowHandler can be used to find Window titles by name"""
    
    def __init__(self, name, regex=False):
        """Initializes a new WindowHandler with the given name and whether
           the name is regex or not"""
        self.name = name
        self.regex = regex

    def getfirst(self):
        """Returns the first window handle name"""
        return self.getname(0)
        
    def getlast(self):
        """Returns the last window handle name"""
        return self.getname(-1)

    def getname(self, index=0):
        """Returns the given window handle name at the given index"""
        return self.getnames()[index]

    def getnames(self):
        """Returns a list of all of the window handle names"""   
        titles = get_wintitles()
        if self.regex:
            return tuple(name for title in titles for name in _re.findall(self.name, title))
        return tuple(title for title in titles if self.name in title)

    def isactive(self):
        """Returns True if this window handle name is active, False otherwise"""
        return bool(self.getnames())

    def wait(self):
        """Waits until this window handle name is active, retries every 1.0 second interval"""
        if not self.isactive():
            print('Waiting for a new window')
            while not self.isactive():
                _time.sleep(1.0)

if __name__ == '__main__':
    print(WindowHandle('.*Python.*', regex=True).getnames())
