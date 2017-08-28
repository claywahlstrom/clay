"""
Histogram development. Still in the early stages
"""

from pack.misc import SortableDict

class HG:
    """Count text into columns for histogram analysis.

    Consumes str or bytes as text
    """
    def __init__(self, columns=None, text=str()):
        if not columns is None:
            assert type(columns) == tuple or type(columns) == list, 'columns need to be tuple'
        if type(text) == bytes:
            text = text.decode('utf8', errors='ignore')
        if columns and not text:
            sd = SortableDict({col: 0 for col in columns})
        else:
            sd = SortableDict({col: text.count(col) for col in columns})
        self.cols = columns
        self.sd = sd
        self.text = text

    def build(self):
        max_element = max(list(self.sd.keys()))
        if type(max_element) == str:
            large_key = len(max_element)
            width = 80 - 1 - large_key
        else: # for ints and floats
            large_key = len(str(max_element))
            width = 80 - 1 - len(str(large_key))

        max_val = max(list(self.sd.values()))
        
        print('width', width)
        print('max val', max_val)
        for (k, v) in self.sd.items():
            print('{:>{}}'.format(k, large_key), '0'*int(width*v/max_val))
        self.max_val = max_val
        self.large_key = large_key
        self.width = width

if __name__ == '__main__':
    s = HG(('bc', 'sac', 'aaa'), 'abbcssaaaaaaaaaaacccssacbbcaddsaacc')
    s.build()
