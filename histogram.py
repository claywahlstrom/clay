"""
Histogram development. Still in the early stages
"""

from pack.misc import SortableDict

class HG:
    """Count text into columns for histogram analysis.

    Consumes str or bytes as text
    """
    def __init__(self, columns, text):
        assert type(columns) == tuple, 'columns need to be tuple'
        if type(text) == bytes:
            text = text.decode('utf8', errors='ignore')
        self.cols = columns
        self.text = text
        self.sd = SortableDict({col: self.text.count(col) for col in self.cols})
        
    def build(self):
        large_key = len(max(list(self.sd.keys())))
        max_val = max(list(self.sd.values()))
        width = 80 - 1 - large_key
        print('width', width)
        print('max val', max_val)
        for (k, v) in self.sd.items():
            print('{:>{}}'.format(k, large_key), '0'*int(width*v/max_val))
        self.max_val = max_val
        self.large_key = large_key
        self.width = width

if __name__ == '__main__':
    s = HG(('bc', 'sac', 'aaa'), 'abbcssaaaacccssacbbcaddsacc')
    s.build()
