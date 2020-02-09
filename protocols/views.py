from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .Protocol import ProtocolLinkedList, RSDStep, SDStep, TDStep

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