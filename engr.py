"""
Engineering module
"""

# Coulomb's constant
C = 6.241*10**18
OHMS_TABLE = {'I':'V/R',
            'V':'I*R',
            'R':'V/I'}
# Standard SI prefixes
PREFIXES = ['Yotta', 'Zetta', 'Exa', 'Peta', 'Tera', 'Giga',
            'Mega', 'kilo', '', 'milli', 'micro(u)', 'nano',
            'pico', 'femto', 'atto', 'zepto', 'yocto']

def get_prefix(scalar, units='m'):
    amount = scalar
    position = PREFIXES.index('')
    pre = str()

    while amount > 1000:
        position -= 1
        pre = PREFIXES[position]
        amount /= 1000

    while amount < 1:
        position += 1
        pre = PREFIXES[position]
        amount *= 1000

    print(scalar, units, '=>', amount, pre, units)

def ohms_law(V=None, I=None, R=None):
    for letter in OHMS_TABLE.keys():
        if eval(letter) is None:
            try:
                return eval(OHMS_TABLE[letter])
            except:
                print('missing keyword arguments, 2 required')
                return

def par(*res):
    return (sum([num**(-1) for n in res for num in n]))**(-1)

series = sum # def

if __name__ == '__main__':
    get_prefix(24582000)
    get_prefix(0.0021040, units='m/s')
    get_prefix(0.00021040)
    print(series([10, par([100, 25, 100, 50, 12.5])]))
    print(ohms_law(V=9, I=15))
