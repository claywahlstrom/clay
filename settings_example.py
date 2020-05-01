
"""
Settings

"""

import os as _os

from clay.env import *

IS_DEVELOPER = False

DOCS_DIR = r'path-to-documents-folder'
FLASK_APP = 'app.py' # a common name for Flask web apps
HOME_DIR = _os.environ['HOME'] if is_unix() else _os.environ['USERPROFILE']
TRASH = _os.path.join(HOME_DIR, 'Desktop', 'clay-trash')
