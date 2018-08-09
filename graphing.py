
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
        print('-' * 30)
    largestlen = max(map(len, list(dictionary.keys())))
    for i in dictionary:
        print(str(i) + ' ' * (largestlen - len(i)), ':', dictionary[i])

def graph(func, start=-5, end=5, step=1, spacing=9,
          precision=10, roundto=14, file=_sys.stdout):
    """Prints a table of values from the given a function,
       bounds, step, and output location"""
    print(str(func), file=file)
    print('-'*30, file=file)
    mapstr = map(str, [start, end, step])
    maxspace = max(map(len, mapstr))
    i = start
    while start <= i <= end:
        numstring = str(round(i, precision))
        print(numstring + ' ' * int(maxspace - len(numstring)), '|',
              end=' ', file=file)
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

    Initial values for each group is zero if no text is supplied.

    Always safe to have max_width be one less than the actual screen width.

    """

    SHORT_LENGTH = 30

    def __init__(self, columns=None, iterable=None,
                 title=None, max_width=SCREEN_WD, sort=True):
        if not columns is None:
            assert type(columns) == tuple or \
                   type(columns) == list, 'columns need to be tuple'
        if type(iterable) == bytes:
            iterable = iterable.decode('utf8', errors='ignore')
        sd = _SortableDict()
        if columns and not iterable:
            for col in columns:
                sd[col] = 0
        else:
            columns = iterable
            for col in columns:
                sd[col] = iterable.count(col)
        if sort:
            sd.sort()

        if title is None:
            title = '['
            for i in list(sd.keys())[:3]:
                title += "'{}', ".format(i)
            title += "..., '{}']".format(list(sd.keys())[-1])
        self.title = title
        self.cols = columns
        self.sd = sd
        self.iterable = iterable
        self.max_width = max_width

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self.sd.items()))

    def build(self, limit=0, shorten_keys=False, with_count=False):
        if type(self.cols[0]) == str:
            longest_key_len = max(map(len, map(str, list(self.sd.keys()))))
        else: # for ints and floats
            # longest str repr of a number
            longest_key_len = len(str(max(list(self.sd.keys()))))
        base_longest_key_len = longest_key_len
        if all(type(x) == int for x in self.sd.values()):
            # if integers, just print out one per count
            width = min(max(self.sd.values()), SCREEN_WD)
            using = 'ints'
        else:
            # otherwise, adjust width for better representation of floats
            width = self.max_width
            using = 'floats'
        if with_count:
            max_count_len = max(map(len, map(str, list(self.sd.values()))))
            width -= 3 - max_count_len
        if longest_key_len > width:
            print('Using shortened keys')
            shorten_keys = True
            longest_key_len = Histogram.SHORT_LENGTH
        max_val = max(list(self.sd.values()))

        print('  Histogram for', self.title)
        print('longest key len', longest_key_len)
        print('          width', width)
        print('        max val', max_val)
        print('          using', using)
        print('     with count', with_count)
        shorten_wings = 5 * ((Histogram.SHORT_LENGTH - 3) // 10)
        for i, (k, v) in enumerate(self.sd.items()):
            if shorten_keys and len(k) > Histogram.SHORT_LENGTH:
                k = k[:shorten_wings] + '...' + k[-shorten_wings:]
            print('{:>{}}'.format(k, longest_key_len), end=' ')
            if with_count:
                print('({:>{}})'.format(v, max_count_len), end=' ')
            try:
                if using == 'ints' and base_longest_key_len < width and \
                   v <= SCREEN_WD - longest_key_len - 1:
                    print('0' * int(v))
                else:
                    print('0' * int(v * width / max_val))
            except Exception as e:
                print(e)
            if limit != 0 and i >= limit:
                break
        self.max_val = max_val
        self.longest_key_len = longest_key_len
        self.width = width

    def sortbycount(self, reverse=False):
        import operator
        std = sorted(self.sd.items(), key=operator.itemgetter(1), reverse=reverse)
        self.sd.clear()
        for i,j in enumerate(std):
            self.sd[j[0]] = j[-1]

if __name__ == '__main__':
    s = Histogram(('bc', 'sac', 'aaa'), 'abbcssaaaaaaaaaaacccssacbbcaddsaacc')
    s.build()

    graph(test_function, -2, 10, 1.012791487897, roundto=5)
