
"""
time module

"""

TAD_BASE = 'https://www.timeanddate.com/astronomy'

DEF_COUNTRY = 'usa'
DEF_CITY = 'vancouver'

def get_time_struct():
    """Return local time as struct object"""
    from time import localtime, time
    return localtime(time())

class SunInfo:
    """Get Sun data from timeanddate.com (c) in the following form:
    |    Rise/Set    |     Daylength       |   Solar Noon
    Sunrise | Sunset | Length | Difference | Time | Million Miles

    Countries with more than one occurence of a city require state abbrev.s,
    such as Portland, OR, and Portland, ME:
         city -> portland-or
         city -> portland-me
    
    """

    cols = 6
    
    def __init__(self, country=DEF_COUNTRY, city=DEF_CITY):
        self.country = country
        self.city = city
        self.build()
        
    def build(self):
        from bs4 import BeautifulSoup as _BS
        import requests as _requests
        req = _requests.get('/'.join([TAD_BASE, self.country, self.city]))
        cont = req.content
        soup = _BS(cont, 'html.parser')
        scraped = [td.text for td in soup.select('#as-monthsun > tbody > tr > td')]

        # parse the data into rows
        data = list()
        for i in range(0, len(scraped), SunInfo.cols):
            data.append(scraped[i: i + SunInfo.cols])

        # store relevant varss
        self.req = req
        self.cont = cont
        self.soup = soup
        self.scraped = scraped
        self.data = data
        
    def get_data(self):
        """Return data retrieved and parsed from timeanddate.com (c)"""
        return self.data

    def get_sunrise(self, day=0):
        """Return string of sunrise time"""
        sunrise = self.data[day][0]
        return sunrise

    def get_sunset(self, day=0):
        """Return string of sunset time"""
        sunset = self.data[day][1]
        return sunset

    def rebuild(self):
        """Alias for `build` method"""
        self.build()
        
def time_until(year, month, day):
    """Find time until year, month, day.
    Returns dt.timedelta object

    """
    import datetime as dt
    start = dt.datetime.today()
    end = dt.datetime(year, month, day, 0, 0, 0)
    return end - start

if __name__ == '__main__':
    print(get_time_struct())
    suninfo = SunInfo()
    print(suninfo.get_sunset())
    
    print('birthday', time_until(2017, 11, 6))
    print('exams over', time_until(2017, 12, 14))
