from django.shortcuts import render, redirect
from django.contrib.auth.forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, UserUpdateForm
from vault_manager.models import Deposit
from .models import Zone, Branch
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Sum

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

    total_op = Zone.objects.all().aggregate(Sum('supervisor__profile__cash')).get('supervisor__profile__cash__sum')
    total_ad = Zone.objects.all().aggregate(Sum('supervisor__profile__add_cash')).get('supervisor__profile__add_cash__sum')
    total_cs = Zone.objects.all().aggregate(Sum('supervisor__profile__closing_balance')).get('supervisor__profile__closing_balance__sum')

    page = request.GET.get('page', 1)

    paginator = Paginator(zones, 12)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "agents/zones.html", {
        'zones': paginator, 'total_op': total_op, 'total_ad': total_ad, 'total_cs': total_cs
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
    
    total_op = Branch.objects.filter(teller__profile__zone__supervisor__username=request.user.username).\
            aggregate(Sum('teller__profile__opening_cash')).get('teller__profile__opening_cash__sum')
    total_ad = Branch.objects.filter(teller__profile__zone__supervisor__username=request.user.username).\
            aggregate(Sum('teller__profile__additional_cash')).get('teller__profile__additional_cash__sum')
    total_cs = Branch.objects.filter(teller__profile__zone__supervisor__username=request.user.username).\
            aggregate(Sum('teller__profile__closing_balance')).get('teller__profile__closing_balance__sum')
    
    branches = Branch.objects.filter(teller__profile__zone=request.user.profile.zone).order_by('name')
    page = request.GET.get('page', 1)
    paginator = Paginator(branches, 8)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "agents/my_branches.html", {
        'branches': paginator, 'total_op': total_op, 'total_ad': total_ad, 'total_cs': total_cs
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