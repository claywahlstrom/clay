
"""
Jobs

TODO: support overtime hours and salary calculations

"""

from collections import OrderedDict
import datetime as dt
import math
import pprint

from clay.graphing import Histogram
from clay.maths import average, median
from clay.util import SortableDict

BREAK_SCHEDULES = {'WA': {'hours': 6, 'length': 0.5},
                   'OR': {'hours': 5, 'length': 1.0}}

DAYS_OF_THE_WEEK = ('Monday',
                    'Tuesday',
                    'Wednesday',
                    'Thursday',
                    'Friday',
                    'Saturday',
                    'Sunday')

DAYS_PER_WEEK = len(DAYS_OF_THE_WEEK)

class Attendance(object):
    """Analyzes CSV time-sheets for jobs in the following format:
           month day year,time in,time out,hours worked

       Attendance sheet is read from 'attendance.csv', so it must exist for
       anything to work."""

    PT_TYPES = ('week', 'month')

    def __init__(self, take_home_ratio, perhour, state, offset=0):
        """Accepts pay ratio, pay per hour, and the payday offset, default 0 is for Monday."""
        import os
        if not(state in BREAK_SCHEDULES):
            raise ValueError(f'state must be in [{", ".join(BREAK_SCHEDULES)}]')
        if not(os.path.exists('attendance.csv')):
            raise FileNotFoundError('attendance.csv doesn\'t exist')
        with open('attendance.csv') as fp:
            file = [line.split(',') for line in fp.read().strip().split('\n') \
                                        if len(line) > 0 and not(line.startswith('#'))]
        assert len(file) > 0, 'file must have at least one entry'
        assert max(map(len, file)) == min(map(len, file)), 'data columns must be consistent'

        if file[0][0] != 'date' or file[0][-1] != 'hours':
            raise RuntimeError('First row of CSV must be column headers including date and hours')

        self.headers = file[0]
        file.pop(0) # remove the header row

        db = [{j: line[i] for i, j in enumerate(self.headers)} for line in file]


        for i, row in enumerate(db):
            db[i]['hours'] = float(db[i]['hours']) # convert the hours from strings to floats

        self.take_home_ratio = take_home_ratio

        self.db       = db
        self.perhour  = perhour
        self.offset   = offset
        self.filtered = {}
        self.pt       = {}
        self.state    = state

    def get_average_hours(self):
        return average(self.get_hours())

    def get_hours(self):
        return list(self.select('hours'))

    def get_total_hours(self):
        return sum(self.get_hours())

    def print_money(self, per):
        """Calculates and prints the take-home estimate for the given period `per`"""
        if per in Attendance.PT_TYPES and per in self.pt:
            exec(f"for i, {per} in enumerate(self.filtered['{per}']): \n \
                       key = list(self.pt['{per}'].keys())[i] \n \
                       money = self.pt['{per}'][key] * self.perhour * self.take_home_ratio \n \
                       print('{per}', str(i) + " + "': ${:,.2f}'.format(money))")
        else:
            print(per, 'is not a supported type')

    def print_money_all(self):
        """Calculates and prints the take-home estimate for the whole job"""
        print('estimate take-home using the ratio {}: ${:,.2f}'.format(round(self.take_home_ratio, 4), \
                                                                       self.get_total_hours() * self.perhour * self.take_home_ratio))

    def print_punchcard(self, names=True):
        # columns are initialized to 0
        hg = Histogram(columns=DAYS_OF_THE_WEEK, sort=not(names))
        for col in hg.data:
            for row in self.db:
                date = dt.datetime.strptime(row['date'], '%m-%d-%Y').weekday()
                if (names and DAYS_OF_THE_WEEK[date] == col) or date == col:
                    hg.sd[col] += 1
        self.weekly_hg = hg
        hg.build()

    def print_report(self):
        hours = self.get_hours()
        print()
        self.setup_pt() # set up both pt's
        print()
        print('by week')
        pprint.pprint(self.pt['week'])
        print()
        print('by month')
        pprint.pprint(self.pt['month'])
        print()
        print('total hours: ', round(self.get_total_hours(), 4))
        self.print_money('week')
        self.print_money_all()
        print()
        print('average:', round(self.get_average_hours(), 4))
        print('median :', round(median(hours), 4))
        print('mode   :', round(max(hours, key=hours.count), 4))
        print()
        self.print_punchcard()
        print()

    def remove_breaks(self, lunches=False):
        """Removes breaks from the punchcard, allows for accurate money calculations"""
        print('Removing breaks using the rules for', self.state)
        print(f"break length is {BREAK_SCHEDULES[self.state]['length']}hr")
        print('count', end='\t')
        print('date', end='\t\t')
        print('hours (before deduction))')

        for i, row in enumerate(self.db):
            print(math.floor(self.db[i]['hours'] / BREAK_SCHEDULES[self.state]['hours']), end='\t')
            print(self.db[i]['date'], end='\t')
            print(self.db[i]['hours'])
            # remove lunch breaks from hours
            self.db[i]['hours'] -= math.floor(self.db[i]['hours'] / \
                                   BREAK_SCHEDULES[self.state]['hours']) * \
                                   BREAK_SCHEDULES[self.state]['length']

    def select(self, attrib, until_date=None):
        if not(attrib in self.headers):
            raise ValueError('attrib must be a header. Headers are ' + ', '.join(self.headers))
        selection = []
        for row in self.db:
            if row['date'] == until_date:
                break
            selection.append(row[attrib])
        return selection

    def setup_pt(self, by=None):
        """Sets up the 'Pivot Table' for the given field. Sets up both tables if by is None"""
        if by == 'month':
            months = OrderedDict()
            fp = open('months.log', 'w')
            for row in self.db:
                mon = row['date'].split('-')[0]
                if not(mon in months):
                    print('new', mon, file=fp)
                    months[mon] = []
                print('adding', row['hours'], 'to', mon, file=fp)
                months[mon].append(row['hours'])
            fp.close()
            sorted_months = OrderedDict()
            for month in months:
                sorted_months[month] = sum(months[month])
            self.filtered['month'] = sorted_months
            self.pt['month'] = sorted_months

        elif by == 'week':

            print('Note: this work week starts on day', self.offset)

            prev = dt.date(2017, 7, 3) # date before any work starts

            fp = open('weeks.log', 'w')

            sorted_weeks = OrderedDict()
            for row in self.db:
                date = dt.datetime.strptime(row['date'], '%m-%d-%Y')
                prevday = get_day_offset(prev.weekday(), self.offset)
                dateday = get_day_offset(date.weekday(), self.offset)
                print(row['date'], file=fp) # print the date
                print('    prev {} : date {}'.format(prevday, dateday), file=fp)
                print(' ' * 4, end='', file=fp)
                if prevday < dateday and len(sorted_weeks) > 0:
                    print('date is bigger than last. using existing week', file=fp)
                else:
                    print('date is smaller than last. adding a new week...', file=fp)
                    sorted_weeks[str(len(sorted_weeks))] = []
                prev = date
                sorted_weeks[str(len(sorted_weeks) - 1)].append(row['hours'])
                print(' ' * 4, end='', file=fp)
                thisweek = sorted_weeks[str(len(sorted_weeks) - 1)]
                print(thisweek, '-> average =', average(thisweek), file=fp)
            fp.close()

            self.filtered['week'] = sorted_weeks
            self.pt['week'] = OrderedDict()
            for week, values in sorted_weeks.items():
                self.pt['week'][week] = sum(values)
        else:
            self.setup_pt('week')
            self.setup_pt('month')
            
def get_day_offset(day, number):
    """Returns an integer representing the day number shifted
    by the given amount"""
    day -= number
    if day < 0:
        day += 7
    return day