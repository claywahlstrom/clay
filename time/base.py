
import datetime as dt

class BaseDateTimeRange:

    """Stores a range of dates or times for easy comparison"""

    def __init__(self, start=None, end=None):
        """Initializes this BaseDateTimeRange"""
        if start is not None and end is not None and start > end:
            raise ValueError('start must be <= end')
        self.__start = start
        self.__end = end

    def __repr__(self, today=None):
        """Returns the string representation for this BaseDateTimeRange"""
        if self.start is None and self.end is None:
            return 'All Time'

        return '{}(start={}, end={})'.format(self.__class__.__name__, self.start, self.end)

    @property
    def start(self) -> dt.date:
        """The start date"""
        return self.__start

    @property
    def end(self) -> dt.date:
        """The end date"""
        return self.__end

    def contains(self, date: dt.date) -> bool:
        """Returns True if the date is within this range, False otherwise"""
        return (self.start is None or self.start <= date) \
            and (self.end is None or date <= self.end)

if __name__ == '__main__':

    from clay.tests import testif
    from clay.utils import qualify

    testif('Raises ValueError when start datetime is after end datetime',
        lambda: BaseDateTimeRange(dt.date(2020, 6, 3), dt.date(2020, 6, 2)),
        None,
        raises=ValueError,
        name=qualify(BaseDateTimeRange.__init__))
