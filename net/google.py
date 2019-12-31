
"""
google: open common Google(TM) apps using Python

"""

from urllib.parse import urlencode as _urlencode

from clay.net.core import DEFAULT_BROWSER

def launch_gs_app(name, browser, url):
    from subprocess import call
    print('Opening {} in {}...'.format(name, browser), end=' ')
    call('start {} "{}"'.format(browser, url), shell=True)
    print('Done')

class GoogleSuite(object):

    SEARCH_URL = 'https://www.google.com/?gws_rd=ssl#newwindow=1&{}'

    def __init__(self, browser=DEFAULT_BROWSER):
        self.browser = browser

    def calendar(self):
        launch_gs_app('calendar', self.browser, 'https://calendar.google.com')

    def drive(self):
        launch_gs_app('drive', self.browser, 'https://drive.google.com')

    def mail(self):
        launch_gs_app('mail', self.browser, 'https://mail.google.com')

    def maps(self):
        launch_gs_app('maps', self.browser, 'https://www.google.com/maps')

    def translate(self):
        launch_gs_app('translate', self.browser, 'https://translate.google.com/')

    def search(self, query):
        launch_gs_app('search', self.browser, GoogleSuite.SEARCH_URL.format(_urlencode([('q', query)])))

if __name__ == '__main__':
    gs = GoogleSuite('chrome')
    gs.mail()
    gs.drive()
    gs.search('test search')
