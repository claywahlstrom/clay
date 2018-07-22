
"""
Basic operations for lines, lists, and files

"""

# possible: rmdup could use "set" object to remove duplicates

TEST_LIST = list(['h', 'e', 'l', 'l', 'o'])

def joinlines(file, sep=', '):
    """Reads and returns the lines of text from the
       given file (object or str) joined by ', '"""
    if type(arg) == list:
        return sep.join(arg)
    elif arg.__class__.__module__ == '_io':
        fp = arg
    elif type(arg) == str:
        fp = open(arg, 'r')
    return fp.read().replace('\n', sep)

def printall(items):
    """Prints each item in items"""
    if type(items) == dict:
        for item in list(items.keys()):
            print(item, ':', items[item])
    else:
        for item in items:
            print(item)

def readlines(meat, lines=0, numbered=True):
    """Reads the given meat (list of str or str), w/ or w/o lines numbered."""
    if type(meat) == str:
        with open(meat,'r') as f:
            chunks = [x.rstrip() for x in f.readlines()]
    elif type(meat) == list:
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
    """Returns a non-duplicated version of the given list"""
    len_before = len(lizt)
    new = list()
    for n in lizt:
        if n not in new:
            new.append(n)
    print(len_before - len(new), 'duplicate(s) removed')
    return new

if __name__ == '__main__':
    print(joinlines(TEST_LIST))
    printall(TEST_LIST)
    readlines('essay.txt', 4)
    rmdup(TEST_LIST)
