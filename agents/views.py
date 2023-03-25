from django.shortcuts import render, redirect
from django.contrib.auth.forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, UserUpdateForm
from vault_manager.models import Deposit
from .models import Zone, Branch
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, "Profile updated successfully 😊")
            return redirect('profile')

    else:
       user_form = UserUpdateForm(instance=request.user)
       profile_form = ProfileUpdateForm(instance=request.user.profile) 

    return render(request, 'agents/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def zones(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    zones = Zone.objects.all().order_by('name')
    page = request.GET.get('page', 1)

    paginator = Paginator(zones, 12)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "agents/zones.html", {
        'zones': paginator
    })


@login_required
def branches(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    branches = Branch.objects.all().order_by('name')
    page = request.GET.get('page', 1)

    paginator = Paginator(branches, 12)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "agents/branches.html", {
        'branches': paginator
    })


@login_required
def my_branches(request):
    if not request.user.profile.is_supervisor:
        raise PermissionDenied()
    
    branches = Branch.objects.filter(teller__profile__zone=request.user.profile.zone).order_by('name')
    page = request.GET.get('page', 1)

    paginator = Paginator(branches, 8)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "agents/my_branches.html", {
        'branches': paginator
    })

@login_required
def my_deposits(request):
    if not request.user.profile.is_supervisor:
        raise PermissionDenied()
    
    deposits = Deposit.objects.filter(cashier=True, 
                                      agent__profile__zone=request.user.profile.zone).all().order_by('-date')
    page = request.GET.get('page', 1)

    paginator = Paginator(deposits, 8)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "agents/my_deposits.html", {
        'deposits': paginator
    })