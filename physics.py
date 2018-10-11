
"""
physics: goodies ranging from constants to mechanics to electromagnetism

"""

import collections as _collections
import math as _math

# defined first for scope solutions
mu0 = 4e-7 * _math.pi # T * m / A : magnetic constant

AVOGADRO = 6.022140857e23 # number of atoms in 12g of Carbon-12
C = 6.24150975e18     # A * s : charge by electrons, Coulomb
G = 6.67408e-11       # m^3 / (kg * s^2) : gravitational constant
R = 0.082057          # L * atm * K^-1 * mol^-1, gas constant
R_energy = 8.314472   # J * K^-1 * mol^-1, gas constant
R_h = 1.09737316e7    # m^-1 : Rydberg's constant
R_y = 2.17987e-18     # J : Rydberg energy
a_g = 9.81            # m/s^2 : acceleration due to gravity
e = 1 / C             # C : charge of an electron
c0 = 299792458        # m/s : speed of light in a vacuum
eps0 = 1 / (mu0 * c0 ** 2) # s^4 * A^2 / (kg * m^3), F / m : electric constant
h = 6.626e-34         # J * s : Plank's constant
k = 9.0e9             # N * m^2 / C^2 : Coulomb's constant
# k = 1 / (4 * _math.pi * e_0) # also Coulomb's constant
mu0 = 4e-7 * _math.pi # T * m / A : magnetic constant

c0 = 1 / _math.sqrt(mu0 * eps0) # m/s : speed of light in a vacuum

KELVIN_OFFSET = 273.15 # degrees
OHMS_TABLE = {'I': 'V/R',
              'V': 'I*R',
              'R': 'V/I'}
# Standard SI prefixes
PREFIXES = ['Yotta', 'Zetta', 'Exa', 'Peta', 'Tera', 'Giga',
            'Mega', 'kilo', '', 'milli', 'micro(u)', 'nano', # '' is the base
            'pico', 'femto', 'atto', 'zepto', 'yocto']

def apply_ohms_law(V=None, I=None, R=None):
    """Fills in and returns the missing value to satisfy Ohm's law"""
    for letter in OHMS_TABLE.keys():
        if eval(letter) is None:
            try:
                return eval(OHMS_TABLE[letter])
            except:
                print('missing keyword arguments, 2 required')
                return

class Charge(object):

    """Class Charge can be used to represent a point charge"""
    
    def __init__(self, position, magnitude):
        self.position  = position
        self.magnitude = magnitude

    def forceon(self, c):
        return Force(self, c)

class Force(object):

    """Class Force can be used to calculate force by one on two"""

    def __init__(self, one, two):
        self.one = one
        self.two = two

    def __repr__(self):
        return 'Force(x=%r,y=%r)' % (self.comp(_math.cos), self.comp(_math.sin))
        
    def mag(self):
        """Returns the magnitude of this force object"""
        return -k * self.one.magnitude * self.two.magnitude / (self.one.position[0] - self.two.position[0]) ** 2

    def comp(self, func):
        """Accepts sin or cos for calculating y and x components respectively"""
        val = round((self.two.position[0] - self.one.position[0]) * self.mag() * func(self.two.position[1] - self.one.position[1]), 40)
        if val == 0: # remove - from -0.0 values
           val *= -1
        return val

def get_capacitorenergy(charge, distance, area):
    """Given charge (C), distance (m) and area (m^2), returns the potential
       energy of this capacitor"""
    return charge ** 2 * distance / (2 * esp0 * area)

def get_dipolemoment(charge, a, l):
    """Returns the magnitude of the dipole moment vector
           charge = charge of the particle in Coulombs
           a      = distance to the perpendicular bisector in meters
           l      = distance between charges in meters"""
    return 1 / (4 * _math.pi * e_0) * charge / (a ** 2 + l ** 2) ** (3/2)

def get_drop_time(displacement, v_i=0, a=a_g):
    """Returns free fall time in seconds starting at t = 0.
       Assumes up as the positive direction for position"""
    from clay.maths import roots
    if v_i:
        t1, t2 = roots(a, v_i, displacement)
        return max(t1, t2)
    else:
        return _math.sqrt(displacement * 2 / a_g)

def get_lorenz_factor(velocity):
    """Returns the Lorenz factor for the given object moving at velocity v"""
    return 1 / _math.sqrt(1 - velocity ** 2 / c ** 2)

def get_prefix(scalar, units='m'):
    """Adjusts the given scalar to a better prefix and prints it out"""
    negative = False
    amount = scalar
    if amount < 0:
        negative = True
        amount *= -1
    position = PREFIXES.index('')
    pre = ''

    while amount > 1000:
        position -= 1
        pre = PREFIXES[position]
        amount /= 1000

    while amount < 1:
        position += 1
        pre = PREFIXES[position]
        amount *= 1000
        
    if negative:
        amount *= -1
    print(scalar, units, '=>', amount, pre, units)

def get_urms(temp, molar_mass):
    """"Returns the root mean square velocity using the given molar mass (g)
        and temperature (*C)"""
    return _math.sqrt(3 * R_energy * (temp + KELVIN_OFFSET) / (molar_mass / 1000))

def requivalent(res, config):
    """Given a list of resistor values and their configuration,
       returns the equivalent resistance"""
    if config == 'series':
        return sum(res)
    elif config == 'parallel':
        return 1 / sum((1 / n for n in res))
    else:
        raise ValueError('That configuration is not supported')

class Position(object):

    def __init__(self, position, time=None, step=None):
        assert type(position) == list
        if step is None:
            step = 1
        self.position = position
        self.time = time
        self.step = step

        if self.time:
            self.dt = [self.time[t+1]-self.time[t] for t in range(len(self.time)-1)]            
        else:
            self.time = list(range(0, len(position), step))
            self.dt = list([step]*(len(self.position)-1))

    def vel(self):
        """Calculates and returns the velocities at each time interval"""
        #self.dp = [self.position[t+1]-self.position[t] for t in range(len(self.position)-1)]
        self.vel = _collections.OrderedDict({t: (self.position[i+1]-self.position[i])/(self.dt[i])/self.step for (i,t) in enumerate(self.time[:-2])})
        return self.vel

    def accel(self):
        """Calculates and returns the accelerations at each time interval"""
        self.dv = [self.vel[t+1]-self.vel[t] for t in range(len(self.vel)-1)]
        self.accel = _collections.OrderedDict({t: (self.dv[i])/(self.dt[i]) for (i,t) in enumerate(self.time[:-3])})
        return self.accel

if __name__ == '__main__':
    print('drop time', get_drop_time(displacement=abs(a_g / 2), v_i=0))
    get_prefix(24582000)
    get_prefix(0.0021040, units='m/s')
    get_prefix(0.00021040)
    pos = Position([0, 4.905, 19.62, 44.145, 78.48, 122.625])
    print('vel =', pos.vel())
    print('accel =', pos.accel())
    print(apply_ohms_law(V=9, I=15))
    POS = Position([1, 4, 9, 16, 25, 36])
    print('velocities', POS.vel())
    print('accels', POS.accel())
    print('requivalent', requivalent([10, requivalent([100, 25, 100, 50, 12.5],
                                                      'parallel')],
                                     'series'))
