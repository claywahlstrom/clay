
"""
time module

"""

DEF_COUNTRY = 'usa'
DEF_CITY    = 'vancouver'

MONTHS = ['january', 'february', 'march',
          'april', 'may', 'june', 'july',
          'august', 'september', 'october',
          'november', 'december']

TAD_BASE = 'https://www.timeanddate.com/astronomy' # astronomy or sun url base

def get_time_struct():
    """Returns the local time as struct object"""
    from time import localtime, time
    return localtime(time())

class SunTime(object):
    """A class for storing sun data collected from timeanddate.com (c) in the following form:
        Rise/Set     |     Daylength       |   Solar Noon
    Sunrise | Sunset | Length | Difference | Time | Million Miles

    Countries with more than one occurence of a city require state abbrev.s,
    such as Portland, OR, and Portland, ME:
         city -> portland-or
         city -> portland-me
    
    """

    COLS = 6
    
    def __init__(self, country=DEF_COUNTRY, city=DEF_CITY):
        self.country = country
        self.city = city
        self.build()

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(country=%s, city=%s)' % (self.__class__.__name__, self.country, self.city)
        
    def build(self):
        """Collects sun data and creates the following fields:
            req  = request response
            cont = web request content
            soup = `bs4` soup object
            data = list of data scraped
        
        """
        from bs4 import BeautifulSoup as _BS
        import requests as _requests
        url = '/'.join([TAD_BASE, self.country, self.city])
        req = _requests.get(url)
        if req.status_code != 200:
            raise Exception('request unsuccessful, url: %s' % url)
        cont = req.content
        soup = _BS(cont, 'html.parser')
        scraped = [td.text for td in soup.select('#as-monthsun > tbody > tr > td')]
        
        message = None
        # check for notes about daylight savings
        if scraped[0].startswith('Note'):
            message = scraped[0]
            print(message)
            scraped = scraped[1:]

        # parse the data into rows
        data = list()
        for i in range(0, len(scraped), SunTime.COLS):
            data.append(scraped[i: i + SunTime.COLS])

        # store relevant vars
        self.url     = url
        self.req     = req
        self.cont    = cont
        self.soup    = soup
        self.scraped = scraped
        self.data    = data
        self.message = message

    def __check_valid(self, day):
        if day < 0 or day >= len(self.data):
            raise ValueError('day must be from 0 to ' + str(len(self.data) - 1))
        
    def get_data(self):
        """Returns data retrieved and parsed from timeanddate.com (c)"""
        return self.data

    def get_message(self):
        """Prints out any important information such as daylight savings messages"""
        return self.message

    def get_sunrise(self, day=0):
        """Returns string of sunrise time"""
        self.__check_valid(day)
        return self.data[day][0]

    def get_sunset(self, day=0):
        """Returns string of sunset time"""
        self.__check_valid(day)
        return self.data[day][1]

    def get_solar_noon(self, day=0):
        """Returns string of the solar noon time"""
        self.__check_valid(day)
        return self.data[day][4]

    def rebuild(self):
        """An alias for building the relevant information. See `build`"""
        self.build()
        
def time_until(year, month, day):
    """Finds time until year, month, day and returns a dt.timedelta object"""
    import datetime as dt
    return dt.datetime(year, month, day) - dt.datetime.today()

if __name__ == '__main__':
    print(get_time_struct())
    sun = SunTime()
    print('sunset tonight', sun.get_sunset())
    
    print('birthday', time_until(2018, 11, 6))
    print('exams over', time_until(2018, 3, 16))
