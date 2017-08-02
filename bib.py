"""
BASIC cit_dict FOR MLA/CHICAGO

CATEGORIES:
# editor/author
# title
# container
# date
# url

# follows MLA 8 standards

"""

# test links:
# link = 'https://www.youtube.com/watch?v=r9cnHO15YgU'
# link ='http://www.crummy.com/software/BeautifulSoup/bs3/documentation.html'
# link = 'https://www.washingtonpost.com/world/europe/european-officials-key-figure-in-paris-attacks-wounded-in-brussels-raid/2016/03/18/b0327da6-ed29-11e5-a9ce-681055c7a05f_story.html'
# link = 'http://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/organic-food/art-20043880'
# link = 'http://www.eufic.org/article/en/health-and-lifestyle/food-choice/artid/social-economic-determinants-food-choice/'

import sys
import time
import urllib.request, urllib.parse, urllib.error

from bs4 import BeautifulSoup

PER = '. '
COM = ', '
SPECS = ['author',
         'title',
         'publisher',
         'site_name']

class Cit:
    def __init__(self, link):
        self.link = link
        self.build()
    def build(self):
        if not self.link:
            self.link = input('self.link: ')
        url = self.link
        page = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(page, 'html.parser')
        cit_dict = dict()

        cit_dict['title'] = self.get_title(soup)

        now = time.ctime().split()
        cit_dict['retrieved'] = ' '.join([str(int(now[2])), now[1] + '.',now[-1]])
        cit_dict['url'] = url

        for prop in SPECS:
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
                cit_string = COM.join([au.split()[-1], ' '.join(au.split()[:-1])])
            else:
                cit_string = au
            cit_string += PER
        if 'title' in list(cit_dict.keys()):
            cit_string += '"' + cit_dict['title'] + '." '
        if 'publisher' in cit_dict.keys():
            cit_string += cit_dict['publisher'] + COM
        cit_string += COM.join([cit_dict['retrieved'], cit_dict['url']]) + PER[0] # using cit_dict
        self.soup = soup
        self.cit_dict = cit_dict
        self.cit_string = cit_string
        
    def get(self):
        return self.cit_string
    def get_title(self, s):
        return s.find('title').cit_string
    def show(self):
        print(self.get())


if __name__ == '__main__':
    if len(sys.argv) > 1:
        link = sys.argv[-1]
    else:
        link = 'http://www.datascribble.com/deep-learning/deep-learning-tensorflow-series-part-1-neural-network/'
    cit = Cit(link)
    cit.show()
