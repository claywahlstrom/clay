
"""
Logging

"""

import datetime as dt

LOG_FMT = '%Y-%m-%d %H:%M:%S'

class Logger:

    """Used log messages to a log file"""

    def __init__(self, name, filename, log_fmt=LOG_FMT):
        """Initializes this Logger with the given name, filename, and format"""
        self.name = name
        self.filename = filename
        self.log_fmt = log_fmt
        self._last_end = '\n'

    def clear(self):
        """Clears the log file"""
        print('Clearing log {}...'.format(self.name))
        with open(self.filename, 'w'):
            pass

    def log(self, message, end='\n'):
        """Adds the given log message to the log file"""
        if self._last_end == '\n':
            now = dt.datetime.now()
            prefix = now.strftime(self.log_fmt) + ' '
        else:
            prefix = ''
        with open(self.filename, 'a+') as fp:
            fp.write(prefix + message + end)
        self._last_end = end
        print('Logged message "{}..." for {}'.format(message[:20], self.name))
