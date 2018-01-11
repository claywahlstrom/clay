"""
Collection of common and advanced math operations
"""

import math
import statistics

from clay import isUnix as _isUnix

if _isUnix():
    LIMPATH = r'/home/clayton/Desktop/get_liminf.log'
else:
    LIMPATH = r'C:\Python36\Lib\site-packages\clay\get_liminf.log'
### finally
##with open(LIMPATH, 'w') as fp:
##    pass

average = statistics.mean # def

class Circle(object):
    """A class for managing basic circular functions"""
    def __init__(self, radius):
        self.radius = radius

    def get_circumference(self):
        return 2 * math.pi * self.radius

    def get_area(self):
        return math.pi * self.radius ** 2

    def get_diameter(self):
        return 2 * self.radius

def cubrt(x):
    """Returns the cubed root of x"""
    return round(x ** (1/3), 12)

def differentiate(f, x, deltax=1e-12):
    """Returns derivative of a function at a point. File version in PyRepo dir

    deltax = 1e-12 or 1e-11 works best."""
    return (f(x + deltax) - f(x)) / (deltax)

def get_factors(num, max_divisor=1000000):
    """Returns a list of factors for the supplied int"""
    assert type(num) == int, 'type int is required'
    factors = list()
    for num in range(1, max_divisor):
        if number % num == 0: # if no remainder
            factors[num] = int(number/num)
    return factors

def get_limit(func, num=0, side=None, step=0.1, dist=1):
    """Returns list of limit values "step" distance apart,
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

def get_mult_of_pi(num):
    """Returns the quotient with divisor as pi"""
    return num / math.pi

def get_roots(a=0, b=0, c=0):
    """Returns a tuple of roots (intersections with the x-axis) for conic equations"""
    if not(a and b and c):
        raise Exception('please enter some values')
    import math
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        import cmath as math
    root1 = (-b - math.sqrt(discriminant))/ (2 * a)
    root2 = (-b + math.sqrt(discriminant))/ (2 * a)
    return root1, root2

def get_smallest_fraction(*args, show=False):
    """Returns a tuple of the given fraction in its simplest form"""
    from fractions import Fraction
    f = Fraction(*args)
    top, bottom = f.numerator, f.denominator
    if show:
        print(top)
        print('-'*max(map(len, map(str, [top, bottom]))))
        print(bottom)
    return top, bottom

def integrate(func, interval=None, rects=10000):
    """Integrates from inclusive tuple (a, b)"""
    if interval is None:
        interval = eval(input("Interval (a, b): "))
    a, b = interval
    if a > b:
        print('note: the calculated area will be negative')
    if b - a > rects:
        rects = b - a
    area = 0
    x = a
    for n in range(rects):
        try:
            area += func(x) * ((b - a) / rsects)
        except Exception as e:
            print('Error:', e)
        x += (b - a) / rects
    return area

def get_liminf(func, i=1, step_mag=False, log=True):
    """Returns the limit to +infinity. Handles division by zero and divergent funcs"""
    if log:
        file = open(LIMPATH, 'w')
        print('get_liminf for', func)
    else:
        from sys import stdout as file

    print('get_liminf for', func, file=file)

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

def get_series_sum(f, a=1, b=None, log=True):
    """Returns sum for series 'f' starting at 'a'. Partial sum if 'b' supplied"""
    if b == None:
        b = 10**4

    print('series summation for', f)
    try:
        f(b)
    except Exception as e:
        print('Factorial in function AND', e)
        b = 80
    if f(b) == 0 or get_liminf(f, i=a, log=log) == 0:
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

# natural log
ln = math.log #def

median = statistics.median # def

class Polar(object):
    """A class to convert from polar coords to cartesian"""
    def __init__(self, radius, angle):
        self.radius = radius
        self.angle = angle

    def get_x(self):
        return self.radius * math.cos(self.angle)
        
    def get_y(self):
        return self.radius * math.sin(self.angle)
        
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
        div = list([i for i in range(2, 1000) if (self.right / (i ** 2)).is_integer()])
        return div[-1] if len(div) > 0 else 1 # ternary operation

def test_f(x):
    return x / (2 * x - 1)

def test_g(x):
    return math.acos(x)

def test_h(x):
    return 1 / x

def test_i(n):
    return (-1) ** n * (1 / n ** 2)

def test_j(n):
    return 5 * (2 / 3) ** n

def test_k(n):
    return n ** 2 / math.factorial(2 * n - 1)

if __name__ == '__main__':
    print('get_smallest_fraction')
    top, bottom = get_smallest_fraction(3, 39, show=True)
    print('INTEGRAL from 0 to 1', integrate(test_g, (0, 1)))
    print('LIMIT OF test_h, expected 0.5')
    lim = get_limit(test_h, num=2, side='right', step=0.001, dist=2)
    print(list(lim.values())[-1])

    print('RADICAL CLASS')
    left = 2
    right = 20
    print('left = {}, right = {}'.format(left, right))
    rad = Radical(left, right)
    print(rad)

    print('LIMITS TO INFINITY')
    print(get_liminf(test_f, step_mag=True, log=False))
    print('expected 0.5')
    print(get_liminf(test_h, step_mag=True, log=True))
    print('expected 0.0')

    print('LIMITS FOR SERIES')
    print(get_series_sum(test_i, log=True))

    import clay.graphing as g
    g.tabulate(test_i, 0, 30)

    print(get_series_sum(test_j, a=0))
    print('expected 15')
    print(get_series_sum(test_k))
    print('expected 1.7449...')


