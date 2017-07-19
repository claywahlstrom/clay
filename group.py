
import sys

class Group:
    """Holds list of objects to display. Mainly used for debugging"""
    def __init__(self, objs=[], module='__main__'):
        assert type(objs) == list, 'Not a list of strings'

        self.objs = objs
        self.module = module
    def add(self,var):
        if type(var) == list:
            for v in var:
                (self.objs).append(vf)
        elif type(var) == str:
            (self.objs).append(var)
    def show(self):
        for ob in self.objs:
            print(ob,self.stats_dict()[ob])
    def stats_dict(self):
        return sys.modules[self.module].__dict__

def write_file(obj, filename):
    STRING = 'stat_dict = {}'.format(obj.stat_dict())
    with open(filename,'w') as f:
        f.write(STRING)

if __name__ == '__main__':
    a = 'string'
    b = int(4)
    c = dict()
    s = Group(['a', 'b', 'c'])
    print('before add')
    s.show()
    d = float(542.2)
    s.add('d')
    print('after add')
    s.show()
    write_file(s, 'Stat_test.txt')
