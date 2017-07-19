"""
Open Google(TM) apps with Python
"""

def app(name, browser, url):
    from subprocess import call
    print('Opening {} in {}'.format(name, browser))
    call('start {} "{}"'.format(browser, url), shell=True)

def calendar(browser='firefox'):
    app('calendar', browser, 'https://calendar.google.com')
    
def drive(browser='firefox'):
    app('drive', browser, 'https://drive.google.com')

def mail(browser='firefox'):
    app('mail', browser, 'https://mail.google.com')

def maps(browser='firefox'):
    app('maps', browser, 'https://www.google.com/maps')

def translate(browser='chrome'):
    app('translate', browser, 'https://translate.google.com/')

def search(query, browser='firefox'):
    from urllib.parse import urlencode
    app('search', browser, 'https://www.google.com/?gws_rd=ssl#newwindow=1&{}'.format(urlencode([('q', query)])))

