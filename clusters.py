
"""
Clusters: for managing data

"""

import collections as _collections
import sys as _sys

class Group(object):
    """Holds list of objects to display. Mainly used for debugging"""
    def __init__(self, objs=list(), module='__main__'):
        assert type(objs) == list, 'Not a list of strings'

        self.objs = objs
        self.module = module
        
    def add(self, var):
        if type(var) == list:
            for v in var:
                (self.objs).append(v)
        elif type(var) == str:
            (self.objs).append(var)
            
    def remove(self, var):
        if type(var) == list:
            for v in var:
                (self.objs).remove(v)
        elif type(var) == str:
            (self.objs).remove(var)
            
    def show(self):
        groupdict = self.get_dict()
        for ob in self.objs:
            print(ob, groupdict[ob])
            
    def get_dict(self):
        return _sys.modules[self.module].__dict__

    def write_file(self, filename):
        string = 'stat_dict = {}'.format(self.get_dict())
        with open(filename,'w') as fp:
            fp.write(string)

class MVAverage(object):
    """Object that maintains length when items are added
    A simple example:
        from random import randint
        from time import sleep
        myav = MVAverage(max_size=5)
        while True:
            myav.append(randint(0, 20))
            print('len', len(myav))
            print('av', myav.get_average())
            sleep(1)

    """
    def __init__(self, ls=list(), max_size=10):
        self.ls = ls[:]
        self.max_size = max_size
        if len(self.ls):
            self.__set_average()

    def __len__(self):
        return len(self.ls)

    def __clean(self):
        while len(self.ls) > self.max_size:
            (self.ls).pop(0)

    def __set_average(self):
        self.__av = sum(self.ls)/len(self.ls)

    def append(self, item):
        (self.ls).append(item)
        self.__clean()
        self.__set_average()

    def get_average(self):
        return self.__av

class SortableDict(_collections.OrderedDict):
    """Sortable dict, child of collections.OrderedDict"""
    def sort(self, reverse=False, debug=False):
        part = list(self.keys()) # extract keys
        part.sort(reverse=reverse) # sorts keys
        if debug:
            print('sorted keys =', part)
        copy = self.copy()
        self.clear()
        for key in part:
            self[key] = copy[key]

if __name__ == '__main__':
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

    a = 'string'
    b = int(4)
    c = dict()
    s = Group(['a', 'b', 'c'])
    print('before add')
    s.show()
    d = float(542.2)
    s.add('d')
    print('after add')
    s.show()
    s.write_file('group_test.txt')
