from django.forms import ModelForm, DateInput
from .models import Event, Experiment


class EventForm(ModelForm):
    class Meta:
        model = Event
        widgets = {
            'start_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%d')
        }
        fields = '__all__'

        def __init__(self, *args, **kwargs):
            super(EventForm, self).__init__(*args, **kwargs)
            self.fields['start_time'].input_formats = ('%Y-%m-%d',)


class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment
        widgets = {
            'earliest_start': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%d'),
            'latest_start': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%d')
        }
        fields = '__all__'

        def __init__(self, *args, **kwargs):
            super(ExperimentForm, self).__init__(*args, **kwargs)
            self.fields['earliest_start'].input_formats = ('%Y-%m-%d',),
            self.fields['latest_start'].input_formats = ('%Y-%m-%d',)
