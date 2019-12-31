
"""
texteffects: Outline and align text on screen based on console size.

Default WIDTH is 80 characters for IDLE and 100 for shell.

"""

from clay.shell.core import is_idle as _is_idle

if _is_idle():
    WIDTH = 80
else:
    WIDTH = 100

def box(text, width=0, height=3, module=False):
    """Prints a formatted box based on size of text w/ thickness of 1.
       Optional module headers to customize titles"""
    if width < len(text) + 4: # if width is zero
        for line in text.split('\n'):
            if len(line) + 4 > width:
                width = len(line) + 4
    assert height >= 3
    if module:
        height += 2

    border = 1

    print('#' * width)

    for x in range(border):
        print('#' + ' ' * (width - 2) + '#')

    for line in text.split('\n'):
        print('#', end='')
        print(line.center(width - 2, ' '), end='')
        print('#')

    for x in range(border):
        print('#' + ' ' * (width - 2) + '#')

    print('#' * width)

def center(text):
    """Justifies the given text to the center"""
    return text.center(WIDTH)

def fullbox(text, thickness=1, border=1):
    """Prints a formatted box based on "thickness" and "border" around text"""
    width = len(text) + thickness * 2 + border * 2
    height = 3 # based on top/bottom or total lines???

    for x in range(thickness):
        print('#' * width)

    for x in range(border): # greater than one
        _fullbox_printline(' ' * (len(text) + 2 * border), thickness)

    _fullbox_printline(text.center(len(text) + 2, ' '), thickness)

    for x in range(border): # greater than one
        _fullbox_printline(' ' * (len(text) + 2 * border), thickness)

    for x in range(thickness):
        print('#' * width)

def _fullbox_printline(text, thickness):
    """A helper for fullbox"""
    print('#' * thickness + text + '#' * thickness)

def left(text):
    """Justifies the given text to the left"""
    return text

def right(text):
    """Justifies the given text to the right"""
    return text.rjust(WIDTH)

def underline(text, char='-'):
    """Returns the given text underlined with char"""
    return text + '\n' + char * len(text)

if __name__ == '__main__':
    print('Box Art Examples:')
    fullbox('Hello full', 2, 1)
    print('')
    box('indexops\n---------\nregex for\nsearching\ndirectories', module=True)

    print(left('hello'))
    print(center('world'))
    print(right('My name is Clay. What\'s yours?'))
    print('UNDERLINE TESTS')
    print(underline('underlined text (-)'))
    print(underline('underlined text (*)', '*'))

