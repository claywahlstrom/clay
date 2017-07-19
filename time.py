
"""
time module

funtions:
    time.struct_time get_time_struct()
    str get_sunset()
    datetime.timedelta time_until()
"""

def get_time_struct():
    """Return local time as struct object"""
    from time import localtime, time
    return localtime(time())

def get_sunset():
    """Return string of sunset time"""
    from bs4 import BeautifulSoup as bs
    from requests import get
    f = get('https://www.timeanddate.com/astronomy/usa/vancouver').content
    soup = bs(f, 'html.parser')
    sunset = [t.text for t in soup.select('#as-monthsun > tbody > tr > td.c.sep')][1] # find first sunset
    return sunset

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
    print(get_sunset())
    
    print(time_until(2017, 6, 26)) # france!!!
    print(time_until(2017, 11, 6))
