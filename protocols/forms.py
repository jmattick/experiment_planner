from django.forms import ModelForm, DateInput
from .models import Event, Experiment, Protocol, Step
from datetime import datetime
from django.forms.models import inlineformset_factory


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
            'earliest_start': DateInput(attrs={'type': 'date', 'value': datetime.now().strftime('%Y-%m-%d')}, format='%Y-%m-%d'),
            'latest_start': DateInput(attrs={'type': 'date', 'value': datetime.now().strftime('%Y-%m-%d')}, format='%Y-%m-%d'),
            'date': DateInput(attrs={'type': 'date', 'value': datetime.now().strftime('%Y-%m-%d')}, format='%Y-%m-%d')
        }
        fields = '__all__'

        def __init__(self, *args, **kwargs):
            super(ExperimentForm, self).__init__(*args, **kwargs)
            self.fields['earliest_start'].input_formats = ('%Y-%m-%d',),
            self.fields['latest_start'].input_formats = ('%Y-%m-%d',)
#
#
# class ProtoclForm(ModelForm):
#     class Meta:
#         model = Protocol
#         fieldsets = [
#             (None, {'fields': ['name']}),
#             ('Days', {'fields': ['days']}),
#             ('Description', {'fields': ['description']})
#         ]
#         inlines = [StepInline]
#         list_display = ('name', 'description', 'days')
#         search_fields = ['name']


class StepForm(ModelForm):
    class Meta:
        model = Step
        exclude = ()


StepFormSet = inlineformset_factory(Protocol, Step, form=StepForm, fields='__all__', extra=3, can_delete=True)