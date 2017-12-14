"""
Align text on screen based on console size. Default WIDTH is 80 characters
"""

WIDTH = 80

def center(text):
    """Justifies the given text to the center"""
    side = (WIDTH-len(text)-len(text)%2)
    return ' '*(side//2)+text+' '*(side//2)

def right(text):
    """Justifies the given text to the right"""
    return ' '*(WIDTH-len(text))+text

def left(text):
    """Justifies the given text to the left"""
    return text

if __name__ == '__main__':
    print(left('hello'))
    print(center('world'))
    print(right('My name is Clay. What\'s yours?'))
