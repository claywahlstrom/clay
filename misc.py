
"""
misc: content that doesn't have a separate module

"""

import datetime as _dt
import time as _time

from bs4 import BeautifulSoup as _BeautifulSoup
import requests as _requests

from clay import isUnix as _isUnix, WEB_HDR as _WEB_HDR

def human_hex(dec):
    """Converts decimal values to human readable hex.
    Mainly used in engineering class
    """
    return hex(dec)[2:]

def map_args(function, iterable, *args, **kwargs):
    """Maps iterable to a function with arguments/keywords.\nDynamic types"""
    return type(iterable)(function(x, *args, **kwargs) for x in iterable)

class Pollen(object):

    """Class Pollen can be used to retrieve and store information about
       the pollen forecast from Weather.com (tm)"""

    EXT = ':4:US'

    def __init__(self, zipcode=98105):
        """Constructs a new Pollen object using the given zipcode"""
        self.zipcode = zipcode
        self.build()
        
    def _get_markup(self, uri):
        req = _requests.get(uri, params=_WEB_HDR)
        tries = 1
        while req.status_code != 200 and tries < 5:
            print('Retrying Pollen request...')
            _time.sleep(2)
            req = _requests.get(uri, params=_WEB_HDR)
            tries += 1
        return req.content

    def build(self, ext=True):
        """Builds and populates the pollen record database"""
        uri = 'https://weather.com/forecast/allergy/l/' + str(self.zipcode)
        if ext:
            uri += self.EXT
        markup = self._get_markup(uri)

        page = _BeautifulSoup(markup, 'html.parser')

        found = page.select('button > div')
        fd = dict()
        if len(found) > 0:
            for elm in found:
                divs = elm.select('div')
                fd[divs[0].getText()] = divs[-1].getText()
        else:
            fd['Today'] = fd[str(_dt.date.today().day + 1)] = 'error'
        self.src = page
        self.records = fd

    def printall(self):
        """Prints all of the records information in a table format"""
        print('Pollen data for', self.zipcode)
        for i, j in self.records.items():
            print('{:>{}}: {}'.format(i, len('Tonight'), j))

    def __get_day(self, day):
        date = str(_dt.date.today().day + day)
        for dong in self.records:
            if dong.endswith(date):
                return self.records[dong]

    def get_today(self):
        """Returns the type of pollen for today"""
        if 'Tonight' in self.records:
            return self.records['Tonight']
        elif 'Today' in self.records:
            return self.records['Today']
        else:
            return self.__get_day(0)
        
    def get_tomorrow(self):
        """Returns the type of pollen forecasted for tomorrow"""
        return self.__get_day(1)

if __name__ == '__main__':

    print(human_hex(2700))

    def func(x, y=2, z=3):
        return x + y + z

    print(map_args(func, (1, 4, 16, 25), z = 4))

    p = Pollen(97132)
    p.printall()
    p.zipcode = 98105
    p.build()
    p.printall()
