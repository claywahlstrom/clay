"""
tables. Makes basic tables and plots
"""

__all__ = ['basic', 'table', 'test_function']

import sys as _sys

def basic(dictionary, name=str()):
    assert type(dictionary) != list
    if name != str():
        print(name.upper())
        print('-'*30)
    largestlen = max(map(len, list(dictionary.keys())))
    for i in dictionary:
        print(str(i) + ' '*(largestlen-len(i)), ':', dictionary[i])

def table(func, start=-5, end=5, step=1, spacing=9, precision=10, roundto=14, file=_sys.stdout):
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
    return x ** (4 / 3) / float(x)

if __name__ == '__main__':

    table(test_function, -2, 10, 1.012791487897, roundto=5)
