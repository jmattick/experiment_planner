from datetime import date, datetime, timedelta
import calendar
import plotly.graph_objects as go
import plotly.offline as opy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db import transaction
from django.urls import reverse_lazy
from .Protocol import ProtocolLinkedList, RSDStep, SDStep, TDStep
from .forms import *
from .models import Event, Experiment, Protocol, Step
import json
from .utils import *


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


def edit_event(request, event_id):
    template_name = 'protocols/event_edit.html'
    event = get_object_or_404(Event, pk=event_id)
    experiment = get_object_or_404(Experiment, pk=event.experiment_id)
    # Form
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            return redirect('protocols:event', event_id=event.id)
    else:
        form = EventForm(instance=event)

    context = {
        'event': event,
        'experiment': experiment,
        'form': form
    }
    return render(request, template_name, context)


def delete_event(request, event_id):
    template_name = 'protocols/event_delete.html'
    event = get_object_or_404(Event, pk=event_id)
    context = {
        'event': event
    }

    if "one" in request.POST:
        Event.objects.get(pk=event_id).delete()  # delete event
        return redirect('protocols:index')
    elif "all" in request.POST:
        Event.objects.filter(experiment_id=event.experiment_id).delete()  # delete all events in experiment
        return redirect('protocols:index')

    return render(request, template_name, context)


def event(request, event_id):
    template_name = 'protocols/event.html'
    context_object_name = 'event'
    event = get_object_or_404(Event, pk=event_id)
    experiment = get_object_or_404(Experiment, pk=event.experiment_id)
    context = {
        context_object_name: event,
        'experiment': experiment
    }
    return render(request, template_name, context)


@login_required
def scheduler(request):
    if request.method == 'POST':
        experiment = Experiment()
        form = ExperimentForm(request.POST, instance=experiment)
        print(form)
        if form.is_valid():
            experiment.created_by = request.user
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


@login_required
def scheduler_options(request, experiment_id):
    template_name = 'protocols/scheduler_options.html'
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    protocol_ll = protocol_to_protocol_ll(experiment.protocol)
    num_days = protocol_ll.total_days()  # max number of days in protocol
    start_range = experiment.latest_start - experiment.earliest_start
    start = experiment.earliest_start
    end = experiment.latest_start + timedelta(days=num_days + 1)
    sched_len = end - start
    events = Event.objects.filter(start_time__gte=start, start_time__lte=end)
    schedule_objs = build_schedule(start, sched_len.days, events)
    scores = score_alignments(protocol_ll, schedule_objs, start_range.days)
    formated_scores = []
    x = []
    y = []
    for score in scores:
        x.append(str(score[0].date()))
        y.append(score[1])
    fig = go.Figure([go.Bar(x=x, y=y)])
    fig.update_layout(
        title={
            'text': 'Scores for each start date',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    div = opy.plot(fig, auto_open=False, output_type='div')

    # Form
    if request.method == 'POST':
        form = ExperimentForm(request.POST, instance=experiment)
        if form.is_valid():
            experiment = form.save()
            if 'add_calendar' in request.POST:
                schedule_objs_events = build_schedule(experiment.date, sched_len.days, events)

                #TODO add to calendar logic here
                d, n = protocol_ll.build_DAG()
                add_experiment_to_calendar(experiment, d, n, schedule_objs_events, request.user)
                return redirect('protocols:index')
            return redirect('protocols:scheduler_options', experiment_id=experiment.id)
    else:
        form = ExperimentForm(instance=experiment)
    # Context
    context = {
        'experiment': experiment,
        'schedule': schedule_objs,
        'graph': div,
        'form': form
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
        events = Event.objects.filter(start_time__date=datetime.now(), created_by=self.request.user)
        context['events'] = events
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month, self.request.user)
        cal = Calendar(d.year, d.month, self.request.user)
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
    protocol_ll = protocol_to_protocol_ll(protocol) #updates dag in protocol
    dag, nodes = protocol_ll.build_DAG()
    json = format_dag_json(dag, nodes)
    context = {
        'protocol': protocol,
        'json': json

    }

    return render(request, template_name, context)


class ProtocolCreate(LoginRequiredMixin, CreateView):
    model = Protocol
    template_name = 'protocols/add_protocol.html'
    fields = ['name', 'description']
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(ProtocolCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['steps'] = StepFormSet(self.request.POST)
        else:
            data['steps'] = StepFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        steps = context['steps']
        form.instance.created_by = self.request.user
        with transaction.atomic():
            self.object = form.save()

            if steps.is_valid():
                steps.instance = self.object
                steps.save()
        return super(ProtocolCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('protocols:detail', kwargs={'protocol_id': self.object.pk})


class ProtocolUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Protocol
    template_name = 'protocols/add_protocol.html'
    fields = ['name', 'description']
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(ProtocolUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['steps'] = StepFormSet(self.request.POST, instance=self.object)
        else:
            data['steps'] = StepFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        steps = context['steps']
        with transaction.atomic():
            self.object = form.save()
            if steps.is_valid():
                steps.instance = self.object
                steps.save()
        return super(ProtocolUpdate, self).form_valid(form)

    def test_func(self):
        protocol = self.get_object()
        if self.request.user == protocol.created_by:
            return True
        return False

    def get_success_url(self):
        return reverse_lazy('protocols:detail', kwargs={'protocol_id': self.object.pk})


class ProtocolDelete(DeleteView):
    model = Protocol
    template_name = 'protocols/delete_protocol.html'
    success_url = reverse_lazy('protocols:index')

    def test_func(self):
        protocol = self.get_object()
        if self.request.user == protocol.created_by:
            return True
        return False