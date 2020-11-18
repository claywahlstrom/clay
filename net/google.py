
"""
google: open common Google(TM) apps using Python

"""

import json as _json
from urllib.parse import urlencode as _urlencode

from clay import settings
from clay.net.core import WebDocument

_gs_web_doc = WebDocument()

def launch_gs_app(name, browser, url):
    """Launches the given app name in the browser using the URL"""
    print('Opening {} in {}...'.format(name, browser), end=' ')
    _gs_web_doc.set_uri(url)
    _gs_web_doc.launch(browser)
    print('Done')

class GoogleSuite(object):

    """Used for quick access to Google Suite(tm) services"""

    SEARCH_URL = 'https://www.google.com/?gws_rd=ssl#newwindow=1&{}'

    def __init__(self, browser=settings.DEFAULT_BROWSER):
        """Initializes this Google Suite(tm)"""
        self.browser = browser

    def calendar(self):
        """Launches the calendar"""
        launch_gs_app('calendar', self.browser, 'https://calendar.google.com')

    def docs(self, path):
        """Launches the documents"""
        with open(path) as fp:
            content = _json.load(fp)

        if 'url' not in content:
            raise RuntimeError('url not in content')

        launch_gs_app('docs', self.browser, content['url'])

    def drive(self):
        """Launches the drive"""
        launch_gs_app('drive', self.browser, 'https://drive.google.com')

    def mail(self):
        """Launches the mail"""
        launch_gs_app('mail', self.browser, 'https://mail.google.com')

    def maps(self):
        """Launches the maps"""
        launch_gs_app('maps', self.browser, 'https://www.google.com/maps')

    def translate(self):
        """Launches the translate"""
        launch_gs_app('translate', self.browser, 'https://translate.google.com/')

    def search(self, query):
        """Launches the search with the given search query"""
        launch_gs_app('search', self.browser, GoogleSuite.SEARCH_URL.format(_urlencode([('q', query)])))

if __name__ == '__main__':
    gs = GoogleSuite('chrome')
    gs.mail()
    gs.drive()
    gs.search('test search')
