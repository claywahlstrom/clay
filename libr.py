
"""
libr: tools for scholars and librarians


"""


import re as _re
import sys as _sys
import time as _time

from bs4 import BeautifulSoup as _BS
import requests as _requests

from clay.lists import rmdup as _rmdup
from clay.web import get_title as _get_title, WEB_HDRS as _WEB_HDRS

COM_SP = ', '
# ! fix topics method for 'e.g.', 'et al. author' and other abbreviations, list in PER_EXCEPTIONS
PER_EXCEPTIONS = ['e.g.', 'et al.', 'i.e.',
                  'Mrs.', 'Ms.', 'Mr.', 'Dr.'] # work in progress, may not be needed if not many in essay
PER_SP = '. '
SHORT_WORDS = ['a', 'am', 'an', 'and', 'for',
               'in', 'of', 'on', 'the', 'to']
TEST_LINKS = [
    'https://www.youtube.com/watch?v=r9cnHO15YgU',
    'http://www.crummy.com/software/BeautifulSoup/bs3/documentation.html'
    'https://www.washingtonpost.com/world/europe/european-officials-key-figure-in-paris-attacks-wounded-in-brussels-raid/2016/03/18/b0327da6-ed29-11e5-a9ce-681055c7a05f_story.html'
    'http://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/organic-food/art-20043880'
    'http://www.eufic.org/article/en/health-and-lifestyle/food-choice/artid/social-economic-determinants-food-choice/'
]


class Essay(object):
    """Class Essay can be used for storing and analyzing essays.
       Converts the given line separator to single carriage returns
       (\n). Start line must be >= 1."""

    def __init__(self, source, line_start=1, line_sep='\n'):
        if line_start < 1:
            raise ValueError('line start must be >= 1')
        self.line_start = line_start
        self.line_sep = line_sep
        end = '\n\n' # default
        if type(source) == bytes:
            if b'\x0c' in text:
                end = '\x0c' # google doc's new page delimiter
            source = source.decode('utf8')
        self.source = source.replace(line_sep, '\n') # for easier parsing
        self.text = '\n'.join(self.source.split('\n')[self.line_start - 1:]) # get main body
        if self.text == self.text.rstrip(): # if no carriage returns at end, adjust text
            self.text += '\n\n'
        if '\n\n\n' in self.text:
            end += '\n' # makes the end of this essay unique for easy trimming

        try:
            self.text = self.text[:(self.text).index(end)] # remove extra fat
        except:
            print('Could not remove extra fat from the text')

        try:
            for exc in PER_EXCEPTIONS:
                self.text = self.text.replace(exc, exc.replace('.', ''))
        except Exception as e:
            print(e)
            print('Could not remove the period exceptions from the text')

    def __repr__(self):
        preview = self.source[:20].replace('\n', '\\n')
        return 'Essay(source={{{}...}}, line_start={})'.format(preview, self.line_start)

    def are_paren_bal(self):
        """Finds if parentheses are balanced, returns boolean"""
        return self.text.count('(') == self.text.count(')')

    def find_extraspace(self):
        """Finds extra spaces, ex. ' .' and '  '"""
        print('Extraspace')
        print(_re.findall('(.{6}  .{6})|(.{6} \.[ \w\n]{6})', self.text))

    def find_firstnlast(self, pdelim='\n'):
        """Simplifies long texts"""
        spl = self.text.split(pdelim)
        if spl.count('') > len(spl) / 2: # if half parsed incorrectly
            print('Please check your pdelim arg')
            return
        for p in spl:
            f = _re.findall('([A-Z][^\.!?]*[\.!?]) [A-Z]', p)
            try:
                first, last = '[0] ' + f[0], '[-1] ' + f[-1]
                print(first)
                print(last)
            except: # if heading of section
                print(p)
            print()

    def find_midcaps(self):
        """Finds unexpected capitals"""
        print('Mid caps')
        mids = list(filter(lambda sent: not('I' in sent),
                           list(_re.findall('\w+ [A-Z]+.{6}', self.text)))) # range for context
        print(mids)

    def find_pronouns(self):
        """Finds uncapitalized I's and prints the result"""
        print('Pronouns (I\'s)')
        print(_re.findall('.{6} i .{6}', self.text))

    def find_topics(self):
        """Finds topic sentences and prints the result"""
        print('Topic sentences')
        print(self.get_topics())

    def find_wrongcaps(self):
        """Displays unexpected capitals"""
        print('Possibly wrong caps')
        print(_re.findall('.{5}\. [a-z0-9].{5}', self.text))

    def fix_quotes(self):
        """Replaces curly quotes with straight ones"""
        for double in ('\x9c', '\x9d'):
            self.text = self.text.replace('\xe2\x80' + double, '"')
        self.text = self.text.replace('\xe2\x80\x99', "'")

    def fix_spaces(self):
        """Replaces improper spacing"""
        self.text = self.text.replace('  ', ' ') # extra space
        self.text = self.text.replace(' .', '.') # period before
        self.text = self.text.replace('.  ', '. ') # space after

    def get_paragraph_count(self):
        """Returns # of paragraphs"""
        return len(self.text.strip().split('\n'))

    def get_paren_citation(self, page_num=True, http_only=False):
        """Returns citations extracted from essay.
           Found using MLA parenthetical standards"""
        parens = _re.findall('\(.*\)', self.text) # prev. [self.text[self.starts[i]+1:self.ends[i]] for i in xrange(len(self.starts))]
        parens = _rmdup(parens)
        if http_only:
            parens = [x for x in parens if 'http' in x]
        if not(page_num):
            parens = [x for x in parens if x[-1].isalpha()] # if last of paren is not page num
        return parens

    def get_period_count(self):
        """Returns # of periods"""
        return (self.text).count('.')

    def get_sentence_count(self):
        """Returns # of sentences"""
        return len(_re.findall('\.\s', self.text))

    def get_topics(self):
        """Returns list of topic sentences"""
        return _re.findall('\n([A-Z][^\.!?]*[\.!?]) ', self.text)

    def get_word_count(self, ignore_headings=True):
        """Returns # of words"""
        lines = self.text.split('\n')
        count = 0
        for line in lines:
            if len(line) > 0:
                # assumes a paragraph has at least one period
                if not(ignore_headings and line.count('.') == 0):
                    count += len(line.split())
        return count

    def print_summary(self):
        """Displays basic stats"""
        print(self)
        print('para', self.get_paragraph_count())
        print('per', self.get_period_count())
        print('sents', self.get_sentence_count())
        print('words', self.get_word_count())

    def save_topics(self, filename='savedtopics.txt'):
        with open(filename, 'w') as f:
            f.write('\n'.join(self.get_topics()))
        print('Topics written to', filename)

class Citation(object):
    """A class for citating content in MLA/Chicago styles

       CATEGORIES:
       # editor/author
       # title
       # container
       # date
       # url

       # follows MLA 8 standards

       Data is stored as a dictionary in the object's `data` attribute

    """

    REQUIRED = ['author',
                'title',
                'publisher',
                'site_name']

    def __init__(self, link):
        self.link = link
        self.build_dict()
        self.to_string()

    def build_dict(self):
        """Sets up the variables"""
        req = _requests.get(self.link)
        page = req.content
        soup = _BS(page, 'html.parser')
        now = _time.ctime().split()
        data = {}

        data['title'] = _get_title(soup)
        data['date_retr'] = ' '.join([str(int(now[2])), now[1] + '.',now[-1]])
        data['url'] = self.link

        for prop in Citation.REQUIRED:
            metas = ['og','article']
            for meta in metas:
                desc = soup.find_all(attrs={'property': meta + ':' + prop})
                if desc: # if found
                    try:
                        data[prop] = desc[0]['content']
                    except Exception as e:
                        print(e)
                    break
                if not(desc):
                    desc = soup.find_all(attrs={'name': prop})
            if desc: # if found
                try:
                    data[prop] = desc[0]['content']
                except Exception as e:
                    print(e)

        if not('author' in data.keys()):
            print('author not found')
            data['author'] = soup.find_all('span', attrs={'itemprop': 'name'})[0].text

        self.data = data
        self.soup = soup
        self.req = req
        self.page = page

    def to_string(self):
        """Builds the citation string and stores it in the string member"""
        string = ''
        if 'author' in self.data.keys():
            au = self.data['author']
            if au.count(' '): # multiple words
                string += COM_SP.join([au.split()[-1], ' '.join(au.split()[:-1])])
            else:
                string += au
            string += PER_SP
        if 'title' in list(self.data.keys()):
            string += '"' + self.data['title'] + '." '
        if 'publisher' in self.data.keys():
            string += self.data['publisher'] + COM_SP
        string += COM_SP.join([self.data['date_retr'], self.data['url']]) + PER_SP[0] # using data
        return string

def define(words):
    """Prints possible definitions for a word by using Cambridge's dictionary"""
    baseuri = 'http://dictionary.cambridge.org/dictionary/english/'
    inituri = baseuri + '?q=' + words.replace(' ','+')
    try:
        f = _requests.get(inituri, headers=_WEB_HDRS).content
        uri = baseuri + words
        f = _requests.get(uri, headers=_WEB_HDRS).content
        soup = _BS(f, 'html.parser')
        print('definitions for', words.capitalize())
        for i in [g.text for g in soup.select('.entry-body__el .def')]:
            print(' '*4 + i)
    except:
        print('No definitions found on', inituri)

def proper_title(title):
    """Returns the title with proper casing"""
    words = title.split(' ')
    title = ' '.join(map(proper_word, words))
    return title[0].upper() + title[1:]

def proper_word(word):
    """Returns the word with proper casing"""
    if word.lower() not in SHORT_WORDS:
        return word.capitalize()
    return word.lower()

def sort_bib(filename):
    """Sorts a bibliography lexicographically, no stdout required.
       You need to sort quoted titles manually though"""

    with open(filename) as fp:
        lines = fp.read().strip().split('\n')

    lines = sorted(lines, key=lambda x: x.replace('"', ''))
    content = '\n'.join(lines)

    with open('sorted_' + filename, 'w') as cont:
        cont.write(content)

if __name__ == '__main__':

    from clay.tests import testif

    with open(r'test_files\essay.txt') as fp:
        fread = fp.read()

    e = Essay(fread, line_start=3, line_sep='\n')
    e.print_summary()
    e.find_wrongcaps()
    e.find_midcaps()
    e.find_extraspace()
    e.find_topics()
    e.fix_spaces()

    with open(r'test_files\essay_fixper.txt','w') as fp:
        fp.write(e.text)

    link = 'http://www.datascribble.com/deep-learning/deep-learning-tensorflow-series-part-1-neural-network/'
    cit = Citation(link)
    print(cit.to_string())

    define('vector quantity')

    testif('proper_word converts short word "hi" correctly',
        proper_word('hello'), 'Hello')
    testif('proper_word converts short word "a" correctly',
        proper_word('a'), 'a')
    testif('proper_title converts title correctly',
        proper_title('the best hot dog on a stick'),
        'The Best Hot Dog on a Stick')
