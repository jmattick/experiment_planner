from django.db import models


class Protocol(models.Model):
    name = models.CharField(max_length=200)
    days = models.IntegerField(default=1)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Step(models.Model):
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE)
    step_number = models.IntegerField(default=0)
    step_text = models.CharField(max_length=1000)
    time_min = models.IntegerField(default=0)
    flexible = models.BooleanField(default=False)
