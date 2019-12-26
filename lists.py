
"""
Basic operations for lines, lists, and files

"""

# possible: rmdup could use "set" object to remove duplicates

import traceback as _traceback

TEST_LIST = ['h', 'e', 'l', 'l', 'o']

def apply(function, vector):
    """Applies the function to the given vector and returns the result
       of the same type"""
    return type(vector)(map(function, vector))

def frange(start, stop, step):
    """Returns a generator that produces a stream of floats from
       start (inclusive) to stop (exclusive) by the given step"""
    if start > stop:
        assert step < 0, 'step must agree with start and stop'
    elif stop > start:
        assert step > 0, 'step must agree with start and stop'
    digits = len(str(step)) - 2 # - 2 to account for "0."
    steps = abs(int(round((stop - start) / step, digits)))
    for x in range(steps):
        yield round(start + x * step, digits)

def join_lines(file, join_sep=', '):
    """Returns the lines of text from the given file (object or str)
       joined by the separator"""
    if type(file) == __builtins__.list:
        return join_sep.join(file)
    elif file.__class__.__module__ == '_io':
        fp = file
    elif type(file) == str:
        fp = open(file, 'r')
    return fp.read().replace('\n', join_sep)

class list(list):

    """Class list contains extension methods that can be used
       to query and filter data like Microsoft's (c) LINQ
       feature used in C#"""

    def first_or_default(self, default=None):
        """Returns the first item in this query or the default if
           the query is empty"""
        return next(iter(self), default)

    def select(self, selector):
        """Returns each element projected into a new form using the selector function"""
        projection = []
        for each in self:
            new_form = None # default form
            try:
                new_form = selector(each)
            except (KeyError, IndexError, TypeError) as ex:
                print('list.select errored on', each)
                _traceback.print_exc()
                raise ex
            projection.append(new_form)
        return list(projection)

    def where(self, predicate):
        """Filters elements based on the given predicate"""
        return list(filter(predicate, self))

    def whereif(self, condition, predicate):
        """Filters elements based on the given condition and predicate"""
        if condition:
            return self.where(predicate)
        else:
            return self

def printall(items):
    """Prints each item from the given items iterable"""
    if type(items) == dict:
        for item in list(items.keys()):
            print(item, ':', items[item])
    else:
        for item in items:
            print(item)

def printlines(content, lines=0, numbered=True):
    """Prints the given content (list of str or str), w/ or w/o line numbers"""
    if type(content) == str:
        with open(content,'r') as f:
            chunks = [x.rstrip() for x in f.readlines()]
    elif type(content) == list:
        chunks = [line.rstrip() for line in lines]
    assert type(chunks) == __builtins__.list

    if not(lines):
        lines = len(chunks)
    chunks = chunks[:lines]
    for num, line in enumerate(chunks):
        if numbered:
            print(str(num).rjust(len(str(lines))), end=' ')
        print(line)

def rmdup(lizt):
    """Returns a non-duplicated version of the given list with order in tact"""
    len_before = len(lizt)
    new = []
    for n in lizt:
        if n not in new:
            new.append(n)
    print(len_before - len(new), 'duplicate(s) removed')
    return new

if __name__ == '__main__':

    from clay.tests import testif

    testif('apply returns correct type (list)',
        type(apply(lambda x: x, [0, 0])),
        __builtins__.list)
    testif('apply returns correct type (tuple)',
        type(apply(lambda x: x, (0, 0))),
        tuple)
    testif('apply returns correct values (floats => ints)',
        apply(int, [0.0, 9.9]),
        [0, 9])
    testif('frange returns correct values',
        list(frange(0, 0.6, 0.1)),
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
    testif('frange returns correct values',
        list(frange(1, 0, -0.25)),
        [1.0, 0.75, 0.5, 0.25])
    testif('frange returns correct values',
        list(frange(0.9, 1.0, 0.1)),
        [0.9])
    testif('frange raises AssertionError when start > stop && step > 0',
        lambda: list(frange(1, 0, 0.25)),
        None,
        raises=AssertionError)
    testif('frange raises AssertionError when stop > start && step < 0',
        lambda: list(frange(0, 1, -0.25)),
        None,
        raises=AssertionError)

    testif('join_lines returns correct string',
        join_lines(TEST_LIST),
        'h, e, l, l, o')

    from clay.utils import Anonymous
    objs = [Anonymous(a=1), Anonymous(a=2, b=3), Anonymous(a=2, b=1)]
    expected_default = Anonymous(a=0)

    testif('list extension "first or default" selects correct element',
        list(objs).where(lambda x: x.a == 2).first_or_default(),
        objs[1])
    testif('list extension "first or default" selects default when no element found',
        list(objs).where(lambda x: x.a == 3).first_or_default(default=expected_default),
        expected_default)
    testif('list extension "select" raises KeyError when key missing',
        lambda: list([{'key': 'value'}]).select(lambda x: x[0]),
        None,
        raises=KeyError)
    testif('list extension "select" raises IndexError when index out of bounds',
        lambda: list([[0]]).select(lambda x: x[1]),
        None,
        raises=IndexError)
    testif('list extension "select" raises TypeError when list indices are of incorrect type',
        lambda: list([[0]]).select(lambda x: x['key']),
        None,
        raises=TypeError)
    testif('list extension "select" selects data from indices',
        list([['John', 'Smith', '1/1/2000']]).select(lambda x: [x[0], x[2]]),
        [['John', '1/1/2000']])

    test_queryable = [{'num': 1}, {'num': 2}, {'num': 2}, {'num': 3}]

    testif('list extensions where-select selects property correctly',
        list(test_queryable).where(lambda x: x['num'] == 2).select(lambda x: x['num']),
        [2, 2])

    printall(TEST_LIST)
    printlines(r'test_files\essay.txt', 4)
    testif('rmdup removes duplicates correctly',
        rmdup(TEST_LIST),
        ['h', 'e', 'l', 'o'])
