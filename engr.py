
"""
Engineering module

"""

# Standard SI prefixes
PREFIXES = ['Yotta', 'Zetta', 'Exa', 'Peta', 'Tera', 'Giga',
            'Mega', 'kilo', '', 'milli', 'micro(u)', 'nano', # '' is the base
            'pico', 'femto', 'atto', 'zepto', 'yocto']

def get_prefix(scalar, units='m'):
    """Adjusts the given scalar to a better prefix and prints it out"""
    negative = False
    amount = scalar
    if amount < 0:
        negative = True
        amount *= -1
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
        
    if negative:
        amount *= -1
    print(scalar, units, '=>', amount, pre, units)

if __name__ == '__main__':
    get_prefix(24582000)
    get_prefix(0.0021040, units='m/s')
    get_prefix(0.00021040)
