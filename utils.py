
"""

Utilities for Python

TODO:
    - fix Linq querable select max size limit by partitioning
      queryable into lists

"""

import collections as _collections
import inspect as _inspect
import sys as _sys

class Anonymous(object):
    """Class Anonymous can be used to initialize properties
       using a list, tuple, or dictionary"""
    def __init__(self, *initial_data, **kwargs):
        for param in initial_data:
            if type(param) == dict:
                for key in param:
                    setattr(self, key, param[key])
            elif type(param) in (list, tuple):
                for item in param:
                    setattr(self, item, item)
            else:
                setattr(self, param, param)
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __repr__(self):
        return r'Anonymous({})'.format(
            ', '.join(name + '=' + str(getattr(self, name)) for name in self.get_attributes()))

    def get_attributes(self):
        attrs = _inspect.getmembers(self, lambda a:not(_inspect.isroutine(a)))
        return [a[0] for a in attrs if a[0].count('__') < 2]

    def to_dict(self):
        result = {}
        for attr in self.get_attributes():
            result[attr] = getattr(self, attr)
        return result

class Linq(object):

    """Class Linq can be used to query and filter data like
       Microsoft's (c) LINQ feature used in C#"""

    MAX_QUERYABLE_LENGTH = 10000

    __queryable_set = False
    __select_called = False

    def __check_queryable_exists():
        if not Linq.__queryable_set:
            raise RuntimeError('Linq queryable must be set')

    def __check_distinct_projection(distinct):
        if len(Linq.__queryable) > Linq.MAX_QUERYABLE_LENGTH and distinct:
            raise MemoryError('Linq cannot process more than ' + \
                             str(Linq.MAX_QUERYABLE_LENGTH) + ' elements for distinct=True')

    def __end_query():
        Linq.__queryable_set = False # select is the last statement

    def count():
        Linq.__check_queryable_exists()
        Linq.__end_query()
        return sum(1 for item in Linq.__queryable)

    def first_or_default(default=None):
        """Returns the first item in this query or None if empty"""
        Linq.__check_queryable_exists()
        Linq.__end_query()
        return next(iter(Linq.__queryable), default)

    def query(queryable):
        """Sets the query source using the given queryable"""
        Linq.__queryable = queryable
        Linq.__queryable_set = True
        Linq.__select_called = False
        return Linq

    def select(props, distinct=False, model=False):
        """Returns a list of properties selected from each member.
           If used, it must be the last step as it returns items
           and not a Linq object."""
        Linq.__check_queryable_exists()
        Linq.__check_distinct_projection(distinct)
        if type(props) == str:
            props = [props]
        if type(props) not in (list, tuple):
            raise TypeError('properties must be of type list or tuple')
        projection = []
        for each in Linq.__queryable:
            if model:
                entity = {}
            else:
                entity = []
            for prop in props:
                if hasattr(each, '__getitem__') and type(prop) in (int, str) \
                    and (prop in each or type(prop) == int or hasattr(each, prop)):
                    if type(prop) == int and prop >= len(each):
                        print('Could not select index {} for {}. Skipping...' \
                            .format(prop, each))
                        continue
                    if model:
                        entity[prop] = each[prop]
                    else:
                        entity.append(each[prop])
                elif hasattr(each, prop):
                    if model:
                        entity[prop] = getattr(each, prop)
                    else:
                        entity.append(getattr(each, prop))
                else:
                    print(each, 'does not have property', prop)
                    if not(model):
                        entity.append(None)
            if len(props) == 1 and not(model):
                entity = entity[0]
            if not(distinct and entity in filtered):
                projection.append(entity)
        Linq.__queryable = projection
        Linq.__select_called = True
        return Linq

    def to_list():
        """Returns this query as a list"""
        Linq.__check_queryable_exists()
        Linq.__end_query()
        return Linq.__queryable

    def where(lambda_expression):
        """Filters elements where the lambda expression evaluates to True"""
        Linq.__check_queryable_exists()
        if Linq.__select_called:
            raise RuntimeWarning('where cannot be called after select')
        Linq.__queryable = list(filter(lambda_expression, Linq.__queryable))
        return Linq

    def whereif(predicate, lambda_expression):
        if predicate:
            return Linq.where(lambda_expression)
        else:
            return Linq

def human_hex(dec):
    """Converts decimal values to human readable hex.
       Mainly used in engineering class"""
    return hex(dec)[2:]

def map_args(function, iterable, *args, **kwargs):
    """Maps iterable to a function with arguments/keywords.
       Dynamic types can be used"""
    return type(iterable)(function(x, *args, **kwargs) for x in iterable)

Model = Anonymous # alias

def _map_args_test(x, y=2, z=3):
    """A test function for the map_args function. Returns the sum of x, y, z"""
    return x + y + z

class SortableDict(_collections.OrderedDict):
    """Sortable dict, child of collections.OrderedDict"""
    def sort(self, reverse=False, debug=False):
        """Sorts this dict"""
        part = list(self.keys()) # extract keys
        part.sort(reverse=reverse) # sorts keys
        if debug:
            print('sorted keys =', part)
        copy = self.copy()
        self.clear()
        for key in part:
            self[key] = copy[key]

class Watch(object):
    """Holds a list of objects to display. Mainly used for tracking variables
       in the debugging phase of a project."""

    def __init__(self, objs=[], module='__main__'):
        if type(objs) != list or any(type(obj) != str for obj in objs):
            raise TypeError('objs must be a list of strings')

        self.objs = objs
        self.module = module

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.objs)

    def add(self, var):
        """Adds the given object to this Watch"""
        if type(var) != str:
            raise TypeError('var must be the string name of the object')
        if callable(self.get_dict()[var]):
            raise TypeError('callable types cannot be added to this watch')

        self.objs.append(var)

    def get_dict(self):
        """Returns the dict for this Watch"""
        return _sys.modules[self.module].__dict__

    def is_watching(self, name):
        return name in self.objs

    def remove(self, var):
        """Removes the given object from this Watch"""
        if type(var) == list:
            for v in var:
                (self.objs).remove(v)
        elif type(var) == str:
            (self.objs).remove(var)

    def start_recording(self, useLocals):
        """Records new objects created after this point until end
           recording is called"""
        self.__start_locals = useLocals.copy().keys()

    def stop_recording(self, useLocals):
        """Adds the new objects since the recording started to this Watch"""
        unique = (x for x in useLocals if x not in self.__start_locals)
        for var in unique:
            self.add(var)

    def view(self, transformer=lambda x: x, useLocals=None, sort=False):
        """Prints out the key, value pairs for this Watch"""
        groupdict = self.get_dict()
        if useLocals:
            groupdict.update(useLocals)

        objs = self.objs
        if sort:
            objs = sorted(objs, key=lambda x: x.lower())

        for ob in objs:
            print(ob, '->', transformer(groupdict[ob]))

    def write_file(self, filename):
        """Writes this Watch to the given file"""
        string = 'stat_dict = {}'.format(self.get_dict())
        with open(filename,'w') as fp:
            fp.write(string)

if __name__ == '__main__':

    from clay.tests import testif

    objs = [Anonymous(a=1), Anonymous(a=2, b=3), Anonymous(a=2, b=1)]

    testif('Linq first or default selects correct element',
        Linq.query(objs).where(lambda x: x.a == 2).first_or_default(),
        objs[1])
    testif('Linq select selects data from indices',
        Linq.query([['John', 'Smith', '1/1/2000']]).select([0, 6, 2]).to_list(),
        [['John', '1/1/2000']])

    test_queryable = [{'num': 1}, {'num': 2}, {'num': 2}, {'num': 3}]

    testif('Linq raises RuntimeError when no queryable specified',
        lambda: Linq.where(lambda x: True),
        None,
        raises=RuntimeError)
    testif('Linq raises RuntimeError when filtering after select',
        lambda: Linq.query(test_queryable).select('num').where(lambda x: x['num'] == 2),
        None,
        raises=RuntimeWarning)
    testif('Linq query selects property correctly',
        Linq.query(test_queryable).where(lambda x: x['num'] == 2).select('num').to_list(),
        [2, 2])

    testif('human_hex converts integer 2700 correctly', human_hex(2700), 'a8c')

    array = (1, 4, 16, 25)
    testif('map_args returns correct type',
        type(map_args(_map_args_test, array, z = 4)),
        type(array))
    testif('map_args returns correct values',
        map_args(_map_args_test, array, z = 4),
        (7, 10, 22, 31))

    obj = Anonymous({
        'one': 1,
        'two': 2,
        'three': 3
    })
    testif('Anonymous sets attribute correctly (1)', obj.one, 1)
    testif('Anonymous sets attribute correctly (2)', obj.two, 2)
    testif('Anonymous sets attribute correctly (3)', obj.three, 3)
    testif('Anonymous has three attributes set', len(obj.get_attributes()), 3)

    person = {
        'friends': [{'id': 0, 'name': 'Carla James'},
                          {'id': 1, 'name': 'Patel Lewis'},
                          {'id': 2, 'name': 'Lacey Brady'}],
        'isActive': True,
        'name': 'Celia Vaughan',
        'gender': 'female',
        'age': 36,
        'greeting': 'Hello, Celia Vaughan! You have 7 unread messages.',
        'longitude': -69.800663,
        'balance': '$3,701.90'}

    person_expected = {
        'age': 36,
        'balance': '$3,701.90',
        'friends': [{'id': 0, 'name': 'Carla James'},
                          {'id': 1, 'name': 'Patel Lewis'},
                          {'id': 2, 'name': 'Lacey Brady'}],
        'gender': 'female',
        'greeting': 'Hello, Celia Vaughan! You have 7 unread messages.',
        'isActive': True,
        'longitude': -69.800663,
        'name': 'Celia Vaughan'}

    celia = SortableDict(person)
    celia.sort()
    testif('SortableDict sorts iterable correctly', celia, person_expected)

    a = 'string'
    b = int(4)
    c = {}
    testif('Watch raises TypeError for incorrect objs type',
        lambda: Watch({'invalid': 'type'}),
        None,
        raises=TypeError)
    testif('Watch raises TypeError for incorrect obj type',
        lambda: Watch([None, 'valid_name', 123]),
        None,
        raises=TypeError)
    w = Watch(['a', 'b', 'c'])
    testif('Watch is not watching d', w.is_watching('d'), False)
    print('before add')
    w.view()
    d = float(542.2)
    w.add('d')
    testif('Watch is watching d', w.is_watching('d'), True)
    print('after add')
    w.view()
    w.write_file(r'test_files\watch_test.txt')

    testif('Watch raises TypeError when adding non-string type',
        lambda: w.add(None),
        None,
        raises=TypeError)
    def test_function(x):
        return x
    testif('Watch raises TypeError when adding callable string type',
        lambda: w.add('test_function'),
        None,
        raises=TypeError)
