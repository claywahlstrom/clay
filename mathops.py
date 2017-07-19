"""
Collection of math operations
"""

import math
import statistics

from pack import LINUX

if LINUX:
    LIMPATH = r'/home/clayton/Desktop/limtoinf.log'
else:
    LIMPATH = r'C:\Python35\Lib\site-packages\pack\limtoinf.log'

with open(LIMPATH, 'w') as f:
    pass


average = statistics.mean # def

def cubrt(x):
    """Return the cubed root of x"""
    return round((x)**(1/3), 12)

def deriv(f, x, deltax=1e-12):
    """Return derivative of a function at a point. File version in #Files dir

    deltax = 1e-12 or 1e-11 works best."""
    return (f(x+deltax)-f(x))/(deltax)

def fracsimp(*args):
    """Simplify fractions"""
    from fractions import Fraction
    f = Fraction(*args)
    top, bottom = f.numerator, f.denominator
##    print(top)
##    print('-'*max(map(len, map(str, [top, bottom]))))
##    print(bottom)
    return top, bottom

def integral(func, interval=None, rects=10000):
    """Integral from tuple (a, b)"""
    if interval is None:
        interval = eval(input("Interval (a,b): "))
    a, b = interval
    if a > b:
        print('note: the calculated area will be negative')
    if b - a > rects:
        rects = b - a
    area = 0
    x = a
    for n in range(rects):
        try:
            area += func(x) * ((b-a)/rects)
        except Exception as e:
            print('Error:', e)
        x += (b-a)/rects
    return area

def limit(func, num=0, side=None, step=0.1, dist=1):
    """Return list of limit values "step" distance apart,
    starting "dist" from num
    """
    from collections import OrderedDict
    lims = OrderedDict()
    if side == 'right':
        x = num + dist
        while x > num:
            try:
                lims[x] = func(x)
            except Exception as e:
                lims[x] = e
            x -= step
        return lims
    else: # left
        x = num - dist
        while x < num:
            try:
                lims[x] = func(x)
            except Exception as e:
                lims[x] = e
            x += step
        return lims

def limtoinf(func, i=1, step_mag=False, log=True):
    """Limit to +infinity. Handles division by zero and divergent funcs"""
    if log:
        file = open(LIMPATH, 'a')
        print('limtoinf for', func)
    else:
        from sys import stdout as file

    print('limtoinf for', func, file=file)

    while True:
        try:
            now = func(i)
            pr = False
            if i % 1000 == 0 and not(step_mag) or i % 10000 == 0 and step_mag: # mags div by 10**4
                pr = True
                print(i, end=', ', file=file)
                print('now', now, end=', ', file=file)

            if step_mag:
                NEXT = func(i*10)
            else:
                NEXT = func(i+1)

            if pr:
                print('NEXT', NEXT, file=file)

            if now == NEXT:
                break
            elif i > 10**64 and step_mag or not(step_mag) and i > 10**6:
                # if function/sequence is decreasing...
                if 0 < NEXT/now < 1:
                    break
                elif abs(NEXT/now) < 1:
                    print('Alternating series (convergent)')
                    break
                else:
                    print("error: Function doesn't converge (i={})".format(i))
                    return None
            if step_mag:
                i *= 10
            else:
                i += 1
        except Exception as e:
            print(e, file=file)
            break

    if log:
        file.close()
    return round(now, 10)

median = statistics.median # def

# natural log
ln = math.log #def

class Radical(object):
    """Class for converting radicals to simplified form"""
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.parent = (self.left, self.right)
        self.__out = self.__least_div()
        self.left *= self.__out
        self.right = int(self.right/(self.__out**2))
    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, (self.left, self.right))
    def __str__(self):
        return (len(str(self.left))+2)*' '+len(str(self.right))*'_'+'\n'+'{}-/{}'.format(self.left, self.right)
    def __least_div(self):
        div = list()
        for i in range(2, 1000):
            if (self.right/(i**2)).is_integer():
                div.append(i)
        if div:
            out = div[-1]
        else:
            out = 1
        return out

def series(f, a=1, b=None, log=True):
    """Return sum for series 'f' starting at 'a'. Partial sum if 'b' supplied"""
    if b == None:
        b = 10**4

    print('series summation for', f)
    try:
        f(b)
    except Exception as e:
        print('Factorial in function AND', e)
        b = 80
    if f(b) == 0 or limtoinf(f, i=a, log=log) == 0:
        tot = 0
        for i in range(a, b+1):
            #print(i, f(i))
            try:
                tot += f(i)
            except Exception as e:
                print(e)
                break
            if f(i) == 0 or i > b: break
        return tot
    else:
        print("Series doesn't converge")
        return None

def test_f(x):
    return x/(2*x-1)

def test_g(x):
    return math.acos(x)

def test_h(x):
    return 1/x

def test_i(n):
    return (-1)**n * (1/n**2)

def test_j(n):
    return 5*(2/3)**n

def test_k(n):
    return n**2/math.factorial(2*n-1)

if __name__ == '__main__':
    print('FRACSIMP')
    top, bottom = fracsimp(3, 39)
    print('INTEGRAL', integral(test_g, (0, 1)))
    print('LIMIT OF test_h, expected 0.5')
    lim = limit(test_h, num=2, side='right', step=0.001, dist=2)
    print(list(lim.values())[-1])

    print('RADICAL CLASS')
    left = 2
    right = 20
    print('left = {}, right = {}'.format(left, right))
    rad = Radical(left, right)
    print(rad)

    print('LIMITS TO INFINITY')
    print(limtoinf(test_f, step_mag=True, log=False))
    print('expected 0.5')
    print(limtoinf(test_h, step_mag=True, log=True))
    print('expected 0.0')

    print('LIMITS FOR SERIES')
    print(series(test_i, log=True))

    import pack.tables as t
    t.table(test_i, 0, 30)

    print(series(test_j, a=0))
    print('expected 15')
    print(series(test_k))
    print('expected 1.7449...')


