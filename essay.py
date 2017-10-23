"""
Analyzer for essays
"""

__all__ = ['Essay', 'savetopics']

# ! fix topics method for 'e.g.', 'et al. author' and other abbreviations, list in EXCEPTIONS
EXCEPTIONS = ['e.g.', 'et al.', 'i.e.'] # work in progress, may not be needed if not many in essay

from re import findall as _findall

from clay.listops import rmdup as _rmdup

class Essay:
    r"""For analytics of essays. Don't use line_start as first sentence Converts line_sep to single '\n'"""
    def __init__(self, source, line_start=1, line_sep='\n'):
        self.line_start = line_start
        end = '\n\n' # default
        if type(source) == bytes:
            if b'\x0c' in text:
                end = '\x0c' # google doc's new page
            source = source.decode('utf8')
        self.source = source.replace(line_sep, '\n') # for easier parsing
        self.text = '\n'.join(self.source.split('\n')[self.line_start-1:]) # get main body
        if self.text == self.text.rstrip(): # if no carriage returns at end, adjust text
            self.text += '\n\n'
        if '\n\n\n' in self.text:
            end += '\n'

        try:
            self.text = self.text[:(self.text).index(end)] # remove extra fat
        except:
            print('Couldn\'t remove extra fat from text')
        
    def extract_paren(self, page_num=True, http_only=False):
        """Return citations extracted from essay.\nFound using parenthetical standards"""
        parens = _findall('\(.*\)', self.text) # prev. [self.text[self.starts[i]+1:self.ends[i]] for i in xrange(len(self.starts))]
        parens = _rmdup(parens)
        if http_only:
            parens = [x for x in parens if 'http' in x]
        if not(page_num):
            parens = [x for x in parens if x[-1].isalpha()] # if last of paren is not page num
        return parens

    def extraspace(self):
        """Find extra spaces, ex. ' .' and '  '"""
        print('Extraspace')
        print(_findall('(.{6}  .{6})|(.{6} \.[ \w\n]{6})', self.text))

    def firstnlast(self, pdelim='\n'):
        """Simplify long texts"""
        spl = self.text.split(pdelim)
        if '' in spl: # if parsed incorrectly
            print('Please check your pdelim arg')
            return
        for p in spl:
            f = _findall('[A-Z][^\.!?]*[\.!?]', p)
            try:
                first, last = '[0] ' + f[0], '[-1] ' + f[-1]
                print(first, last)
            except: # if heading of section
                print(p)

    def fix_spaces(self):
        """Fix bad spaces"""
        self.text = self.text.replace('  ', ' ') # xtra sp
        self.text = self.text.replace(' .', '.') # per bef
        self.text = self.text.replace('.  ', '. ') # sp aft

    def midcaps(self):
        """Find unexpected capitals"""
        print('Mid caps')
        mids = list(filter(lambda sent: not('I' in sent), list(_findall('\w+ [A-Z]+.{6}', self.text)))) # range for context
        print(mids)

    def paragraphs(self):
        """Return # of paragraphs"""
        return len(self.text.strip().split('\n'))

    def paren_bal(self):
        """Find if parentheses are balanced, returns boolean"""
        return self.text.count('(') == self.text.count(')')

    def periods(self):
        """Return # of periods"""
        return (self.text).count('.')

    def pronouns(self):
        """Find uncapitalized I's"""
        print('Pronouns (I\'s)')
        print(_findall('.{6} i .{6}', self.text))

    def sents(self):
        """Return # of sentences"""
        return len(_findall('\.\s', self.text))

    def stats(self):
        """Display basic stats"""
        print(self)
        print('para', self.paragraphs())
        print('per', self.periods())
        print('sents', self.sents())
        print('words', self.words())

    def topics(self):
        """Return list of topic sentences"""
        return _findall('\n([A-Z][^\.!?]*[\.!?]) ', self.text)

    def words(self):
        """Return # of words"""
        return len(self.text.split())

    def wrongcaps(self):
        """Display unexpected capitals"""
        print('Wrong caps')
        print(_findall('.{5}\. [a-z0-9].{5}', self.text))

def savetopics(essay, filename='savedtopics.txt'):
    with open(filename,'w') as f:
        f.write('\n'.join(essay.topics()))
    print('Topics written to', filename)

if __name__ == '__main__':
    with open('essay.txt') as f:
        fread = f.read()
    e = Essay(fread, line_start=3, line_sep='\n')
    e.stats()
    e.wrongcaps()
    e.midcaps()
    e.extraspace()
    print('Topics')
    print(e.topics())
    e.fix_spaces()
    with open('essayfixper.txt','w') as f:
        f.write(e.text)
