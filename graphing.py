"""
Graphing: basic graphing data structures

histogram: Make histograms to visualize data frequency
tables: Make basic tables and plots

"""

import sys as _sys

from clay.clusters import SortableDict as _SortableDict

SCREEN_WD = 80

def tabulate(dictionary, name=str()):
    """Prints a basic table from the given dictionary called `name`"""
    assert type(dictionary) != list
    if name != str():
        print(name.upper())
        print('-'*30)
    largestlen = max(map(len, list(dictionary.keys())))
    for i in dictionary:
        print(str(i) + ' '*(largestlen-len(i)), ':', dictionary[i])

def graph(func, start=-5, end=5, step=1, spacing=9, precision=10, roundto=14, file=_sys.stdout):
    """Prints a table of values from the given a function, bounds, step, and output location"""
    print(str(func), file=file)
    print('-'*30, file=file)
    mapstr = map(str, [start, end, step])
    maxspace = max(map(len, mapstr))
    i = start
    while start <= i <= end:
        numstring = str(round(i, precision))
        print(numstring + ' '*int(maxspace-len(numstring)), '|', end=' ', file=file)
        try:
            print(round(func(i), roundto), file=file)
        except TypeError as te:
            print(func(i), file=file)
        except KeyError as ke:
            print('Error:', ke, file=file)
        except ZeroDivisionError:
            print('undefined', file=file)
        except ValueError:
            print('domain error', file=file)
        i = round(i + step, 14)

def test_function(x):
    """Function for testing `table`"""
    return x ** (4 / 3) / float(x)

class Histogram(object):
    """Counts objects into groups for histogram analysis.

    Consumes columns as a range of values, required
    Consumes str or bytes as text, optional

    Initial values for each groups is zero if no text is supplied
    """
    def __init__(self, columns=None, iterable=None, title=None, max_width=SCREEN_WD):
        if not columns is None:
            assert type(columns) == tuple or type(columns) == list, 'columns need to be tuple'
        if type(iterable) == bytes:
            iterable = iterable.decode('utf8', errors='ignore')
        if columns and not iterable:
            sd = _SortableDict({col: 0 for col in columns})
        else:
            sd = _SortableDict({col: iterable.count(col) for col in columns})
        sd.sort()

        self.cols = columns
        self.sd = sd
        self.iterable = iterable
        if title is None:
            title = str(list(sd.keys())[:4]) + ' ...'
        self.title = title
        self.max_width = max_width

    def build(self):
        if type(self.cols[0]) == str:
            max_element = str()
            for elm in self.sd.keys():
                if len(elm) > len(max_element):
                    max_element = elm
            large_key = len(max_element)
            width = self.max_width - 1 - large_key
        else: # for ints and floats
            max_element = max(list(self.sd.keys()))
            large_key = len(str(max_element))
            width = self.max_width - 1 - len(str(large_key))

        max_val = max(list(self.sd.values()))

        print('Histogram for', self.title)
        print('width', width)
        print('max val', max_val)
        for (k, v) in self.sd.items():
            print('{:>{}}'.format(k, large_key), '0'*int(width*v/max_val))
        self.max_val = max_val
        self.large_key = large_key
        self.width = width

    def byvalue(self, reverse=False):
        import operator
        std = sorted(self.sd.items(), key=operator.itemgetter(1), reverse=reverse)
        self.sd.clear()
        for i,j in enumerate(std):
            self.sd[j[0]] = j[-1]
    
if __name__ == '__main__':
    s = Histogram(('bc', 'sac', 'aaa'), 'abbcssaaaaaaaaaaacccssacbbcaddsaacc')
    s.build()
    
    graph(test_function, -2, 10, 1.012791487897, roundto=5)
