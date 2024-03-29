
"""
libr: tools for scholars and librarians

"""

import re as _re
import time as _time

from bs4 import BeautifulSoup as _BS
import requests as _requests

from clay.lists import rmdup as _rmdup
from clay.net.core import get_title as _get_title, HEADERS as _HEADERS

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
    """
    Class Essay can be used for storing and analyzing essays.
    Converts the given line separator to single carriage returns
    (\n). Start line must be >= 1.

    """

    def __init__(self, source: object, line_start: int=1, line_sep: str='\n') -> None:
        """Initializes this essay with the given source, line start, and line separator"""
        if line_start < 1:
            raise ValueError('line start must be >= 1')
        self.line_start = line_start
        self.line_sep = line_sep
        end = '\n\n' # default
        if isinstance(source, bytes):
            if b'\x0c' in source:
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

    def __repr__(self) -> str:
        """Returns the string representation of this essay"""
        preview = self.source[:20].replace('\n', '\\n')
        return '{}(source={{{}...}}, line_start={})'.format(
            self.__class__.__name__, preview, self.line_start)

    def are_paren_bal(self) -> bool:
        """Returns True if parentheses are balanced, False otherwise"""
        return self.text.count('(') == self.text.count(')')

    def find_extraspace(self) -> None:
        """Finds extra spaces, ex. ' .' and '  '"""
        print('Extraspace')
        print(_re.findall('(.{6}  .{6})|(.{6} \.[ \w\n]{6})', self.text))

    def find_firstnlast(self, pdelim: str='\n') -> None:
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

    def find_midcaps(self) -> None:
        """Finds unexpected capitals"""
        print('Mid caps')
        mids = list(filter(lambda sent: not('I' in sent),
                           list(_re.findall('\w+ [A-Z]+.{6}', self.text)))) # range for context
        print(mids)

    def find_pronouns(self) -> None:
        """Finds uncapitalized I's and prints the result"""
        print('Pronouns (I\'s)')
        print(_re.findall('.{6} i .{6}', self.text))

    def find_topics(self) -> None:
        """Finds topic sentences and prints the result"""
        print('Topic sentences')
        print(self.get_topics())

    def find_wrongcaps(self) -> None:
        """Displays unexpected capitals"""
        print('Possibly wrong caps')
        print(_re.findall('.{5}\. [a-z0-9].{5}', self.text))

    def fix_quotes(self) -> None:
        """Replaces curly quotes with straight ones"""
        self.text = replace_smart_quotes(self.text)

    def fix_spaces(self) -> None:
        """Replaces improper spacing"""
        self.text = self.text.replace('  ', ' ') # extra space
        self.text = self.text.replace(' .', '.') # period before
        self.text = self.text.replace('.  ', '. ') # space after

    def get_paragraph_count(self) -> None:
        """Returns # of paragraphs"""
        return len(self.text.strip().split('\n'))

    def get_paren_citation(self, page_num: bool=True, http_only: bool=False) -> list:
        """
        Returns citations extracted from essay.
        Found using MLA parenthetical standards

        """
        parens = _re.findall('\(.*\)', self.text)
        parens = _rmdup(parens)
        if http_only:
            parens = [x for x in parens if 'http' in x]
        if not(page_num):
            parens = [x for x in parens if x[-1].isalpha()] # if last of paren is not page num
        return parens

    def get_period_count(self) -> int:
        """Returns # of periods"""
        return (self.text).count('.')

    def get_sentence_count(self) -> int:
        """Returns # of sentences"""
        return len(_re.findall('\.\s', replace_smart_quotes(self.text).replace('"', '')))

    def get_topics(self) -> list:
        """Returns list of topic sentences"""
        return _re.findall('\n([A-Z][^\.!?]*[\.!?]) ', self.text)

    def get_word_count(self, ignore_headings: bool=True) -> int:
        """Returns # of words"""
        lines = self.text.split('\n')
        count = 0
        for line in lines:
            if len(line) > 0:
                # assumes a paragraph has at least one period
                if not(ignore_headings and line.count('.') == 0):
                    count += len(line.split())
        return count

    def print_summary(self) -> None:
        """Displays basic stats"""
        print(self)
        print('para', self.get_paragraph_count())
        print('per', self.get_period_count())
        print('sents', self.get_sentence_count())
        print('words', self.get_word_count())

    def save_topics(self, filename: str='saved-topics.txt') -> None:
        """Saves the topic sentences to the given filename"""
        with open(filename, 'w') as f:
            f.write('\n'.join(self.get_topics()))
        print('Topics written to', filename)

class Citation(object):
    """
    A class for citating content in MLA/Chicago styles

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

    def __init__(self, link: str) -> None:
        """Initializes this citation"""
        self.link = link
        self.build_dict()

    def build_dict(self) -> None:
        """Sets up the variables"""
        req = _requests.get(self.link)
        page = req.content
        soup = _BS(page, 'html.parser')
        now = _time.ctime().split()

        self.data = {}
        self.data['title'] = _get_title(soup)
        self.data['date_retr'] = ' '.join([str(int(now[2])), now[1] + '.',now[-1]])
        self.data['url'] = self.link

        for prop in Citation.REQUIRED:
            metas = ['og','article']
            for meta in metas:
                desc = soup.find_all(attrs={'property': meta + ':' + prop})
                if desc: # if found
                    try:
                        self.data[prop] = desc[0]['content']
                    except Exception as e:
                        print(e)
                    break
                if not desc:
                    desc = soup.find_all(attrs={'name': prop})
                if desc: # if found
                    try:
                        self.data[prop] = desc[0]['content']
                    except Exception as e:
                        print(e)

        if 'author' not in self.data.keys():
            print('author not found')
            self.data['author'] = soup.find_all('span', attrs={'itemprop': 'name'})[0].text

        self.soup = soup
        self.req = req
        self.page = page

    def to_string(self) -> str:
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
        string += COM_SP.join([self.data['date_retr'], self.data['url']]) + PER_SP[0]
        return string

def define(words) -> None:
    """Prints possible definitions for a word by using Cambridge's dictionary"""
    baseuri = 'http://dictionary.cambridge.org/dictionary/english/'
    inituri = baseuri + '?q=' + words.replace(' ','+')
    try:
        f = _requests.get(inituri, headers=_HEADERS).content
        uri = baseuri + words
        f = _requests.get(uri, headers=_HEADERS).content
        soup = _BS(f, 'html.parser')
        print('definitions for', words.capitalize())
        for i in [g.text for g in soup.select('.entry-body__el .def')]:
            print(' '*4 + i)
    except:
        print('No definitions found on', inituri)

def proper_title(title: str, ignore_acronyms: bool=True) -> str:
    """Returns the title with proper casing"""
    words = title.split(' ')
    title = ' '.join(
        map(lambda word: proper_word(word, ignore_acronyms=ignore_acronyms),
            words))
    return title[0].upper() + title[1:]

def proper_word(word: str, ignore_acronyms: bool=True) -> str:
    """Returns the word with proper casing"""
    if word.isupper() and not ignore_acronyms:
        return word
    elif word.lower() not in SHORT_WORDS:
        return word.capitalize()
    return word.lower()

def replace_smart_quotes(text: str, encoding: str='utf8') -> str:
    """Replaces smart single and double quotes with straight ones"""
    encoded = text.encode(encoding)
    for single in (b'\x98', b'\x99'):
            encoded = encoded.replace(b'\xe2\x80' + single, b'\'')
    for double in (b'\x93', b'\x94', b'\x9c', b'\x9d'):
            encoded = encoded.replace(b'\xe2\x80' + double, b'"')
    return encoded.decode(encoding)

def sort_bib(filename: str) -> None:
    """
    Sorts a bibliography lexicographically, no stdout required.
    You need to sort quoted titles manually though

    """

    with open(filename) as fp:
        lines = fp.read().strip().split('\n')

    lines = sorted(lines, key=lambda x: x.replace('"', ''))
    content = '\n'.join(lines)

    with open('sorted-' + filename, 'w') as cont:
        cont.write(content)

if __name__ == '__main__':

    from clay.tests import testif
    from clay.utils import qualify

    with open(r'test_files\essay.txt') as fp:
        fread = fp.read()

    e = Essay(fread, line_start=3, line_sep='\n')
    e.print_summary()
    e.find_wrongcaps()
    e.find_midcaps()
    e.find_extraspace()
    e.find_topics()
    e.fix_spaces()

    with open(r'test_files\essay-fixper.txt','w') as fp:
        fp.write(e.text)

    link = 'https://www.theatlantic.com/science/archive/2019/04/what-happens-human-body-space/586966/'
    cit = Citation(link)
    print(cit.to_string())

    define('vector quantity')

    testif('converts title correctly',
        proper_title('the best hot dog on a stick'),
        'The Best Hot Dog on a Stick',
        name=qualify(proper_title))

    testif('converts short word "hi" correctly',
        proper_word('hello'),
        'Hello',
        name=qualify(proper_word))
    testif('converts short word "a" correctly',
        proper_word('a'),
        'a',
        name=qualify(proper_word))
