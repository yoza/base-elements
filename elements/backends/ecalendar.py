from datetime import date
from calendar import HTMLCalendar

from django.utils.safestring import mark_safe
from django.forms.extras.widgets import SelectDateWidget
from django.utils.dates import WEEKDAYS_ABBR
from django.conf import settings

from mainpage.dates import MONTHS_ALL


class eCalendar(HTMLCalendar):

    def __init__(self, firstweekday=settings.FIRST_DAY_OF_WEEK):
        HTMLCalendar.__init__(self, firstweekday)

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        if day == 0:
            return '<td class="noday">&nbsp;</td>' # day outside month
        elif day in self.active_days:
            dd = date(self.active_year, self.active_month, day)
            """
            success_day_url = reverse('events_archive_day',
                                      args=[dd.strftime('%Y'),
                                            dd.strftime('%m'),
                                            dd.strftime('%d')])
            """
            success_day_url  = "/"
            return '<td class="%s active"><a href="%s" '\
                   'class="active">%d</a></td>' % (
                self.cssclasses[weekday], success_day_url, day)
        else:
            return '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return '<TH class="%s">%s<DIV class="dayborder">&nbsp;</DIV></TH>' % (self.cssclasses[day],
                                           WEEKDAYS_ABBR[day].title()[:2])

    def formatweekheader(self):
        """
        Return a header for a week as a table row.
        """
        return '<THEAD>%s</THEAD>' % super(eCalendar, self).formatweekheader()

    def opt_years(self, theyear):
        """
        Return years options list with selected year
        """
        years = range(settings.CALENDAR_RANGE[0],settings.CALENDAR_RANGE[1],1)
        listyears = ''
        for i in years:
            sel = ''
            if int(i) == int(theyear):
                sel = 'selected="selected"'
            listyears +='<OPTION %s value="%d">%d</OPTION>' % (sel, i, i)
        return listyears

    def opt_month(self, themonth):
        """
        Return months options list with selected month
        """
        listmonth = ''
        for i in MONTHS_ALL:
            sel = ''
            if int(i) == int(themonth):
                sel = 'selected="selected"'
            listmonth +='<OPTION %s value="%d">%s</OPTION>' % (sel, i, MONTHS_ALL[i].title().rstrip())
        return listmonth

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a selected month name as a table caption with months and years options.
        """
        v = []
        a = v.append
        a('<CAPTION>')
        a('<FORM class="form" action="" id="ecalendar">')
        a('<SELECT autocomplete="off" id="ca_month" name="month">%s</SELECT>' % self.opt_month(themonth))
        if withyear:
            a('<SELECT autocomplete="off" id="ca_year" name="year">%s</SELECT>' % self.opt_years(theyear))
        a('</FORM>')
        a('</CAPTION>')
        return mark_safe(''.join(v))

    def formatmonth(self, theyear, themonth, withyear=True, active_days=[]):
        """
        Return a formatted month as a table.
        """
        self.active_days = active_days
        self.active_year = theyear
        self.active_month = themonth

        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)
