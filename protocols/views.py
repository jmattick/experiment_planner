from datetime import date, datetime, timedelta
import calendar
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.views.generic import ListView
from .Protocol import ProtocolLinkedList, RSDStep, SDStep, TDStep
from .forms import EventForm, ExperimentForm
from .models import Event, Experiment, Protocol, Step

from .utils import build_schedule, Calendar, protocol_to_protocol_ll, score_alignments, ScheduleObject


class CalendarView(ListView):
    model = Event
    template_name = 'protocols/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)

        return context


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month


def create_event(request):
    form = EventForm()
    context = {
        'form': form,
    }
    return render(request, 'protocols/new_event.html', context)


def event(request, event_id):
    template_name = 'protocols/event.html'
    context_object_name = 'event'
    event = get_object_or_404(Event, pk=event_id)
    return render(request, template_name, {context_object_name: event})


def scheduler(request):
    if request.method == 'POST':
        experiment = Experiment()
        form = ExperimentForm(request.POST, instance=experiment)
        print(form)
        if form.is_valid():
            experiment = form.save()
            print(experiment)
            print(experiment.pk)
            return redirect('protocols:scheduler_options', experiment_id=experiment.id)
    else:
        experiment = Experiment()
        print('get:')
        print(experiment.id)
        form = ExperimentForm(instance=experiment)
    template_name = 'protocols/scheduler.html'
    context = {
        'form': form
    }
    return render(request, template_name, context)


def scheduler_options(request, experiment_id):
    template_name = 'protocols/scheduler_options.html'
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    protocol_ll = protocol_to_protocol_ll(experiment.protocol)

    num_days = protocol_ll.total_days() #max number of days in protocol
    start_range = experiment.latest_start - experiment.earliest_start
    print(start_range.days)
    start = experiment.earliest_start
    end = experiment.latest_start + timedelta(days=num_days + 1)
    sched_len = end - start
    events = Event.objects.filter(start_time__gte=start, start_time__lte=end)

    schedule_objs = build_schedule(start, sched_len.days, events)

    score_alignments(protocol_ll, schedule_objs, start_range.days)
    context = {
        'experiment': experiment,
        'schedule': schedule_objs
    }
    return render(request, template_name, context)


def index(request):
    """"index view"""
    template_name = 'protocols/index.html'
    context_object_name = 'protocol_list'
    return render(request, template_name, {context_object_name: Protocol.objects.all()})


class IndexView(ListView):
    """Index view containing calendar"""
    template_name = 'protocols/index.html'
    context_object_name = 'protocol_list'
    model = Protocol

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol_list'] = Protocol.objects.all()
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)

        return context


def detail(request, protocol_id):
    """detail view"""
    template_name = "protocols/detail.html"
    context_object_name = 'protocol'
    protocol = get_object_or_404(Protocol, pk=protocol_id)
    steps = Step.objects.filter(protocol=protocol) #get all step associated with protocol
    protocol_to_protocol_ll(protocol) #updates dag in protocol

    return render(request, template_name, {context_object_name: protocol})



