
"""
Utilities for Python


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
        if not self:
            return r'Anonymous()'
        return r'Anonymous({})'.format(
            ', '.join(name + '=' + str(getattr(self, name)) for name in self.get_attributes())
        )

    def get_attributes(self):
        attrs = _inspect.getmembers(self, lambda a:not(_inspect.isroutine(a)))
        return [a[0] for a in attrs if a[0].count('__') < 2]

    def to_dict(self):
        result = {}
        for attr in self.get_attributes():
            result[attr] = getattr(self, attr)
        return result

class FixedSizeQueue(object):
    """Object that maintains length when items are added to it."""
    def __init__(self, ls=[], max_size=10):
        self.__ls = _collections.deque(ls[:], max_size)
        self.max_size = max_size

    def __len__(self):
        return len(self.__ls)

    def add(self, element):
        """Adds the given element to the back of the queue"""
        (self.__ls).append(element)

    def get_average(self):
        """Returns the average for this queue if the elements are summable"""
        if len(self.__ls) == 0:
            raise Exception('length must be >= 1')
        return sum(self.__ls) / len(self.__ls)

    def get_list(self):
        """Returns this queue"""
        return self.__ls

class Linq(object):

    """Class Linq can be used to query and filter data like
       Microsoft's (c) LINQ feature used in C#"""

    def __init__(self):
        """Initializes this Linq object"""
        self.__queryable = None
        self.__members = None
        self.__select_called = False

    def __get_query_source(self):
        if self.__members is None:
            query_source = self.__queryable
        else:
            query_source = self.__members
        return query_source

    def first_or_default(self, default=None):
        """Returns the first item in this query or None if empty"""
        if self.__queryable is None or self.__members is None:
            raise RuntimeError('queryable or members cannot be none')
        if len(self.__members) > 0:
            return self.__members[0]
        return default

    def query(self, queryable):
        """Sets the query source using the given queryable"""
        self.__init__() # reset vars
        self.__queryable = queryable
        return self

    def select(self, props):
        """Returns a list of properties selected from each member.
           If used, it must be the last step as it returns items
           and not a Linq object."""
        if type(props) == str:
            props = [props]
        if not(type(props) in (list, tuple)):
            raise ValueError('properties must be a list or tuple')
        filtered = []
        query_source = self.__get_query_source()            
        for each in query_source:
            selectable = []
            for prop in props:
                if type(each) == dict and prop in each:
                    selectable.append(each[prop])
                elif hasattr(each, prop):
                    selectable.append(getattr(each, prop))
                else:
                    print(each, 'does not have property', prop)
                    selectable.append(None)
            if len(props) == 1:
                selectable = selectable[0]
            filtered.append(selectable)
        self.__members = filtered
        self.__select_called = True
        return self

    def to_list(self):
        """Returns this query as a list"""
        return self.__members

    def where(self, lambda_expression):
        """Filters elements where the lambda expression evaluates to True"""
        if self.__select_called:
            raise RuntimeWarning('members cannot be overwritten after select called')
        members = []
        query_source = self.__get_query_source()
        for each in query_source:
            if lambda_expression(each):
                members.append(each)
        self.__members = members
        return self

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

ViewModel = Model # alias

class Watch(object):
    """Holds a list of objects to display. Mainly used for tracking variables
       in the debugging phase of a project."""

    def __init__(self, objs=[], module='__main__'):
        assert type(objs) == list, 'Not a list of strings'

        self.objs = objs
        self.module = module

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.objs)

    def add(self, var):
        """Adds the given object to this Watch"""
        if type(var) == list:
            for v in var:
                (self.objs).append(v)
        elif type(var) == str:
            (self.objs).append(var)
        else:
            raise ValueError()

    def get_dict(self):
        """Returns this Watch's dict"""
        return _sys.modules[self.module].__dict__

    def remove(self, var):
        """Removes the given object from this Watch"""
        if type(var) == list:
            for v in var:
                (self.objs).remove(v)
        elif type(var) == str:
            (self.objs).remove(var)

    def show(self, useLocals=None):
        """Prints out the key, value pairs for this Watch"""
        groupdict = self.get_dict()
        if useLocals:
            groupdict.update(useLocals)
        for ob in self.objs:
            print(ob, '->', groupdict[ob])

    def write_file(self, filename):
        """Writes this Watch to the given file"""
        string = 'stat_dict = {}'.format(self.get_dict())
        with open(filename,'w') as fp:
            fp.write(string)

if __name__ == '__main__':

    import pprint
    from random import randint

    print('--------')
    myav = FixedSizeQueue(max_size=5)
    myav.add(0) # ensures while-loop entry
    while myav.get_average() < 10:
        myav.add(randint(0, 15))
        print('list', myav.get_list())
        print('  len', len(myav))
        print('  av ', myav.get_average())
    print('--------')

    objs = [Anonymous(a=1), Anonymous(a=2, b=3), Anonymous(a=2, b=1)]

    print(get_first_or_default(objs, 2, 'a'))

    print('human hex for 2700 is', human_hex(2700))
    array = (1, 4, 16, 25)
    print('map args for', array, '->', map_args(_map_args_test, array, z = 4))

    obj = Anonymous({
        'one': 1,
        'two': 2,
        'three': 3
    })
    print('prints', obj.one, '-> expects 1')
    print('prints', obj.two, '-> expects 2')
    print('prints', obj.three, '-> expects 3')
    print('get attrs prints', len(obj.get_attributes()) == 3, '-> expects True')

    person = {'friends': [{'id': 0, 'name': 'Carla James'},
                          {'id': 1, 'name': 'Patel Lewis'},
                          {'id': 2, 'name': 'Lacey Brady'}],
              'isActive': True, 'name': 'Celia Vaughan',
              'gender': 'female', 'age': 36,
              'greeting': 'Hello, Celia Vaughan! You have 7 unread messages.',
              'longitude': -69.800663, 'balance': '$3,701.90'}

    print('before sort')
    print(person)
    celia = SortableDict(person)
    celia.sort()
    print('after sort')
    pprint.pprint(celia)

    a = 'string'
    b = int(4)
    c = {}
    s = Watch(['a', 'b', 'c'])
    print('before add')
    s.show()
    d = float(542.2)
    s.add('d')
    print('after add')
    s.show()
    s.write_file('watch_test.txt')
