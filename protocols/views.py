from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Protocol, Step


def index(request):
    """"index view"""
    template_name = 'protocols/index.html'
    context_object_name = 'protocol_list'
    return render(request, template_name, {context_object_name: Protocol.objects.all()})


def detail(request, protocol_id):
    """detail view"""
    template_name = "protocols/detail.html"
    context_object_name = 'protocol'
    protocol = get_object_or_404(Protocol, pk=protocol_id)

    return render(request, template_name, {context_object_name: protocol})