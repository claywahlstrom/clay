
"""
Clusters: for managing data such as variables, lists and dictionaries

"""

import collections as _collections
import sys as _sys

class FixedSizeQueue(object):
    """Object that maintains length when items are added to it."""
    def __init__(self, ls=list(), max_size=10):
        self.__ls = ls[:]
        self.max_size = max_size

    def __len__(self):
        return len(self.__ls)

    def __clean(self):
        """Removes elements from the queue until max size has been reached"""
        while len(self.__ls) > self.max_size:
            (self.__ls).pop(0)

    def add(self, element):
        """Adds the given element to the back of the queue"""
        (self.__ls).append(item)
        self.__clean()

    def get_average(self):
        """Returns the average for this queue if the elements are summable"""
        if len(self.__ls) == 0:
            raise Exception('length must be >= 1')
        return sum(self.__ls) / len(self.__ls)

    def get_list(self):
        """Returns this queue"""
        return self.__ls

class Grouping(object):
    """Holds a list of objects to display. Mainly used for tracking variables
       in the debugging phase of a project."""
    
    def __init__(self, objs=list(), module='__main__'):
        assert type(objs) == list, 'Not a list of strings'

        self.objs = objs
        self.module = module

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.objs)

    def add(self, var):
        """Adds the given object to this grouping"""
        if type(var) == list:
            for v in var:
                (self.objs).append(v)
        elif type(var) == str:
            (self.objs).append(var)
        else:
            raise ValueError()

    def get_dict(self):
        """Returns this grouping's dict"""
        return _sys.modules[self.module].__dict__

    def remove(self, var):
        """Removes the given object from this grouping"""
        if type(var) == list:
            for v in var:
                (self.objs).remove(v)
        elif type(var) == str:
            (self.objs).remove(var)

    def show(self, useLocals=None):
        """Prints out the key, value pairs for this grouping"""
        groupdict = self.get_dict()
        if useLocals:
            groupdict.update(useLocals)
        for ob in self.objs:
            print(ob, '->', groupdict[ob])

    def write_file(self, filename):
        """Writes this grouping to the given file"""
        string = 'stat_dict = {}'.format(self.get_dict())
        with open(filename,'w') as fp:
            fp.write(string)

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

if __name__ == '__main__':

    from random import randint
    from time import sleep

    print('--------')
    myav = FixedSizeQueue(max_size=5)
    myav.add(0) # ensures while-loop entry
    while myav.get_average() < 10:
        myav.add(randint(0, 15))
        print('list', myav.get_list())
        print('  len', len(myav))
        print('  av ', myav.get_average())
    print('--------')

    a = 'string'
    b = int(4)
    c = dict()
    s = Grouping(['a', 'b', 'c'])
    print('before add')
    s.show()
    d = float(542.2)
    s.add('d')
    print('after add')
    s.show()
    s.write_file('clusters_test.txt')

    person = {'friends': [{'id': 0, 'name': 'Carla James'},
                          {'id': 1, 'name': 'Patel Lewis'},
                          {'id': 2, 'name': 'Lacey Brady'}],
              'isActive': True, 'name': 'Celia Vaughan',
              'gender': 'female', 'age': 36,
              'greeting': 'Hello, Celia Vaughan! You have 7 unread messages.',
              'longitude': -69.800663, 'balance': '$3,701.90'}

    print(person, type(person))
    celia = SortableDict(person)
    celia.sort()
    print(celia, type(celia))
