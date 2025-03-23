
"""
Dates

"""

from collections.abc import Callable
import datetime as dt
import math
import os
import traceback

from clay.decors import obsolete
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

def get_next_weekdays(date: dt.date, n: int):
    """Returns a list of day names n number of days out from date"""
    wkdy = date.weekday()
    return (WEEKDAYS * math.ceil((wkdy + n) / 6))[wkdy:wkdy + n]

def conv_date_to_datetime(date: dt.date) -> dt.datetime:
    """Returns the given date converted to a datetime"""
    return dt.datetime(date.year, date.month, date.day)

def get_first_of_year_last(date: dt.date) -> dt.date:
    """Returns the last year's date given a date or datetime"""
    return dt.date(date.year - 1, 1, 1)

def get_first_of_year(date: dt.date) -> dt.date:
    """Returns this year's date given a date or datetime"""
    return dt.date(date.year, 1, 1)

def get_first_of_year_next(date: dt.date) -> dt.date:
    """Returns the next year's date given a date or datetime"""
    return dt.date(date.year + 1, 1, 1)

def get_first_of_quarter(date: dt.date) -> dt.date:
    """
    Returns this quarter's date given a date or datetime.
    Quarters are on the 1st, 4th, 7th, and 10th months

    """

    month = date.month

    if month <= 3:
        month = 1
    elif month <= 6:
        month = 4
    elif month <= 9:
        month = 7
    elif month <= 12:
        month = 10

    return dt.date(date.year, month, 1)

def get_first_of_quarter_next(date: dt.date) -> dt.date:
    """
    Returns the next quarter's date.
    Quarters are on the 1st, 4th, 7th, and 10th months

    """

    # store references to this date
    year = date.year
    month = date.month
    day = date.day

    # if after Oct 1st
    if day > 1 and month >= 10:
        # push to new year's
        year += 1
        month = 1
    # otherwise
    if date.year == year:
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

    return dt.date(year, month, 1)

def get_first_of_month(date: dt.date) -> dt.date:
    """Returns first of month given a date or datetime"""
    return dt.date(date.year, date.month, 1)

def get_first_of_month_next(date: dt.date) -> dt.date:
    """Returns the 1st of the next month's date given a date"""
    year = date.year
    month = date.month + 1

    if month > 12:
        year += 1
        month = 1

    return dt.date(year, month, 1)

def get_last_of_month(date: dt.date) -> dt.date:
    """Returns last of month given a date"""
    return get_first_of_month_next(date) - dt.timedelta(days=1)

def get_end_of_year(date: dt.date) -> dt.date:
    """Returns end of year given a date"""
    return dt.date(date.year, 12, 31)

def get_this_week(date: dt.date, reference: dt.date) -> dt.date:
    """Returns this week's date given a reference date"""
    now = conv_date_to_datetime(date)
    reference = conv_date_to_datetime(reference)

    if reference > now:
        sign = 1
    elif reference == now:
        sign = 0
    else: # reference < self
        sign = -1

    return (now + sign * dt.timedelta(days=abs(now - reference).days % 7)).date()

def get_next_week(date: dt.date) -> dt.datetime:
    """Returns the next week's date given a datetime"""
    return (conv_date_to_datetime(date) + dt.timedelta(days=7)).date()

def get_next_week_with_ref(date: dt.date, reference: dt.date) -> dt.datetime:
    """Returns the next week's occurrence of the reference date"""
    return get_next_week(get_this_week(date, reference))

def get_next_day_midnight(date: dt.date) -> dt.date:
    """Returns midnight of the next day"""
    return (conv_date_to_datetime(date) + dt.timedelta(days=1)).date()

def get_ymd_str(date: dt.date) -> str:
    """Returns the given date as year, month, day string"""
    return date.strftime(YMD_FMT)

def get_yest_ymd(fmt: str=YMD_FMT) -> str:
    """Returns yesterday's date in given format (default YYYY/MM/DD)"""
    return (dt.datetime.today() - dt.timedelta(days=1)).strftime(fmt)

def get_today_ymd(fmt: str=YMD_FMT) -> str:
    """Returns today's date in given format (default YYYY/MM/DD)"""
    return dt.date.today().strftime(fmt)

def get_tmw_ymd(fmt: str=YMD_FMT) -> str:
    """Returns tomorrow's date in given format (default YYYY/MM/DD)"""
    return (dt.datetime.today() + dt.timedelta(days=1)).strftime(fmt)

class Date(dt.date):

    """
    Provides extension methods to the `datetime.date` type

    """

    @obsolete
    @staticmethod
    def todatetime(date) -> dt.datetime:
        """Returns the given date converted to a datetime"""
        return dt.datetime(date.year, date.month, date.day)

    @obsolete
    def to_ymd_str(self) -> str:
        """Returns the given date as year, month, day string"""
        return self.strftime(YMD_FMT)

    #region Last

    @obsolete
    def last_year(self) -> 'Date':
        """Returns the last year's date given a date or datetime"""
        return Date(self.year - 1, 1, 1)

    #endregion

    #region This

    @obsolete
    def this_year(self) -> 'Date':
        """Returns this year's date given a date or datetime"""
        return Date(self.year, 1, 1)

    @obsolete
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

    @obsolete
    def this_month(self) -> 'Date':
        """Returns this month's date given a date or datetime"""
        return Date(self.year, self.month, 1)

    @obsolete
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

    @obsolete
    def next_year(self) -> 'Date':
        """Returns the next year's date given a date or datetime"""
        return Date(self.year + 1, 1, 1)

    @obsolete
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

    @obsolete
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

    @obsolete
    def next_week(self) -> 'Date':
        """Returns the next week's date given a datetime"""
        return extend_date(Date.todatetime(self) + dt.timedelta(days=7))

    @obsolete
    def next_week2(self, reference: dt.date) -> 'Date':
        """Returns the next week's occurrence of the reference date"""
        return extend_date(self.this_week(reference)).next_week()

    @obsolete
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

@obsolete
def extend_date(date) -> Date:
    """Extends the given date using the `Date` type"""
    if not isinstance(date, dt.date):
        raise TypeError('date must of base type datetime.date')
    return Date(date.year, date.month, date.day)

def add_months(date: dt.date, months: int) -> dt.date:
    """Returns a new date with the given number of months added"""

    # store modifiable year and month
    year = date.year
    month = date.month

    # add months
    month += months

    # perform rollbacks and rollovers
    while month <= 0:
        year -= 1
        month += 12
    while month > 12:
        year += 1
        month -= 12

    days_in_month = {
        1: 31,
        2: 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }

    # create date
    try:
        return dt.date(year, month, date.day)
    except ValueError:
        # handle case month has less than 31 days
        day = days_in_month[month]
        # if it is leap year and February
        if year % 4 == 0 and month == 2:
            day += 1 # handle leap day
        return dt.date(year, month, day)

class NonceDailyRule:

    """
    Allows an expression to be run once per day.

    """

    def __init__(self, filename: str, lambda_expr: Callable) -> None:
        """Initializes this NonceRule using filename and lambda expression"""
        self.filename = filename
        self.lambda_expr = lambda_expr

    def get_name(self) -> str:
        """Returns the name of this NonceRule from the filename"""
        return os.path.splitext(os.path.basename(self.filename))[0]

    def do_expr(self) -> None:
        """Evaluates the expression if it is a new day"""
        print('Running NonceRule {}'.format(self.get_name()))
        with open(self.filename) as fp:
            last_date = fp.read()
        now = get_today_ymd()
        if now != last_date:
            try:
                self.lambda_expr()
                with open(self.filename, 'w') as fp:
                    fp.write(now)
            except:
                # log exception
                traceback.print_exc()
            print('Done')
        else:
            print('Already run on: {}'.format(last_date))

if __name__ == '__main__':

    from clay.tests import testif, testraises
    from clay.utils import qualify

    testif('returns correct weekdays (n=0)',
        get_next_weekdays(dt.date(2024, 7, 13), 0),
        [],
        name=qualify(get_next_weekdays))
    testif('returns correct weekdays (n=1)',
        get_next_weekdays(dt.date(2024, 7, 13), 1),
        ['Saturday'],
        name=qualify(get_next_weekdays))
    testif('returns correct weekdays (n=5)',
        get_next_weekdays(dt.date(2024, 7, 13), 5),
        ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday'],
        name=qualify(get_next_weekdays))

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

    # testraises('raises TypeError when extending invalid type',
    #     lambda: extend_date(None),
    #     TypeError,
    #     name=qualify(extend_date))

    # testif('returns correct datetime',
    #     Date.todatetime(dt.date(2019, 4, 22)),
    #     dt.datetime(2019, 4, 22),
    #     name=qualify(Date.todatetime))

    testif('returns correct date for last year',
        get_first_of_year_last(dt.date(2019, 4, 22)),
        dt.date(2018, 1, 1),
        name=qualify(get_first_of_year_last))

    testif('returns correct date for this year',
        get_first_of_year(dt.date(2019, 4, 22)),
        dt.date(2019, 1, 1),
        name=qualify(get_first_of_year))

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
            get_first_of_quarter(test[0]),
            test[1],
            name=qualify(get_first_of_quarter))

    testif('returns correct date for this month',
        get_first_of_month(dt.date(2019, 4, 22)),
        dt.date(2019, 4, 1),
        name=qualify(get_first_of_month))

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
            get_this_week(test[0], test[1]),
            test[2],
            name=qualify(get_this_week))

    last_of_month_tests = [
        (dt.date(2020, 1, 1), dt.date(2020, 1, 31)),
        (dt.date(2019, 2, 1), dt.date(2019, 2, 28)),
        (dt.date(2020, 2, 1), dt.date(2020, 2, 29)),
        (dt.date(2020, 3, 12), dt.date(2020, 3, 31)),
        (dt.date(2020, 3, 31), dt.date(2020, 3, 31)),
    ]

    for test in last_of_month_tests:
        testif('returns correct date ({})'.format(test[0]),
            get_last_of_month(test[0]),
            test[1],
            name=qualify(get_last_of_month))

    end_of_year_tests = [
        (dt.date(2022, 1, 1), dt.date(2022, 12, 31)),
        (dt.date(2022, 6, 1), dt.date(2022, 12, 31)),
        (dt.date(2022, 12, 31), dt.date(2022, 12, 31)),
        (dt.date(2023, 1, 1), dt.date(2023, 12, 31)),
    ]

    for test in end_of_year_tests:
        testif('returns correct date ({})'.format(test[0]),
            get_end_of_year(test[0]),
            test[1],
            name=qualify(get_end_of_year))

    next_month_advance_tests = [
        (dt.date(2020, 11, 1), dt.date(2020, 12, 1)),
        (dt.date(2020, 11, 15), dt.date(2020, 12, 1))
    ]

    for test in next_month_advance_tests:
        testif('returns correct advance date ({})'.format(test[0]),
            get_first_of_month_next(test[0]),
            test[1],
            name=qualify(get_first_of_month_next))

    next_month_rollover_tests = [
        (dt.date(2020, 12, 1), dt.date(2021, 1, 1)),
        (dt.date(2020, 12, 15), dt.date(2021, 1, 1))
    ]

    for test in next_month_rollover_tests:
        testif('returns correct rollover date ({})'.format(test[0]),
            get_first_of_month_next(test[0]),
            test[1],
            name=qualify(get_first_of_month_next))

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
            get_first_of_quarter_next(test[0]),
            test[1],
            name=qualify(get_first_of_quarter_next))

    next_week_tests = [
        (dt.date(2020, 5, 24), dt.date(2020, 5, 31)),
        (dt.date(2020, 5, 31), dt.date(2020, 6, 7))
    ]

    for test in next_week_tests:
        testif('returns correct date ({})'.format(test[0]),
            get_next_week(test[0]),
            test[1],
            name=qualify(get_next_week))

    next_week2_tests = [
        (dt.date(2020, 5, 31), dt.date(2020, 6, 7)),
        (dt.date(2020, 6, 1), dt.date(2020, 6, 8)),
        (dt.date(2020, 6, 6), dt.date(2020, 6, 13)),
        (dt.date(2020, 6, 7), dt.date(2020, 6, 7))
    ]

    sunday = dt.date(2020, 5, 31)
    for test in next_week2_tests:
        testif('returns correct date ({}, reference {})'.format(sunday, test[0]),
            get_next_week_with_ref(sunday, test[0]),
            test[1],
            name=qualify(get_next_week_with_ref))

    testif('returns correct next day midnight date',
        get_next_day_midnight(dt.date(2020, 5, 30)),
        dt.date(2020, 5, 31),
        name=qualify(get_next_day_midnight))

    testif('returns correct rollover date',
        get_next_day_midnight(dt.date(2020, 5, 31)),
        dt.date(2020, 6, 1),
        name=qualify(get_next_day_midnight))

    testif('returns correct date if more than two years ago',
        add_months(dt.date(2022, 2, 18), -29),
        dt.date(2019, 9, 18),
        name=qualify(add_months))
    testif('returns correct date if two years ago',
        add_months(dt.date(2022, 2, 18), -24),
        dt.date(2020, 2, 18),
        name=qualify(add_months))
    testif('returns correct date if last year rollover',
        add_months(dt.date(2022, 2, 18), -2),
        dt.date(2021, 12, 18),
        name=qualify(add_months))
    testif('returns correct date if last month',
        add_months(dt.date(2022, 2, 18), -1),
        dt.date(2022, 1, 18),
        name=qualify(add_months))
    testif('returns correct date if no months',
        add_months(dt.date(2022, 2, 18), 0),
        dt.date(2022, 2, 18),
        name=qualify(add_months))
    testif('returns correct date if this year',
        add_months(dt.date(2022, 2, 18), 8),
        dt.date(2022, 10, 18),
        name=qualify(add_months))
    testif('returns correct date if next year rollover',
        add_months(dt.date(2022, 2, 18), 11),
        dt.date(2023, 1, 18),
        name=qualify(add_months))
    testif('returns correct date if next year',
        add_months(dt.date(2022, 2, 18), 12),
        dt.date(2023, 2, 18),
        name=qualify(add_months))
    testif('returns correct date if more than one year',
        add_months(dt.date(2022, 4, 7), 14),
        dt.date(2023, 6, 7),
        name=qualify(add_months))
    testif('returns correct date if two years',
        add_months(dt.date(2022, 4, 7), 24),
        dt.date(2024, 4, 7),
        name=qualify(add_months))
    testif('returns correct date if more than two years',
        add_months(dt.date(2022, 8, 3), 29),
        dt.date(2025, 1, 3),
        name=qualify(add_months))

    print('yest ymd', get_yest_ymd())
    print('today ymd', get_today_ymd())
    print('tmw ymd', get_tmw_ymd())

    nonce_noext = NonceDailyRule(r'C:\alerts\jersey', lambda: print('Running jersey alert'))
    testif('returns correct name',
        nonce_noext.get_name(),
        'jersey',
        name=qualify(NonceDailyRule.get_name))
    nonce_wext = NonceDailyRule(r'C:\alerts\jersey.txt', lambda: print('Running jersey alert'))
    testif('returns correct name',
        nonce_wext.get_name(),
        'jersey',
        name=qualify(NonceDailyRule.get_name))
