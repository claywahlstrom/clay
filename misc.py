
"""
misc: imports that don't have their own module yet

"""

from clay import isUnix as _isUnix

def human_hex(dec):
    """Converts decimal values to human readable hex.
    Mainly used in engineering class
    """
    return hex(dec)[2:]

def map_args(function, iterable, *args, **kwargs):
    """Maps iterable to a function with arguments/keywords.\nDynamic types"""
    return type(iterable)(function(x, *args, **kwargs) for x in iterable)

if __name__ == '__main__':

    print(human_hex(2700))

    def func(x, y=2, z=3):
        return x + y + z
    print(map_args(func, (1, 4, 16, 25), z = 4))
