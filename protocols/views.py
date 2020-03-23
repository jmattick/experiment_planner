from datetime import date, datetime, timedelta
import calendar
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.views.generic import ListView
from .Protocol import ProtocolLinkedList, RSDStep, SDStep, TDStep
from .forms import EventForm, ExperimentForm
from .models import Event, Experiment, Protocol, Step

from .utils import Calendar


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
    context = {
        'experiment': experiment
    }
    return render(request, template_name, context)


def index(request):
    """"index view"""
    template_name = 'protocols/index.html'
    context_object_name = 'protocol_list'
    return render(request, template_name, {context_object_name: Protocol.objects.all()})


class IndexView(ListView):
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
    protocol_ll = ProtocolLinkedList() #initialize protocol linked list
    for s in steps: #loop through all steps to add to protocol linked list
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
    dag, nodes = protocol_ll.build_DAG() #store the dag and nodes in variables to be passed
    protocol.protocol_ll = protocol_ll

    protocol.nodes = nodes
    protocol.dag = []
    for node in nodes:
        v = list(dag[node])
        v.sort()
        protocol.dag.append(str(node) + ': ' + str(v))

    return render(request, template_name, {context_object_name: protocol})