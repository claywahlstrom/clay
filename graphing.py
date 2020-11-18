
"""
Graphing: basic structures for visualizing data


"""

import operator as _operator
import sys as _sys

from clay.settings import CONSOLE_WIDTH
from clay.utils import SortableDict as _SortableDict

class Graph(object):

    """Used to graph two-dimensional data"""

    SHORT_LENGTH = 30

    def __init__(self, data, title=None, max_width=CONSOLE_WIDTH, sort=True):
        """Initializes this graph with the given data, title, width, and sort option"""
        if type(data) is _SortableDict:
            sd = data
        else:
            if not isinstance(data, dict):
                raise TypeError('data needs to be in key-value pairs')

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
        """Returns the string representation of this graph"""
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self.sd.items()))

    def build(self, limit=0, shorten_keys=False, with_count=False):
        """Builds the graph and prints it to stdout"""
        longest_key_len = max(map(lambda x: len(str(x)), self.sd.keys()))
        longest_value_len = max(map(lambda x: len(str(x)), self.sd.values()))
        max_value = max(self.sd.values())
        width = self.max_width - 1 # account for the key-value spacer
        if with_count:
            # account for the count spacer and parens
            width -= longest_value_len + 3
        if shorten_keys or longest_key_len >= width:
            width -= Graph.SHORT_LENGTH
            longest_key_len = Graph.SHORT_LENGTH
        # if the max value stays within the width
        if max_value <= width:
            using = 'ints'
        else:
            using = 'floats'

        print('        Graph for', self.title)
        print('            limit', limit)
        print('  longest key len', longest_key_len)
        print('longest value len', longest_value_len)
        print('      graph width', width)
        print('        max width', self.max_width)
        print('        max value', max_value)
        print('            using', using)
        print('       with count', with_count)
        shorten_wings = 5 * ((Graph.SHORT_LENGTH - 3) // 10)
        for i, (k, v) in enumerate(self.sd.items()):
            if shorten_keys and len(k) > Graph.SHORT_LENGTH:
                k = k[:shorten_wings] + '...' + k[-shorten_wings:]
            print('{:>{}}'.format(k, longest_key_len), end=' ')
            if with_count:
                print('({:>{}})'.format(v, longest_value_len), end=' ')
            try:
                if using == 'ints':
                    print('0' * int(v))
                else:
                    print('0' * int(v / max_value * width))
            except Exception as e:
                print(e)
            if limit != 0 and i >= limit:
                break

        # graphed attributes
        self.limit = limit
        self.longest_key_len = longest_key_len
        self.longest_value_len = longest_value_len
        self.width = width
        self.max_value = max_value
        self.using = using
        self.with_count = with_count

    def sort_by(self, name, reverse=False):
        """
        Sorts the graph data by the given name (column or count,
        raises `ValueError` if other)

        """
        if name not in ('column', 'count'):
            raise ValueError('name must be column or count')
        std = sorted(self.sd.items(), key=_operator.itemgetter(('column', 'count').index(name)), reverse=reverse)
        self.sd.clear()
        for i,j in enumerate(std):
            self.sd[j[0]] = j[-1]

class Histogram(Graph):
    """
    Counts objects into groups for histogram analysis.

    Consumes columns as a range of values, required
    Consumes str or bytes as text, optional

    Initial values for each group is zero if no text is supplied.

    Always safe to have max_width be one less than the actual screen width.

    """

    def __init__(self, columns=None, data=None, title=None,
            max_width=CONSOLE_WIDTH, sort=True):
        """Initializes this histogram"""
        if columns is not None and type(columns) not in (tuple, list):
            raise TypeError('columns must be of type tuple')

        if isinstance(data, bytes):
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
    if not hasattr(dictionary, 'keys'):
        raise TypeError('dictionary must derive from type dict')
    if len(name) > 0:
        print(name.upper())
        print('-' * 30)
    largestlen = max(map(lambda key: len(str(key)), list(dictionary.keys())))
    for i in dictionary:
        print('{:{}} : {}'.format(i, largestlen, dictionary[i]))

def tabulatef(func, start=-5, end=5, step=1, spacing=9,
        precision=10, roundto=14, file=_sys.stdout):
    """
    Prints a table of values from the given a function,
    bounds, step, and output location

    """
    print('Table for {} on [{}, {}]'.format(func.__name__, start, end),  file=file)
    print('-'*30, file=file)
    mapstr = map(str, [start, end, step])
    maxspace = max(map(len, mapstr))
    if start < 0:
        maxspace += 1
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
