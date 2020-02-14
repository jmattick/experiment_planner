# from django.test import TestCase
from .Protocol import ProtocolLinkedList, RSDStep, Step, SDStep, TDStep
# Create your tests here.
import timeit


def test_protocol_add_step_length():
    prot = ProtocolLinkedList()
    prot.add_step(Step("1"))
    return prot.length() == 1


def test_protocol_add_many_steps_length():
    prot = ProtocolLinkedList()
    for i in range(10):
        prot.add_step(Step("step"))
    return prot.length() == 10


def test_protocol_add_sdstep_length():
    prot = ProtocolLinkedList()
    prot.add_step(SDStep("1"))
    return prot.length() == 1


def test_protocol_add_many_sdssteps_length():
    prot = ProtocolLinkedList()
    for i in range(10):
        prot.add_step(SDStep("step"))
    return prot.length() == 10


def test_protocol_add_rsdstep_length():
    prot = ProtocolLinkedList()
    prot.add_step(RSDStep("1"))
    return prot.length() == 1


def test_protocol_add_many_rsdssteps_length():
    prot = ProtocolLinkedList()
    for i in range(10):
        prot.add_step(RSDStep("step"))
    return prot.length() == 10


def test_protocol_add_tdstep_length():
    prot = ProtocolLinkedList()
    prot.add_step(TDStep("1"))
    return prot.length() == 1


def test_protocol_add_many_tdssteps_length():
    prot = ProtocolLinkedList()
    for i in range(10):
        prot.add_step(TDStep("step"))
    return prot.length() == 10


def test_protocol_add_step_total_days():
    prot = ProtocolLinkedList()
    prot.add_step(Step("1", 2))
    return prot.total_days() == 2


def test_protocol_add_many_steps_total_days():
    prot = ProtocolLinkedList()
    total = 0
    for i in range(10):
        total += i
        prot.add_step(Step("step", i))
    return prot.total_days() == total


def test_protocol_add_sdstep_total_days():
    prot = ProtocolLinkedList()
    prot.add_step(SDStep("1", 2))
    return prot.total_days() == 2


def test_protocol_add_many_sdssteps_total_days():
    prot = ProtocolLinkedList()
    total = 0
    for i in range(10):
        total += i
        prot.add_step(SDStep("step", i))
    return prot.total_days() == total


def test_protocol_add_rsdstep_total_days():
    prot = ProtocolLinkedList()
    prot.add_step(RSDStep("1",2))
    return prot.total_days() == 2


def test_protocol_add_many_rsdssteps_total_days():
    prot = ProtocolLinkedList()
    total = 0
    for i in range(10):
        total += i
        prot.add_step(RSDStep("step", i))
    return prot.total_days() == total


def test_protocol_add_tdstep_total_days():
    prot = ProtocolLinkedList()
    prot.add_step(TDStep("1", 2))
    return prot.total_days() == 2


def test_protocol_add_many_tdssteps_total_days():
    prot = ProtocolLinkedList()
    total = 0
    for i in range(10):
        total += i
        prot.add_step(TDStep("step", i))
    return prot.total_days() == total

