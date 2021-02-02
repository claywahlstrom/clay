
"""
Settings

"""

import os as _os
import sys as _sys

from clay import env

IS_DEVELOPER = False

DEFAULT_BROWSER = 'firefox'
DOWNLOAD_CHUNK_SIZE = int(1e6) # bytes

DOCS_DIR = r'path-to-documents-folder'
FLASK_APP = 'app.py' # a common name for Flask web apps
HOME_DIR = _os.environ['HOME' if env.is_posix() else 'USERPROFILE']
PACKAGE_DIR = _os.path.join(_sys.prefix, 'Lib', 'site-packages', 'clay')
LOGS_DIR = _os.path.join(PACKAGE_DIR, 'logs')
TRASH = _os.path.join(HOME_DIR, 'Desktop', 'clay-trash')

CONSOLE_WIDTH = 80

JOBS_BREAK_SCHEDULES = {
    'WA': {'hours': 6, 'length': 0.5},
    'OR': {'hours': 5, 'length': 1.0}
}

SEARCH_EXCLUSIONS = [
    '.android', '.AndroidStudio1.5', 'eclipse', '.gradle', '.idlerc',
    '.jmc', '.matplotlib', '.oracle_jre_usage', '.pdfsam', '.phet',
    '3D Objects', 'AppData', 'Application Data', 'eclipse', 'Android',
    'NuGet'
]

SONG_TEMPO = 60 # default beats per minute
