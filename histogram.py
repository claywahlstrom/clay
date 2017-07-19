"""
Histogram development. Still in the early stages
"""

from pack.misc import SortableDict

class HG(object):
    """Count text into columns for histogram analysis.

    Consumes str or bytes as text
    """
    def __init__(self, columns, text):
        assert type(columns) == tuple, 'columns need to be tuple'
        if type(text) == bytes:
            text = text.decode('utf8', errors='ignore')
        self.cols = columns
        self.text = text
        self.d = SortableDict({col: self.text.count(col) for col in self.cols})
        
    def build(self):
        m_val = max(list(self.d.values()))
        large_key = len(max(list(self.d.keys())))
        width = 80 - 1 - large_key
        print('wd', width)
        for (k, v) in self.d.items():
            print('{:>{}}'.format(k, large_key), '0'*int(width*v/m_val))


if __name__ == '__main__':
    s = HG(('bc', 'sac', 'c'), 'abbcssaaaacccssacbbcaddsacc')
    s.build()
