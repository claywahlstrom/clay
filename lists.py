
"""
Basic operations for lines, lists, and files

"""

# possible: rmdup could use "set" object to remove duplicates

import io as _io
import traceback as _traceback

def apply(function, vector):
    """Applies the function to the given vector and returns the result
       of the same type"""
    return type(vector)(map(function, vector))

def frange(start, stop, step):
    """Returns a generator that produces a stream of floats from
       start (inclusive) to stop (exclusive) by the given step"""
    if start > stop:
        assert step < 0, 'step must agree with start and stop'
    elif stop > start:
        assert step > 0, 'step must agree with start and stop'
    digits = len(str(step)) - 2 # - 2 to account for "0."
    steps = abs(int(round((stop - start) / step, digits)))
    for x in range(steps):
        yield round(start + x * step, digits)

def join_lines(file, join_sep=', '):
    """Returns the lines of text from the given file (object or str)
       joined by the separator"""
    if file.__class__.__module__ == '_io':
        fp = file
    elif isinstance(file, str):
        fp = open(file, 'r')
    return fp.read().replace('\n', join_sep)

def extend(iterable=()):
    """Returns an instance of Enumerable using the given iterable"""

    if not isinstance(iterable, (list, set, tuple)):
        raise TypeError('iterable must be of type list, set or tuple')

    base = type(iterable)

    class Enumerable(base):

        """Class Enumerable contains extension methods that can be
           used to query and filter data like Microsoft's (c) LINQ
           feature in C#"""

        def __repr__(self):
            """Returns the string representation of this Enumerable"""
            return '{}({})'.format(self.__class__.__name__, base(self))

        def first_or_default(self, default=None):
            """Returns the first item in this Enumerable or
               the default if this Enumerable is empty"""
            return next(iter(self), default)

        def group_by(self, property):
            """Returns items grouped by the given property"""
            grouped = {}
            for each in self:
                if property in each:
                    if each[property] not in grouped:
                        grouped[each[property]] = []
                    grouped[each[property]].append(each)
                else:
                    print('Could not group by {}: {}'.format(property, each))
            return grouped

        def select(self, selector):
            """Returns a list of items projected into
               a new form using the selector function"""
            projection = []
            for each in self:
                new_form = None # default form
                try:
                    new_form = selector(each)
                except (KeyError, IndexError, TypeError) as ex:
                    print('{}.select errored on {}'.format(
                        self.__class__.__name__,
                        each))
                    _traceback.print_exc()
                    raise ex
                projection.append(new_form)
            return Enumerable(projection)

        def where(self, predicate):
            """Filters items based on the given predicate"""
            return Enumerable(base(filter(predicate, self)))

        def whereif(self, condition, predicate):
            """Filters items based on the given condition and predicate"""
            if condition:
                return self.where(predicate)
            else:
                return self

        @property
        def base(self):
            """Base class for this Enumerable"""
            return base

    return Enumerable(iterable)

def printall(items):
    """Prints each item from the given items iterable"""
    if isinstance(items, dict):
        for key, value in items.items():
            print(key, ':', value)
    else:
        for item in items:
            print(item)

def printlines(content, lines=0, numbered=True):
    """Prints the given content (list of str or str), w/ or w/o line numbers"""
    if not isinstance(content, (list, str)):
        raise TypeError('content must be of type str or list')

    if isinstance(content, str):
        with open(content, 'r') as fp:
            content = fp.readlines()

    chunks = [line.rstrip() for line in content]

    if not(lines):
        lines = len(chunks)
    chunks = chunks[:lines]
    for num, line in enumerate(chunks):
        if numbered:
            print(str(num).rjust(len(str(lines))), end=' ')
        print(line)

def rmdup(lizt):
    """Returns a non-duplicated version of the given list with order in tact"""
    len_before = len(lizt)
    new = []
    for n in lizt:
        if n not in new:
            new.append(n)
    print(len_before - len(new), 'duplicate(s) removed')
    return new

if __name__ == '__main__':

    from clay.tests import testif

    TEST_FILE = _io.StringIO('h\ne\nl\nl\no')
    TEST_LIST = ['h', 'e', 'l', 'l', 'o']

    testif('apply returns correct type (list)',
        type(apply(lambda x: x, [0, 0])),
        list)
    testif('apply returns correct type (tuple)',
        type(apply(lambda x: x, (0, 0))),
        tuple)
    testif('apply returns correct values (floats => ints)',
        apply(int, [0.0, 9.9]),
        [0, 9])
    testif('frange returns correct values',
        list(frange(0, 0.6, 0.1)),
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
    testif('frange returns correct values',
        list(frange(1, 0, -0.25)),
        [1.0, 0.75, 0.5, 0.25])
    testif('frange returns correct values',
        list(frange(0.9, 1.0, 0.1)),
        [0.9])
    testif('frange raises AssertionError when start > stop && step > 0',
        lambda: list(frange(1, 0, 0.25)),
        None,
        raises=AssertionError)
    testif('frange raises AssertionError when stop > start && step < 0',
        lambda: list(frange(0, 1, -0.25)),
        None,
        raises=AssertionError)

    testif('join_lines returns correct string',
        join_lines(TEST_FILE),
        'h, e, l, l, o')

    testif('extend raises TypeError for invalid iterable (str)',
        lambda: extend('string'),
        None,
        raises=TypeError)
    testif('extend raises TypeError for invalid iterable (dict)',
        lambda: extend({}),
        None,
        raises=TypeError)

    from clay.models import Anonymous
    objs = [Anonymous(a=1), Anonymous(a=2, b=3), Anonymous(a=2, b=1)]
    expected_default = Anonymous(a=0)

    testif('Enumerable "first or default" selects correct element',
        extend(objs).where(lambda x: x.a == 2).first_or_default(),
        objs[1])
    testif('Enumerable "first or default" selects default when no element found',
        extend(objs).where(lambda x: x.a == 3).first_or_default(default=expected_default),
        expected_default)
    testif('Enumerable "select" raises KeyError when key missing',
        lambda: extend([{'key': 'value'}]).select(lambda x: x[0]),
        None,
        raises=KeyError)
    testif('Enumerable "select" raises IndexError when index out of bounds',
        lambda: extend([[0]]).select(lambda x: x[1]),
        None,
        raises=IndexError)
    testif('Enumerable "select" raises TypeError when list indices are of incorrect type',
        lambda: extend([[0]]).select(lambda x: x['key']),
        None,
        raises=TypeError)
    testif('Enumerable "select" selects data from indices',
        extend([['John', 'Smith', '1/1/2000']]).select(lambda x: [x[0], x[2]]),
        [['John', '1/1/2000']])

    test_iterable = [{'num': 1}, {'num': 2}, {'num': 2}, {'num': 3}]

    testif('Enumerable where-select selects property correctly',
        extend(test_iterable).where(lambda x: x['num'] == 2).select(lambda x: x['num']),
        [2, 2])

    printall(TEST_LIST)
    printlines(r'test_files\essay.txt', 4)
    testif('rmdup removes duplicates correctly',
        rmdup(TEST_LIST),
        ['h', 'e', 'l', 'o'])
