
"""
Jobs

Future features: overtime hour detection for increased accuracy

"""

from collections import OrderedDict
import datetime
import math
import pprint

from clay.clusters import SortableDict
from clay.graphing import Histogram
from clay.maths import average, median

DAYS_PER_WEEK = 7

def offsetby(day, number):
    """Returns an integer representing the day number shifted
    by the given amount"""
    day -= number
    if day < 0:
        day += 7
    return day

class Attendance(object):
    """Analyzes CSV time-sheets for jobs in the following format:
           month day year,time in,time out,hours worked

       Attendance sheet is read from 'attendance.csv', so it must exist for
       anything to work."""

    HEADERS = ('date', 'time_in', 'time_out', 'hours')
    PT_TYPES = ('week', 'month')
       
    def __init__(self, take_home_ratio, perhour, offset=0):
        """Accepts pay ratio, pay per hour, and the payday offset, default 0 is Monday."""
        import os
        assert os.path.exists('attendance.csv'), 'file attendance.csv doesn\'t exist'
        with open('attendance.csv') as fp:
            file = [line.split(',') for line in fp.read().strip().split('\n')]
        assert len(file) > 0, 'file must have at least one entry'
        
        db = [{j: line[i] for i, j in enumerate(Attendance.HEADERS)} for line in file]
        
        for i, row in enumerate(db):
            db[i]['hours'] = float(db[i]['hours']) # convert the hours from strings to floats
                
        self.take_home_ratio = take_home_ratio

        self.db       = db
        self.perhour  = perhour
        self.offset   = offset
        self.filtered = dict()
        self.pt       = dict()

    def money(self, per):
        """Calculates and prints the take-home estimate for the given period `per`"""
        if per in Attendance.PT_TYPES and per in self.pt:
            exec("""for i, {0} in enumerate(self.filtered['{0}']): print('{0}', str(i) + ': $' + str(round(self.pt['{0}'][list(self.pt['{0}'].keys())[i]] * self.perhour * self.take_home_ratio, 4)))""".format(per))

    def moneyall(self):
        """Calculates and prints the take-home estimate for the whole job"""
        print('estimate take-home using the ratio {}: ${}'.format(round(self.take_home_ratio, 4), \
                                                                  round(self.get_total_hours() * self.perhour * self.take_home_ratio, 4)))

    def get_average_hours(self):
        return average(self.get_hours())
        
    def select(self, attrib):
        if not(attrib in Attendance.HEADERS):
            raise ValueError('attrib must be a header. Headers are ' + ', '.join(Attendance.HEADERS))
        return (row[attrib] for row in self.db)
        
    def get_hours(self):
        return list(self.select('hours'))

    def punchcard(self):
        # columns are initialized to 0
        hg = Histogram(columns=list(range(DAYS_PER_WEEK)))
        for col in hg.cols:
            for row in self.db:
                date = datetime.datetime.strptime(row['date'], '%m-%d-%Y')
                if date.weekday() == col:
                    hg.sd[col] += 1
        hg.build()
        self.hg = hg

    def get_total_hours(self):
        return sum(self.get_hours())

    def printreport(self):
        print()
        self.setup_pt(by='week')
        pprint.pprint(self.pt['week'])

        print()
        self.setup_pt(by='month')
        pprint.pprint(self.pt['month'])

        print()
        print('total hours: ', round(self.get_total_hours(), 4))

        self.money(per='week')
        self.moneyall()

        print()
        print('average:', round(self.get_average_hours(), 4))
        print('median:', round(median(self.get_hours()), 4))
        print()
        self.punchcard()
        print(self.hg.sd)

    def removebreaks(self, lunches=False):
        """Removes breaks from the punchcard, allows for accurate money calculations"""
        for i, row in enumerate(self.db):
            self.db[i]['hours'] -= math.floor(self.db[i]['hours'] / 5) * 0.5 # remove lunch breaks from hours

    def setup_pt(self, by=None):
        """Sets up the 'Pivot Table' for the given field. Sets up both tables if by is None"""
        if by == 'month':
            months = OrderedDict()
            fp = open('months.log', 'w')
            for row in self.db:
                mon = row['date'].split('-')[0]
                if not(mon in months):
                    print('new', mon, file=fp)
                    months[mon] = list()
                print('adding', row['hours'], 'to', mon, file=fp)
                months[mon].append(row['hours'])
            fp.close()
            sorted_months = OrderedDict()
            for month in months:
                sorted_months[month] = sum(months[month])
            self.filtered['month'] = sorted_months
            self.pt['month'] = sorted_months

        elif by == 'week':

            print('Note: work week starts on day', self.offset)

            prev = datetime.date(2017, 7, 3) # date before any work starts

            fp = open('weeks.log', 'w')

            sorted_weeks = OrderedDict()
            for row in self.db:
                date = datetime.datetime.strptime(row['date'], '%m-%d-%Y')
                prevday = offsetby(prev.weekday(), self.offset)
                dateday = offsetby(date.weekday(), self.offset)
                print(row['date'], file=fp) # print the date
                print('    prev {} : date {}'.format(prevday, dateday), file=fp)
                print(' '*4, end=str(), file=fp)
                if prevday < dateday and len(sorted_weeks) > 0:
                    print('date is bigger than last. using existing week', file=fp)
                else:
                    print('date is smaller than last. adding a new week...', file=fp)
                    sorted_weeks[str(len(sorted_weeks))] = list()
                prev = date
                sorted_weeks[str(len(sorted_weeks) - 1)].append(row['hours'])
                print(' '*4, end=str(), file=fp)
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
