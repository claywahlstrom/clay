"""
Align text on screen based on console size. Default WIDTH is 80px
"""

WIDTH = 80

def center(text):
    """Justify to center"""
    side = (WIDTH-len(text)-len(text)%2)
    return ' '*(side//2)+text+' '*(side//2)

def right(text):
    """Justify to right"""
    return ' '*(WIDTH-len(text))+text

def left(text):
    """Justify to left"""
    return text

if __name__ == '__main__':
    print(left('hello'))
    print(center('world'))
    print(right('My name is Clay'))
