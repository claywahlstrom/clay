
"""
Basic operations for lines, lists, and files

"""

from collections import abc
import io

def apply(function: abc.Callable, vector: abc.Iterable) -> abc.Iterable:
    """
    Applies the function to the given vector and returns the result
    of the same type

    """
    return type(vector)(map(function, vector))

def frange(start: int, stop: int, step: float) -> abc.Generator:
    """
    Returns a generator that produces a stream of floats from
    start (inclusive) to stop (exclusive) by the given step

    """
    if start > stop:
        assert step < 0, 'step must agree with start and stop'
    elif stop > start:
        assert step > 0, 'step must agree with start and stop'
    digits = max(0, len(str(step)) - 2) # - 2 to account for "0."
    steps = abs(int(round((stop - start) / step, digits)))
    for x in range(steps):
        yield round(start + x * step, digits)

def join_lines(file: object, join_sep: str=', ') -> str:
    """
    Returns the lines of text from the given file (object or str)
    joined by the separator

    """
    if file.__class__.__module__ == '_io':
        fp = file
    elif isinstance(file, str):
        fp = open(file, 'r')
    else:
        raise TypeError(file)
    return fp.read().replace('\n', join_sep)

def printall(items: abc.Iterable) -> None:
    """Prints each item from the given items iterable"""
    if isinstance(items, dict):
        for key, value in items.items():
            print(key, ':', value)
    else:
        for item in items:
            print(item)

def printlines(content: str, lines: int=0, numbered: bool=True) -> None:
    """Prints the given content (list of str or str), w/ or w/o line numbers"""
    if not isinstance(content, (list, str)):
        raise TypeError('content must be of type str or list')

    if isinstance(content, str):
        with open(content, 'r') as fp:
            content = fp.readlines()

    chunks = [line.rstrip() for line in content]

    if lines == 0:
        lines = len(chunks)
    chunks = chunks[:lines]
    for num, line in enumerate(chunks):
        if numbered:
            print(str(num).rjust(len(str(lines))), end=' ')
        print(line)

def rmdup(lizt: abc.Iterable, show_output: bool=False) -> abc.Iterable:
    """Returns a non-duplicated version of the given list with order in tact"""
    len_before = len(lizt)
    new = []
    for n in lizt:
        if n not in new:
            new.append(n)

    if show_output:
        print(len_before - len(new), 'duplicate(s) removed from {}'
            .format(str(lizt)[:30] + '...'))

    return new

def sample(data, rate=26):
    """Takes samples of data at the given rate"""
    for i, item in enumerate(data):
        if i % rate == 0:
            yield item

if __name__ == '__main__':

    from clay.tests import testif, testraises
    from clay.utils import qualify

    TEST_FILE = io.StringIO('h\ne\nl\nl\no')
    TEST_LIST = ['h', 'e', 'l', 'l', 'o']

    testif('returns correct type (list)',
        type(apply(lambda x: x, [0, 0])),
        list,
        name=qualify(apply))
    testif('returns correct type (tuple)',
        type(apply(lambda x: x, (0, 0))),
        tuple,
        name=qualify(apply))
    testif('returns correct values (floats => ints)',
        apply(int, [0.0, 9.9]),
        [0, 9],
        name=qualify(apply))
    testif('returns correct values',
        list(frange(0, 0.6, 0.1)),
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        name=qualify(frange))
    testif('returns correct values',
        list(frange(1, 0, -0.25)),
        [1.0, 0.75, 0.5, 0.25],
        name=qualify(frange))
    testif('returns correct values',
        list(frange(0.9, 1.0, 0.1)),
        [0.9],
        name=qualify(frange))
    testraises('start > stop && step > 0',
        lambda: list(frange(1, 0, 0.25)),
        AssertionError,
        name=qualify(frange))
    testraises('stop > start && step < 0',
        lambda: list(frange(0, 1, -0.25)),
        AssertionError,
        name=qualify(frange))

    testraises('file is incorrect type',
        lambda: join_lines(1234),
        TypeError,
        name=qualify(join_lines))
    testif('returns correct string',
        join_lines(TEST_FILE),
        'h, e, l, l, o',
        name=qualify(join_lines))

    printall(TEST_LIST)
    printlines(r'test_files\essay.txt', 4)
    testif('rmdup removes duplicates correctly',
        rmdup(TEST_LIST),
        ['h', 'e', 'l', 'o'])

    testraises('rate=0',
        lambda: list(sample(range(10, 120 + 1), 0)),
        ZeroDivisionError,
        name=qualify(sample))
    testif('returns empty if no data',
        list(sample([])),
        [],
        name=qualify(sample))
    testif('returns correct numbers (rate=26)',
        list(sample(range(10, 120 + 1))),
        [10, 36, 62, 88, 114],
        name=qualify(sample))
    testif('returns correct numbers (rate=15)',
        list(sample(range(9, 65), rate=15)),
        [9, 24, 39, 54],
        name=qualify(sample))
