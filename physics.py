
from collections import OrderedDict
import math

# acceleration due to gravity
a_g = -9.81 # m/s^2

def get_drop_time(distance):
    return math.sqrt((distance * 2) / a_g)

class Position:
    def __init__(self, position, time=None, step=None):
        assert type(position) == list
        if step is None:
            step = 1
        self.position = position
        self.time = time
        self.step = step

        if self.time:
            self.dt = [self.time[t+1]-self.time[t] for t in range(len(self.time)-1)]            
        else:
            self.time = list(range(0, len(position), step))
            self.dt = list([step]*(len(self.position)-1))

    def vel(self):
        #self.dp = [self.position[t+1]-self.position[t] for t in range(len(self.position)-1)]
        self.vel = OrderedDict({t: (self.position[i+1]-self.position[i])/(self.dt[i])/self.step for (i,t) in enumerate(self.time[:-2])})
        return self.vel

    def accel(self):
        self.dv = [self.vel[t+1]-self.vel[t] for t in range(len(self.vel)-1)]
        self.accel = OrderedDict({t: (self.dv[i])/(self.dt[i]) for (i,t) in enumerate(self.time[:-3])})
        return self.accel

if __name__ == '__main__':
    pos = Position([0, 4.905, 19.62, 44.145, 78.48, 122.625])
    print('vel =', pos.vel())
    print('accel =', pos.accel())
    POS = Position([1, 4, 9, 16, 25, 36])
    print('velocity', POS.vel())
    print('accel', POS.accel())
