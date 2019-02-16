
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

class Linq(object):

    """Class Linq can be used to query and filter data like
       Microsoft's (c) LINQ feature used in C#"""

    MAX_QUERYABLE_LENGTH = 10000

    __queryable_set = False
    __select_called = False

    def __check_queryable_exists():
        if not(Linq.__queryable_set):
            raise RuntimeError('Linq queryable must be set')

    def __check_distinct_projection(distinct):
        if len(Linq.__queryable) > Linq.MAX_QUERYABLE_LENGTH and distinct:
            raise ValueError('Linq cannot process more than ' + \
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
        if not(type(props) in (list, tuple)):
            raise ValueError('properties must be a list or tuple')
        projection = []
        for each in Linq.__queryable:
            if model:
                entity = {}
            else:
                entity = []
            for prop in props:
                if type(each) == dict and prop in each:
                    if model:
                        entity[prop] = each[prop]
                    else:
                        entity.append(each[prop])
                elif type(prop) == int:
                    if prop >= len(each):
                        print('Could not select index {} for {}. Skipping...' \
                            .format(prop, each))
                    else:
                        if model:
                            raise RuntimeError('cannot include properties ' \
                                               'for entity without properties')
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

    def show(self, transformer=lambda x: x, useLocals=None, sort=False):
        """Prints out the key, value pairs for this Watch"""
        groupdict = self.get_dict()
        if useLocals:
            groupdict.update(useLocals)

        objs = self.objs
        if sort:
            objs = sorted(objs, key=lambda x: x.lower())
        
        for ob in objs:
            print(ob, '->', transformer(groupdict[ob]))

    def start_recording(self, useLocals):
        """Records new objects created after this point until end
           recording is called"""
        self._start_locals = useLocals.copy().keys()

    def stop_recording(self, useLocals):
        """Adds the new objects since the recording started to this Watch"""
        unique = (x for x in useLocals if x not in self._start_locals)
        for var in unique:
            self.add(var)

    def write_file(self, filename):
        """Writes this Watch to the given file"""
        string = 'stat_dict = {}'.format(self.get_dict())
        with open(filename,'w') as fp:
            fp.write(string)

if __name__ == '__main__':

    import pprint
    from random import randint

    objs = [Anonymous(a=1), Anonymous(a=2, b=3), Anonymous(a=2, b=1)]

    print(Linq.query(objs).where(lambda x: x.a == 2).first_or_default())
    print(Linq.query([['John', 'Smith', '1/1/2000']]).select([0, 6, 2]))

    test_queryable = [{'num': 1}, {'num': 2}, {'num': 2}, {'num': 3}]

    try:
        Linq.where(lambda x: True)
    except Exception as e:
        print(e)
    try:
        Linq.query(test_queryable).select('num').where(lambda x: x['num'] == 2)
    except Exception as e:
        print('where is after select:', e)
    try:
        print(Linq.query(test_queryable).where(lambda x: x['num'] == 2).select('num'))
    except Exception as e:
        print(e)

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
    print('is watching d should be False =>', s.is_watching('d'))
    print('before add')
    s.show()
    d = float(542.2)
    s.add('d')
    print('is watching d should be True =>', s.is_watching('d'))
    print('after add')
    s.show()
    s.write_file('watch_test.txt')
