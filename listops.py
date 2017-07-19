"""
Basic operations for lines, lists, and files
"""

# possible: rmdup could use "set" object to remove duplicates

TEST_LIST = list(['h','e','l','l','o'])

def jnrows(arg, sep=', '):
    """Join rows of a file to a line with sep, defaults to ', '
    Returns a string
    """
    if type(arg) == list:
        return sep.join(arg)
    elif arg.__class__.__module__ == '_io':
        f = arg
    elif type(arg) == str:
        f = open(arg, 'r')
    return f.read().replace('\n', sep)

def printall(Items):
    """Print all items in Items"""
    if type(Items) == dict:
        for item in list(Items.keys()):
            print(item, ':', Items[item])
    else:
        for item in Items:
            print(item)

def readmeat(meat, ltr=False, numbers=True):
    """Read meat (list or str), w/ or w/o line numbers."""
    if type(meat) == str:
        with open(meat,'r') as f:
            lines = [x.rstrip() for x in f.readlines()]
    elif type(meat) == list:
        lines = [line.rstrip() for line in lines]
    assert type(lines) == list
    
    if not(ltr):
        ltr = len(lines)
    for line in range(ltr):
        if numbers:
            print(str(line).rjust(len(str(ltr))), lines[line])
        else:
            print(lines[line])

def rmdup(lizt):
    """Return non-duplicated list. Note: NOT A METHOD"""
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
