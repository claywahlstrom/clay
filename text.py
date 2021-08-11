
"""
text: Outline and align text on screen based on console size.

Default WIDTH is 80 characters for IDLE and 100 for shell.

"""

from collections import abc
import pprint

from clay.env import is_idle as _is_idle

if _is_idle():
    WIDTH = 80
else:
    from clay.settings import CONSOLE_WIDTH as WIDTH

def box(text: str, width: int=0, height: int=3, for_module: bool=False) -> None:
    """
    Prints a formatted box based on size of text w/ thickness of 1.
    Optional module headers to customize titles

    """
    if width < len(text) + 4: # if width is zero
        for line in text.split('\n'):
            if len(line) + 4 > width:
                width = len(line) + 4
    assert height >= 3
    if for_module:
        height += 2

    border = 1

    print('#' * width)

    for _ in range(border):
        print('#' + ' ' * (width - 2) + '#')

    for line in text.split('\n'):
        print('#', end='')
        print(line.center(width - 2, ' '), end='')
        print('#')

    for _ in range(border):
        print('#' + ' ' * (width - 2) + '#')

    print('#' * width)

def center(text: str) -> str:
    """Justifies the given text to the center"""
    return text.center(WIDTH)

def fullbox(text: str, thickness: int=1, border: int=1) -> None:
    """Prints a formatted box based on "thickness" and "border" around text"""
    width = len(text) + thickness * 2 + border * 2

    for _ in range(thickness):
        print('#' * width)

    for _ in range(border): # greater than one
        _fullbox_printline(' ' * (len(text) + 2 * border), thickness)

    _fullbox_printline(text.center(len(text) + 2, ' '), thickness)

    for _ in range(border): # greater than one
        _fullbox_printline(' ' * (len(text) + 2 * border), thickness)

    for _ in range(thickness):
        print('#' * width)

def _fullbox_printline(text: str, thickness: int) -> None:
    """A helper for fullbox"""
    print('#' * thickness + text + '#' * thickness)

def left(text: str) -> str:
    """Justifies the given text to the left"""
    return text

def right(text: str) -> str:
    """Justifies the given text to the right"""
    return text.rjust(WIDTH)

def is_capitalized(text: str) -> str:
    """Returns True if the given text is capitalized, False otherwise"""
    if not text: return False
    return text[0].isupper()

def uncapitalize(text: str) -> str:
    """Returns the given text uncapitalized"""
    # return early if empty string or none
    if not text: return ''
    # return lower if one character
    elif len(text) == 1:
        return text[0].lower()
    # return as-is if first word is uppercase
    elif text.split(' ')[0].isupper():
        return text
    # return lower first character and rest of string
    else:
        return text[0].lower() + text[1:]

def underline(text: str, char: str='-') -> str:
    """Returns the given text underlined with char"""
    return text + '\n' + char * len(text)

def pretty_print(heading: str, data: object) -> None:
    """Pretty prints the heading and data"""
    print(underline(heading))
    pprint.pprint(data)

def remove_padding(string: str) -> str:
    """Returns the given string stripped and with double-spaces as single-spaces"""
    string = string.strip()
    while '  ' in string:
        string = string.replace('  ', ' ')
    return string

def remove_padding_many(strings: abc.Iterable) -> abc.Iterable:
    """
    Returns the given iterable of strings stripped and with double-spaces as single-spaces

    """
    return type(strings)(map(remove_padding, strings))

if __name__ == '__main__':

    from clay.tests import testif
    from clay.utils import qualify

    print('Box Art Examples:')
    fullbox('Hello full', 2, 1)
    print('')
    box('indexops\n---------\nregex for\nsearching\ndirectories', for_module=True)

    print(left('hello'))
    print(center('world'))
    print(right('My name is Clay. What\'s yours?'))
    print('UNDERLINE TESTS')
    print(underline('underlined text (-)'))
    print(underline('underlined text (*)', '*'))

    testif('returns False if text less than two characters',
        is_capitalized(''),
        False,
        name=qualify(is_capitalized))
    testif('returns True if first character capitalized',
        is_capitalized('Hi'),
        True,
        name=qualify(is_capitalized))

    testif('returns empty string if text empty',
        uncapitalize(''),
        '',
        name=qualify(uncapitalize))
    testif('returns uncapitalized text (1 character)',
        uncapitalize('H'),
        'h',
        name=qualify(uncapitalize))
    testif('returns uncapitalized text (>1 character)',
        uncapitalize('Hello'),
        'hello',
        name=qualify(uncapitalize))
    testif('returns text as-is (uppercase word)',
        uncapitalize('HELLO world'),
        'HELLO world',
        name=qualify(uncapitalize))

    testif('removes text padding',
        remove_padding(' remove spaces  from padded   test string  '),
        'remove spaces from padded test string',
        name=qualify(remove_padding))
    testif('removes many text paddings',
        remove_padding_many([' remove spaces  from padded   test string  ', ' my  string']),
        ['remove spaces from padded test string', 'my string'],
        name=qualify(remove_padding_many))
