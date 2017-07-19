
from collections import OrderedDict

class Position:
    def __init__(self, xs, time=None, step=None):
        assert type(xs) == list
        if step is None:
            step = 1
        if not time and step:
            time = [t for t in range(0, len(xs), step)]
        self.xs = xs
        self.time = time
        self.dt = [self.time[t+1]-self.time[t] for t in range(len(self.time)-1)]
        
    def vel(self):
        self.dx = [self.xs[t+1]-self.xs[t] for t in range(len(self.xs)-1)]
        self.vel = OrderedDict({t:(self.xs[i+1]-self.xs[i])/ \
                                (self.dt[i]) for (i,t) in enumerate(self.time[:-1])})
        return self.vel
    def accel(self):
        self.dv = [self.vel[t+1]-self.vel[t] for t in range(len(self.vel)-1)]
        self.accel = OrderedDict({t:(self.dv[i])/ \
                                 (self.dt[i]) for (i,t) in enumerate(self.time[:-2])})
        return self.accel


if __name__ == '__main__':
    pos = Position([0,4.905,19.62,44.145,78.48,122.625], step=1)
    print('vel =', pos.vel())
    print('accel =', pos.accel())
    POS = Position([1, 4, 9, 16, 25, 36])
    print(POS.vel())
    print(POS.accel())
