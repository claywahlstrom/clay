
"""
Collection of common and advanced math operations

"""

import fractions
import math
import os

from clay.env import is_posix as _is_posix
from clay.lists import apply as _apply
from clay import settings

if _is_posix():
    LIMPATH_FMT = r'/home/clay/Desktop/liminf-{}.log'
else:
    LIMPATH_FMT = os.path.join(settings.PACKAGE_DIR, 'logs', 'liminf-{}.log')

TESTS = {
    'alternating': lambda n: (-1) ** n * (1 / n ** 2),
    'convergent': lambda n: 5 * (2 / 3) ** n,
    'convergent1': lambda x: x / (2 * x - 1),
    'convergent2': lambda n: n ** 2 / math.factorial(2 * n - 1),
    'harmonic': lambda n: 1 / n,
    'imaginary': lambda x: math.sqrt(-1),
    'invtrig': lambda x: math.acos(x),
    'quadratic': lambda n: 1 + 2 * n + n ** 2,
    'quadratic2': lambda n: n ** 2 + 1,
    'quadratic3': lambda x: math.sqrt(0.9 * (1.7 - x) ** 2)
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
    """
    Returns the slope of the given function at the point x
    using the midpoint method. A deltax of 1e-12 or 1e-11
    works best.

    """

    # the following formula is the average between the slopes using
    # the right limit [(f(x + deltax) - f(x)) / deltax] and
    # the left limit [(f(x) - f(x - deltax)) / deltax]
    return (f(x + deltax) - f(x - deltax)) / (2 * deltax)

dfdx = differential # alias

def factors(number):
    """Returns a mapping of factors for the given int"""
    if not isinstance(number, int):
        raise TypeError('number must be an int')
    factors = {}
    for num in range(1, number + 1):
        if number % num == 0: # if no remainder
            factors[num] = int(number / num)
    return factors

def print_fraction(fraction):
    """Prints the the given Fraction in a pretty manner"""
    if not isinstance(fraction, fractions.Fraction):
        raise TypeError('fraction must be of type Fraction, found %s' % type(fraction).__name__)
    num = fraction.numerator
    den = fraction.denominator
    print(num)
    print('-' * len(str(max(num, den))))
    print(den)

def integrate(func, interval=None, rects=100000):
    """
    Returns the result of the integral from the inclusive
    interval (a, b) using a Riemann sum approximation

    """
    if interval is None or not isinstance(interval, tuple):
        interval = eval(input('Interval (a, b): '))
    a, b = interval
    if a > b:
        print('note: the calculated area will be negative')
    if b - a > rects:
        rects = b - a
    area = 0
    x = a
    dx = (b - a) / rects
    for n in range(rects):
        try:
            area += func(x) * dx
        except Exception as e:
            print('Error:', e)
        x += dx
    return area

def liminf(func, i=1, step_mag=False, logging=None):
    """
    Returns the limit to +infinity. Handles division by zero
    and divergent funcs

    """

    file = None

    if logging is not None:
        if not isinstance(logging, str):
            raise TypeError(logging)

        file = open(logging, 'w')
        print('liminf for', func, file=file)

    now = math.nan

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

    if logging and file:
        file.close()
    return round(now, 10)

def limit(func, num=0, side=None, step=0.1, dist=1):
    """
    Returns list of limit values "step" distance apart,
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

def max_M(func, interval):
    """Returns the max M of the given function on a closed interval"""
    if type(interval) not in (list, tuple):
        raise TypeError('interval must be an iterable')
    if len(interval) != 2:
        raise ValueError('interval must have two values')
    step = 0.001
    m = interval[0]
    mval = abs(func(m))
    for i in range(m, interval[1] + step, step):
        if abs(func(m)) > mval:
            m = i
            mval = abs(func(m))
    return m

class Polar(object):
    """Class Polar can be used to convert from polar to cartesian"""
    def __init__(self, radius, theta, phi=math.pi/2):
        self.radius = radius
        self.theta = theta
        self.phi = phi

    @property
    def x(self):
        """The Cartesian x-value"""
        return round(self.radius * math.sin(self.phi) * math.cos(self.theta), 12)

    @property
    def y(self):
        """The Cartesian y-value"""
        return round(self.radius * math.sin(self.phi) * math.sin(self.theta), 12)

    @property
    def z(self):
        """The Cartesian z-value"""
        return round(self.radius * math.cos(self.phi), 12)

class Radical(object):

    """
    Class Radical can be used to simplify radicals

    Properties:
        outside = integer outside the radical
        inside  = integer inside the radical
        parent  = a copy of the radical before simplification

    """

    def __init__(self, outside, inside):
        """Initializes this radical using the given inside and outside integers"""
        if not isinstance(outside, int) or not isinstance(inside, int):
            raise TypeError('outside and inside must be of type int')
        self.outside = outside
        self.inside = inside
        self._parent = None

    def __repr__(self):
        """Returns the representation of this radical"""
        return '%s(%d, %d)' % (self.__class__.__name__, self.outside, self.inside)

    def __str__(self):
        """Returns the string representation of this radical"""
        outside = self.outside if self.outside > 1 else ''
        return (len(str(outside)) + 2) * ' ' + len(str(self.inside)) * '_' \
                + '\n' + '{}-/{}'.format(outside, self.inside)

    def __greatest_power(self, n):
        """Returns the greatest sqaure the inside can be divided by"""
        squares = []
        for i in range(1, self.inside):
            if (self.inside / i ** n).is_integer():
                squares.append(i ** n)
        return squares[-1]

    def __set_parent(self):
        """Sets the parent of this radical"""
        self._parent = Radical(self.outside, self.inside)

    def simplify(self, n=2):
        """Simplifies this radical"""
        self.__set_parent()
        out = self.__greatest_power(n)
        self.outside *= int(out ** (1 / n))
        self.inside = int(self.inside / out)

    @property
    def parent(self):
        """The parent radical"""
        return self._parent

def roots(a=0, b=0, c=0):
    """
    Returns a tuple of roots (intersections with the x-axis)
    for conic equations

    """
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

def roots_approx(positive, initial_guess, dp=0, isclose_dp=9):
    """
    Retuns roots for the given polynomial function positive
    using successive approximation to find the roots to the
    polynomial function.

    Parameters:
        initial_guess = initial guess for a root
        dp            = decimals to round roots to (no rounding if 0)
        isclose_dp    = isclose decimal points for comparison

    """

    def negative(x):
        """
        Returns the complementing negative value for the polynomial
        function

        """
        return -positive(x)

    # math.isclose is introduced in Python 3.5 and thus is not widely
    # supported between versions of Python 3. isclose aims to bridge
    # this gap by rounding the two given digits to the specified number
    # of decimal places
    def isclose(x, y, isclose_dp):
        """
        Returns True if x and y are close up to isclose_dp decimal places,
        False otherwise

        """
        return round(x, isclose_dp) == round(y, isclose_dp)

    roots = []
    x = initial_guess
    for f in (negative, positive):
        try:
            result = f(x)
        except ValueError as ve:
            break
        while not isclose(x, result, isclose_dp):
            x = result
            try:
                result = f(x)
            except ValueError as ve:
                break
        roots.append(result)
    return [root if dp == 0 else round(root, dp) for root in roots]

def roots_newtons_method(f, x):
    """
    Given a function and float guess, returns the roots using
    Newton's Method

    """
    return _roots_newtons_method_helper(f, x, 0)

def _roots_newtons_method_helper(f, x, n):
    """
    Given expected input and call n, returns expected and throws
    an exception if not

    """
    if math.isclose(f(x), 0, rel_tol=1e-9, abs_tol=1e-9):
        return round(x, 9)
    elif n > 200: # if reached max recursion depth
        raise RuntimeError('no roots for {}'.format(f))
    return _roots_newtons_method_helper(f, x - f(x) / differential(f, x), n + 1)

def round_qty(obj, digits=4):
    """
    Rounds the given quantity (iterable or other quantity that
    round can be applied to) to the given number of digits

    """
    if type(obj) in (list, tuple):
        return _apply(round_qty, obj)
    else:
        return round(obj, digits)

def series_sum(f, a=1, b=None, logging=True):
    """
    Returns sum for the given series f starting at a.
    Partial sum if b is supplied

    """
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

    from clay.tests import testif, testraises
    from clay.utils import qualify

    print('Printing fraction 3/39...')
    print_fraction(Fraction(3, 39))

    testif('returns correct value for inverse trig from 0 to 1',
        integrate(TESTS['invtrig'], (0, 1)),
        1.0,
        transformer=lambda x: round(x, 4),
        name=qualify(integrate))
    # TODO: compare rounding to math.isclose
    testif('returns correct value close to 0.5 for harmonic function',
        limit(TESTS['harmonic'], num=2, side='right', step=0.001, dist=2),
        0.5,
        transformer=lambda x: round(list(x.values())[-1], 9),
        name=qualify(limit))

    print('LIMITS TO INFINITY')
    testif('returns 0.5 for converging function towards infinity',
        liminf(TESTS['convergent1'], step_mag=True,
            logging=LIMPATH_FMT.format('convergent1')),
        0.5,
        name=qualify(liminf))
    testif('returns 0.0 for converging function towards infinity',
        liminf(TESTS['harmonic'], step_mag=True,
            logging=LIMPATH_FMT.format('harmonic')),
        0.0,
        name=qualify(liminf))

    testif('returns empty list for polynomials without roots',
        roots_approx(TESTS['imaginary'], 0, 3),
        [],
        name=qualify(roots_approx))
    testif('returns correct roots for polynomials with roots',
        roots_approx(TESTS['quadratic3'], 0, 3, 9),
        [-31.428, 0.828],
        name=qualify(roots_approx))

    testif('returns correct root',
        roots_newtons_method(TESTS['quadratic'], 10),
        -1.0,
        transformer=lambda x: round(x, 4))
    testraises('no root found',
        lambda: roots_newtons_method(TESTS['quadratic2'], 10),
        RuntimeError,
        name=qualify(roots_newtons_method))

    testif('rounds scalar value correctly',
        round_qty(0.00009),
        0.0001,
        name=qualify(round_qty))
    testif('rounds vector values correctly',
        round_qty([0.00009, 0.02004, 1.0]),
        [0.0001, 0.02, 1.0],
        name=qualify(round_qty))

    print()
    print('RADICAL CLASS')
    rad = Radical(2, 20)
    testif('returns correct string for radical with outside',
        rad.__str__(), '   __\n2-/20',
        name=qualify(Radical.__str__))
    rad.simplify()
    testif('returns correct string for simplified radical with outside (n=2)',
        rad.__str__(), '   _\n4-/5',
        name=qualify(Radical.__str__))
    rad3 = Radical(4, 27)
    rad3.simplify(n=3)
    testif('returns correct string simplified radical with outside (n=3)',
        rad3.__str__(), '    _\n12-/1',
        name=qualify(Radical.__str__))
    irreducible_radical = Radical(1, 5)
    irreducible_radical.simplify()
    testif('returns correct string for simplified radical with no outside',
        irreducible_radical.__str__(), '  _\n-/5',
        name=qualify(Radical.__str__))
    print()
    print('LIMITS FOR SERIES')
    print(series_sum(TESTS['alternating'], logging=LIMPATH_FMT.format('alternating')))

    import clay.graphing as g
    g.tabulatef(TESTS['alternating'], 0, 10)

    testif('returns correct value (convergent function)',
        series_sum(TESTS['convergent'], a=0),
        15,
        name=qualify(series_sum))
    testif('returns correct value (convergent2 function)',
        series_sum(TESTS['convergent2']),
        1.7449,
        transformer=lambda x: round(x, 4),
        name=qualify(series_sum))
