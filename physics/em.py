
"""
em: Electricity and Magnetism

"""

import math

from clay.physics import constants as const
from clay.physics.core import Force

def apply_ohms_law(V=None, I=None, R=None):
    """Fills in and returns the unspecified value to satisfy Ohm's law"""
    if len(list(filter(lambda x: x, (V, I, R)))) < 2:
        raise ValueError('at least two variables must be specified')
    elif I and R:
        return I * R
    elif V and R:
        return V / R
    else: # V and I
        return V / I

def capacitor_energy(charge, distance, area):
    """Given charge (C), distance (m) and area (m^2), returns the potential
       energy of this capacitor"""
    return charge ** 2 * distance / (2 * const.epsilon_0 * area)

class Charge(object):

    """Class Charge can be used to represent a point charge"""

    def __init__(self, position, magnitude):
        """Initializes this charge with the given position and magnitude"""
        self.position  = position
        self.magnitude = magnitude

    def forceon(self, c):
        """Returns the force by this charge on the given charge `c`"""
        return Force(self, c)

def dipole_moment(charge, a, l):
    """
    Returns the magnitude of the dipole moment vector
        charge = charge of the particle in Coulombs
        a      = distance to the perpendicular bisector in meters
        l      = distance between charges in meters

    """
    return 1 / (4 * math.pi * const.epsilon_0) * charge / (a ** 2 + l ** 2) ** (3/2)

def requivalent(res, config):
    """
    Given a list of resistor values and their configuration,
    returns the equivalent resistance

    """
    if config == 'series':
        return sum(res)
    elif config == 'parallel':
        return 1 / sum((1 / n for n in res))
    else:
        raise ValueError('The given configuration is not supported: ' + config)

if __name__ == '__main__':

    from clay.tests import testif, testraises
    from clay.utils import qualify

    testraises('variables not specified (none given)',
        lambda: apply_ohms_law(),
        ValueError,
        name=qualify(apply_ohms_law))
    testraises('variables not specified (V given)',
        lambda: apply_ohms_law(V=2),
        ValueError,
        name=qualify(apply_ohms_law))
    testif('returns correct value (V)',
        apply_ohms_law(I=1, R=2),
        2,
        name=qualify(apply_ohms_law))
    testif('returns correct value (I)',
        apply_ohms_law(V=1, R=2),
        0.5,
        name=qualify(apply_ohms_law))
    testif('returns correct value (R)',
        apply_ohms_law(V=1, I=4),
        0.25,
        name=qualify(apply_ohms_law))

    testraises('configuration invalid',
        lambda: requivalent([], 'unknown'),
        ValueError,
        name=qualify(requivalent))
    testif('returns correct resistor equivalent',
        requivalent(
            [10, requivalent([100, 25, 100, 50, 12.5], 'parallel')],
            'series'),
        16.25,
        name=qualify(requivalent))
