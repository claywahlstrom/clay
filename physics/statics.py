
"""

Module used for analyzing objects and systems in static equilibrium


"""

from clay.maths.core import round_qty as _r

def id_member(name, value):
    """Given the member name and value, prints the axial force type
       and returns its magnitude. Assumes the initial direction of the
       reaction force points away from the joint."""
    if value < 0:
        stress_type = 'C'
    elif value == 0:
        stress_type = '0'
    else: # value > 0
        stress_type = 'T'
    print('member {}: {} ({})'.format(name, _r(value), stress_type))
    return value

if __name__ == '__main__':

    # TESTS
    id_member('TAB', -1)
    id_member('TBC', 0)
    id_member('TCD', 1)
    
