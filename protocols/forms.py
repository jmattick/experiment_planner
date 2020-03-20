from django.forms import ModelForm, DateInput
from .models import Event


class EventForm(ModelForm):
    class Meta:
        model = Event
        widgets = {
            'start_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
        }
        fields = '__all__'

        def __init__(self, *args, **kwargs):
            super(EventForm, self).__init__(*args, **kwargs)
            self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)
