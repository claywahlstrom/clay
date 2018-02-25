
"""
lib: a librarian's library

"""

# test links:
# link = 'https://www.youtube.com/watch?v=r9cnHO15YgU'
# link ='http://www.crummy.com/software/BeautifulSoup/bs3/documentation.html'
# link = 'https://www.washingtonpost.com/world/europe/european-officials-key-figure-in-paris-attacks-wounded-in-brussels-raid/2016/03/18/b0327da6-ed29-11e5-a9ce-681055c7a05f_story.html'
# link = 'http://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/organic-food/art-20043880'
# link = 'http://www.eufic.org/article/en/health-and-lifestyle/food-choice/artid/social-economic-determinants-food-choice/'

import sys as _sys
import time as _time

from bs4 import BeautifulSoup as _BS
import requests as _requests

from clay import WEB_HDR as _WEB_HDR
from clay.web import get_title as _get_title

COM = ', '
PER = '. '

# TODO: break up build method into subroutines
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
        self.build_string()

    def build_dict(self):
        """Sets up the variables"""
        req = _requests.get(self.link)
        page = req.content
        soup = _BS(page, 'html.parser')
        now = _time.ctime().split()
        data = dict()

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

    def build_string(self):
        """Builds the citation string and stores it in the string member"""
        string = str()
        if 'author' in self.data.keys():
            au = self.data['author']
            if au.count(' '): # multiple words
                string += COM.join([au.split()[-1], ' '.join(au.split()[:-1])])
            else:
                string += au
            string += PER
        if 'title' in list(self.data.keys()):
            string += '"' + self.data['title'] + '." '
        if 'publisher' in self.data.keys():
            string += self.data['publisher'] + COM
        string += COM.join([self.data['date_retr'], self.data['url']]) + PER[0] # using data
        self.string = string

    def get(self):
        return self.string

    def show(self):
        print(self.get())

def define(words):
    """Prints possible definitions for a word by using Cambridge's dictionary"""
    baseuri = 'http://dictionary.cambridge.org/dictionary/english/'
    inituri = baseuri + '?q=' + words.replace(' ','+')
    try:
        f = _requests.get(inituri, headers=_WEB_HDR).content
        uri = baseuri + words
        f = _requests.get(uri, headers=_WEB_HDR).content
        soup = _BS(f, 'html.parser')
        print('definitions for', words.capitalize())
        for i in [g.text for g in soup.select('.entry-body__el .def')]:
            print(' '*4 + i)
    except:
        print('No definitions found on', inituri)

def sort_bib(filename):
    """Sorts a bibliography lexicographically, no stdout required

    You need to sort quoted titles manually though
    """

    with open(filename) as fp:
        lines = fp.read().strip().split('\n')

    lines = sorted(lines, key=lambda x: x.replace('"', ''))
    content = '\n'.join(lines)

    with open('sorted_' + filename, 'w') as cont:
        cont.write(content)

class Title(object):
    """A class for creating proper titles"""
    SKIP_LIST = ['a','am','an','and',
                 'for','in','of',
                 'on','the','to']

    def __init__(self, title):
        self.title = title
        self.create()

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.title)

    def __xcaptilize(self, word):
        if word.lower() not in Title.SKIP_LIST:
            return word.capitalize()
        return word.lower()

    def create(self):
        words = self.title.split(' ')
        self.__get = ' '.join(map(self.__xcaptilize, words))
        self.__get = self.__get[0].upper() + self.__get[1:]

    def get(self):
        return self.__get

if __name__ == '__main__':
    if len(_sys.argv) > 1:
        link = _sys.argv[-1]
    else:
        link = 'http://www.datascribble.com/deep-learning/deep-learning-tensorflow-series-part-1-neural-network/'
    cit = Citation(link)
    cit.show()

    # define('vector quantity')

    bt = Title('the best hot dog on a stick')
    print(bt.get())
