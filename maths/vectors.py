
"""
vectors: vector operations simply written and easy to use

The notation for vectors is [i, j, ...] and angles
are in radians unless otherwise specified.

"""

import math

GLOBAL_ROUNDING = 4

def add(vector1, vector2, *vectors):
    """Returns the summation of the given vectors"""
    return apply(sum, list(zip(vector1, vector2, *vectors)))

def apply(function, vector):
    """Applies the function to the given vector and returns the result"""
    return type(vector)(map(function, vector))

def cross(v1, v2):
    """Returns the cross product of the given two vectors
       using the formulaic definition"""
    i = v1[1] * v2[2] - v2[1] * v1[2]
    j = v1[0] * v2[2] - v2[0] * v1[2]
    k = v1[0] * v2[1] - v2[0] * v1[1]
    return [i, -j, k]

def dot(vector1, vector2, angle):
    """Returns the dot product of two vectors at some angle theta"""
    return mag(vector1) * mag(vector2) * math.cos(angle)

def dot_comp(vector1, vector2):
    """Returns the dot product of two vectors using their components"""
    return sum(map(lambda x: x[0] * x[1], zip(vector1, vector2)))

def mag(vector):
    """Returns the magnitude of the given vector"""
    return math.sqrt(sum(x ** 2 for x in vector))

def mag_moment(distance, force, angle):
    """Returns the moment magnitude given the distance, force, and angle"""
    return distance * force * math.sin(angle)

def mult(vector, scalar):
    """Returns a scalar multiple of the given vector"""
    return apply(lambda x: x * scalar, vector)

def r(obj):
    """Rounds the given vector or scalar to GLOBAL_ROUNDING digits"""
    if type(obj) in (list, tuple):
        return apply(r, obj)
    else:
        return round(obj, GLOBAL_ROUNDING)

scale = mult

def vect(magnitude, angle=0):
    """Returns a vector of the given magnitude and direction in component form"""
    return [magnitude * math.cos(angle), magnitude * math.sin(angle)]

if __name__ == '__main__':

    from clay.tests import it

    it('add returns correct value (2 vectors)',
       add([0, 1, 1], [1, 1, 0]),
       [1, 2, 1])
    it('add returns correct value (>2 vectors)',
       add([0, 1, 1], [1, 1, 0], [1, 1, 1]),
       [2, 3, 2])
    it('cross returns correct value',
       cross([3, -3, 1], [4, 9, 2]),
       [-15, -2, 39])
    it('cross returns correct value (parallel)',
       cross([3, -3, 1], [-12, 12, -4]),
       [0, 0, 0])
    it('dot returns correct value',
       dot([1, 0], [0, 1], math.pi / 2), 0,
       transformer=lambda x: r(x))
    it('dot_comp returns correct value using vector components',
       dot_comp([1, 2], [3, 4]), 11)
    it('mag returns correct magnitude',
       mag([1 / math.sqrt(3), 1 / math.sqrt(3), 1 / math.sqrt(3)]), 1)
    it('mult returns correct vector when scaled',
       mult([1, 2], 3), [3, 6])
    it('r rounds scalar value correctly',
       r(0.00009), 0.0001)
    it('r rounds vector values correctly',
       r([0.00009, 0.02004, 1.0]), [0.0001, 0.02, 1.0])
