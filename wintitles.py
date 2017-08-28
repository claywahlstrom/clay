
import re
import time
import ctypes as _ctypes

EnumWindows = _ctypes.windll.user32.EnumWindows
EnumWindowsProc = _ctypes.WINFUNCTYPE(_ctypes.c_bool, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))
GetWindowTextW = _ctypes.windll.user32.GetWindowTextW
GetWindowTextLengthW = _ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = _ctypes.windll.user32.IsWindowVisible
 
def foreach_window(hwnd, lParam): # callback func
    if IsWindowVisible(hwnd):
        length = GetWindowTextLengthW(hwnd)
        buff = _ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buff, length + 1)
        titles.append(buff.value)
    return True

def getpath(regex):
    titles = get_wintitles()
    for title in titles:
        found = re.findall(regex, title)
        if found:
            return found[0]

def get_wintitles():
    global titles
    titles = list()
    EnumWindows(EnumWindowsProc(foreach_window), 0)
    while str() in titles:
        titles.remove(str())
    return titles

def isopen(regex):
    return bool(set([title for title in get_wintitles() if re.findall(regex, title)]))

def testopen(regex):
    if not isopen(regex):
        # set_title('Open the editor first')
        print('Open the editor first')
        while not isopen(regex):
            time.sleep(1)

if __name__ == '__main__':
    print(getpath(get_wintitles(), '.*Python.*'))
