

"""
Collection of common and advanced math operations

"""

import math
import statistics

from clay.shell import isUnix as _isUnix

if _isUnix():
    LIMPATH = r'/home/clayton/Desktop/get_liminf.log'
else:
    LIMPATH = r'C:\Python36\Lib\site-packages\clay\get_liminf.log'
### finally clear the file
##with open(LIMPATH, 'w') as fp:
##    pass

average = statistics.mean # def

class Circle(object):
    """A class for managing basic circular functions"""
    def __init__(self, radius):
        self.radius = radius

    def get_circumference(self):
        """Returns the circumference of this circle"""
        return 2 * math.pi * self.radius

    def get_area(self):
        """Returns the area of this circle"""
        return math.pi * self.radius ** 2

    def get_diameter(self):
        """Returns the diameter of this circle"""
        return 2 * self.radius

def cubrt(x):
    """Returns the cubed root of x"""
    return round(x ** (1/3), 12)

def differentiate(f, x, deltax=1e-12):
    """Returns the derivative of the given function at the point x.
       function at a point. File version in PyRepo dir

       deltax = 1e-12 or 1e-11 works best."""
    return (f(x + deltax) - f(x)) / (deltax)

def get_factors(number):
    """Returns a list of factors for the given int"""
    assert type(number) == int, 'type int is required'
    factors = {}
    for num in range(1, number + 1):
        if number % num == 0: # if no remainder
            factors[num] = int(number / num)
    return factors

def get_limit(func, num=0, side=None, step=0.1, dist=1):
    """Returns list of limit values "step" distance apart,
       starting "dist" from num"""
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

def get_M(func, interval):
    """Returns the max M of the given function on the closed interval"""
    assert type(interval) == list or type(interval) == tuple \
           and len(interval) == 2
    m = interval[0]
    mval = abs(func(m))
    for i in interval[1:]:
        if abs(func(m)) > mval:
            m = i
            mval = func(m)
    return m        

def get_mult_of_pi(number):
    """Returns the quotient with divisor as pi"""
    return number / math.pi

def get_roots(a=0, b=0, c=0):
    """Returns a tuple of roots (intersections with the x-axis)
       for conic equations"""
    if not(a and b and c):
        raise Exception('please enter some values')
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        import cmath as math
    root1 = (-b - math.sqrt(discriminant)) / (2 * a)
    root2 = (-b + math.sqrt(discriminant)) / (2 * a)
    return root1, root2

class FractionReducer(object):
    """Class FractionReducer can be used to reduce fractions to
       simplest form"""
    
    def __init__(self, *args):
        """Initializes the reducer to the given `any`, type str preferred"""
        from fractions import Fraction
        f = Fraction(*args)
        self.top, self.bottom = f.numerator, f.denominator
        
    def get_reduced(self):
        """Returns a tuple of the given fraction in its simplest form"""
        return self.top, self.bottom

    def print(self):
        """Prints this fraction in visual representation"""
        print(self.top)
        print('-' * len(str(max(self.top, self.bottom))))
        print(self.bottom)

def integrate(func, interval=None, rects=100000):
    """Returns the integral from the inclusive tuple (a, b) using
       a Riemann sum approximation"""
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
            area += func(x) * ((b - a) / rects)
        except Exception as e:
            print('Error:', e)
        x += (b - a) / rects
    return area

def get_liminf(func, i=1, step_mag=False, log=True):
    """Returns the limit to +infinity. Handles division by zero
       and divergent funcs"""
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
            if i % 1000 == 0 and not(step_mag) or i % 10000 == 0 \
               and step_mag: # mags div by 10**4
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
                if 0 < NEXT / now < 1:
                    print('Series converges')
                    break
                elif abs(NEXT / now) < 1:
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
    """Returns sum for the given series f starting at a.
       Partial sum if b is supplied"""
    if b == None:
        b = 10 ** 4

    print('series summation for', f)
    try:
        f(b)
    except Exception as e:
        print('Factorial in function AND', e)
        b = 80
    if f(b) == 0 or get_liminf(f, i=a, log=log) == 0:
        tot = 0
        for i in range(a, b + 1):
            # print(i, f(i))
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

def newtons_method(f, x):
    """Given a function and float guess, returns the roots using
       Newton's Method"""
    return _newtons_method_helper(f, x, 0)

def _newtons_method_helper(f, x, n):
    """Given expected input and call n, returns expected and throws
       an exception if not"""
    if math.isclose(f(x), 0, rel_tol=1e-9, abs_tol=1e-9):
        return round(x, 9)
    elif n > 200: # max recursion depth
        raise ValueError('no roots for function', f)
    return _newtons_method_helper(f, x - f(x) / differentiate(f, x), n + 1)

class Polar(object):
    """Class Polar can be used to convert from polar to cartesian"""
    def __init__(self, radius, angle):
        self.radius = radius
        self.angle = angle

    def get_x(self):
        return self.radius * math.cos(self.angle)
        
    def get_y(self):
        return self.radius * math.sin(self.angle)
        
class Radical(object):
    """Class Radical can be used to simplify radicals"""
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
        return (len(str(self.left))+2) * ' ' + len(str(self.right)) * '_' \
                + '\n' + '{}-/{}'.format(self.left, self.right)

    def __least_div(self):
        div = list([i for i in range(2, self.right) \
                        if (self.right / (i ** 2)).is_integer()])
        return div[-1] if len(div) > 0 else 1 # ternary operation

def test_limf(x):
    return x / (2 * x - 1)

def test_invtrig(x):
    return math.acos(x)

def test_harmonic(x):
    return 1 / x

def test_alternating(n):
    return (-1) ** n * (1 / n ** 2)

def test_convergent(n):
    return 5 * (2 / 3) ** n

def test_convergent2(n):
    return n ** 2 / math.factorial(2 * n - 1)

def test_quadratic(n):
    return 1 + 2 * n + n ** 2

def test_quadratic2(n):
    return n ** 2 + 1

if __name__ == '__main__':
    print('DEMO')
    print('------------') # 12
    print('FractionReducer(3, 39).print()')
    FractionReducer(3, 39).print()
    print('INTEGRAL from 0 to 1', integrate(test_invtrig, (0, 1)))
    print('LIMIT OF test_harmonic, expected 0.5')
    lim = get_limit(test_harmonic, num=2, side='right', step=0.001, dist=2)
    print(list(lim.values())[-1])

    print('expecting', -1.0)
    print('testing newtons_method: ', newtons_method(test_quadratic, 10))
    try:
        print('expecting ValueError')
        print('testing: ', newtons_method(test_quadratic2, 10))
    except Exception as e:
        print(e)
    print('RADICAL CLASS')
    left = 2
    right = 20
    print('left = {}, right = {}'.format(left, right))
    rad = Radical(left, right)
    print(rad)

    print('LIMITS TO INFINITY')
    print('expecting 0.5')
    print(get_liminf(test_limf, step_mag=True, log=False))
    print('expecting 0.0')
    print(get_liminf(test_harmonic, step_mag=True, log=True))

    print('LIMITS FOR SERIES')
    print(get_series_sum(test_alternating, log=True))

    import clay.graphing as g
    g.graph(test_alternating, 0, 30)

    print('expecting 15')
    print(get_series_sum(test_convergent, a=0))
    print('expecting 1.7449...')
    print(get_series_sum(test_convergent2))

