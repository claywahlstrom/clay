
"""
common physical constants

"""

import math as _math

ACCEL_GRAV = 9.80665           # m/s^2 : acceleration due to gravity
AVOGADRO = 6.022140857e23      # number of atoms in 12g of Carbon-12
BOLTZMANN = 1.38065e-23        # m^2 * kg / (s^2 * K), also GAS_ENERGY / AVOGADRO
COULOMB = 6.24150975e18        # A * s : charge of electrons, Coulomb
COULOMB_LAW = 9.0e9            # N * m^2 / C^2 : Coulomb's constant
# k = 1 / (4 * _math.pi * e_0) # also Coulomb's constant
ELEMENTARY_CHAGE = 1 / COULOMB # C : elementary charge
EPSILON_0 = 8.854187817e-12    # s^4 * A^2 / (kg * m^3), F / m : electric constant, also 1 / (mu0 * c0 ** 2)
GAS = 0.082057                 # L * atm * K^-1 * mol^-1, gas constant
GAS_ENERGY = 8.314472          # J * K^-1 * mol^-1, gas constant
GRAVITATION = 6.67408e-11      # m^3 / (kg * s^2) : gravitational constant
KELVIN_OFFSET = 273.15         # degrees : Kelvin to degrees offset
K_WATER = 1e-14                # ionic product constant of water
MAGNETIC = 4e-7 * _math.pi     # T * m / A : magnetic constant
PLANCK = 6.626e-34             # J * s : Planck's constant
RYDBERG = 1.09737316e7         # m^-1 : Rydberg's constant
RYDBERG_ENERGY = 2.17987e-18   # J : Rydberg energy
SPEED_OF_LIGHT = 299792458     # m/s : speed of light in a vacuum, also 1 / _math.sqrt(mu0 * eps0)
SPEED_OF_SOUND = 343           # m/s : room temperature air

# symbolic aliases
symbolic = {
    'C': COULOMB,
    'G': GRAVITATION,
    'R': GAS,
    'R_energy': GAS_ENERGY,
    'R_h': RYDBERG,
    'R_y': RYDBERG_ENERGY,
    'a_g': ACCEL_GRAV,
    'c0': SPEED_OF_LIGHT,
    'e': ELEMENTARY_CHAGE,
    'eps0': EPSILON_0,
    'h': PLANCK,
    'k': COULOMB_LAW,
    'mu0': MAGNETIC,
    'k_b': BOLTZMANN
}
