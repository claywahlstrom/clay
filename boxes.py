"""
Box creation for text
"""

import math as _math

def fullbox(text, thickness=1, border=1):
    """Formats box based on "thickness" and "border" around text"""
    width = len(text)+thickness*2+border*2
    height = 3 # based on top/bottom or total lines???

    box = str()
    for x in range(thickness):
        box += '#'*width+'\n'
    
    for x in range(border): # greater than one
        box += '#'*thickness+' '*(len(text)+border*2)+'#'*thickness+'\n'

    box += '#'*thickness+' '*border+text+' '*border+'#'*thickness+'\n'
    
    for x in range(border): # greater than one
        box += '#'*thickness+' '*(len(text)+border*2)+'#'*thickness+'\n'
        
    for x in range(thickness):
        box += '#'*width+'\n'
        
    return box

def box(text, width=0, height=3, module=False):
    """Formats box based on size of text w/ thickness of 1.

    Option for module headers to customize titles

    """
    if width < len(text)+4: # if width is zero
        for line in text.split('\n'):
            if len(line) >= width:
                width = len(line)+4
    assert height >= 3
    if module:
        height += 2

    box = str()
    
    border = 1

    print('width', width)

    box += '#'*width+'\n'
    
    for x in range(border):
        box += '#' + ' '*(width - 2) + '#' + '\n'
        
    # side = (width-2-len(text)-1) / 2
    for line in text.split('\n'):
        space = [' '] * width
        space[0] = '#'; space[-1] = '#'
        ind = _math.floor(width / 2 - len(line)/2 - (width + 1) % 2)
        print('ind', ind)
        space[ind:ind+len(line)] = line
        box += ''.join(space)+'\n'

    for x in range(border):
        box += '#'+' '*(width-2)+'#\n'
        
    box += '#'*width+'\n'
    return box

if __name__ == '__main__':
    print('Examples:')
    print(fullbox('Hello full', 2, 1))
    print('')
    print(box('indexops\nregex\nfor searching', module=True))
    input('done')
