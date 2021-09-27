
"""
thermodynamics

"""

def x(yf, y, yg):
    """Returns the quality of the two-phase mixture"""
    if y < yf:
        return 0
    elif y > yg:
        return 1
    else:
        return (y - yf) / (yg - yf)

if __name__ == '__main__':

    from clay.tests import testif
    from clay.utils import qualify

    single_phase_tests = [
        ((2, 1, 3), 0),
        ((2, 4, 3), 1)
    ]

    for test in single_phase_tests:
        testif('returns correct quality for single-phase mixture (x: {})'.format(test[1]),
            x(*test[0]),
            test[1],
            name=qualify(x))

    two_phase_tests = [
        ((1, 5, 8), 0.57143),
        ((0.00079275, 0.01505, 0.04925), 0.29422)
    ]

    for test in two_phase_tests:
        testif('returns correct quality for two-phase mixture (x: {})'.format(test[1]),
            round(x(*test[0]), 5),
            test[1],
            name=qualify(x))
