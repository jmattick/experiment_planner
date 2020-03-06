from django.db import models
from django.urls import reverse
from django.utils import timezone
import datetime
from .Protocol import ProtocolLinkedList, RSDStep, SDStep, TDStep


class Protocol(models.Model):
    name = models.CharField(max_length=200)
    days = models.IntegerField(default=1)
    description = models.CharField(max_length=200)
    protocol_ll = ProtocolLinkedList()

    def __str__(self):
        return self.name


class Step(models.Model):
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE)
    # step_number = models.IntegerField(default=0)
    type = models.CharField(max_length=50, choices=[('default', 'default'), ('SDS', 'SDS'), ('RSDS', 'RSDS'), ('TDS', 'TDS')])
    step_text = models.CharField(max_length=1000)
    time_min = models.IntegerField(default=0)
    # flexible = models.BooleanField(default=False)
    days_between = models.IntegerField(default=1)
    gap_days = models.IntegerField(default=0)

    #
    # if type == "TDS":
    #     protocol.object.protocol_ll.add_step(TDStep(step_text, time_min, days_between, gap_days))
    # elif type == "RSDS":
    #     protocol.protocol_ll.add_step(RSDStep(step_text, time_min, days_between, gap_days))
    # else:
    #     protocol.protocol_ll.add_step(SDStep(step_text, time_min, days_between, gap_days))


class Feature(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    details = models.CharField(max_length=1000)


class Event(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField(default=timezone.now,)
    minutes = models.IntegerField(default=5)

    def __str__(self):
        return self.title

    @property
    def get_html_url(self):
        url = reverse('protocols:event_edit', args=(self.id,))
        return f'<a href="{url}">{self.title}</a>'








