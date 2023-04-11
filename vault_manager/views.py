from .models import (MainVault, ZoneVault, Account, Withdraw, Deposit, Refund, Borrow, CurrencyTransaction)
from agents.models import Movement
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from datetime import datetime
from django.contrib.auth.models import User
from agents.models import Branch, Zone
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import CreateView, UpdateView
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .utils import gmd
import csv
import os

@login_required
def index(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return HttpResponseRedirect(reverse('reports'))

@login_required
def dashboard(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    account = Account.objects.filter(name='Main Vault').first()
    opening_cash = Deposit.objects.filter(
                    date__year=timezone.now().year, date__month=timezone.now().month, date__day=timezone.now().day,
                    supervisor=True, deposit_type="Opening Cash"
                    ).aggregate(Sum('amount')).get('amount__sum')
    if not opening_cash:
        opening_cash = 0

    additional_cash = Deposit.objects.filter(
                    date__year=datetime.now().year, date__month=datetime.now().month, date__day=datetime.now().day,
                    supervisor=True, deposit_type="Additional Cash"
                    ).aggregate(Sum('amount')).get('amount__sum')
    if not additional_cash:
        additional_cash = 0

    users = len(User.objects.all())
    zone_cnt = len(Zone.objects.all())

    page = request.GET.get('page', 1)
    zones = Zone.objects.all().order_by('name')
    paginator = Paginator(zones, 3)
    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    branches = len(Branch.objects.all())
    t_withdrawals = len(
        Withdraw.objects.filter(date__year=datetime.now().year, date__month=datetime.now().month, date__day=datetime.now().day).all())
    withdrawals_amount = Withdraw.objects.filter(date__year=datetime.now().year, date__month=datetime.now().month, 
                                                 date__day=datetime.now().day).all().aggregate(Sum('amount')).get('amount__sum')
    if not withdrawals_amount:
        withdrawals_amount = 0

    t_borrows = len(
        Borrow.objects.filter(date__year=datetime.now().year, date__month=datetime.now().month, date__day=datetime.now().day).all())
    borrow_amount = Borrow.objects.filter(date__year=datetime.now().year, date__month=datetime.now().month, 
                                                 date__day=datetime.now().day).all().aggregate(Sum('amount')).get('amount__sum')
    if not borrow_amount:
        borrow_amount = 0

    deposit_amount = Deposit.objects.filter(date__year=datetime.now().year, date__month=datetime.now().month, 
                                                 date__day=datetime.now().day).all().aggregate(Sum('amount')).get('amount__sum')
    if not deposit_amount:
        deposit_amount = 0
        
    deposits = len(Deposit.objects.filter(date__year=datetime.now().year, date__month=datetime.now().month, date__day=datetime.now().day).all())
    s_reports = len(MainVault.objects.all())
    c_reports =  len(ZoneVault.objects.all())
    return render(request, "vault/dashboard.html", {
        'account': account, 'users': users, 'zone_cnt': zone_cnt, 'branches': branches, 't_withdrawals': t_withdrawals, 
        'withdrawals_amount': withdrawals_amount, 'deposits': deposits, 'opening_cash': opening_cash, 'additional_cash': additional_cash,
        'deposit_amount': deposit_amount, 'zones': paginator, 's_reports': s_reports, 'c_reports': c_reports, 'borrow_amount': borrow_amount,
        't_borrows': t_borrows
    })
    
@login_required
def cashier_deposits(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    deposits = Deposit.objects.filter(cashier=True).all().order_by('-date')
    page = request.GET.get('page', 1)

    paginator = Paginator(deposits, 8)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/cashier_deposits.html", {
        'deposits': paginator
    })

@login_required
def supervisor_deposits(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    deposits = Deposit.objects.filter(supervisor=True).all().order_by('-date')
    page = request.GET.get('page', 1)

    paginator = Paginator(deposits, 8)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/supervisor_deposits.html", {
        'deposits': paginator
    })

@login_required
def refunds(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    refunds = Refund.objects.all().order_by('-date')
    page = request.GET.get('page', 1)

    paginator = Paginator(refunds, 8)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/refunds.html", {
        'refunds': paginator
    })

@login_required
def vault_log(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    logs = Movement.objects.all().order_by('-date')
    page = request.GET.get('page', 1)

    paginator = Paginator(logs, 10)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/vault_log.html", {
        'logs': paginator
    })

@login_required
def accounts(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    accounts = Account.objects.all().order_by('-date')
    page = request.GET.get('page', 1)

    paginator = Paginator(accounts, 10)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/vault_accounts.html", {
        'accounts': paginator
    })

@login_required
def withdrawals(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    withdrawals = Withdraw.objects.all().order_by('-date')
    page = request.GET.get('page', 1)

    paginator = Paginator(withdrawals, 10)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/withdrawals.html", {
        'withdrawals': paginator
    })

@login_required
def borrows(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    borrows = Borrow.objects.all().order_by('-date')
    page = request.GET.get('page', 1)

    paginator = Paginator(borrows, 10)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/borrows.html", {
        'borrows': paginator
    })

@login_required
def currency_transactions(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    transactions = CurrencyTransaction.objects.all().order_by('-date')
    page = request.GET.get('page', 1)

    paginator = Paginator(transactions, 10)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/currency_transactions.html", {
        'transactions': paginator
    })

@login_required
def my_withdrawals(request):
    if request.user.is_staff or request.user.profile.is_supervisor:
        withdrawals = Withdraw.objects.filter(withdrawer=request.user).all().order_by('-date')
        page = request.GET.get('page', 1)

        paginator = Paginator(withdrawals, 10)

        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)

        return render(request, "vault/my_withdrawals.html", {
            'withdrawals': paginator
        })
    raise PermissionDenied()

@login_required
def my_borrows(request):
    if request.user.is_staff or request.user.profile.is_supervisor:
        borrows = Borrow.objects.filter(borrower=request.user).all().order_by('-date')
        page = request.GET.get('page', 1)

        paginator = Paginator(borrows, 10)

        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)

        return render(request, "vault/my_borrows.html", {
            'borrows': paginator
        })
    raise PermissionDenied()


@login_required
def reports(request):
    if request.user.profile.is_supervisor:
        reports = MainVault.objects.filter(reporter=request.user).all().order_by('-date')
        page = request.GET.get('page', 1)
        paginator = Paginator(reports, 8)

        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)
        return render(request, "vault/s_reports.html", {
            'reports': paginator
        })
    elif request.user.profile.is_cashier:
        reports = ZoneVault.objects.filter(reporter=request.user).all().order_by('-date')
        page = request.GET.get('page', 1)
        paginator = Paginator(reports, 8)

        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)
        return render(request, "vault/c_reports.html", {
            'reports': paginator
        })
    raise PermissionDenied()


@login_required
def daily_supervisor_reports(request):
    if request.user.is_staff:
        reports = MainVault.objects.all().order_by('-date')
        page = request.GET.get('page', 1)
        paginator = Paginator(reports, 8)

        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)
        return render(request, "vault/supervisor_reports.html", {
            'reports': paginator
        })
    raise PermissionDenied()


@login_required
def daily_cashier_reports(request):
    if request.user.is_staff:
        reports = ZoneVault.objects.all().order_by('-date')
        page = request.GET.get('page', 1)
        paginator = Paginator(reports, 8)

        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)
        return render(request, "vault/cashier_reports.html", {
            'reports': paginator
        })
    raise PermissionDenied()


class CreditSupervisorAccount(LoginRequiredMixin, CreateView):
    model = Deposit
    template_name = "vault/deposit_form.html"
    fields = ['agent', 'deposit_type', 'amount', 'account']

    def form_valid(self, form):
        if form.instance.account.balance - form.instance.amount < 0:
            messages.error(self.request, "Insufficient Fund 😥")
            return HttpResponseRedirect('credit_supervisor')
        form.instance.supervisor = True

        send_mail(
            'Credit Supervisor Account',
            f'{self.request.user.first_name} {self.request.user.last_name} credited {form.instance.agent.first_name} {form.instance.agent.last_name}\'s account with {gmd(form.instance.amount)}.', 
            'yonnatech.g@gmail.com',
            [os.environ.get('send_email_to', 'ljawla@yonnaforexbureau.com')],
            fail_silently=False,
        )
        movement = Movement(name=self.request.user,
                            action=f"Credited {form.instance.agent.username}'s account with {gmd(form.instance.amount)}.")
        movement.save()
        account = get_object_or_404(Account, id=form.instance.account.id)
        account.balance -= form.instance.amount
        account.save()
        messages.success(self.request, "Agent's account credited successfully 😊")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        context = super(CreditSupervisorAccount, self).get_context_data(*args, **kwargs)
        context['button'] = 'Credit'
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['agent'].queryset = User.objects.filter(profile__is_supervisor=True).exclude(id=self.request.user.id)
        return form

class UpdateSupervisorAccount(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Deposit
    template_name = "vault/deposit_form.html"
    fields = ['agent', 'deposit_type', 'amount', 'account']

    def form_valid(self, form):
        movement = Movement(name=self.request.user,
                            action=f"Updated the deposit of {form.instance.agent.username}. Amount: {gmd(form.instance.amount)}.")
        movement.save()
        messages.success(self.request, "Deposit updated successfully.")
        return super().form_valid(form)
    
    
    def test_func(self):
        deposit = self.get_object()
        return not deposit.status
    
    def get_context_data(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        context = super(UpdateSupervisorAccount, self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        return context


class CreditCashierAccount(LoginRequiredMixin, CreateView):
    model = Deposit
    template_name = "vault/deposit_form.html"
    fields = ['agent', 'deposit_type', 'amount']

    def form_valid(self, form):
        form.instance.account = Account.objects.filter(name="Main Vault").first()
        if form.instance.deposit_type == "Opening Cash":
            if self.request.user.profile.opening_cash - form.instance.amount < 0:
                if self.request.user.profile.additional_cash - form.instance.amount >= 0:
                    self.request.user.profile.opening_cash -= form.instance.amount
                    self.request.user.profile.save()
                else:
                    messages.error(self.request, "Insufficient Fund 😥")
                    return HttpResponseRedirect(reverse('my_deposits'))
            else:
                self.request.user.profile.opening_cash -= form.instance.amount
                self.request.user.profile.save()
        else:
            if self.request.user.profile.additional_cash - form.instance.amount < 0:
                if self.request.user.profile.opening_cash - form.instance.amount >= 0:
                    self.request.user.profile.opening_cash -= form.instance.amount
                    self.request.user.profile.save()
                else:
                    messages.error(self.request, "Insufficient Fund 😥")
                    return HttpResponseRedirect(reverse('my_deposits'))
            else:
                self.request.user.profile.additional_cash -= form.instance.amount
                self.request.user.profile.save()
                
        form.instance.cashier = True
        movement = Movement(name=self.request.user,
                            action=f"Credited {form.instance.agent.username}'s account with {gmd(form.instance.amount)}.")
        movement.save()
        send_mail(
            'Credit Cashier Account',
            f'{self.request.user.first_name} {self.request.user.last_name} credited {form.instance.agent.first_name} {form.instance.agent.last_name}\'s account with {gmd(form.instance.amount)}.', 
            'yonnatech.g@gmail.com',
            [os.environ.get('send_email_to', 'ljawla@yonnaforexbureau.com')],
            fail_silently=False,
        )
        self.request.user.profile.save()
        messages.success(self.request, "Agent's account credited successfully 😊")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.profile.is_supervisor:
            raise PermissionDenied()
        context = super(CreditCashierAccount, self).get_context_data(*args, **kwargs)
        context['button'] = 'Credit'
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['agent'].queryset = User.objects.filter(profile__is_cashier=True, 
                                                            profile__zone=self.request.user.profile.zone).exclude(id=self.request.user.id)
        return form

class UpdateCashierAccount(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Deposit
    template_name = "vault/deposit_form.html"
    fields = ['agent', 'deposit_type', 'amount', 'account']

    def form_valid(self, form):
        movement = Movement(name=self.request.user,
                            action=f"Updated the deposit of {form.instance.agent.username}. Amount: {gmd(form.instance.amount)}.")
        movement.save()
        messages.success(self.request, "Deposit updated successfully.")
        return super().form_valid(form)
    
    
    def test_func(self):
        deposit = self.get_object()
        return not deposit.status
    
    def get_context_data(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        context = super(UpdateCashierAccount, self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        return context
    
@login_required
def approve_cashier_deposit(request):
    if request.method == "POST":
        deposit = get_object_or_404(Deposit, id=request.POST["id"])
        deposit.status = True
        if deposit.deposit_type == "Opening Cash":
            deposit.agent.profile.cash += deposit.amount
            deposit.agent.profile.opening_cash += deposit.amount
        else:
            deposit.agent.profile.additional_cash += deposit.amount
            deposit.agent.profile.add_cash += deposit.amount
        movement = Movement(name=request.user,
                            action=f"Approved {deposit.agent.username}'s deposit of {gmd(deposit.amount)}")
        deposit.agent.profile.closing_balance = 0
        deposit.agent.profile.has_return = False
        movement.save()
        deposit.agent.profile.save()
        deposit.save()
        messages.success(request, "Deposit Approved")
        return HttpResponseRedirect(reverse('cashier_deposits'))
    
@login_required
def approve_cashier_report(request):
    if request.method == "POST":
        report = get_object_or_404(ZoneVault, id=request.POST["id"])
        report.status = True
        report.reporter.profile.cash = 0
        report.reporter.profile.add_cash = 0
        report.reporter.profile.opening_cash = 0
        report.reporter.profile.additional_cash = 0
        report.reporter.profile.has_return = True
        report.reporter.profile.closing_balance = report.closing_balance

        movement = Movement(name=request.user,
                            action=f"Approved {report.reporter.username}'s report")
        movement.save()
        report.reporter.profile.save()
        report.save()
        messages.success(request, "Report Approved")
        return HttpResponseRedirect(reverse('daily_cashier_reports'))
    
@login_required
def approve_supervisor_report(request):
    if request.method == "POST":
        report = get_object_or_404(MainVault, id=request.POST["id"])
        report.status = True
        report.reporter.profile.cash = 0
        report.reporter.profile.add_cash = 0
        report.reporter.profile.opening_cash = 0
        report.reporter.profile.additional_cash = 0
        report.reporter.profile.has_return = True

        account = Account.objects.filter(name="Main Vault").first()
        if account:
            account.balance += report.closing_balance
            account.save()
        else:
            messages.error(request, "Couldn't find the Main Vault Account")
            return HttpResponseRedirect("accounts")
        
        report.reporter.profile.closing_balance = report.closing_balance
        
        movement = Movement(name=request.user,
                            action=f"Approved {report.reporter.username}'s report")
        movement.save()
        report.reporter.profile.save()
        report.save()
        messages.success(request, "Report Approved")
        return HttpResponseRedirect(reverse('daily_supervisor_reports'))

@login_required
def approve_supervisor_deposit(request):
    if request.method == "POST":
        deposit = get_object_or_404(Deposit, id=request.POST["id"])
        deposit.status = True
        if deposit.deposit_type == "Opening Cash":
            deposit.agent.profile.cash += deposit.amount
            deposit.agent.profile.opening_cash += deposit.amount
        else:
            deposit.agent.profile.additional_cash += deposit.amount
            deposit.agent.profile.add_cash += deposit.amount
        movement = Movement(name=request.user,
                            action=f"Approved {deposit.agent.username}'s deposit of {gmd(deposit.amount)}")
        movement.save()
        deposit.agent.profile.save()
        deposit.save()
        deposit.agent.profile.closing_balance = 0
        deposit.agent.profile.has_return = False
        messages.success(request, "Deposit Approved")
        return HttpResponseRedirect(reverse('supervisor_deposits'))

@login_required
def approve_withdrawal_request(request):
    if request.method == "POST":
        withdrawal = get_object_or_404(Withdraw, id=request.POST["id"])
        withdrawal.status = True
        withdrawal.account.balance += withdrawal.amount
        withdrawal.save()
        withdrawal.account.save()
        movement = Movement(name=request.user, action=f"Approved {withdrawal.withdrawer.username}'s \
                             withdrawal request of {gmd(withdrawal.amount)}")
        movement.save()
        messages.success(request, "Withdrawal Accepted")
        return HttpResponseRedirect(reverse('withdrawals'))

@login_required
def approve_borrow_request(request):
    if request.method == "POST":
        borrow = get_object_or_404(Borrow, id=request.POST["id"])
        borrow.status = True
        borrow.account.balance += borrow.amount
        borrow.save()
        borrow.account.save()
        movement = Movement(name=request.user, action=f"Approved {borrow.borrower.username}'s \
                             borrow request of {gmd(borrow.amount)}")
        movement.save()
        messages.success(request, "Borrow Accepted")
        return HttpResponseRedirect(reverse('borrows'))

@login_required
def disapprove_withdrawal_request(request):
    if request.method == "POST":
        withdrawal = get_object_or_404(Withdraw, id=request.POST["id"])
        withdrawal.delete()
        movement = Movement(name=request.user, action=f"Disapproved {withdrawal.withdrawer.username}'s \
                             withdrawal request of {gmd(withdrawal.amount)}")
        movement.save()
        messages.success(request, "Withdrawal Rejected 😔")
        return HttpResponseRedirect(reverse('withdrawals'))

@login_required
def disapprove_borrow_request(request):
    if request.method == "POST":
        borrow = get_object_or_404(Borrow, id=request.POST["id"])
        borrow.delete()
        movement = Movement(name=request.user, action=f"Disapproved {borrow.borrower.username}'s \
                             borrow request of {gmd(borrow.amount)}")
        movement.save()
        messages.success(request, "Borrow Rejected 😔")
        return HttpResponseRedirect(reverse('borrows'))


class RefundAgent(LoginRequiredMixin, CreateView):
    model = Refund
    template_name = "vault/refund_form.html"
    fields = ['refund_type', 'agent', 'amount']

    def form_valid(self, form):
        if form.instance.refund_type == "Add to Opening Cash":
            form.instance.agent.profile.cash += form.instance.amount
            form.instance.agent.profile.opening_cash += form.instance.amount
        elif form.instance.refund_type == "Add to Additional Cash":
            form.instance.agent.profile.add_cash += form.instance.amount
            form.instance.agent.profile.additional_cash += form.instance.amount
        elif form.instance.refund_type == "Deduct from Opening Cash":
            if form.instance.agent.profile.opening_cash - form.instance.amount >= 0:
                form.instance.agent.profile.cash -= form.instance.amount
                form.instance.agent.profile.opening_cash -= form.instance.amount
            else:
                messages.error(self.request, "The amount is not available in the agents account")
                return HttpResponseRedirect("refund")
        else:
            if form.instance.agent.profile.additional_cash - form.instance.amount >= 0:
                form.instance.agent.profile.add_cash -= form.instance.amount
                form.instance.agent.profile.additional_cash -= form.instance.amount
            else:
                messages.error(self.request, "The amount is not available in the agents account")
                return HttpResponseRedirect("refund")
        messages.success(self.request, "Agent's account refunded successfully")
        movement = Movement(name=self.request.user, action=f"Refunded {form.instance.agent.username}'s account with a refund type of \
                            {form.instance.refund_type} of amount {gmd(form.instance.amount)}.")
        movement.save()
        form.instance.agent.profile.save()
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        context = super(RefundAgent, self).get_context_data(*args, **kwargs)
        context['button'] = 'Refund'
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['agent'].queryset = User.objects.all().exclude(is_staff=True)
        return form


class WithdrawCash(LoginRequiredMixin, CreateView):
    model = Withdraw
    template_name = "vault/withdraw_form.html"
    fields = ['bank', 'cheque_number', 'amount', 'account', 'comment']

    def form_valid(self, form):
        form.instance.withdrawer = self.request.user
        movement = Movement(name=self.request.user, action=f"Sent a withdrawal request of amount {gmd(form.instance.amount)}.")
        movement.save()

        send_mail(
            'Cash Withdrawal Request',
            f'{self.request.user.first_name} {self.request.user.last_name} sent a withdrawal request of {gmd(form.instance.amount)}.', 
            'yonnatech.g@gmail.com',
            [os.environ.get('send_email_to', 'ljawla@yonnaforexbureau.com')],
            fail_silently=False,
        )
        messages.success(self.request, "Cash withdrawal request is sent successfully")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        if self.request.user.is_staff or self.request.user.profile.is_supervisor:
            context = super(WithdrawCash, self).get_context_data(*args, **kwargs)
            context['button'] = 'Withdraw'
            context['legend'] = 'Withdraw Cash'
            return context
        raise PermissionDenied()


class BorrowCash(LoginRequiredMixin, CreateView):
    model = Borrow
    template_name = "vault/withdraw_form.html"
    fields = ['customer_name', 'address', 'phone', 'amount', 'account']

    def form_valid(self, form):
        form.instance.borrower = self.request.user
        movement = Movement(name=self.request.user, action=f"Sent a borrow request of amount {gmd(form.instance.amount)}.")
        movement.save()

        send_mail(
            'Cash Borrow Request',
            f'{self.request.user.first_name} {self.request.user.last_name} sent a borrow request of {gmd(form.instance.amount)}.', 
            'yonnatech.g@gmail.com',
            [os.environ.get('send_email_to', 'ljawla@yonnaforexbureau.com')],
            fail_silently=False,
        )
        messages.success(self.request, "Cash borrow request is sent successfully")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        if self.request.user.is_staff or self.request.user.profile.is_supervisor:
            context = super(BorrowCash, self).get_context_data(*args, **kwargs)
            context['button'] = 'Borrow'
            context['legend'] = 'Borrow Cash'
            return context
        raise PermissionDenied()


class UpdateWithdrawCash(LoginRequiredMixin, UpdateView):
    model = Withdraw
    template_name = "vault/withdraw_form.html"
    fields = ['bank', 'cheque_number', 'amount', 'account', 'comment']

    def form_valid(self, form):
        movement = Movement(name=self.request.user, action=f"Updated the withdrawal request of \
                            {form.instance.withdrawer.username}. Amount: {gmd(form.instance.amount)}.")
        movement.save()
        messages.success(self.request, "Withdrawal request updated successfully.")
        return super().form_valid(form)
    
    
    def test_func(self):
        withdrawal = self.get_object()
        return not withdrawal.status
    
    def get_context_data(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        context = super(UpdateWithdrawCash, self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        context['legend'] = 'Update Withdraw Cash'
        return context


class UpdateBorrowCash(LoginRequiredMixin, UpdateView):
    model = Borrow
    template_name = "vault/withdraw_form.html"
    fields = ['customer_name', 'address', 'phone', 'amount', 'account']

    def form_valid(self, form):
        movement = Movement(name=self.request.user, action=f"Updated the borrow request of \
                            {form.instance.borrower.username}. Amount: {gmd(form.instance.amount)}.")
        movement.save()
        messages.success(self.request, "Borrow request updated successfully.")
        return super().form_valid(form)
    
    
    def test_func(self):
        borrow = self.get_object()
        return not borrow.status
    
    def get_context_data(self, *args, **kwargs):
        if self.request.user.is_staff or self.request.user.profile.is_supervisor:
            context = super(UpdateBorrowCash, self).get_context_data(*args, **kwargs)
            context['button'] = 'Update'
            context['legend'] = 'Update Cash Borrowed'
            return context
        raise PermissionDenied()


class SupervisorReporting(LoginRequiredMixin, CreateView):
    model = MainVault
    template_name = "vault/daily_report_form.html"
    fields = ['opening_cash', 'additional_cash', 'closing_balance']

    def form_valid(self, form):
        if self.request.user.profile.has_return:
            messages.error(self.request, "You have already submitted your report")
            return HttpResponseRedirect(reverse("reports"))
        form.instance.reporter = self.request.user
        form.instance.zone = self.request.user.profile.zone

        send_mail(
            'Daily Supervisor Report',
            f'{self.request.user.first_name} {self.request.user.last_name} sent his daily report', 
            'yonnatech.g@gmail.com',
            [os.environ.get('send_email_to', 'ljawla@yonnaforexbureau.com')],
            fail_silently=False,
        )
        messages.success(self.request, "Your daily report have been submitted successfully")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.profile.is_supervisor:
            raise PermissionDenied()
        context = super(SupervisorReporting, self).get_context_data(*args, **kwargs)
        context['button'] = 'Send'
        return context
    


class UpdateSupervisorReporting(LoginRequiredMixin, UserPassesTestMixin,UpdateView):
    model = MainVault
    template_name = "vault/daily_report_form.html"
    fields = ['opening_cash', 'additional_cash', 'closing_balance']

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        form.instance.zone = self.request.user.profile.zone
        messages.success(self.request, "Daily Report Updated Successfully")
        return super().form_valid(form)
    
    def test_func(self):
        report = self.get_object()
        return not report.status

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.profile.is_supervisor:
            raise PermissionDenied()
        context = super(UpdateSupervisorReporting, self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        return context
    


class CashierReporting(LoginRequiredMixin, CreateView):
    model = ZoneVault
    template_name = "vault/daily_report_form.html"
    fields = ['cashier_name', 'opening_cash', 'additional_cash', 'closing_balance']
    # fields = ['location', 'opening_cash', 'additional_cash', 'closing_balance', 'euro', 'us_dollar', 'gbp_pound', 
    #           'swiss_krona', 'nor_krona', 'swiss_franck', 'cfa', 'denish_krona', 'cad_dollar']

    def form_valid(self, form):
        if self.request.user.profile.has_return:
            messages.error(self.request, "You have already submitted your report")
            return HttpResponseRedirect(reverse("reports"))
        form.instance.reporter = self.request.user
        form.instance.branch = self.request.user.profile.branch
        form.instance.zone = self.request.user.profile.zone

        send_mail(
            'Daily Cashier Report',
            f'{self.request.user.first_name} {self.request.user.last_name} sent his daily report', 
            'yonnatech.g@gmail.com',
            [os.environ.get('send_email_to', 'ljawla@yonnaforexbureau.com')],
            fail_silently=False,
        )
        messages.success(self.request, "Your daily report have been submitted successfully")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.profile.is_cashier:
            raise PermissionDenied()
        context = super(CashierReporting, self).get_context_data(*args, **kwargs)
        context['button'] = 'Send'
        return context
    
class ReturnCashierAccount(LoginRequiredMixin, CreateView):
    model = ZoneVault
    template_name = "vault/daily_report_form.html"
    fields = ['cashier_name', 'reporter', 'opening_cash', 'additional_cash', 'closing_balance']
    # fields = ['location', 'reporter', 'opening_cash', 'additional_cash', 'closing_balance', 'euro', 'us_dollar', 'gbp_pound', 
    #           'swiss_krona', 'nor_krona', 'swiss_franck', 'cfa', 'denish_krona', 'cad_dollar']

    def form_valid(self, form):
        if form.instance.reporter.profile.has_return:
            messages.error(self.request, f"You have already submitted {form.instance.reporter.username}'s report")
            return HttpResponseRedirect(reverse("reports"))
        form.instance.branch = form.instance.reporter.profile.branch
        form.instance.zone = form.instance.reporter.profile.zone

        send_mail(
            'Daily Cashier Report',
            f'{self.request.user.first_name} {self.request.user.last_name} sent his daily report', 
            'yonnatech.g@gmail.com',
            [os.environ.get('send_email_to', 'ljawla@yonnaforexbureau.com')],
            fail_silently=False,
        )
        messages.success(self.request, "Your daily report have been submitted successfully")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        if (not self.request.user.profile.is_supervisor) and (not self.request.user.is_staff):
            raise PermissionDenied()
        context = super(ReturnCashierAccount, self).get_context_data(*args, **kwargs)
        context['button'] = 'Send'
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['reporter'].queryset = User.objects.filter(profile__is_cashier=True, 
                                                            profile__zone=self.request.user.profile.zone).exclude(id=self.request.user.id)
        return form
    
class UpdateCashierReporting(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ZoneVault
    template_name = "vault/daily_report_form.html"
    fields = ['cashier_name', 'opening_cash', 'additional_cash', 'closing_balance']

    def form_valid(self, form):
        messages.success(self.request, "Daily Report Updated Successfully")
        return super().form_valid(form)
    
    def test_func(self):
        report = self.get_object()
        return not report.status

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateCashierReporting, self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        return context

class UpdateReturnCashierAccount(LoginRequiredMixin, UpdateView):
    model = ZoneVault
    template_name = "vault/daily_report_form.html"
    fields = ['cashier_name', 'reporter', 'opening_cash', 'additional_cash', 'closing_balance']

    def form_valid(self, form):
        messages.success(self.request, "Daily Report Updated Successfully")
        return super().form_valid(form)
    
    def test_func(self):
        report = self.get_object()
        return not report.status

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateReturnCashierAccount, self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        return context


def generate_cashier_report(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    cr = ZoneVault.objects.filter(date__year=timezone.now().year, date__month=timezone.now().month, 
                                  date__day=timezone.now().day).order_by("date")
    if not cr:
        messages.error(request, "No Cashier Reports Available For Export")
        return HttpResponseRedirect(reverse("dashboard"))

    headers  =["ZONE", "BRANCH", "TELLER", "OPENING CASH", "ADDITIONAL CASH", "TOTAL", "CLOSING BALANCE", "EURO", 
               "USD", "GBP", "CFA", "Swiss Krona", "Nor Krona", "Swiss Franck", "Denish Krona", "Cad Dollar", "DATE"]
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="cashier_reports.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(["DAILY CASHIER REPORTS"])
    writer.writerow(headers)
    for r in cr:
        writer.writerow((r.reporter.profile.zone.name, r.reporter.profile.branch.name, f'{r.reporter.first_name} {r.reporter.last_name}',
                                r.opening_cash, r.additional_cash, r.opening_cash + r.additional_cash, r.closing_balance,
                                r.euro, r.us_dollar, r.gbp_pound, r.cfa, r.swiss_krona, r.nor_krona, r.swiss_franck, r.denish_krona, 
                                r.cad_dollar, r.date.strftime("%Y-%m-%d")))
    return response

def generate_supervisor_report(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    cr = MainVault.objects.filter(date__year=timezone.now().year, date__month=timezone.now().month, 
                                  date__day=timezone.now().day).order_by("date")
    if not cr:
        messages.error(request, "No Supervisor Reports Available For Export")
        return HttpResponseRedirect(reverse("dashboard"))
    
    headers  =["ZONE", "SUPERVISOR", "OPENING CASH", "ADDITIONAL CASH", "TOTAL", "CLOSING BALANCE", "EURO", 
               "USD", "GBP", "CFA", "Swiss Krona", "Nor Krona", "Swiss Franck", "Denish Krona", "Cad Dollar", "STATUS", "DATE"]
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="supervisor_reports.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(["DAILY SUPERVISOR REPORTS"])
    writer.writerow(headers)
    for r in cr:
        writer.writerow((r.reporter.profile.zone.name, f'{r.reporter.first_name} {r.reporter.last_name}',
                                r.opening_cash, r.additional_cash, r.opening_cash + r.additional_cash, r.closing_balance,
                                r.euro, r.us_dollar, r.gbp_pound, r.cfa, r.swiss_krona, r.nor_krona, r.swiss_franck, r.denish_krona, 
                                r.status, r.cad_dollar, r.date.strftime("%Y-%m-%d")))
    return response

def generate_withdrawal_report(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    dw = Withdraw.objects.filter(date__year=timezone.now().year, date__month=timezone.now().month, 
                                  date__day=timezone.now().day).order_by("date")
    if not dw:
        messages.error(request, "No withdrawal Reports Available For Export")
        return HttpResponseRedirect(reverse("dashboard"))
    headers  =["AGENT FULLNAME", "ZONE", "BANK", "CHEQUE NUMBER", "AMOUNT", "STATUS", "COMMENT", "DATE"]
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="withdrawal_reports.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(["DAILY WITHDRAWAL REPORTS"])
    writer.writerow(headers)
    for w in dw:
        writer.writerow((f'{w.withdrawer.first_name} {w.withdrawer.last_name}', w.withdrawer.profile.zone.name, w.bank, w.cheque_number,
                          w.amount, w.status, w.comment, w.date.strftime("%Y-%m-%d")))

    return response

def generate_cashier_deposit_report(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    cd = Deposit.objects.filter(date__year=timezone.now().year, date__month=timezone.now().month, 
                                        date__day=timezone.now().day,
                                        cashier=True).order_by("date")
    if not cd:
        messages.error(request, "No cashier deposit reports is available for export")
        return HttpResponseRedirect(reverse('dashboard'))
    
    headers  =["ZONE", "BRANCH", "TELLER", "AMOUNT", "DEPOSIT TYPE", "STATUS", "DATE"]
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="withdrawal_reports.csv"'},
    )
    writer = csv.writer(response)
    writer = csv.writer(response)
    writer.writerow(["DAILY CASHIER DEPOSIT REPORTS"])
    writer.writerow(headers)
    for d in cd:
        writer.writerow((d.agent.profile.zone.name, d.agent.profile.branch.name, f'{d.agent.first_name} {d.agent.last_name}',
                         d.amount, d.deposit_type, d.status, d.date.strftime("%Y-%m-%d")))
    return response

def generate_supervisor_deposit_report(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    sd = Deposit.objects.filter(date__year=timezone.now().year, date__month=timezone.now().month, 
                                        date__day=timezone.now().day,
                                        supervisor=True).order_by("date")
    if not sd:
        messages.error(request, "No Supervisor Deposit Reports Available For Export")
        return HttpResponseRedirect(reverse("dashboard"))

    headers  =["ZONE", "SUPERVISOR", "AMOUNT", "DEPOSIT TYPE", "STATUS", "DATE"]
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="withdrawal_reports.csv"'},
    )
    writer = csv.writer(response)
    writer = csv.writer(response)
    writer.writerow(["DAILY SUPERVISOR DEPOSIT REPORTS"])
    writer.writerow(headers)
    for d in sd:
        writer.writerow((d.agent.profile.zone.name, f'{d.agent.first_name} {d.agent.last_name}',
                        d.amount, d.deposit_type, d.status, d.date.strftime("%Y-%m-%d")))
    return response


class CurrencyTransact(LoginRequiredMixin, CreateView):
    model = CurrencyTransaction
    template_name = "vault/currency_transact_form.html"
    fields = ['customer_name', 'phone_number', 'id_number', 'type', 'currency', 'currency_amount', 'rate', 'account']

    def form_valid(self, form):
        form.instance.agent = self.request.user
        form.instance.total_amount = form.instance.rate * form.instance.currency_amount
        if form.instance.type == "buy":
            if form.instance.account.balance - (form.instance.currency_amount * form.instance.rate) < 0:
                messages.error(self.request, "Insufficient Fund 😥")
                return HttpResponseRedirect(reverse('currency_transactions'))

        if form.instance.type == "buy":
            send_mail(
                'Currency Purchase',
                f'{self.request.user.first_name} {self.request.user.last_name} purchased {form.instance.currency_amount} {form.instance.currency} from {form.instance.customer_name} at {gmd(form.instance.total_amount)}.', 
                'yonnatech.g@gmail.com',
                [os.environ.get('send_email_to', 'ljawla@yonnaforexbureau.com')],
                fail_silently=False,
            )
        elif form.instance.type == "sell":
            send_mail(
                'Currency Sell',
                f'{self.request.user.first_name} {self.request.user.last_name} sold {form.instance.currency_amount} {form.instance.currency} to {form.instance.customer_name} at {gmd(form.instance.total_amount)}.', 
                'yonnatech.g@gmail.com',
                [os.environ.get('send_email_to', 'ljawla@yonnaforexbureau.com')],
                fail_silently=False,
            )
        else:
            messages.error(self.request, "Invalid transaction type")
            return HttpResponseRedirect('currency_transact')
            
        if form.instance.type == "buy":
            movement = Movement(name=self.request.user,
                            action=f'{self.request.user.first_name} {self.request.user.last_name} purchased {form.instance.currency_amount} {form.instance.currency} from {form.instance.customer_name} at {form.instance.rate}. Total: {gmd(form.instance.total_amount)}.')
        else:
            movement = Movement(name=self.request.user,
                            action=f'{self.request.user.first_name} {self.request.user.last_name} sold {form.instance.currency_amount} {form.instance.currency} to {form.instance.customer_name} at {form.instance.rate}. Total: {gmd(form.instance.total_amount)}.')
        movement.save()

        if form.instance.type == "buy":
            messages.success(self.request, "Currency bought successfully 😊")
        else:
            messages.success(self.request, "Currency sold successfully 😊")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        context = super(CurrencyTransact, self).get_context_data(*args, **kwargs)
        context['button'] = 'Process'
        return context

class UpdateCurrencyTransact(LoginRequiredMixin, UpdateView):
    model = CurrencyTransaction
    template_name = "vault/currency_transact_form.html"
    fields = ['customer_name', 'phone_number', 'id_number', 'type', 'currency', 'currency_amount', 'rate', 'account']

    def form_valid(self, form):
        movement = Movement(name=self.request.user,
                            action=f'Updated a currency transaction of {form.instance.currency_amount} {form.instance.currency} from {form.instance.customer_name} at {gmd(form.instance.total_amount)}.')
        movement.save()
        messages.success(self.request, "Deposit updated successfully.")
        return super().form_valid(form)
    
    
    def test_func(self):
        deposit = self.get_object()
        return not deposit.status
    
    def get_context_data(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        context = super(UpdateCurrencyTransact, self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        return context

@login_required
def disapprove_currency_transaction(request):
    if request.method == "POST":
        transaction = get_object_or_404(CurrencyTransaction, id=request.POST["id"])
        transaction.delete()
        movement = Movement(name=request.user, action=f"Disapproved {transaction.agent.username}'s \
                             currency transaction of {gmd(transaction.total_amount)}")
        movement.save()
        messages.success(request, "Transaction Disapproved 😔")
        return HttpResponseRedirect(reverse('currency_transactions'))

@login_required
def approve_currency_transaction(request):
    if request.method == "POST":
        transaction = get_object_or_404(CurrencyTransaction, id=request.POST["id"])
        transaction.status = True
        account = get_object_or_404(Account, id=transaction.account.id)
        if transaction.type == "buy":
            account.balance -= transaction.total_amount
        else:
            account.balance += transaction.total_amount
        transaction.save()
        account.save()
        movement = Movement(name=request.user, action=f"Approved {transaction.agent.username}'s \
                             currency transaction of {gmd(transaction.total_amount)}")
        movement.save()
        messages.success(request, "Transaction Approved")
        return HttpResponseRedirect(reverse('currency_transactions'))