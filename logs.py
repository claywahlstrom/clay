
"""
Logging

"""

import datetime as dt

LOG_FMT = '%Y-%m-%d %H:%M:%S'

class Logger:

    """Used log messages to a log file"""

    def __init__(self, name: str, filename: str, log_fmt: str=LOG_FMT) -> None:
        """Initializes this Logger with the given name, filename, and format"""
        self.name = name
        self.filename = filename
        self.log_fmt = log_fmt
        self._last_end = '\n'

    def clear(self) -> None:
        """Clears the log file"""
        print('Clearing log {}...'.format(self.name))
        with open(self.filename, 'w'):
            pass

    def log(self, message: str, end: str='\n') -> None:
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
