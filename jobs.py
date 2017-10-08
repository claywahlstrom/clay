

from collections import OrderedDict
import datetime
import math

from clay.histogram import HG
from clay.maths import average
from clay.misc import SortableDict

class Attendance:
    """Analyzes CSV time-sheets for jobs in the following format:
         month day year,time in,time out,hours worked
         
    Attendance sheet is read from 'attendance.csv', so it must exist for
    anything to work.
    """


    def __init__(self, pay_ratio, perhour):
        import os
        assert os.path.exists('attendance.csv'), 'file attendance.csv doesn\'t exist'
        with open('attendance.csv') as fp:
            file = [line.split(',') for line in fp.read().strip().split('\n')]

        hours = list(map(float, (line[-1] for line in file)))

        total_hours = sum(hours)
        cum_average = average(list(hours))

        self.file = file
        self.hours = hours
        self.total_hours = total_hours
        self.cum_average = cum_average
        self.ratio = pay_ratio
        self.perhour = perhour
        
        self.pt = dict()
        self.pt_done = list()

    def money(self, per=None):
        if per in ('week', 'month') and per + 's' in self.pt_done:
            exec("""for i, {0} in enumerate(self.{1}): print('{0}', str(i) + ': $' + str(round(self.pt['{0}'][list(self.pt['{0}'].keys())[i]] * self.perhour * self.ratio, 4)))""".format(per, per + 's'))

    def moneyall(self):
        print('estimate take-home using the ratio {}: ${}'.format(self.ratio, round(self.total_hours * self.perhour * self.ratio, 4)))

    def get_punchcard(self):
        # columns are initialized to 0
        hg = HG(columns=list(range(7)))
        for col in hg.cols:
            for line in self.file:
                date = datetime.datetime.strptime(line[0], '%m %d %Y')
                if date.weekday() == col:
                    hg.sd[col] += 1
        hg.build()
        self.hg = hg

    def removebreaks(self, lunches=False):
        """Remove breaks from the punchcard, allows for accurate money calculations"""
        for i, hour in enumerate(self.hours):
            #self.hours[i] -= 0.25 * math.floor(self.hours[i] / 3) # small breaks every 3 hours
            self.hours[i] -= math.floor(hour / 5) * 0.5 # lunch break
            self.file[i][-1] = str(self.hours[i])
        total_hours = sum(self.hours)
        cum_average = average(list(self.hours))
        self.total_hours = total_hours
        self.cum_average = cum_average

    def setup_pt(self, by=None):
        """Set up the 'Pivot Table' for each month"""
        if by == 'month':
            # parse file
            months = OrderedDict()
            fp = open('months.log', 'w')
            for line in self.file:
                mon = line[0].split()[0]
                if not(mon in months):
                    print('new', mon, file=fp)
                    months[mon] = list()
                print('adding', line[-1], 'to', mon, file=fp)
                months[mon].append(float(line[-1]))
            fp.close()
            pt_months = OrderedDict()
            for month in months:
                pt_months[month] = sum(months[month])
            self.pt['month'] = pt_months

            new_months = OrderedDict()
            for i, line in months:
                new_months[i] = line
            self.pt['month'] = pt_months
            self.months = months
            self.pt_done.append('months')
        elif by == 'week':
            weeks = list()

            print('Note: weeks start on a Monday')

            prev = datetime.date(2017, 7, 3)

            fp = open('weeks.log', 'w')

            for line in self.file:
                date = datetime.datetime.strptime(line[0], '%m %d %Y')
                print(datetime.datetime.strftime(date, '%m-%d-%Y'), file=fp)
                print('    prev {} : date {}'.format(prev.weekday(), date.weekday()), file=fp)
                print(' '*4, end=str(), file=fp)
                if prev.weekday() < date.weekday() and weeks:
                    print('date is bigger and weeks exists', file=fp)
                    weeks[-1].append(float(line[-1]))
                    prev = date
                else:
                    print('date is smaller than last. adding a new week...', file=fp)
                    weeks.append([float(line[-1])])
                    prev = date
                print(' '*4, end=str(), file=fp)
                print(weeks[-1], 'average', average(weeks[-1]), file=fp)
            fp.close()
            pt_weeks = OrderedDict()
            for i, line in enumerate(weeks):
                pt_weeks[i] = sum(line)
            self.pt['week'] = pt_weeks

            new_weeks = OrderedDict()
            for i, line in enumerate(weeks):
                new_weeks[i] = line
            self.weeks = new_weeks
            self.pt_done.append('weeks')
        else:
            print('Cannot setup a pt for None... lol')
