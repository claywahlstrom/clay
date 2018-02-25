
"""
Opens Google(TM) apps with Python

"""

DEF_BROWSER = 'firefox'

def g_app(name, browser, url):
    from subprocess import call
    print('Opensing {} in {}'.format(name, browser))
    call('start {} "{}"'.format(browser, url), shell=True)

def calendar(browser=DEF_BROWSER):
    g_app('calendar', browser, 'https://calendar.google.com')
    
def drive(browser=DEF_BROWSER):
    g_app('drive', browser, 'https://drive.google.com')

def mail(browser=DEF_BROWSER):
    g_app('mail', browser, 'https://mail.google.com')

def maps(browser=DEF_BROWSER):
    g_app('maps', browser, 'https://www.google.com/maps')

def translate(browser='chrome'):
    g_app('translate', browser, 'https://translate.google.com/')

def search(query, browser=DEF_BROWSER):
    from urllib.parse import urlencode
    g_app('search', browser, 'https://www.google.com/?gws_rd=ssl#newwindow=1&{}'.format(urlencode([('q', query)])))

