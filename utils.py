
"""
Utilities for Python

"""

import collections as _collections
import inspect as _inspect
import sys as _sys

class Anonymous(object):
    """Class Anonymous can be used to initialize attributes
       using dictionaries and keyword arguments"""
    def __init__(self, *initial_data, **kwargs):
        """Initializes this Anonymous"""
        self.update(*initial_data, **kwargs)

    def __repr__(self):
        """Returns the string representation for this Anonymous"""
        return r'Anonymous({})'.format(
            ', '.join(name + '=' + str(getattr(self, name)) for name in self.get_attributes()))

    def get_attributes(self):
        """Returns the attributes for this Anonymous"""
        attrs = _inspect.getmembers(self, lambda a:not(_inspect.isroutine(a)))
        return [a[0] for a in attrs if a[0].count('__') < 2]

    def to_dict(self):
        """Returns the attributes as key-value pairs for this Anonymous"""
        result = {}
        for attr in self.get_attributes():
            result[attr] = getattr(self, attr)
        return result

    def update(self, *initial_data, **kwargs):
        """Updates attributes using dictionaries and keyword arguments"""
        for param in initial_data:
            for key in param.keys():
                setattr(self, key, param[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

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
    def sort(self, key=None, reverse=False, debug=False):
        """Sorts this dict"""
        part = list(self.keys()) # extract keys
        part.sort(key=key, reverse=reverse) # sorts keys
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
        if type(objs) not in (list, tuple) or any(type(obj) != str for obj in objs):
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
        if type(var) in (list, tuple):
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

    testif('human_hex converts integer 2700 correctly', human_hex(2700), 'a8c')

    array = (1, 4, 16, 25)
    testif('map_args returns correct type',
        type(map_args(_map_args_test, array, z = 4)),
        type(array))
    testif('map_args returns correct values',
        map_args(_map_args_test, array, z = 4),
        (7, 10, 22, 31))

    testif('Anonymous raises AttributeError for invalid argument types',
        lambda: Anonymous([1, 2, 3]),
        None,
        raises=AttributeError)
    obj = Anonymous({
        'one': 1,
        'two': 2,
    }, three=3)
    testif('Anonymous sets attribute correctly (1)', obj.one, 1)
    testif('Anonymous sets attribute correctly (2)', obj.two, 2)
    testif('Anonymous sets attribute correctly (3)', obj.three, 3)
    testif('Anonymous has three attributes set', len(obj.get_attributes()), 3)
    obj.update({'two': obj.three}, three=obj.two) # swap the values of two and three
    testif('Anonymous updates attributes correctly',
        (obj.two, obj.three),
        (3, 2))
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
    w.write_file(r'test_files\watch-test.txt')

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
