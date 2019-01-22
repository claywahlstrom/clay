

"""
Collection of common and advanced math operations

"""

import math
import statistics

from clay.shell import is_unix as _is_unix

if _is_unix():
    LIMPATH_FMT = r'/home/clay/Desktop/liminf-{}.log'
else:
    LIMPATH_FMT = r'C:\Python37\Lib\site-packages\clay\liminf-{}.log'

TESTS = {
    'alternating': lambda n: (-1) ** n * (1 / n ** 2),
    'convergent': lambda n: 5 * (2 / 3) ** n,
    'convergent1': lambda x: x / (2 * x - 1),
    'convergent2': lambda n: n ** 2 / math.factorial(2 * n - 1),
    'harmonic': lambda n: 1 / n,
    'invtrig': lambda x: math.acos(x),
    'quadratic': lambda n: 1 + 2 * n + n ** 2,
    'quadratic2': lambda n: n ** 2 + 1
}

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

def differential(f, x, deltax=1e-12):
    """Returns the derivative of the given function at the point x.
       function at a point. File version in PyRepo dir

       deltax = 1e-12 or 1e-11 works best."""
    return (f(x + deltax) - f(x)) / (deltax)
    
def factors(number):
    """Returns a list of factors for the given int"""
    if type(number) != int:
        raise ValueError('number must be an int')
    factors = {}
    for num in range(1, number + 1):
        if number % num == 0: # if no remainder
            factors[num] = int(number / num)
    return factors

def print_fraction(fraction):
    if type(fraction).__name__ != 'Fraction':
        raise ValueError('fraction must be of type Fraction, found %s' % type(fraction).__name__)
    num = fraction.numerator
    den = fraction.denominator
    print(num)
    print('-' * len(str(max(num, den))))
    print(den)

def integral(func, interval=None, rects=100000):
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

def liminf(func, i=1, step_mag=False, logging=None):
    """Returns the limit to +infinity. Handles division by zero
       and divergent funcs"""
       
    if logging is not None:
        if type(logging) == str:
            file = open(logging, 'w')

        print('liminf for', func, file=file)

    while True:
        try:
            now = func(i)
            pr = False
            if i % 1000 == 0 and not(step_mag) or i % 10000 == 0 \
               and step_mag: # mags div by 10**4
                pr = True
                if logging is not None:
                    print(i, end=', ', file=file)
                    print('now', now, end=', ', file=file)

            if step_mag:
                NEXT = func(i*10)
            else:
                NEXT = func(i+1)

            if pr and logging is not None:
                print('NEXT', NEXT, file=file)

            if now == NEXT:
                break
            elif i > 10**32 and step_mag or not(step_mag) and i > 10**6:
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
            if logging is not None:
                print(e, file=file)
            break

    if logging is not None:
        file.close()
    return round(now, 10)

def limit(func, num=0, side=None, step=0.1, dist=1):
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

def max_M(func, interval):
    """Returns the max M of the given function on the closed interval"""
    if not(type(interval) in (list, tuple)) and len(interval) != 2:
        raise ValueError('interval must be iterable and have two values')
    step = 0.001
    m = interval[0]
    mval = abs(func(m))
    for i in range(m, interval[1] + step, step):
        if abs(func(m)) > mval:
            m = i
            mval = abs(func(m))
    return m        

def multiplicity(q, N):
    """Returns the multiplicity Omega given the number of objects
       distribute q and the number of objects to distribute to N"""
    return int(math.factorial(q + N - 1) / (math.factorial(q) * math.factorial(N - 1)))

def nchoosek(n, k):
    """Returns the number of combinations of n items taken k at a time"""
    if n < k:
        return 0
    return int(math.factorial(n) / (math.factorial(k) * math.factorial(n - k)))
    
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
    def __init__(self, outside, inside):
        self.left = outside
        self.right = inside
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

def roots(a=0, b=0, c=0):
    """Returns a tuple of roots (intersections with the x-axis)
       for conic equations"""
    if not(a and b and c):
        raise Exception('please enter some values')
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        import cmath as m
    else:
        m = math
    root1 = (-b - m.sqrt(discriminant)) / (2 * a)
    root2 = (-b + m.sqrt(discriminant)) / (2 * a)
    return root1, root2
    
def roots_newtons_method(f, x):
    """Given a function and float guess, returns the roots using
       Newton's Method"""
    return _roots_newtons_method_helper(f, x, 0)

def _roots_newtons_method_helper(f, x, n):
    """Given expected input and call n, returns expected and throws
       an exception if not"""
    if math.isclose(f(x), 0, rel_tol=1e-9, abs_tol=1e-9):
        return round(x, 9)
    elif n > 200: # max recursion depth
        raise ValueError('no roots for {}'.format(f))
    return _roots_newtons_method_helper(f, x - f(x) / differential(f, x), n + 1)

def series_sum(f, a=1, b=None, logging=True):
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
    if f(b) == 0 or liminf(f, i=a, logging=logging) == 0:
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
        
if __name__ == '__main__':

    from fractions import Fraction

    from clay.tests import it

    print('DEMO')
    print('------------') # 12 count
    print('Printing fraction 3/39...')
    print_fraction(Fraction(3, 39))
    it('returns correct integral for inverse trig from 0 to 1',
        integral(TESTS['invtrig'], (0, 1)), 1.0,
        transformer=lambda x: round(x, 4))
    it('limit of harmonic function returns double close to 0.5',
        limit(TESTS['harmonic'], num=2, side='right', step=0.001, dist=2), 0.5,
        transformer=lambda x: round(list(x.values())[-1], 9)) # compare to math.isclose

    print('LIMITS TO INFINITY')
    it('limit to infinity for converging function is 1/2',
        liminf(TESTS['convergent1'], step_mag=True,
            logging=LIMPATH_FMT.format('convergent1')), 0.5)
    it('limit to infinity for converging function is 0.0',
        liminf(TESTS['harmonic'], step_mag=True,
            logging=LIMPATH_FMT.format('harmonic')), 0.0)
    
    it('multiplicity returns correct quantity for (4, 3)',
        multiplicity(4, 3), 15)

    it('returns correct root using Newton\'s method',
        roots_newtons_method(TESTS['quadratic'], 10), -1.0,
        transformer=lambda x: round(x, 4))
    try:
        print('Newton\'s method for quadratic should throw ValueError')
        roots_newtons_method(TESTS['quadratic2'], 10)
    except Exception as e:
        print('Exception: %s' % e)
    print()
    print('RADICAL CLASS')
    left = 2
    right = 20
    print('left = {}, right = {}'.format(left, right))
    rad = Radical(left, right)
    print(rad)
    print()
    print('LIMITS FOR SERIES')
    print(series_sum(TESTS['alternating'], logging=LIMPATH_FMT.format('alternating')))

    import clay.graphing as g
    g.tabulatef(TESTS['alternating'], 0, 10)

    it('returns correct series sum for convergent function',
        series_sum(TESTS['convergent'], a=0), 15)
    it('returns correct series sum for convergent2 function',
        series_sum(TESTS['convergent2']), 1.7449,
        transformer=lambda x: round(x, 4))

