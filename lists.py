
"""
Basic operations for lines, lists, and files

"""

import io as _io
import traceback as _traceback

from clay.models import Interface as _Interface
from clay.utils import qualify as _qualify

def apply(function, vector):
    """
    Applies the function to the given vector and returns the result
    of the same type

    """
    return type(vector)(map(function, vector))

def frange(start, stop, step):
    """
    Returns a generator that produces a stream of floats from
    start (inclusive) to stop (exclusive) by the given step

    """
    if start > stop:
        assert step < 0, 'step must agree with start and stop'
    elif stop > start:
        assert step > 0, 'step must agree with start and stop'
    digits = len(str(step)) - 2 # - 2 to account for "0."
    steps = abs(int(round((stop - start) / step, digits)))
    for x in range(steps):
        yield round(start + x * step, digits)

def join_lines(file, join_sep=', '):
    """
    Returns the lines of text from the given file (object or str)
    joined by the separator

    """
    if file.__class__.__module__ == '_io':
        fp = file
    elif isinstance(file, str):
        fp = open(file, 'r')
    return fp.read().replace('\n', join_sep)

class IEnumerable(_Interface):

    """Interface for enumerable objects"""

    def __init__(self):
        self.raise_if_base(IEnumerable)

    def copy(self):
        raise NotImplementedError(_qualify(self.copy))

    def first_or_default(self):
        raise NotImplementedError(_qualify(self.first_or_default))

    def last_or_default(self):
        raise NotImplementedError(_qualify(self.last_or_default))

    def group_by(self):
        raise NotImplementedError(_qualify(self.group_by))

    def order_by(self):
        raise NotImplementedError(_qualify(self.order_by))

    def select(self):
        raise NotImplementedError(_qualify(self.select))

    def where(self):
        raise NotImplementedError(_qualify(self.where))

    def whereif(self):
        raise NotImplementedError(_qualify(self.whereif))

    @property
    def base(self):
        raise NotImplementedError('IEnumerable.base')

def extend(iterable=()):
    """Returns an instance of Enumerable using the given iterable"""

    if not isinstance(iterable, (list, set, tuple)):
        raise TypeError('iterable must be of type list, set or tuple')

    base = type(iterable)

    class Enumerable(base, IEnumerable):

        """
        Class Enumerable contains extension methods that can be
        used to query and filter data like Microsoft's (c) LINQ
        feature in C#

        """

        def __repr__(self):
            """Returns the string representation of this Enumerable"""
            return '{}({})'.format(self.__class__.__name__, base(self))

        def copy(self):
            """Returns a shallow copy of this Enumerable"""
            if base is tuple:
                to_copy = base(list(self).copy())
            else:
                to_copy = base(self).copy()
            return Enumerable(to_copy)

        def first_or_default(self, default=None):
            """
            Returns the first item in this Enumerable or
            the default if this Enumerable is empty

            """
            return next(iter(self), default)

        def last_or_default(self, default=None):
            """
            Returns the last item in this Enumerable or
            the default if this Enumerable is empty

            """
            return self[-1] if self else default

        def group_by(self, property):
            """Returns items grouped by the given property"""
            grouped = {}
            for each in self:
                if property in each:
                    if each[property] not in grouped:
                        grouped[each[property]] = Enumerable([])
                    grouped[each[property]].append(each)
                else:
                    print('Could not group by {}: {}'.format(property, each))
            return grouped

        def order_by(self, key=None, reverse=False):
            """Returns items ordered by the given key selector"""
            return Enumerable(base(sorted(self, key=key, reverse=reverse)))

        def select(self, selector):
            """
            Returns a list of items projected into
            a new form using the selector function

            """
            return Enumerable(base(map(selector, self)))

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

class Queryable:

    """Used to delay iterable evaluation to improve performance"""

    def __init__(self, iterable):
        """Initializes this queryable using the given iterable"""
        self._expr = iter(iterable)
        self._type = type(iterable)

    def copy(self):
        """Returns a shallow copy of this queryable"""
        to_copy = list(self).copy()
        return Queryable(to_copy)

    def first_or_default(self, default=None):
        """
        Returns the first item in this queryable or
        the default if this queryable is empty

        """
        return next(self._expr, default)

    def last_or_default(self, default=None):
        """
        Returns the last item in this queryable or
        the default if this queryable is empty

        """
        data = self.to_list()
        return data[-1] if data else default

    def group_by(self, property):
        """Groups items by the given property"""
        grouped = {}
        for each in self:
            if property in each:
                if each[property] not in grouped:
                    grouped[each[property]] = []
                grouped[each[property]].append(each)
            else:
                print('Could not group by {}: {}'.format(property, each))

        # convert the groups to queryables
        for group in grouped:
            grouped[group] = Queryable(grouped[group])

        return grouped

    def order_by(self, key=None, reverse=False):
        """Orders items by the given key selector"""
        self._expr = iter(sorted(self._expr, key=key, reverse=reverse))
        return self

    def select(self, selector):
        """Projects items into a new form using the selector function"""
        self._expr = map(selector, self._expr)
        return self

    def where(self, predicate):
        """Filters items based on the given predicate"""
        self._expr = filter(predicate, self._expr)
        return self

    def whereif(self, condition, predicate):
        """Filters items based on the given condition and predicate"""
        if condition:
            return self.where(predicate)
        else:
            return self

    def to_list(self):
        """Reduces the queryable expression to a list"""
        return list(self._expr)

    def to_set(self):
        """Reduces the queryable expression to a set"""
        return set(self._expr)

    def to_tuple(self):
        """Reduces the queryable expression to a tuple"""
        return tuple(self._expr)

    def to_type(self):
        """Reduces the queryable expression to its type"""
        return self.type(self._expr)

    @property
    def type(self):
        """Iterable type for this queryable"""
        return self._type

def query(iterable=()):
    """Returns an instance of Queryable using the given iterable"""
    return Queryable(iterable)

def rmdup(lizt, show_output=False):
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

if __name__ == '__main__':

    from clay.tests import testif, testraises
    from clay.utils import qualify

    TEST_FILE = _io.StringIO('h\ne\nl\nl\no')
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

    testif('returns correct string',
        join_lines(TEST_FILE),
        'h, e, l, l, o',
        name=qualify(join_lines))

    testraises('invalid iterable (str)',
        lambda: extend('string'),
        TypeError,
        name=qualify(extend))
    testraises('invalid iterable (dict)',
        lambda: extend({}),
        TypeError,
        name=qualify(extend))

    from clay.models import Anonymous
    objs = [Anonymous(a=1), Anonymous(a=2, b=3), Anonymous(a=2, b=1)]
    expected_default = Anonymous(a=0)

    testif('selects correct element',
        extend(objs).where(lambda x: x.a == 2).first_or_default(),
        objs[1],
        name=qualify(IEnumerable.first_or_default))
    testif('selects default when no element found (default not specified)',
        extend(objs).where(lambda x: x.a == 3).first_or_default(),
        None,
        name=qualify(IEnumerable.first_or_default))
    testif('selects default when no element found (default specified)',
        extend(objs).where(lambda x: x.a == 3).first_or_default(default=expected_default),
        expected_default,
        name=qualify(IEnumerable.first_or_default))
    testif('selects correct element',
        extend(objs).where(lambda x: x.a == 2).last_or_default(),
        objs[2],
        name=qualify(IEnumerable.last_or_default))
    testif('selects default when no element found (default not specified)',
        extend(objs).where(lambda x: x.a == 3).last_or_default(),
        None,
        name=qualify(IEnumerable.last_or_default))
    testif('selects default when no element found (default specified)',
        extend(objs).where(lambda x: x.a == 3).last_or_default(default=expected_default),
        expected_default,
        name=qualify(IEnumerable.last_or_default))
    testraises('key missing',
        lambda: extend([{'key': 'value'}]).select(lambda x: x[0]),
        KeyError,
        name=qualify(IEnumerable.select))
    testraises('index out of bounds',
        lambda: extend([[0]]).select(lambda x: x[1]),
        IndexError,
        name=qualify(IEnumerable.select))
    testraises('list indices are of incorrect type',
        lambda: extend([[0]]).select(lambda x: x['key']),
        TypeError,
        name=qualify(IEnumerable.select))
    testif('selects data from indices',
        extend([['John', 'Smith', '1/1/2000']]).select(lambda x: [x[0], x[2]]),
        [['John', '1/1/2000']],
        name=qualify(IEnumerable.select))

    test_iterable = [{'num': 1}, {'num': 2}, {'num': 2}, {'num': 3}]

    testif('where-select selects property correctly',
        extend(test_iterable).where(lambda x: x['num'] == 2).select(lambda x: x['num']),
        [2, 2],
        name=qualify(IEnumerable.select))

    testif('selects correct element',
        query(objs).where(lambda x: x.a == 2).first_or_default(),
        objs[1],
        name=qualify(Queryable.first_or_default))
    testif('selects default when no element found (default not specified)',
        query(objs).where(lambda x: x.a == 3).first_or_default(),
        None,
        name=qualify(Queryable.first_or_default))
    testif('selects default when no element found (default specified)',
        query(objs).where(lambda x: x.a == 3).first_or_default(default=expected_default),
        expected_default,
        name=qualify(Queryable.first_or_default))
    testif('selects correct element',
        query(objs).where(lambda x: x.a == 2).last_or_default(),
        objs[2],
        name=qualify(Queryable.last_or_default))
    testif('selects default when no element found (default not specified)',
        query(objs).where(lambda x: x.a == 3).last_or_default(),
        None,
        name=qualify(Queryable.last_or_default))
    testif('selects default when no element found (default specified)',
        query(objs).where(lambda x: x.a == 3).last_or_default(default=expected_default),
        expected_default,
        name=qualify(Queryable.last_or_default))
    testraises('key missing',
        lambda: query([{'key': 'value'}]).select(lambda x: x[0]).to_list(),
        KeyError,
        name=qualify(Queryable.select))
    testraises('index out of bounds',
        lambda: query([[0]]).select(lambda x: x[1]).to_list(),
        IndexError,
        name=qualify(Queryable.select))
    testraises('list indices are of incorrect type',
        lambda: query([[0]]).select(lambda x: x['key']).to_list(),
        TypeError,
        name=qualify(Queryable.select))
    testif('selects data from indices',
        query([['John', 'Smith', '1/1/2000']]) \
            .select(lambda x: [x[0], x[2]]) \
            .to_list(),
        [['John', '1/1/2000']],
        name=qualify(Queryable.select))
    testif('where-select selects property correctly',
        query(test_iterable) \
            .where(lambda x: x['num'] == 2) \
            .select(lambda x: x['num']) \
            .to_list(),
        [2, 2],
        name=qualify(Queryable.select))

    printall(TEST_LIST)
    printlines(r'test_files\essay.txt', 4)
    testif('rmdup removes duplicates correctly',
        rmdup(TEST_LIST),
        ['h', 'e', 'l', 'o'])
