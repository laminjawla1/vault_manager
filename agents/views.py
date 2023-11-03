from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import *
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import redirect, render

from vault_manager.models import Deposit, Account

from .forms import CreditMyCashierForm, ProfileUpdateForm, UserUpdateForm, ReturnCashierAccountForm
from .models import Branch, Zone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import datetime


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
    profile_form = ProfileUpdateForm(instance=request.user.profile) 
    route = 'agents/profile.html' if request.user.profile.is_cashier else 'agents/admin/profile.html'
    return render(request, route, {
        'user_form': UserUpdateForm(instance=request.user), 'profile_form': profile_form
    })

@login_required
def all_agents(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    return render(request, "agents/all_agents.html", {
        'agents': User.objects.filter(Q(profile__is_supervisor=True) | Q(profile__is_cashier=True))
    })


@login_required
def zones(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    zones = Zone.objects.all().order_by('name').exclude(name="Head Office")

    total_op = Zone.objects.all().aggregate(Sum('supervisor__profile__opening_cash')).get('supervisor__profile__opening_cash__sum')
    total_ad = Zone.objects.all().aggregate(Sum('supervisor__profile__additional_cash')).get('supervisor__profile__additional_cash__sum')
    total_cs = Zone.objects.all().aggregate(Sum('supervisor__profile__closing_balance')).get('supervisor__profile__closing_balance__sum')

    return render(request, "agents/zones.html", {
        'zones': zones, 'total_op': total_op, 'total_ad': total_ad, 'total_cs': total_cs
    })


@login_required
def branches(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    branches = Branch.objects.all().order_by('name')
    return render(request, "agents/branches.html", {
        'branches': branches, 'form': ReturnCashierAccountForm
    })


@login_required
def my_branches(request):
    if not request.user.profile.is_supervisor:
        raise PermissionDenied()
    total_op = Branch.objects.filter(teller__profile__zone__supervisor__username=request.user.username).\
            aggregate(Sum('teller__profile__opening_cash')).get('teller__profile__opening_cash__sum')
    total_ad = Branch.objects.filter(teller__profile__zone__supervisor__username=request.user.username).\
            aggregate(Sum('teller__profile__additional_cash')).get('teller__profile__additional_cash__sum')
    total_cs = Branch.objects.filter(teller__profile__zone__supervisor__username=request.user.username).\
            aggregate(Sum('teller__profile__closing_balance')).get('teller__profile__closing_balance__sum')
    
    branches = Branch.objects.filter(teller__profile__zone=request.user.profile.zone).order_by('name')
    return render(request, "agents/my_branches.html", {
        'branches': branches, 'total_op': total_op, 'total_ad': total_ad, 'total_cs': total_cs,
    })

@login_required
def branches_under(request, username):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    total_op = Branch.objects.filter(teller__profile__zone__supervisor__username=username).\
            aggregate(Sum('teller__profile__opening_cash')).get('teller__profile__opening_cash__sum')
    total_ad = Branch.objects.filter(teller__profile__zone__supervisor__username=username).\
            aggregate(Sum('teller__profile__additional_cash')).get('teller__profile__additional_cash__sum')
    total_cs = Branch.objects.filter(teller__profile__zone__supervisor__username=username).\
            aggregate(Sum('teller__profile__closing_balance')).get('teller__profile__closing_balance__sum')
    
    branches = Branch.objects.filter(teller__profile__zone__supervisor__username=username).order_by('name')
    return render(request, "agents/branches_under.html", {
        'branches': branches, 'caption': f'Branches Under {username}',
        'total_op': total_op, 'total_ad': total_ad, 'total_cs': total_cs
    })

@login_required
def my_deposits(request):
    if not request.user.profile.is_supervisor:
        raise PermissionDenied()
    form = CreditMyCashierForm(request.user.profile.zone)
    if request.method == 'POST':
        form = CreditMyCashierForm(request.user.profile.zone, request.POST)
        if form.is_valid():
            form.instance.account = Account.objects.filter(name="Main Vault").first()
            if request.user.profile.balance - form.instance.amount >= 0:
                request.user.profile.balance -= form.instance.amount
                request.user.profile.save()
            else:
                messages.error(request, "Insufficient Fund 😥")
                return HttpResponseRedirect(reverse('my_deposits'))
            form.instance.cashier = True
            messages.success(request, "Agent's account credited successfully 😊")
            form.save()
        return HttpResponseRedirect(reverse('my_deposits'))
    zone = request.user.profile.zone
    return render(request, "agents/my_deposits.html", {
        'deposits': Deposit.objects.filter(cashier=True, agent__profile__zone=zone), 'form': form
    })