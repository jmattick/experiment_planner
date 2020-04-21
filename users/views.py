from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm
from protocols.models import Protocol, Experiment


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created. You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Account is updated.')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    experiments = Experiment.objects.filter(created_by=request.user)
    protocols = Protocol.objects.filter(created_by=request.user)
    context = {
        'form': form,
        'experiments': experiments,
        'protocols': protocols
    }
    return render(request, 'users/profile.html', context)
