
"""
Align text on screen based on console size. Default WIDTH is 80 characters
for IDLE and 100 for shell.

"""

from clay.shell import isIdle as _isIdle

if _isIdle():
    WIDTH = 80
else:
    WIDTH = 100

def center(text):
    """Justifies the given text to the center"""
    return text.center(WIDTH)

def right(text):
    """Justifies the given text to the right"""
    return text.rjust(WIDTH)

def left(text):
    """Justifies the given text to the left"""
    return text

if __name__ == '__main__':
    print(left('hello'))
    print(center('world'))
    print(right('My name is Clay. What\'s yours?'))
