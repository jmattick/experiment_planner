from datetime import datetime, timedelta
from calendar import HTMLCalendar

from .models import Event


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    def formatday(self, day, events):
        events_per_day = events.filter(start_time__day=day)
        d = ''
        t = 0
        for event in events_per_day:
            t += int(event.minutes)
            d += f'<li class="calendar_list"> {event.get_html_url} </li>'
        trans = t / 480
        if trans > 1:
            trans = 1
        if day != 0:
            return f"<td style='background-color:rgba(223,76,115,{trans})'><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month)
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        return cal


class ScheduleObject():
    def __init__(self, date=None, score=0):
        self.date = date
        self.score = score


def build_schedule(start, days, events):
    schedule_objs = []
    ##get total time of all events for each day
    curr = start
    for i in range(days):
        events_per_day = events.filter(start_time__day=curr.day)
        t = 0
        for e in events_per_day:
            t += int(e.minutes)
        schedule_objs.append(ScheduleObject(curr, t))
        curr = curr + timedelta(days=1)
    print(schedule_objs)
    return schedule_objs
