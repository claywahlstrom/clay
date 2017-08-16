
"""
misc: imports that don't have their own module
"""

from pack import UNIX

def define(words):
    """Display Cambridge dictionary definitions"""
    from bs4 import BeautifulSoup as bs
    from requests import get
    f = get('https://dictionary.cambridge.org/us/dictionary/english/' + words.split()[0] + '?q=' + words.replace(' ','+')).content
    soup = bs(f, 'html.parser')
    print('definitions for', words.capitalize())
    for i in [g.text for g in soup.select('.entry-body__el .def')]:
        print('    ' + i)

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
        myav = MVAverage(Max=10)
        while True:
            myav.append(randint(0, 20))
            print('len', len(myav))
            print('av', myav.get_average())
            sleep(1)

    """
    def __init__(self, List=[], Max=10):
        self.List = List[:]
        self.Max = Max
        if len(self.List):
            self.__set_average()
    def __len__(self):
        return len(self.List)
    def __clean(self):
        while len(self.List) > self.Max:
            (self.List).pop(0)
    def __set_average(self):
        self.__av = sum(self.List)/len(self.List)
    def append(self, item):
        (self.List).append(item)
        self.__clean()
        self.__set_average()
    def get_average(self):
        return self.__av

if UNIX:
    print("<module 'winsound'> not available")
else:
    from winsound import Beep as note # def

def save(text, name='text.txt'):
    """Save to file with file numbering"""
    from os.path import exists
    SP = name.split('.')
    x = 1
    while True:
        name = SP[0]+str(x)+''.join(SP[1:-1])+'.'+SP[-1]
        if not exists(name):
            break
        x += 1
    with open(name,'w') as s:
        s.write(str(text))
    return name

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

class Title(object):
    """Create proper book titles"""
    skip_list = ['a','am','an','and',
                 'for','in','of',
                 'on','the','to']
    def __init__(self, title):
        self.title = title
        self.create()
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__,self.title)
    def __xcaptilize(self, word):
        if word.lower() not in self.skip_list:
            return word.capitalize()
        return word.lower()
    def create(self):
        words = self.title.split(' ')
        self.__get = ' '.join(map(self.__xcaptilize, words))
        self.__get = self.__get[0].upper() + self.__get[1:]
    def get(self):
        return self.__get

if __name__ == '__main__':
    define('vector quantity')
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

    bt = Title('the best hot dog on a stick')
    print(bt.get())

