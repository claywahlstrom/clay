
"""
Classes and extensions to make iterables more fluent.

"""

from collections import abc, OrderedDict

from clay.models import Interface as _Interface
from clay.utils import qualify as _qualify

class IEnumerable(_Interface):

    """Interface for enumerable objects"""

    # iterable is passed here to allow tuples
    def __init__(self, iterable: abc.Iterable) -> None:
        self.raise_if_base(IEnumerable)

    def copy(self) -> 'IEnumerable':
        raise NotImplementedError(_qualify(self.copy))

    def any(self, predicate: abc.Callable=lambda x: True) -> bool:
        raise NotImplementedError(_qualify(self.any))

    def first_or_default(self, default: object=None) -> object:
        raise NotImplementedError(_qualify(self.first_or_default))

    def last_or_default(self, default: object=None) -> object:
        raise NotImplementedError(_qualify(self.last_or_default))

    def group_by(self, property: str) -> abc.Hashable:
        raise NotImplementedError(_qualify(self.group_by))

    def group_by_key(self,
            key_selector: abc.Callable,
            element_selector: abc.Callable=lambda x: x) -> abc.Hashable:
        raise NotImplementedError(_qualify(self.group_by_key))

    def order_by(self, key: abc.Callable=None, reverse: bool=False) -> 'IEnumerable':
        raise NotImplementedError(_qualify(self.order_by))

    def select(self, selector: abc.Callable) -> 'IEnumerable':
        raise NotImplementedError(_qualify(self.select))

    def select_many(self, selector: abc.Callable) -> 'IEnumerable':
        raise NotImplementedError(_qualify(self.select_many))

    def skip(self, count: int) -> 'IEnumerable':
        raise NotImplementedError(_qualify(self.skip))

    def diff(self, other: 'IEnumerable') -> 'IEnumerable':
        raise NotImplementedError(_qualify(self.diff))

    def distinct(self) -> 'IEnumerable':
        raise NotImplementedError(_qualify(self.distinct))

    def where(self, predicate: abc.Callable) -> 'IEnumerable':
        raise NotImplementedError(_qualify(self.where))

    def whereif(self, condition: bool, predicate: abc.Callable) -> 'IEnumerable':
        raise NotImplementedError(_qualify(self.whereif))

    @property
    def base(self) -> abc.Iterable:
        raise NotImplementedError('IEnumerable.base')

def group_items(iterable: abc.Iterable, property: str) -> abc.Hashable:
    grouped = OrderedDict()
    for each in iterable:
        if property in each:
            if each[property] not in grouped:
                grouped[each[property]] = []
            grouped[each[property]].append(each)
        else:
            print('Could not group by {}: {}'.format(property, each))
    return grouped

def group_items_by_key(iterable: abc.Iterable,
        key_selector: abc.Callable,
        element_selector: abc.Callable=lambda x: x) -> abc.Hashable:
    grouped = OrderedDict()
    for each in iterable:
        try:
            key = key_selector(each)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(element_selector(each))
        except AttributeError:
            print('Could not group by key or element selector: {}'.format(each))
    return grouped

def extend(iterable: abc.Iterable=()):
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

        def __repr__(self) -> str:
            """Returns the string representation of this Enumerable"""
            return '{}({})'.format(self.__class__.__name__, base(self))

        def copy(self) -> IEnumerable:
            """Returns a shallow copy of this Enumerable"""
            if base is tuple:
                to_copy = base(list(self).copy())
            else:
                to_copy = base(self).copy()
            return Enumerable(to_copy)

        def any(self, predicate: abc.Callable=lambda x: True) -> bool:
            """Returns True if there are any items matching the predicate, False otherwise"""
            return any(map(predicate, self))

        def first_or_default(self, default: object=None) -> object:
            """
            Returns the first item in this Enumerable or
            the default if this Enumerable is empty

            """
            return next(iter(self), default)

        def last_or_default(self, default: object=None) -> object:
            """
            Returns the last item in this Enumerable or
            the default if this Enumerable is empty

            """
            return self[-1] if self else default

        def group_by(self, property: str) -> abc.Hashable:
            """Groups items by the given property"""
            return group_items(self, property)

        def group_by_key(self,
                key_selector: abc.Callable,
                element_selector: abc.Callable=lambda x: x) -> abc.Hashable:
            """Groups items by the given key and element selectors"""
            return group_items_by_key(self, key_selector, element_selector)

        def order_by(self, key: abc.Callable=None, reverse: bool=False) -> IEnumerable:
            """Returns items ordered by the given key selector"""
            return Enumerable(base(sorted(self, key=key, reverse=reverse)))

        def select(self, selector: abc.Callable) -> IEnumerable:
            """
            Returns a list of items projected into
            a new form using the selector function

            """
            return Enumerable(base(map(selector, self)))

        def select_many(self, selector: abc.Callable) -> IEnumerable:
            """
            Projects items into a new form using the selector function
            and flattens the results into one list

            """
            return Enumerable(base(sum(self.select(selector), [])))

        def skip(self, count: int) -> IEnumerable:
            """Skips count number of items and returns the result"""
            return Enumerable(base(list(self)[count:]))

        def diff(self, other: 'IEnumerable') -> IEnumerable:
            """
            Returns the set difference of this enumerable and another iterable

            """
            return Enumerable(base(set(self).difference(other)))

        def distinct(self) -> IEnumerable:
            """Filters items down to distinct ones"""
            return Enumerable(base(set(self)))

        def where(self, predicate: abc.Callable) -> IEnumerable:
            """Filters items based on the given predicate"""
            return Enumerable(base(filter(predicate, self)))

        def whereif(self, condition: bool, predicate: abc.Callable) -> IEnumerable:
            """Filters items based on the given condition and predicate"""
            if condition:
                return self.where(predicate)
            else:
                return self

        @property
        def base(self) -> abc.Iterable:
            """Base class for this Enumerable"""
            return base

    return Enumerable(iterable)

class Queryable:

    """Used to delay iterable evaluation to improve performance"""

    def __init__(self, iterable: abc.Iterable) -> None:
        """Initializes this queryable using the given iterable"""
        self._expr = iter(iterable)
        self._type = type(iterable)

    def copy(self) -> 'Queryable':
        """Returns a shallow copy of this queryable"""
        # create a copy of the source
        to_copy = list(self._expr).copy()
        # reset the source expression to not affect the source
        self._expr = iter(self._type(to_copy))
        # return the copied queryable
        return Queryable(to_copy)

    def any(self, predicate: abc.Callable=lambda x: True) -> bool:
        """Returns True if there are any items matching the predicate, False otherwise"""
        return any(map(predicate, self._expr))

    def first_or_default(self, default: object=None) -> object:
        """
        Returns the first item in this queryable or
        the default if this queryable is empty

        """
        return next(self._expr, default)

    def last_or_default(self, default: object=None) -> object:
        """
        Returns the last item in this queryable or
        the default if this queryable is empty

        """
        data = self.to_list()
        return data[-1] if data else default

    def group_by(self, property: str) -> abc.Hashable:
        """Groups items by the given property"""
        grouped = group_items(self, property)

        # convert the groups to queryables
        for group in grouped:
            grouped[group] = Queryable(grouped[group])

        return grouped

    def group_by_key(self,
            key_selector: abc.Callable,
            element_selector: abc.Callable=lambda x: x) -> abc.Hashable:
        """Groups items by the given key and element selectors"""
        grouped = group_items_by_key(self, key_selector, element_selector)

        # convert the groups to queryables
        for group in grouped:
            grouped[group] = Queryable(grouped[group])

        return grouped

    def order_by(self, key: abc.Callable=None, reverse: bool=False) -> 'Queryable':
        """Orders items by the given key selector"""
        self._expr = iter(sorted(self._expr, key=key, reverse=reverse))
        return self

    def select(self, selector: abc.Callable) -> 'Queryable':
        """Projects items into a new form using the selector function"""
        self._expr = map(selector, self._expr)
        return self

    def select_many(self, selector: abc.Callable) -> 'Queryable':
        """
        Projects items into a new form using the selector function
        and flattens the results into one list

        """
        self._expr = iter(sum(self.select(selector)._expr, []))
        return self

    def skip(self, count: int) -> 'Queryable':
        """Skips count number of items and returns the queryable"""
        for i in range(count):
            try:
                next(self._expr)
            except StopIteration:
                break
        return self

    def diff(self, other: 'Queryable') -> 'Queryable':
        """
        Returns the set difference of this queryable and another iterable

        """
        return self.where(lambda item: item not in other)

    def distinct(self) -> 'Queryable':
        """Filters items down to distinct ones"""
        self._expr = iter(self._type(set(self._expr)))
        return self

    def where(self, predicate: abc.Callable) -> 'Queryable':
        """Filters items based on the given predicate"""
        self._expr = filter(predicate, self._expr)
        return self

    def whereif(self, condition: bool, predicate: abc.Callable) -> 'Queryable':
        """Filters items based on the given condition and predicate"""
        if condition:
            return self.where(predicate)
        else:
            return self

    def to_list(self) -> list:
        """Reduces the queryable expression to a list"""
        return list(self._expr)

    def to_set(self) -> set:
        """Reduces the queryable expression to a set"""
        return set(self._expr)

    def to_tuple(self) -> tuple:
        """Reduces the queryable expression to a tuple"""
        return tuple(self._expr)

    def to_type(self) -> abc.Iterable:
        """Reduces the queryable expression to its type"""
        return self.type(self._expr)

    def to_enum(self) -> IEnumerable:
        """Reduces the queryable expression to an enumerable"""
        return extend(self.to_list())

    @property
    def type(self) -> abc.Iterable:
        """Iterable type for this queryable"""
        return self._type

def query(iterable: abc.Iterable=()) -> Queryable:
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

    testif('accepts tuple as iterable (empty)',
        isinstance(extend(tuple()), tuple),
        True,
        name=_qualify(extend))
    testif('accepts tuple as iterable',
        isinstance(extend(tuple((1, 2, 3))), tuple),
        True,
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
    testif('returns correct results',
        extend([1, 2, 2, 3]).diff([1, 2]),
        [3],
        name=_qualify(IEnumerable.diff))
    testif('returns correct results',
        extend([1, 2, 2, 3]).distinct(),
        [1, 2, 3],
        name=_qualify(IEnumerable.distinct))

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
    testif('returns correct results',
        query([1, 2, 2, 3]).diff([1, 2]).to_list(),
        [3],
        name=_qualify(Queryable.diff))
    testif('returns correct results',
        query([1, 2, 2, 3]).distinct().to_list(),
        [1, 2, 3],
        name=_qualify(Queryable.distinct))

    test_iterable_select_many = [
        {
            'teacher': 'Teacher1',
            'students': [
                'Student1',
                'Student2'
            ]
        },
        {
            'teacher': 'Teacher2',
            'students': [
                'Student2',
                'Student3'
            ]
        }
    ]

    testif('flattens results correctly',
        extend(test_iterable_select_many) \
            .select_many(lambda x: x['students']),
        ['Student1', 'Student2', 'Student2', 'Student3'],
        name=_qualify(IEnumerable.select_many))

    testif('flattens results correctly',
        query(test_iterable_select_many) \
            .select_many(lambda x: x['students']) \
            .to_list(),
        ['Student1', 'Student2', 'Student2', 'Student3'],
        name=_qualify(Queryable.select_many))

    testif('skips elements correctly (count: 0)',
        extend([0, 2, 4, 6]) \
            .skip(0),
        [0, 2, 4, 6],
        name=_qualify(IEnumerable.skip))
    testif('skips elements correctly (count: 2)',
        extend([0, 2, 4, 6]) \
            .skip(2),
        [4, 6],
        name=_qualify(IEnumerable.skip))
    testif('skips elements correctly (count: 5)',
        extend([0, 2, 4, 6]) \
            .skip(5),
        [],
        name=_qualify(IEnumerable.skip))

    testif('skips elements correctly (count: 0)',
        query([0, 2, 4, 6]) \
            .skip(0) \
            .to_list(),
        [0, 2, 4, 6],
        name=_qualify(Queryable.skip))
    testif('skips elements correctly (count: 2)',
        query([0, 2, 4, 6]) \
            .skip(2) \
            .to_list(),
        [4, 6],
        name=_qualify(Queryable.skip))
    testif('skips elements correctly (count: 5)',
        query([0, 2, 4, 6]) \
            .skip(5) \
            .to_list(),
        [],
        name=_qualify(Queryable.skip))

    testif('selects correct element for tuple (explicit)',
        extend(tuple((1, 2, 3))).where(lambda x: x == 2).first_or_default(),
        2,
        name=_qualify(IEnumerable.first_or_default))
    testif('selects correct element for tuple (implicit)',
        extend((1, 2, 3)).where(lambda x: x == 2).first_or_default(),
        2,
        name=_qualify(IEnumerable.first_or_default))
