"""
Basic operations for lines, lists, and files

"""

# possible: rmdup could use "set" object to remove duplicates

TEST_LIST = list(['h', 'e', 'l', 'l', 'o'])

def jnrows(arg, sep=', '):
    """Joins rows of a file to a line with `sep`, defaults to ', '
    Returns a string
    """
    if type(arg) == list:
        return sep.join(arg)
    elif arg.__class__.__module__ == '_io':
        fp = arg
    elif type(arg) == str:
        fp = open(arg, 'r')
    return fp.read().replace('\n', sep)

def printall(items):
    """Prints all items in items"""
    if type(items) == dict:
        for item in list(items.keys()):
            print(item, ':', items[item])
    else:
        for item in items:
            print(item)

def readmeat(meat, lines=0, numbers=True):
    """Reads meat (list or str), w/ or w/o line numbers."""
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
        if numbers:
            print(str(num).rjust(len(str(lines))), end=' ')
        print(line)

def rmdup(lizt):
    """Returns non-duplicated list. Note: NOT A METHOD"""
    len_before = len(lizt)
    new = list()
    for n in lizt:
        if n not in new:
            new.append(n)
    print(len_before - len(new), 'duplicate(s) removed')
    return new

if __name__ == '__main__':
    print(jnrows(TEST_LIST))
    printall(TEST_LIST)
    readmeat('essay.txt', 4)
    rmdup(TEST_LIST)
