
"""
Basic operations for lines, lists, and files

"""

# possible: rmdup could use "set" object to remove duplicates

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
    if type(file) == list:
        return join_sep.join(file)
    elif file.__class__.__module__ == '_io':
        fp = file
    elif type(file) == str:
        fp = open(file, 'r')
    return fp.read().replace('\n', join_sep)

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
    assert type(chunks) == list
    
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
        list)
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
    try:
        print(list(frange(1, 0, 0.25)))
    except AssertionError as ae:
        print('AssertionError successfully thrown (start > stop && step > 0)')
    try:
        print(list(frange(0, 1, -0.25)))
    except AssertionError as ae:
        print('AssertionError successfully thrown (stop > start && step < 0)')

    testif('join_lines returns correct string',
        join_lines(TEST_LIST),
        'h, e, l, l, o')
    printall(TEST_LIST)
    printlines(r'test_files\essay.txt', 4)
    testif('rmdup removes duplicates correctly',
        rmdup(TEST_LIST),
        ['h', 'e', 'l', 'o'])
