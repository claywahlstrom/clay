
"""
misc: imports that don't have their own module yet
"""

from pack import UNIX

def human_hex(dec):
    """Convert decimal values to human readable hex.
    Mainly used in engineering class
    """
    return hex(dec)[2:]

def map_args(function, iterable, *args, **kwargs):
    """map iterable to a function with arguments/keywords.\nDynamic types"""
    return type(iterable)(function(x, *args, **kwargs) for x in iterable)

class MVAverage(object):
    """``list`` object that maintains length when items are added
    A simple example seen here:
        from random import randint
        from time import sleep
        myav = MVAverage(max_size=10)
        while True:
            myav.append(randint(0, 20))
            print('len', len(myav))
            print('av', myav.get_average())
            sleep(1)

    """
    def __init__(self, ls=[], max_size=10):
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

if UNIX:
    print("<module 'winsound'> not available")
else:
    from winsound import Beep as note # def

import collections
class SortableDict(collections.OrderedDict):
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

    print(human_hex(2700))

    def func(x, y = 2, z = 3):
        return x + y + z
    print(map_args(func, (1, 4, 16, 25), z = 4))

    print('BEEP!')
    note(880, 100)

    skeleton = {'friends': [{'id': 0, 'name': 'Carla James'},
                            {'id': 1, 'name': 'Patel Lewis'},
                            {'id': 2, 'name': 'Lacey Brady'}],
                'isActive': True, 'name': 'Celia Vaughan',
                'gender': 'female', 'age': 36,
                'greeting': 'Hello, Celia Vaughan! You have 7 unread messages.',
                'longitude': -69.800663, 'balance': '$3,701.90'}

    print(skeleton, type(skeleton))
    celia = SortableDict(skeleton)
    print(celia, type(celia))


