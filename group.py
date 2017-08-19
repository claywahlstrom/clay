
import sys as _sys

class Group:
    """Holds list of objects to display. Mainly used for debugging"""
    def __init__(self, objs=list(), module='__main__'):
        assert type(objs) == list, 'Not a list of strings'

        self.objs = objs
        self.module = module
        
    def add(self, var):
        if type(var) == list:
            for v in var:
                (self.objs).append(v)
        elif type(var) == str:
            (self.objs).append(var)
            
    def remove(self, var):
        if type(var) == list:
            for v in var:
                (self.objs).remove(v)
        elif type(var) == str:
            (self.objs).remove(var)
            
    def show(self):
        groupdict = self.get_dict()
        for ob in self.objs:
            print(ob, groupdict[ob])
            
    def get_dict(self):
        return _sys.modules[self.module].__dict__

def write_file(obj, filename):
    STRING = 'stat_dict = {}'.format(obj.get_dict())
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
    write_file(s, 'group_test.txt')
