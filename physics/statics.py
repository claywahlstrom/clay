
"""
Module used for analyzing objects and systems in static equilibrium

"""

from clay.maths.core import round_qty as _r

def id_member(name, value):
    """
    Given the member name and value, returns the member name, value,
    and axial force type identified as a string. Assumes the initial
    direction of the reaction force points away from the joint.

    """
    if value < 0:
        stress_type = 'C'
    elif value == 0:
        stress_type = '0'
    else: # value > 0
        stress_type = 'T'
    return 'member {}: {} ({})'.format(name, _r(value), stress_type)

if __name__ == '__main__':

    from clay.tests import testif

    testif('id_member identifies compression correctly',
        id_member('TAB', -1),
        'member TAB: -1 (C)')
    testif('id_member identifies no external loads correctly',
        id_member('TBC', 0),
        'member TBC: 0 (0)')
    testif('id_member identifies tension correctly',
        id_member('TCD', 1),
        'member TCD: 1 (T)')
