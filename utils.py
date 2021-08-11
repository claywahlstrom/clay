
"""
Utilities for Python

"""

from collections import abc as _abc
import collections as _collections
import sys as _sys

def human_hex(dec: int) -> hex:
    """
    Converts decimal values to human readable hex.
    Mainly used in engineering class

    """
    return hex(dec)[2:]

def map_args(function: _abc.Callable,
        iterable: _abc.Iterable,
        *args,
        **kwargs) -> _abc.Iterable:
    """
    Maps iterable to a function with arguments/keywords.
    Dynamic types can be used

    """
    return type(iterable)(function(x, *args, **kwargs) for x in iterable)

def _map_args_test(x: float, y: float=2, z: float=3) -> float:
    """A test function for the map_args function. Returns the sum of x, y, z"""
    return x + y + z

def qualify(obj: object) -> str:
    """Returns the qualified name of this object"""
    # if a function or bound method
    if hasattr(obj, '__qualname__'):
        name = obj.__qualname__
    # if not an instance of an object
    elif hasattr(obj, '__name__'):
        name = obj.__name__
    # if an instance of an object
    else:
        name = obj.__class__.__name__

    return name

class SortableDict(_collections.OrderedDict):
    """Sortable dict, child of collections.OrderedDict"""
    def sort(self,
            key: _abc.Callable=None,
            reverse: bool=False,
            debug: bool=False) -> None:
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
    """
    Holds a list of objects to display. Mainly used for tracking variables
    in the debugging phase of a project.

    """

    def __init__(self, objs: _abc.Iterable=[], module: str='__main__') -> None:
        """Initializes this watch. Raises `TypeError` if `objs` is not a list of strings"""
        if not isinstance(objs, (list, set, tuple)) \
                or any(not isinstance(obj, str) for obj in objs):
            raise TypeError('objs must be a list of strings')

        self.objs = objs
        self.module = module

    def __repr__(self) -> str:
        """Returns the string representation of this watch"""
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.objs)

    def add(self, var: str) -> None:
        """Adds the given object to this watch"""
        if not isinstance(var, str):
            raise TypeError('var must be the string name of the object')
        if callable(self.get_dict()[var]):
            raise TypeError('callable types cannot be added to this watch')

        self.objs.append(var)

    def get_dict(self) -> dict:
        """Returns the dict for this watch"""
        return _sys.modules[self.module].__dict__

    def is_watching(self, name: str) -> bool:
        """Returns True if this watch is watching the given name, False otherwise"""
        return name in self.objs

    def remove(self, var: object) -> None:
        """Removes the given object(s) from this Watch"""
        if isinstance(var, (list, set, tuple)):
            for v in var:
                self.objs.remove(v)
        elif isinstance(var, str):
            self.objs.remove(var)

    def start_recording(self, useLocals: bool) -> None:
        """
        Records new objects created after this point until `end_recording` is called

        """
        self.__start_locals = useLocals.copy().keys()

    def stop_recording(self, useLocals: bool) -> None:
        """Adds the new objects since the recording started to this Watch"""
        unique = (x for x in useLocals if x not in self.__start_locals)
        for var in unique:
            self.add(var)

    def view(self,
            transformer: _abc.Callable=lambda x: x,
            useLocals: bool=None,
            sort: bool=False) -> None:
        """Prints out the key-value pairs for this Watch"""
        groupdict = self.get_dict()
        if useLocals:
            groupdict.update(useLocals)

        objs = self.objs
        if sort:
            objs = sorted(objs, key=lambda x: x.lower())

        for ob in objs:
            value = transformer(groupdict[ob])
            print('{}: {} = {}'.format(ob, type(value).__name__, value))

    def write_file(self, filename: str) -> None:
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

    from tkinter import Button, _test

    class A:
        def method(self) -> None:
            pass

    qualify_tests = {
        'imported': [
            (Button, 'Button'),
            (Button.invoke, 'Button.invoke'),
            (Button(), 'Button'),
            (Button().invoke, 'Button.invoke'),
            (_test, '_test')
        ],
        'local': [
            (A, 'A'),
            (A.method, 'A.method'),
            (A(), 'A'),
            (A().method, 'A.method'),
            (qualify, 'qualify')
        ]
    }

    for locality, tests in qualify_tests.items():
        for test in tests:
            testif('qualify returns correct string ({} {})'.format(locality, test[1]),
                qualify(test[0]),
                test[1])

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
