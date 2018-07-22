
"""
Box creation for text

"""

import math as _math

def fullbox(text, thickness=1, border=1):
    """Prints a formatted box based on "thickness" and "border" around text"""
    width = len(text) + thickness * 2 + border * 2
    height = 3 # based on top/bottom or total lines???

    for x in range(thickness):
        print('#' * width)
    
    for x in range(border): # greater than one
        __printline(' ' * (len(text) + 2 * border), thickness)

    __printline(text.center(len(text) + 2, ' '), thickness)
    
    for x in range(border): # greater than one
        __printline(' ' * (len(text) + 2 * border), thickness)
        
    for x in range(thickness):
        print('#' * width)

def __printline(text, thickness):
    """A helper for fullbox"""
    print('#' * thickness + text + '#' * thickness)

def box(text, width=0, height=3, module=False):
    """Prints a formatted box based on size of text w/ thickness of 1.

    Option for module headers to customize titles

    """
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
        
    print('#'*width)

if __name__ == '__main__':
    print('Examples:')
    fullbox('Hello full', 2, 1)
    print('')
    box('indexops\n---------\nregex for\nsearching\ndirectories', module=True)
    input('done')
