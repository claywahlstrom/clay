
"""
common physical constants

"""

import math as _math

class Constant:
    '''Used to signify a named physical constant'''

    def __init__(self, name, value, units=None):
        super().__init__()
        if not isinstance(name, str):
            raise TypeError('name must be of type str')
        if not isinstance(value, (complex, float, int)):
            raise TypeError('value must be a numerical type')
        if units is not None and not isinstance(units, str):
            raise TypeError('units must be of type str')
        self.__name = name
        self.__value = value
        self.__units = units

    def __repr__(self):
        return '%s(name=%r, value=%r, units=%r)' % (
            self.__class__.__name__,
            self.name,
            self.value,
            self.units)

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __mul__(self, other):
        return self.value * other

    def __truediv__(self, other):
        return self.value / other

    def __floordiv__(self, other):
        return self.value // other

    def __mod__(self, other):
        return self.value % other

    def __divmod__(self, other):
        return divmod(self.value, other)

    def __pow__(self, other, modulo=0):
        return self.value ** other % modulo

    def __radd__(self, other):
        return other + self.value

    def __rsub__(self, other):
        return other - self.value

    def __rmul__(self, other):
        return other * self.value

    def __rtruediv__(self, other):
        return other / self.value

    def __rfloordiv__(self, other):
        return other // self.value

    def __rmod__(self, other):
        return other % self.value

    def __rdivmod__(self, other):
        return divmod(other, self.value)

    def __rpow__(self, other, modulo=0):
        return other ** self.value % modulo

    def __neg__(self):
        return -self.value

    def __pos__(self):
        return self.value

    def __abs__(self):
        return abs(self.value)

    def __complex__(self):
        return complex(self.value)

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)

    def __round__(self, ndigits=None):
        return round(self.value, ndigits)

    def __trunc__(self):
        raise NotImplementedError()

    def __floor__(self):
        return _math.floor(self.value)

    def __ceil__(self):
        return _math.ceil(self.value)

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    @property
    def units(self):
        return self.__units

accel_grav = Constant('Acceleration due to gravity', 9.80665, 'm/s^2')
avogadro = Constant('Avogadro\'s constant', 6.022140857e23, 'number of atoms in 12g of Carbon-12')
boltzmann = Constant('Boltzmann\'s constant', 1.38065e-23, 'm^2 * kg / (s^2 * K)') # GAS_ENERGY / AVOGADRO
coulomb = Constant('Charge of electrons, Coulomb', 6.24150975e18, 'A * s')
coulomb_law = Constant('Coulomb\'s constant', 9.0e9, 'N * m^2 / C^2') # 1 / (4 * _math.pi * e_0)
elementary_chage = Constant('Elementary charge', 1 / coulomb.value, 'C')
epsilon_0 = Constant('Electric constant, also 1 / (mu0 * c0 ** 2)', 8.854187817e-12, 's^4 * A^2 / (kg * m^3), F / m')
gas = Constant('Gas constant', 0.082057, 'L * atm * K^-1 * mol^-1')
gas_energy = Constant('Gas constant', 8.314472, 'J * K^-1 * mol^-1')
gravitation = Constant('Gravitational constant', 6.67408e-11, 'm^3 / (kg * s^2)')
k_water = Constant('Ionic product constant of water', 1e-14)
kelvin_offset = Constant('Kelvin to degrees offset', 273.15, 'degrees')
magnetic = Constant('Magnetic constant', 4e-7 * _math.pi, 'T * m / A')
planck = Constant('Planck\'s constant', 6.626e-34, 'J * s')
rydberg = Constant('Rydberg\'s constant', 1.09737316e7, 'm^-1')
rydberg_energy = Constant('Rydberg energy', 2.17987e-18, 'J')
speed_of_light = Constant('Speed of light in a vacuum', 299792458, 'm/s') # 1 / _math.sqrt(mu0 * eps0)
speed_of_sound = Constant('Room temperature air', 343, 'm/s')

# symbolic aliases
symbolic = {
    'a_g': accel_grav,
    'Na': avogadro,
    'k_b': boltzmann,
    'C': coulomb,
    'k': coulomb_law,
    'e': elementary_chage,
    'eps0': epsilon_0,
    'R': gas,
    'R_energy': gas_energy,
    'G': gravitation,
    'mu0': magnetic,
    'h': planck,
    'R_h': rydberg,
    'R_y': rydberg_energy,
    'c0': speed_of_light,
    'c': speed_of_sound
}

if __name__ == '__main__':

    from clay.tests import testif

    testif('Constant initializer raises TypeError for invalid name type',
        lambda: Constant(0, 0, None),
        None,
        raises=TypeError)
    testif('Constant initializer raises TypeError for invalid value type',
        lambda: Constant('name', 'value', None),
        None,
        raises=TypeError)
    testif('Constant initializer raises TypeError for invalid units type',
        lambda: Constant('name', 0, 0),
        None,
        raises=TypeError)
    testif('Constant supports built-in method (complex)', complex(accel_grav), 9.80665 + 0j)
    testif('Constant supports built-in method (float)', float(accel_grav), 9.80665)
    testif('Constant supports built-in method (int)', int(accel_grav), 9)
    testif('Constant is represented correctly',
        repr(accel_grav),
        "Constant(name='Acceleration due to gravity', value=9.80665, units='m/s^2')")
