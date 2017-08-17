"""
Open Google(TM) apps with Python
"""

def_browser = 'firefox'

def g_app(name, browser, url):
    from subprocess import call
    print('Opening {} in {}'.format(name, browser))
    call('start {} "{}"'.format(browser, url), shell=True)

def calendar(browser=def_browser):
    g_app('calendar', browser, 'https://calendar.google.com')
    
def drive(browser=def_browser):
    g_app('drive', browser, 'https://drive.google.com')

def mail(browser=def_browser):
    g_app('mail', browser, 'https://mail.google.com')

def maps(browser=def_browser):
    g_app('maps', browser, 'https://www.google.com/maps')

def translate(browser='chrome'):
    g_app('translate', browser, 'https://translate.google.com/')

def search(query, browser=def_browser):
    from urllib.parse import urlencode
    g_app('search', browser, 'https://www.google.com/?gws_rd=ssl#newwindow=1&{}'.format(urlencode([('q', query)])))

