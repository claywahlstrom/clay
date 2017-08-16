"""
web module
"""

from subprocess import call as _call

from requests import get as _get
from bs4 import BeautifulSoup as _BS

from pack import UNIX as _UNIX

def get_web_title(url):
    soup = _BS(_get(url).content, 'html.parser')
    return soup.html.title.text

def openweb(url, browser='firefox'):
    """Open pages in web browsers. "url" can be a list of urls"""

    if type(url) == str:
        url = [url]
    if type(url) == list:
        for link in url:
            if _UNIX:
                _call(['google-chrome', link], shell=True)
            else:
                _call(['start', browser, link.replace('&', '^&')], shell=True)

class WebElements:
    def __init__(self, page=str(), element=str(), method='find_all'):
        if not(page) and not(element):
            page = 'https://www.google.com'
            element = 'a'

        self.source = _get(page)
        self.soup = _BS(self.source.content, 'html.parser')
        self.method = method
        self.element = element
    def get_element(self, element):
        self.__found = eval('self.soup.{}("{}")'.format(self.method, element))
        return self.__found

    def show(self):
        print('Elements:')
        for i in self.__found:
            print(i.text)
    def get(self):
        return self.__found

if __name__ == '__main__':
    print(get_web_title('https://www.google.com'))
    we = WebElements()
    we.show()
