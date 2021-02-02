
"""
Net factories

"""

from clay.net.builders import WeatherPollenApiUrlBuilder, WundergroundUrlBuilder

class PollenUrlBuilderFactory(object):

    """Used to allow access to the pollen URL builders"""

    def __init__(self):
        """Initializes thie pollen URL builder factory"""
        self.__weather = WeatherPollenApiUrlBuilder()
        self.__wunderground = WundergroundUrlBuilder()

    @property
    def weather(self):
        """Returns the Weather.com(tm) URL builder"""
        return self.__weather

    @property
    def wunderground(self):
        """Returns the Wunderground(tm) URL builder"""
        return self.__wunderground
