
"""
net builders: Mainly for URL builders

"""

import urllib.parse

class UrlBuilder(object):
    """Can be used to build formatted URLs"""

    def __init__(self, base_url):
        """Initializes this UrlBuilder"""
        self.base_url = base_url
        self.reset()

    def __repr__(self):
        """Returns the string representation of this UrlBuilder"""
        return 'UrlBuilder(base_url={},\n'.format(self.base_url) \
            + ' ' * 4 + 'url={})'.format(self.__url)

    def append_segments(self, *paths):
        """Appends the given path segments to the URL"""
        # if joining the URL with the first path segment yeilds two '/'s
        if self.__url.endswith('/') and paths[0].startswith('/'):
            paths = list(paths) # allow for mutability
            paths[0] = paths[0][1:] # remove the / not part of the base URL
        # if joining the URL or the first path segment yeilds no '/'s
        elif not self.__url.endswith('/') and not paths[0].startswith('/'):
            self.__url += '/' # add one /
        self.__url += '/'.join(paths)
        return self

    def with_query_params(self, params):
        """Adds the given query params key-value pairs to the URL"""
        return self.with_query_string(urllib.parse.urlencode(params))

    def with_query_string(self, string):
        """Adds the given query string to the URL"""
        # if URL is the same as the base and only scheme separators exist
        if self.__url == self.base_url and self.__url.count('/') == 2:
            # suffix with / before adding query params
            self.__url += '/'
        # add separator if query params already exist,
        # otherwise add query params start symbol
        self.__url += '&' if '?' in self.__url else '?'
        self.__url += string
        return self

    def reset(self):
        """Resets the URL to the base URL"""
        self.__url = self.base_url

    def build(self):
        """Builds the URL string for this UrlBuilder"""
        return self.__url

class WeatherPollenApiUrlBuilder(UrlBuilder):

    """Used to build URLs for the Weather.com(tm) pollen API"""

    def __init__(self):
        """Initializes this builder"""
        super().__init__('https://api.weather.com/v2/indices/pollen/daypart/7day')
        self.base_url = self.with_query_params({
            'apiKey': 'e1f10a1e78da46f5b10a1e78da96f525', # was 6532d6454b8aa370768e63d6ba5a832e
            'format': 'json',
            'language': 'en-US'
        }).build()

    def with_geocode(self, lat, lon):
        """Adds the geocode latitude and longitude param to the URL"""
        return self.reset() or self.with_query_params({'geocode': str(lat) + ',' + str(lon)})

class WundergroundUrlBuilder(UrlBuilder):

    """Used to build URLs for retrieving data from Wunderground.com(tm)"""

    def __init__(self):
        """Initializes this builder"""
        super().__init__('https://www.wunderground.com/health/us/')

    def with_location(self, state, city, station):
        """Sets the location for the data source"""
        return self.append_segments(state, city, station)

if __name__ == '__main__':

    from clay.net.core import EXAMPLE_URL
    from clay.tests import testif
    from clay.utils import qualify

    expected_url = 'http://example.com/?key=value'
    for test_url in ('http://example.com/', EXAMPLE_URL):
        url_builder = UrlBuilder(test_url)
        url_builder.with_query_string('key=value')
        testif('adds query string correctly', url_builder.build(), expected_url, name=qualify(UrlBuilder))
    expected_url = 'http://example.com/path/segment'
    for test_url in ('http://example.com/', EXAMPLE_URL):
        url_builder = UrlBuilder(test_url)
        for test_path in ('path', '/path'):
            url_builder.reset()
            url_builder.append_segments(test_path, 'segment')
            testif('adds path segments correctly', url_builder.build(), expected_url, name=qualify(UrlBuilder))
    print(url_builder) # test the string representation
    testif('resets URL to base correctly',
        url_builder.reset() or url_builder.build(),
        EXAMPLE_URL,
        name=qualify(UrlBuilder))

    testif('builds correct resource path',
        WundergroundUrlBuilder().with_location('wa', 'vancouver', 'KWAVANCO547').build(),
        'https://www.wunderground.com/health/us/wa/vancouver/KWAVANCO547',
        name=qualify(WundergroundUrlBuilder.with_location))
