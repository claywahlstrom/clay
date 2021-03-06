
"""
Classes and extensions to make iterables more fluent.

"""

from clay.models import Interface as _Interface
from clay.utils import qualify as _qualify

class IEnumerable(_Interface):

    """Interface for enumerable objects"""

    def __init__(self):
        self.raise_if_base(IEnumerable)

    def copy(self):
        raise NotImplementedError(_qualify(self.copy))

    def any(self):
        raise NotImplementedError(_qualify(self.any))

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

        def any(self, predicate=lambda x: True):
            """Returns True if there are any items matching the predicate, False otherwise"""
            return any(map(predicate, self))

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

    def any(self, predicate=lambda x: True):
        """Returns True if there are any items matching the predicate, False otherwise"""
        return any(map(predicate, self._expr))

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

if __name__ == '__main__':

    from clay.tests import testif, testraises

    testraises('invalid iterable (str)',
        lambda: extend('string'),
        TypeError,
        name=_qualify(extend))
    testraises('invalid iterable (dict)',
        lambda: extend({}),
        TypeError,
        name=_qualify(extend))

    testif('returns False if empty (no predicate)',
        extend([]).any(),
        False,
        name=_qualify(IEnumerable.any))
    testif('returns True if not empty (no predicate)',
        extend([0]).any(),
        True,
        name=_qualify(IEnumerable.any))
    testif('returns False if not empty and no matches (with predicate)',
        extend([0]).any(lambda x: x == 1),
        False,
        name=_qualify(IEnumerable.any))
    testif('returns True if not empty and has matches (with predicate)',
        extend([0]).any(lambda x: x == 0),
        True,
        name=_qualify(IEnumerable.any))

    testif('returns False if empty (no predicate)',
        query([]).any(),
        False,
        name=_qualify(Queryable.any))
    testif('returns True if not empty (no predicate)',
        query([0]).any(),
        True,
        name=_qualify(Queryable.any))
    testif('returns False if not empty and no matches (with predicate)',
        query([0]).any(lambda x: x == 1),
        False,
        name=_qualify(Queryable.any))
    testif('returns True if not empty and has matches (with predicate)',
        query([0]).any(lambda x: x == 0),
        True,
        name=_qualify(Queryable.any))

    from clay.models import Anonymous
    objs = [Anonymous(a=1), Anonymous(a=2, b=3), Anonymous(a=2, b=1)]
    expected_default = Anonymous(a=0)

    testif('selects correct element',
        extend(objs).where(lambda x: x.a == 2).first_or_default(),
        objs[1],
        name=_qualify(IEnumerable.first_or_default))
    testif('selects default when no element found (default not specified)',
        extend(objs).where(lambda x: x.a == 3).first_or_default(),
        None,
        name=_qualify(IEnumerable.first_or_default))
    testif('selects default when no element found (default specified)',
        extend(objs).where(lambda x: x.a == 3).first_or_default(default=expected_default),
        expected_default,
        name=_qualify(IEnumerable.first_or_default))
    testif('selects correct element',
        extend(objs).where(lambda x: x.a == 2).last_or_default(),
        objs[2],
        name=_qualify(IEnumerable.last_or_default))
    testif('selects default when no element found (default not specified)',
        extend(objs).where(lambda x: x.a == 3).last_or_default(),
        None,
        name=_qualify(IEnumerable.last_or_default))
    testif('selects default when no element found (default specified)',
        extend(objs).where(lambda x: x.a == 3).last_or_default(default=expected_default),
        expected_default,
        name=_qualify(IEnumerable.last_or_default))
    testraises('key missing',
        lambda: extend([{'key': 'value'}]).select(lambda x: x[0]),
        KeyError,
        name=_qualify(IEnumerable.select))
    testraises('index out of bounds',
        lambda: extend([[0]]).select(lambda x: x[1]),
        IndexError,
        name=_qualify(IEnumerable.select))
    testraises('list indices are of incorrect type',
        lambda: extend([[0]]).select(lambda x: x['key']),
        TypeError,
        name=_qualify(IEnumerable.select))
    testif('selects data from indices',
        extend([['John', 'Smith', '1/1/2000']]).select(lambda x: [x[0], x[2]]),
        [['John', '1/1/2000']],
        name=_qualify(IEnumerable.select))

    test_iterable = [{'num': 1}, {'num': 2}, {'num': 2}, {'num': 3}]

    testif('where-select selects property correctly',
        extend(test_iterable).where(lambda x: x['num'] == 2).select(lambda x: x['num']),
        [2, 2],
        name=_qualify(IEnumerable.select))

    testif('selects correct element',
        query(objs).where(lambda x: x.a == 2).first_or_default(),
        objs[1],
        name=_qualify(Queryable.first_or_default))
    testif('selects default when no element found (default not specified)',
        query(objs).where(lambda x: x.a == 3).first_or_default(),
        None,
        name=_qualify(Queryable.first_or_default))
    testif('selects default when no element found (default specified)',
        query(objs).where(lambda x: x.a == 3).first_or_default(default=expected_default),
        expected_default,
        name=_qualify(Queryable.first_or_default))
    testif('selects correct element',
        query(objs).where(lambda x: x.a == 2).last_or_default(),
        objs[2],
        name=_qualify(Queryable.last_or_default))
    testif('selects default when no element found (default not specified)',
        query(objs).where(lambda x: x.a == 3).last_or_default(),
        None,
        name=_qualify(Queryable.last_or_default))
    testif('selects default when no element found (default specified)',
        query(objs).where(lambda x: x.a == 3).last_or_default(default=expected_default),
        expected_default,
        name=_qualify(Queryable.last_or_default))
    testraises('key missing',
        lambda: query([{'key': 'value'}]).select(lambda x: x[0]).to_list(),
        KeyError,
        name=_qualify(Queryable.select))
    testraises('index out of bounds',
        lambda: query([[0]]).select(lambda x: x[1]).to_list(),
        IndexError,
        name=_qualify(Queryable.select))
    testraises('list indices are of incorrect type',
        lambda: query([[0]]).select(lambda x: x['key']).to_list(),
        TypeError,
        name=_qualify(Queryable.select))
    testif('selects data from indices',
        query([['John', 'Smith', '1/1/2000']]) \
            .select(lambda x: [x[0], x[2]]) \
            .to_list(),
        [['John', '1/1/2000']],
        name=_qualify(Queryable.select))
    testif('where-select selects property correctly',
        query(test_iterable) \
            .where(lambda x: x['num'] == 2) \
            .select(lambda x: x['num']) \
            .to_list(),
        [2, 2],
        name=_qualify(Queryable.select))
