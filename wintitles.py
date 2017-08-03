
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

def get_wintitles():
    global titles
    titles = list()
    EnumWindows(EnumWindowsProc(foreach_window), 0)
    while str() in titles:
        titles.remove('')
    return titles

if __name__ == '__main__':
    print(get_wintitles())
