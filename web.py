"""
web module
"""

from pack import LINUX


def openweb(url, browser='firefox'):
    """Open pages in web browsers. "url" can be a list of urls"""
    from subprocess import call
    if type(url) == str:
        url = [url]
    if type(url) == list:
        for link in url:
            if LINUX:
                call(['google-chrome', link], shell=True)
            else:
                call(['start', browser, link.replace('&', '^&')], shell=True)

class WebElements:
    def __init__(self, element, page=str(), method='find_all'):
        if not(page):
            page = 'https://multiethnicblog.wordpress.com/2016/09/17/how-to-read-literature-part-ii-literary-theories/'
        from requests import get
        from bs4 import BeautifulSoup
        self.source = get(page)
        self.soup = BeautifulSoup(((self.source).content).decode('utf8'), 'html.parser')
        self.__found = eval('self.soup.{}("{}")'.format(method, element))

    def show(self):
        for i in self.__found:
            print(i.text)
    def get(self):
        return self.__found
