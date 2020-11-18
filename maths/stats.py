
"""
stats: module for statistical analysis

"""

import math as _math

def multiplicity(q, N):
    """
    Returns the multiplicity Omega given the number of objects q
    and the number of cells to distribute to N

    """
    return int(_math.factorial(q + N - 1) /
        (_math.factorial(q) * _math.factorial(N - 1)))

def nchoosek(n, k):
    """Returns the number of combinations of n items taken k at a time"""
    if n < k:
        return 0
    return partition(n, [k, n - k])

C = nchoosek # alias

def perms(n, k):
    """Returns the number of permutations of n items taken k at a time"""
    if n < k:
        return 0
    return partition(n, [n - k])

P = perms # alias

def partition(n, ks):
    """
    Returns the number of ways the given n objects can be arranged
    in groups of size k. ks must be an iterable of k values

    """
    if type(ks) not in (list, tuple):
        raise TypeError('ks must be an iterable')
    if not ks:
        raise ValueError('ks must have at least one value')
    elif min(ks) < 0:
        raise ValueError('group size k must be non-negative')
    num = _math.factorial(n)
    den = 1
    for k in ks:
        den *= _math.factorial(k)
    return int(num / den)

if __name__ == '__main__':

    from clay.tests import testif

    multiplicity_tests = [
        # q,  N, return value
        (12, 12, 1352078),
        (11, 12, 705432),
        (10, 12, 352716),
        ( 9, 12, 167960),
        ( 8, 12, 75582),
        ( 7, 12, 31824),
        ( 6, 12, 12376),
        ( 5, 12, 4368),
        ( 4, 12, 1365),
        ( 3, 12, 364),
        ( 2, 12, 78),
        ( 1, 12, 12),
        ( 0, 12, 1)
    ]

    for m_test in multiplicity_tests:
        testif('multiplicity returns correct value (q={}, n={})'
                .format(m_test[0], m_test[1]),
            multiplicity(m_test[0], m_test[1]),
            m_test[2])

    testif('nchoosek returns 0 when n < k',
        nchoosek(0, 1),
        0)
    testif('nchoosek calls partition correctly',
        nchoosek(15, 10),
        partition(15, [10, 5]))

    testif('perms returns 0 when n < k',
        perms(0, 1),
        0)
    testif('perms calls partition correctly',
        perms(8, 4),
        partition(8, [4]))

    testif('partition raises TypeError for invalid ks type',
        lambda: partition(0, 0),
        None,
        raises=TypeError)
    testif('partition raises ValueError for empty ks iterable',
        lambda: partition(0, []),
        None,
        raises=ValueError)
    testif('partition raises ValueError for negative k value',
        lambda: partition(0, [0, -1]),
        None,
        raises=ValueError)
    testif('partition returns correct value (one partition)',
        partition(15, [15]),
        1)
    testif('partition returns correct value (two partitions)',
        partition(15, [10, 5]),
        3003)
    testif('partition returns correct value (many partitions)',
        partition(15, [6, 4, 5]),
        630630)
