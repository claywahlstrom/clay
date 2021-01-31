
"""
builders: Mainly for URL builders

"""

import urllib

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

class WundergroundUrlBuilder(UrlBuilder):

    """Used to build URLs for retrieving data from Wunderground.com(tm)"""

    def __init__(self):
        """Initializes this builder"""
        super().__init__('https://www.wunderground.com/health/us/')

    def with_location(self, state, city, station):
        """Sets the location for the data source"""
        self.url = self.base_url + '/'.join((state, city, station))
        return self

    def to_string(self):
        """Returns the built URL"""
        return self.url

if __name__ == '__main__':

    from clay.net.core import EXAMPLE_URL
    from clay.tests import testif

    expected_url = 'http://example.com/?key=value'
    for test_url in ('http://example.com/', EXAMPLE_URL):
        url_builder = UrlBuilder(test_url)
        url_builder.with_query_string('key=value')
        testif('UrlBuilder adds query string correctly', url_builder.build(), expected_url)
    expected_url = 'http://example.com/path/segment'
    for test_url in ('http://example.com/', EXAMPLE_URL):
        url_builder = UrlBuilder(test_url)
        for test_path in ('path', '/path'):
            url_builder.reset()
            url_builder.append_segments(test_path, 'segment')
            testif('UrlBuilder adds path segments correctly', url_builder.build(), expected_url)
    print(url_builder) # test the string representation
    testif('UrlBuilder resets URL to base correctly',
        url_builder.reset() or url_builder.build(),
        EXAMPLE_URL)
