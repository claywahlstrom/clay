"""
Engineering module
"""

# Coulomb's constant
C = 6.241*10**18
OHMS_TABLE = {'I':'V/R',
            'V':'I*R',
            'R':'V/I'}
# Standard SI prefixes
prefixes = ['T','G','M','k','','m','u','n','p']

def get_prefix(am, label='Amps'):
    amt = am
    position = prefixes.index('')
    pre = str()

    while amt > 1000:
        amt /= 1000
        position -= 1
        pre = prefixes[position]

    while amt < 1:
        amt *= 1000
        position += 1
        pre = prefixes[position]

    print(am, label, '=>', amt, pre + label)

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
    get_prefix(0.0021040)
    get_prefix(0.00021040)
    print(series([10, par([100, 25, 100, 50, 12.5])]))
    print(ohms_law(V=9, I=15))
