
"""
Net helpers

"""

from clay.files.core import File as _File
from clay.net.core import WebDocument as _WebDocument
from clay import settings

def launch_links(filename, browser=settings.DEFAULT_BROWSER):
    """Launches links from a line-based text file"""
    doc = _WebDocument()
    file = _File(filename)
    links = filter(lambda x: x, file.parse(strip=True))
    for link in links:
        try:
            doc.set_uri(link)
            print('Launching "{}"...'.format(link))
            doc.launch(browser=browser)
        except ValueError:
            print('URI "{}" is not a valid'.format(link))
