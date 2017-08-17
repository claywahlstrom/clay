"""
lib: a librarian's library

The function 'define' has probles ATM...

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

class Cit:
    """Basic citation class for MLA/Chicago styles

    CATEGORIES:
    # editor/author
    # title
    # container
    # date
    # url

    # follows MLA 8 standards

    """

    COM = ', '
    PER = '. '
    SPECS = ['author',
             'title',
             'publisher',
             'site_name']

    def __init__(self, link):
        self.link = link
        self.build()

    def build(self):
        while not(self.link):
            self.link = input('link? ')
        url = self.link
        page = _requests.get(self.link).content
        soup = _BS(page, 'html.parser')
        cit_dict = dict()

        cit_dict['title'] = self.get_title(soup)

        now = _time.ctime().split()
        cit_dict['retrieved'] = ' '.join([str(int(now[2])), now[1] + '.',now[-1]])
        cit_dict['url'] = url

        for prop in Cit.SPECS:
            metas = ['og','article']
            for meta in metas:
                desc = soup.find_all(attrs={'property': meta + ':' + prop})
                if desc: # if found
                    try:
                        cit_dict[prop] = desc[0]['content']
                    except Exception as e:
                        print(e)
                    break
                if not(desc):
                    desc = soup.find_all(attrs={'name': prop})
            if desc: # if found
                try:
                    cit_dict[prop] = desc[0]['content']
                except Exception as e:
                    print(e)
        cit_string = str()
        if not('author' in cit_dict.keys()):
            print('author not found')
            cit_dict['author'] = soup.find_all('span', attrs={'itemprop': 'name'})[0].text
        if 'author' in cit_dict.keys():
            au = cit_dict['author']
            if len(au.split()) > 1:
                cit_string = Cit.COM.join([au.split()[-1], ' '.join(au.split()[:-1])])
            else:
                cit_string = au
            cit_string += Cit.PER
        if 'title' in list(cit_dict.keys()):
            cit_string += '"' + cit_dict['title'] + '." '
        if 'publisher' in cit_dict.keys():
            cit_string += cit_dict['publisher'] + Cit.COM
        cit_string += Cit.COM.join([cit_dict['retrieved'], cit_dict['url']]) + Cit.PER[0] # using cit_dict
        self.soup = soup
        self.cit_dict = cit_dict
        self.cit_string = cit_string

    def get(self):
        return self.cit_string

    def get_title(self, s):
        return s.find('title').cit_string

    def show(self):
        print(self.get())

def define(words):
    """Display Cambridge dictionary definitions"""
    uri = 'http://dictionary.cambridge.org/dictionary/english/' + words.split()[0] + '?q=' + words.replace(' ','+')
    print(uri)
    f = _requests.get(uri).content
    soup = _BS(f, 'html.parser')
    print('definitions for', words.capitalize())
    for i in [g.text for g in soup.select('.entry-body__el .def')]:
        print(' '*4 + i)

class Title:
    """Create proper book titles"""
    SKIP_LIST = ['a','am','an','and',
                 'for','in','of',
                 'on','the','to']

    def __init__(self, title):
        self.title = title
        self.create()

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__,self.title)

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
    cit = Cit(link)
    cit.show()

    # define('vector quantity')

    bt = Title('the best hot dog on a stick')
    print(bt.get())
