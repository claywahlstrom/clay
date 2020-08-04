
"""
text: Outline and align text on screen based on console size.

Default WIDTH is 80 characters for IDLE and 100 for shell.

"""

import pprint

from clay.env import is_idle as _is_idle

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

def is_capitalized(text):
    """Returns True if the given text is capitalized, False otherwise"""
    if not text: return False
    return text[0].isupper()

def uncapitalize(text):
    """Returns the given text uncapitalized"""
    if not text: return ''
    elif len(text) == 1:
        return text[0].lower()
    else:
        return text[0].lower() + text[1:]

def underline(text, char='-'):
    """Returns the given text underlined with char"""
    return text + '\n' + char * len(text)

def pretty_print(heading, data):
    """Pretty prints the heading and data"""
    print(underline(heading))
    pprint.pprint(data)

if __name__ == '__main__':

    from clay.tests import testif

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

    testif('Returns False if text less than two characters',
        is_capitalized(''),
        False)
    testif('Returns True if first character capitalized',
        is_capitalized('Hi'),
        True)

    testif('Returns empty string if text empty',
        uncapitalize(''),
        '')
    testif('Returns uncapitalized text (1 character)',
        uncapitalize('H'),
        'h')
    testif('Returns uncapitalized text (>1 character)',
        uncapitalize('Hello'),
        'hello')
