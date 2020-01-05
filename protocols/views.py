from django.shortcuts import render
from django.http import HttpResponse

from .models import Protocol, Step


def index(request):
    """"index view"""
    template_name = 'protocols/index.html'
    context_object_name = 'protocol_list'
    return render(request, template_name, {context_object_name: Protocol.objects.all()})

