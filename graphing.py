
"""
Graphing: basic structures for visualizing data


"""

from collections import OrderedDict as _OrderedDict
import operator as _operator
import sys as _sys

from clay.util import SortableDict as _SortableDict

SCREEN_WD = 80

class Graph(object):

    SHORT_LENGTH = 30

    def __init__(self, data, title=None, max_width=SCREEN_WD, sort=True):
        if type(data) == _SortableDict:
            sd = data
        else:
            if type(data) not in (_OrderedDict, dict):
                raise ValueError('data needs to be in key-value pairs')

            sd = _SortableDict()
            for indep in data:
                sd[indep] = data[indep]

        if sort:
            sd.sort()

        if title is None:
            title = '['
            for i in list(sd.keys())[:3]:
                title += "'{}', ".format(i)
            title += "..., '{}']".format(list(sd.keys())[-1])

        self.data = data
        self.max_width = max_width
        self.sd = sd
        self.title = title

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self.sd.items()))

    def build(self, limit=0, shorten_keys=False, with_count=False):
        if type(list(self.sd.keys())[0]) == str:
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
        if width + longest_key_len + 1 > SCREEN_WD:
            using = 'floats'
        width = max(width, SCREEN_WD) - longest_key_len - 1
        if with_count:
            max_count_len = max(map(len, map(str, list(self.sd.values()))))
            width -= 3 + max_count_len
        if longest_key_len > width:
            print('Using shortened keys')
            shorten_keys = True
            longest_key_len = Graph.SHORT_LENGTH

        max_val = max(list(self.sd.values()))

        print('      Graph for', self.title)
        print('longest key len', longest_key_len)
        print('    graph width', width)
        print('      max value', max_val)
        print('          using', using)
        print('     with count', with_count)
        shorten_wings = 5 * ((Graph.SHORT_LENGTH - 3) // 10)
        for i, (k, v) in enumerate(self.sd.items()):
            if shorten_keys and len(k) > Graph.SHORT_LENGTH:
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

    def sort_by(self, name, reverse=False):
        if not(name in ('column', 'count')):
            raise ValueError('name must be column or count')
        std = sorted(self.sd.items(), key=_operator.itemgetter(('column', 'count').index(name)), reverse=reverse)
        self.sd.clear()
        for i,j in enumerate(std):
            self.sd[j[0]] = j[-1]

class Histogram(Graph):
    """Counts objects into groups for histogram analysis.

       Consumes columns as a range of values, required
       Consumes str or bytes as text, optional

       Initial values for each group is zero if no text is supplied.

       Always safe to have max_width be one less than the actual screen width.

    """

    def __init__(self, columns=None, data=None, title=None,
                 max_width=SCREEN_WD, sort=True):
        if columns is not None and type(columns) not in (tuple, list):
            raise ValueError('columns needs to be tuple')

        if type(data) == bytes:
            data = data.decode('utf8', errors='ignore')
        sd = _SortableDict()
        if columns and data is None:
            data = [0] * len(columns)
        elif columns is None and data:
            columns = data

        for col in columns:
            if not(col in sd): # prevents overwrite for string data
                sd[col] = data.count(col)

        super(Histogram, self).__init__(sd, title=title, max_width=max_width, sort=sort)

def tabulate(dictionary, name=''):
    """Prints a basic table from the given dictionary called `name`"""
    assert type(dictionary) != list
    if len(name) > 0:
        print(name.upper())
        print('-' * 30)
    largestlen = max(map(len, list(dictionary.keys())))
    for i in dictionary:
        print(str(i) + ' ' * (largestlen - len(i)), ':', dictionary[i])

def tabulatef(func, start=-5, end=5, step=1, spacing=9,
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
    """Function used for testing"""
    return x ** (4 / 3) / float(x)

if __name__ == '__main__':
    s = Histogram(columns=('bc', 'sac', 'aaa'), data='abbcssaaaaaaaaaaacccssacbbcaddsaacc')
    s.build()

    tabulatef(test_function, -2, 10, 1.012791487897, roundto=5)
