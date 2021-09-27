
"""
springs

"""

def kequivalent(springs, config):
    """
    Given a list of spring constant values and their configuration,
    returns the equivalent spring constant

    """
    if config == 'parallel':
        return sum(springs)
    elif config == 'series':
        return 1 / sum((1 / n for n in springs))
    else:
        raise ValueError('The given configuration is not supported: ' + config)

if __name__ == '__main__':

    from clay.tests import testif, testraises
    from clay.utils import qualify

    testraises('configuration invalid',
        lambda: kequivalent([], 'unknown'),
        ValueError,
        name=qualify(kequivalent))

    testif('returns correct spring constant equivalent',
        kequivalent(
            [10, kequivalent([100, 25, 100, 50, 12.5], 'series')],
            'parallel'),
        16.25,
        name=qualify(kequivalent))
