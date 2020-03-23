from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .Protocol import ProtocolLinkedList, RSDStep, SDStep, TDStep
from .models import Event, Step


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


def protocol_to_protocol_ll(protocol):
    """Function to convert django protocol model into a ProtocolLinkedLIst"""
    steps = Step.objects.filter(protocol=protocol)  # get all step associated with protocol
    protocol_ll = ProtocolLinkedList()  # initialize protocol linked list
    for s in steps:  # loop through all steps to add to protocol linked list
        step_text = s.step_text
        time_min = s.time_min,
        days_between = s.days_between
        gap_days = s.gap_days
        if s.type == "TDS":
            protocol_ll.add_step(TDStep(step_text, time_min, days_between, gap_days))
        elif s.type == "RSDS":
            protocol_ll.add_step(RSDStep(step_text, time_min, days_between, gap_days))
        else:
            protocol_ll.add_step(SDStep(step_text, time_min, days_between, gap_days))
    dag, nodes = protocol_ll.build_DAG()  # store the dag and nodes in variables to be passed
    protocol.protocol_ll = protocol_ll

    protocol.nodes = nodes
    protocol.dag = []
    for node in nodes:
        v = list(dag[node])
        v.sort()
        protocol.dag.append(str(node) + ': ' + str(v))
    return protocol_ll