
"""
Interop module to MATLAB(r) functions

"""

from matplotlib.pyplot import *

def interp(xs, ys, xq):
    """Returns the linearly-interpolated value using the first point"""
    m = (ys[1] - ys[0]) / (xs[1] - xs[0])
    return m * (xq - xs[0]) + ys[0]

def matrix2str(matrix):
    """Returns the given matrix as a string for entry into MATLAB(r)"""
    string = '['
    for row in matrix:
        string += '\t'.join(map(str, row)) + '\n'
    return string + '];'

def meshgrid(a, b):
    """Returns the coordinates of rectangular grid"""
    A = list([a] * len(b))
    B = transpose([b] * len(a))
    return A, B

def solve_ode(dy, tspan, y0):
    """
    Returns the solutions to the ODE given the differential,
    time span, and initial value

    """
    if len(tspan) != 2:
        raise ValueError('tspan must be include 2 times')
    t0, tf = tspan
    y, t = [], []
    y_val, time = y0, t0
    dt = min(100, tf - t0) / 1000 # ensure at least 10 data points
    while time <= tf:
        try:
            y_val += dy(time, y_val) * dt
            y.append(y_val)
            t.append(time)
        except ZeroDivisionError:
            print('Zero division occured for t={}'.format(time))
        time += dt
    return t, y

def transpose(matrix):
    """Returns the transpose for the given matrix"""
    if not matrix:
        return []
    elif matrix[0] and not isinstance(matrix[0], list):
        return [[elem] for elem in matrix]
    return list(map(list, zip(*matrix)))

if __name__ == '__main__':

    from clay.tests import testif
    from clay.utils import qualify

    testif('meshes grid correctly',
        meshgrid([0, 1], [2, 3, 4]),
        ([[0, 1], [0, 1], [0, 1]], [[2, 2], [3, 3], [4, 4]]),
        name=qualify(meshgrid))

    dy = lambda t, y: 0.01 * y * (100 - y)
    t, y = solve_ode(dy, [0, 11], 10)

    plot(t, y)
    title('Total Population vs Time')
    xlabel('Time (s)'); ylabel('Total Population')
    legend(['y(t)']); grid()
    show()

    testif('flips 1-D matrix correctly',
        transpose([1, 2, 3, 4]),
        [[1], [2], [3], [4]],
        name=qualify(transpose))
    testif('flips 2-D matrix correctly',
        transpose([[1, 2], [3, 4]]),
        [[1, 3], [2, 4]],
        name=qualify(transpose))
