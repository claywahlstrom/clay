
"""
physics: includes goodies from constants to mechanics to electromagnetism

"""

from collections import OrderedDict
import math as _math

AVOGADRO = 6.022140857e23 # atoms in 12g of Carbon-12
C = 6.24150975e18     # A*s, charge by electrons, Coulomb
G = 6.67408e-11       # m^3 / (kg * s^2), gravitational constant
R_h = 1.09737316e7    # m^-1, Rydberg's constant
R_y = 2.17987e-18     # J, Rydberg energy
a_g = 9.81            # m/s^2, acceleration due to gravity
c = 299792458         # m/s, speed of light in a vacuum
e = 1 / C             # charge of an electron
esp0 = 8.85418782e-12 # m^-3 kg^-1 s^4 A^2, electric constant
h = 6.626e-34         # J*s, Plank's constant
k = 9.0e9             # N * m^2 / C^2, Coulomb's constant
# k = 1 / (4 * _math.pi * e_0) # also Coulomb's constant

OHMS_TABLE = {'I':'V/R',
              'V':'I*R',
              'R':'V/I'}

def dipolemoment(charge, a, l):
    """Returns the magnitude of the dipole moment vector
           charge = charge of the particle in Coulombs
           a      = distance to the perpendicular bisector in meters
           l      = distance between charges in meters
    """
    return 1 / (4 * _math.pi * e_0) * charge / (a ** 2 + l ** 2) ** (3/2)

class Charge(object):

    """Class Charge can be used to represent a point charge"""
    
    def __init__(self, position, magnitude):
        self.position  = position
        self.magnitude = magnitude

    def force(self, c):
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

def get_drop_time(displacement, v_i=0, a=a_g):
    """Returns free fall time in seconds starting at t = 0.
       Assumes up as the positive direction for position"""
    from clay.maths import get_roots
    if v_i:
        t1, t2 = get_roots(a, v_i, displacement)
        return max(t1, t2)
    else:
        return _math.sqrt(displacement * 2 / a_g)

def ohms_law(V=None, I=None, R=None):
    """Fills in and returns the missing value to satisfy Ohm's law"""
    for letter in OHMS_TABLE.keys():
        if eval(letter) is None:
            try:
                return eval(OHMS_TABLE[letter])
            except:
                print('missing keyword arguments, 2 required')
                return

def parallel(res):
    """Given a list of resistor values, returns the equivalent resistance"""
    return 1 / sum((1 / n for n in res))

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
        self.vel = OrderedDict({t: (self.position[i+1]-self.position[i])/(self.dt[i])/self.step for (i,t) in enumerate(self.time[:-2])})
        return self.vel

    def accel(self):
        """Calculates and returns the accelerations at each time interval"""
        self.dv = [self.vel[t+1]-self.vel[t] for t in range(len(self.vel)-1)]
        self.accel = OrderedDict({t: (self.dv[i])/(self.dt[i]) for (i,t) in enumerate(self.time[:-3])})
        return self.accel

series = sum # def

if __name__ == '__main__':
    print('drop time', get_drop_time(displacement=abs(a_g / 2), v_i=0))
    pos = Position([0, 4.905, 19.62, 44.145, 78.48, 122.625])
    print('vel =', pos.vel())
    print('accel =', pos.accel())
    print(ohms_law(V=9, I=15))
    POS = Position([1, 4, 9, 16, 25, 36])
    print('velocities', POS.vel())
    print('accels', POS.accel())
    print(series([10, par([100, 25, 100, 50, 12.5])]))    
