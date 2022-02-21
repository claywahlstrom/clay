
"""
Dates

"""

import datetime as dt

from clay.time.base import BaseDateTimeRange

# date formats
MDY_FMT = '%m/%d/%Y'
MDY_DASH_FMT = '%m-%d-%Y'
YMD_FMT = '%Y/%m/%d'
YMD_DASH_FMT = '%Y-%m-%d'

# days of the week
MONDAY = dt.date(2019, 4, 22)
TUESDAY = dt.date(2019, 4, 23)
WEDNESDAY = dt.date(2019, 4, 24)
THURSDAY = dt.date(2019, 4, 25)
FRIDAY = dt.date(2019, 4, 26)
SATURDAY = dt.date(2019, 4, 27)
SUNDAY = dt.date(2019, 4, 28)

WEEKDAYS = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday',
    'Friday', 'Saturday', 'Sunday'
]
WEEKDAYS_SHORT = ['M', 'TU', 'W', 'TH', 'F', 'SA', 'SU']

class Date(dt.date):

    """
    Provides extension methods to the `datetime.date` type

    """

    @staticmethod
    def todatetime(date) -> dt.datetime:
        """Returns the given date converted to a datetime"""
        return dt.datetime(date.year, date.month, date.day)

    #region Last

    def last_year(self) -> 'Date':
        """Returns the last year's date given a date or datetime"""
        return Date(self.year - 1, 1, 1)

    #endregion

    #region This

    def this_year(self) -> 'Date':
        """Returns this year's date given a date or datetime"""
        return Date(self.year, 1, 1)

    def this_quarter(self) -> 'Date':
        """
        Returns this quarter's date given a date or datetime.
        Quarters are on the 1st, 4th, 7th, and 10th months

        """

        month = self.month

        if month <= 3:
            month = 1
        elif month <= 6:
            month = 4
        elif month <= 9:
            month = 7
        elif month <= 12:
            month = 10

        return Date(self.year, month, 1)

    def this_month(self) -> 'Date':
        """Returns this month's date given a date or datetime"""
        return Date(self.year, self.month, 1)

    def this_week(self, reference) -> 'Date':
        """Returns this week's date given a reference date"""
        now = Date.todatetime(self)

        if reference > self:
            sign = 1
        elif reference == self:
            sign = 0
        else: # reference < self
            sign = -1

        return extend_date(now + sign * dt.timedelta(days=abs(self - reference).days % 7))

    #endregion

    #region Next

    def next_year(self) -> 'Date':
        """Returns the next year's date given a date or datetime"""
        return Date(self.year + 1, 1, 1)

    def next_month(self) -> 'Date':
        """Returns the 1st of the next month's date given a date"""
        year = self.year
        month = self.month
        day = self.day

        month += 1
        if month > 12:
            year += 1
            month = 1

        return Date(year, month, 1)

    def next_quarter(self) -> 'Date':
        """
        Returns the next quarter's date.
        Quarters are on the 1st, 4th, 7th, and 10th months

        """

        # store references to this date
        year = self.year
        month = self.month
        day = self.day

        # if after Oct 1st
        if day > 1 and month >= 10:
            # push to new year's
            year += 1
            month = 1
        # otherwise
        if self.year == year:
            # if after the 1st
            if day > 1:
                # push to next month
                month += 1

            # set up 2-month look-ahead
            plus2 = month + 2
            # check quarter conditions using look-ahead
            if plus2 >= 10:
                month = 10
            elif plus2 >= 7:
                month = 7
            elif plus2 >= 4:
                month = 4
            else:
                month = 1

        return Date(year, month, 1)

    def next_week(self) -> 'Date':
        """Returns the next week's date given a datetime"""
        return extend_date(Date.todatetime(self) + dt.timedelta(days=7))

    def next_week2(self, reference) -> 'Date':
        """Returns the next week's occurrence of the reference date"""
        return extend_date(self.this_week(reference)).next_week()

    def next_day(self) -> 'Date':
        """Returns midnight of the next day"""
        return extend_date(Date.todatetime(self) + dt.timedelta(days=1))

    #endregion

class DateRange(BaseDateTimeRange):

    """Stores a range of dates for easy comparison"""

    def __repr__(self, today=dt.date.today()) -> str:
        """Returns the string representation for this DateRange"""
        if self.start is None and self.end is None:
            return 'All Time'

        if self.start is None:
            string = 'Beginning'
        elif self.start == today:
            string = 'Today'
        else:
            string = self.start.strftime(YMD_FMT)

        if self.end == today:
            if self.start == today:
                return string
            else:
                return string + ' - Today'
        elif self.end is None:
            string += ' - Continuous'
        else:
            string += ' - ' + self.end.strftime(YMD_FMT)
        return string

def days_to_mail(weekday: int) -> int:
    """
    Returns the number of days to send an item through priority
    mail within the U.S. given the weekday (Monday: 0 - Sunday: 6)

    """
    if weekday < 0 or weekday > 6:
        raise ValueError('weekday must be from 0 to 6')
    usually = 2 # days for priority mail within the U.S.
    # if approaching Sunday when no mail is delivered
    if weekday >= 4:
        # return the usual incremented one day
        return usually + 1
    else:
        # return the usual
        return usually

def extend_date(date) -> Date:
    """Extends the given date using the `Date` type"""
    if not isinstance(date, dt.date):
        raise TypeError('date must of base type datetime.date')
    return Date(date.year, date.month, date.day)

def extend_months(date: dt.date, months: int) -> dt.date:
    """Extends the given date by the given number of months"""

    # store modifiable year and month
    year = date.year
    month = date.month

    # add months
    month += months

    # perform rollovers
    while month > 12:
        year += 1
        month -= 12

    # create date
    return dt.date(year, month, date.day)

if __name__ == '__main__':

    from clay.tests import testif, testraises
    from clay.utils import qualify

    date_range_repr_tests = [
        # start, end, expected repr
        (None, None, 'All Time'),
        (None, dt.date(2020, 6, 1), 'Beginning - 2020/06/01'),
        (None, dt.date(2020, 6, 2), 'Beginning - Today'),
        (dt.date(2020, 6, 2), None, 'Today - Continuous'),
        (dt.date(2020, 6, 2), dt.date(2020, 6, 2), 'Today'),
        (dt.date(2020, 6, 2), dt.date(2020, 6, 3), 'Today - 2020/06/03'),
        (dt.date(2020, 6, 1), dt.date(2020, 6, 2), '2020/06/01 - Today'),
        (dt.date(2020, 6, 1), dt.date(2020, 6, 3), '2020/06/01 - 2020/06/03')
    ]

    for test in date_range_repr_tests:
        testif('returns correct string representation for (start: {}, end: {})'.format(test[0], test[1]),
            DateRange(test[0], test[1]).__repr__(today=dt.date(2020, 6, 2)),
            test[2],
            name=qualify(DateRange.__repr__))

    for weekday in (-1, 7):
        testraises('raises ValueError if weekday invalid (weekday = {})'.format(weekday),
            lambda: days_to_mail(weekday),
            ValueError,
            name=qualify(days_to_mail))

    days_to_mail_tests = [
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
        (4, 3),
        (5, 3),
        (6, 3)
    ]

    for test in days_to_mail_tests:
        testif('returns correct days for weekday {}'.format(test[0]),
            days_to_mail(test[0]),
            test[1],
            name=qualify(days_to_mail))

    testraises('raises TypeError when extending invalid type',
        lambda: extend_date(None),
        TypeError,
        name=qualify(extend_date))

    testif('returns correct datetime',
        Date.todatetime(dt.date(2019, 4, 22)),
        dt.datetime(2019, 4, 22),
        name=qualify(Date.todatetime))

    testif('returns correct date for last year',
        extend_date(dt.date(2019, 4, 22)).last_year(),
        dt.date(2018, 1, 1),
        name=qualify(Date.last_year))

    testif('returns correct date for this year',
        extend_date(dt.date(2019, 4, 22)).this_year(),
        dt.date(2019, 1, 1),
        name=qualify(Date.this_year))

    this_quarter_tests = [
        (dt.date(2019, 1, 1), dt.date(2019, 1, 1)),
        (dt.date(2019, 1, 2), dt.date(2019, 1, 1)),
        (dt.date(2019, 2, 2), dt.date(2019, 1, 1)),
        (dt.date(2019, 4, 1), dt.date(2019, 4, 1)),
        (dt.date(2019, 4, 2), dt.date(2019, 4, 1)),
        (dt.date(2019, 5, 5), dt.date(2019, 4, 1)),
        (dt.date(2019, 7, 1), dt.date(2019, 7, 1)),
        (dt.date(2019, 7, 2), dt.date(2019, 7, 1)),
        (dt.date(2019, 10, 1), dt.date(2019, 10, 1)),
        (dt.date(2019, 10, 2), dt.date(2019, 10, 1))
    ]

    for test in this_quarter_tests:
        testif('returns correct date ({})'.format(test[0]),
            extend_date(test[0]).this_quarter(),
            test[1],
            name=qualify(Date.this_quarter))

    testif('returns correct date for this month',
        extend_date(dt.date(2019, 4, 22)).this_month(),
        dt.date(2019, 4, 1),
        name=qualify(Date.this_month))

    this_week_tests = [
        (dt.date(2020, 5, 31), dt.date(2020, 5, 31), dt.date(2020, 5, 31)),
        (dt.date(2020, 5, 31), dt.date(2020, 6, 1), dt.date(2020, 6, 1)),
        (dt.date(2020, 6, 3), dt.date(2020, 5, 27), dt.date(2020, 6, 3)),
        (dt.date(2020, 6, 3), dt.date(2020, 5, 24), dt.date(2020, 5, 31)),
        (dt.date(2020, 6, 3), dt.date(2020, 5, 26), dt.date(2020, 6, 2)),
        (dt.date(2020, 6, 3), dt.date(2020, 5, 30), dt.date(2020, 5, 30))
    ]

    for test in this_week_tests:
        testif('returns correct date ({}, reference {})'.format(test[0], test[1]),
            extend_date(test[0]).this_week(test[1]),
            test[2],
            name=qualify(Date.this_week))

    next_month_advance_tests = [
        (dt.date(2020, 11, 1), dt.date(2020, 12, 1)),
        (dt.date(2020, 11, 15), dt.date(2020, 12, 1))
    ]

    for test in next_month_advance_tests:
        testif('returns correct advance date ({})'.format(test[0]),
            extend_date(test[0]).next_month(),
            test[1],
            name=qualify(Date.next_month))

    next_month_rollover_tests = [
        (dt.date(2020, 12, 1), dt.date(2021, 1, 1)),
        (dt.date(2020, 12, 15), dt.date(2021, 1, 1))
    ]

    for test in next_month_rollover_tests:
        testif('returns correct rollover date ({})'.format(test[0]),
            extend_date(test[0]).next_month(),
            test[1],
            name=qualify(Date.next_month))

    next_quarter_tests = [
        (dt.date(2019, 1, 1), dt.date(2019, 1, 1)),
        (dt.date(2019, 1, 2), dt.date(2019, 4, 1)),
        (dt.date(2019, 2, 2), dt.date(2019, 4, 1)),
        (dt.date(2019, 4, 1), dt.date(2019, 4, 1)),
        (dt.date(2019, 4, 2), dt.date(2019, 7, 1)),
        (dt.date(2019, 5, 5), dt.date(2019, 7, 1)),
        (dt.date(2019, 7, 1), dt.date(2019, 7, 1)),
        (dt.date(2019, 7, 2), dt.date(2019, 10, 1)),
        (dt.date(2019, 10, 1), dt.date(2019, 10, 1)),
        (dt.date(2019, 10, 2), dt.date(2020, 1, 1))
    ]

    for test in next_quarter_tests:
        testif('returns correct date ({})'.format(test[0]),
            extend_date(test[0]).next_quarter(),
            test[1],
            name=qualify(Date.next_quarter))

    next_week_tests = [
        (dt.date(2020, 5, 24), dt.date(2020, 5, 31)),
        (dt.date(2020, 5, 31), dt.date(2020, 6, 7))
    ]

    for test in next_week_tests:
        testif('returns correct date ({})'.format(test[0]),
            extend_date(test[0]).next_week(),
            test[1],
            name=qualify(Date.next_week))

    next_week2_tests = [
        (dt.date(2020, 5, 31), dt.date(2020, 6, 7)),
        (dt.date(2020, 6, 1), dt.date(2020, 6, 8)),
        (dt.date(2020, 6, 6), dt.date(2020, 6, 13)),
        (dt.date(2020, 6, 7), dt.date(2020, 6, 7))
    ]

    sunday = dt.date(2020, 5, 31)
    for test in next_week2_tests:
        testif('returns correct date ({}, reference {})'.format(sunday, test[0]),
            extend_date(sunday).next_week2(test[0]),
            test[1],
            name=qualify(Date.next_week2))

    testif('returns correct advance date',
        extend_date(dt.date(2020, 5, 30)).next_day(),
        dt.date(2020, 5, 31),
        name=qualify(Date.next_day))

    testif('returns correct rollover date',
        extend_date(dt.date(2020, 5, 31)).next_day(),
        dt.date(2020, 6, 1),
        name=qualify(Date.next_day))

    testif('returns correct date if no months',
        extend_months(dt.date(2022, 2, 18), 0),
        dt.date(2022, 2, 18),
        name=qualify(extend_months))
    testif('returns correct date if this year',
        extend_months(dt.date(2022, 2, 18), 8),
        dt.date(2022, 10, 18),
        name=qualify(extend_months))
    testif('returns correct date if next year rollover',
        extend_months(dt.date(2022, 2, 18), 11),
        dt.date(2023, 1, 18),
        name=qualify(extend_months))
    testif('returns correct date if next year',
        extend_months(dt.date(2022, 2, 18), 12),
        dt.date(2023, 2, 18),
        name=qualify(extend_months))
    testif('returns correct date if more than one year',
        extend_months(dt.date(2022, 4, 7), 14),
        dt.date(2023, 6, 7),
        name=qualify(extend_months))
    testif('returns correct date if two years',
        extend_months(dt.date(2022, 4, 7), 24),
        dt.date(2024, 4, 7),
        name=qualify(extend_months))
    testif('returns correct date if more than two years',
        extend_months(dt.date(2022, 8, 3), 29),
        dt.date(2025, 1, 3),
        name=qualify(extend_months))
