import csv
import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView

from agents.models import Branch, Zone
from django.shortcuts import redirect

from .forms import (UpdateVaultAccountForm, CreditSupervisorAccountForm, BankWithdrawalForm, 
                    ReturnCashierAccountForm, CashierReportingForm, BankDepositForm, SupervisorReportingForm,
                    CurrencyTransactionsForm, LoanForm, RefundAgentForm)
from .models import (Account, BankDeposit, Borrow, CurrencyTransaction,
                     Deposit, MainVault, Refund, Withdraw, ZoneVault)
from .utils import gmd
from django.db.models import Q


@login_required
def index(request):
    if request.user.is_staff or request.user.profile.is_supervisor:
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return HttpResponseRedirect(reverse('reports'))

@login_required
def dashboard(request):
    if not request.user.is_staff and not request.user.profile.is_supervisor:
        raise PermissionDenied()
    if request.user.is_staff:
        account = Account.objects.filter(name='Main Vault').first()
        opening_cash = Deposit.objects.filter(
                        date__year=timezone.now().year, date__month=timezone.now().month, date__day=timezone.now().day,
                        supervisor=True, deposit_type="Opening Cash"
                        ).aggregate(Sum('amount')).get('amount__sum') or 0
        additional_cash = Deposit.objects.filter(
                        date__year=datetime.now().year, date__month=datetime.now().month, date__day=datetime.now().day,
                        supervisor=True, deposit_type="Additional Cash"
                        ).aggregate(Sum('amount')).get('amount__sum') or 0
        users = User.objects.count()
        zone_cnt = Zone.objects.count()

        page = request.GET.get('page')
        zones = Zone.objects.all().order_by('name')
        paginator = Paginator(zones, 15)
        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)

        branches = Branch.objects.count()
        t_withdrawals = len(
            Withdraw.objects.filter(date__year=datetime.now().year, date__month=datetime.now().month, date__day=datetime.now().day).all())
        withdrawals_amount = Withdraw.objects.filter(date__year=datetime.now().year, date__month=datetime.now().month, 
                                                    date__day=datetime.now().day).all().aggregate(Sum('amount')).get('amount__sum') or 0
        t_borrows = len(
            Borrow.objects.filter(date__year=datetime.now().year, date__month=datetime.now().month, date__day=datetime.now().day).all())
        borrow_amount = Borrow.objects.filter(date__year=datetime.now().year, date__month=datetime.now().month, 
                                                    date__day=datetime.now().day).all().aggregate(Sum('amount')).get('amount__sum') or 0
        deposit_amount = Deposit.objects.filter(date__year=datetime.now().year, date__month=datetime.now().month, 
                                                    date__day=datetime.now().day).all().aggregate(Sum('amount')).get('amount__sum') or 0
        deposits = Deposit.objects.filter(
            date__year=datetime.now().year,
            date__month=datetime.now().month,
            date__day=datetime.now().day,
            supervisor=True
        ).count()
        return render(request, "vault/admin/admin_dashboard.html", {
            'account': account, 'users': users, 'zone_cnt': zone_cnt, 'branches': branches, 't_withdrawals': t_withdrawals, 
            'withdrawals_amount': withdrawals_amount, 'deposits': deposits, 'opening_cash': opening_cash, 'additional_cash': additional_cash,
            'deposit_amount': deposit_amount, 'zones': paginator, 'loan_amount': borrow_amount,
            't_loans': t_borrows, 'current_date' : datetime.now()
        })
    elif request.user.profile.is_supervisor:
        opening_cash = Deposit.objects.filter(
                        date__year=timezone.now().year, date__month=timezone.now().month, date__day=timezone.now().day,
                        supervisor=True, deposit_type="Opening Cash"
                        ).aggregate(Sum('amount')).get('amount__sum') or 0
        additional_cash = Deposit.objects.filter(
                        date__year=datetime.now().year, date__month=datetime.now().month, date__day=datetime.now().day,
                        supervisor=True, deposit_type="Additional Cash"
                        ).aggregate(Sum('amount')).get('amount__sum') or 0
        branches = Branch.objects.filter(teller__profile__zone__supervisor=request.user).order_by('name')
        total_branches = branches.count()

        page = request.GET.get('page', 1)
        paginator = Paginator(branches, 15)
        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)
        return render(request, "vault/admin/supervisor_dashboard.html", {
            'opening_cash': opening_cash, 'additional_cash': additional_cash, 'branches': paginator, 'total_branches': total_branches,
            'current_date' : datetime.now()
        })
    
@login_required
def cashier_deposits(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    deposits = Deposit.objects.filter(cashier=True).all().order_by('status', '-date')
    page = request.GET.get('page', 1)

    paginator = Paginator(deposits, 20)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/cashier_deposits.html", {
        'deposits': paginator, 'current_date' : datetime.now()
    })

@login_required
def supervisor_deposits(request):
    # Authorization
    if not request.user.is_staff:
        raise PermissionDenied()
    
    # Checking for filtering or new deposit requests
    if request.method == 'POST':
        form  = CreditSupervisorAccountForm(request.POST)
        if form.is_valid():
            if form.instance.account.balance - form.instance.amount < 0:
                messages.error(request, "Insufficient Fund 😥")
                return HttpResponseRedirect(reverse('supervisor_deposits'))
            form.instance.supervisor = True
            form.instance.account.balance -= form.instance.amount
            form.instance.account.save()
            form.save()
            messages.success(request, "Agent's account credited successfully 😊")
            return HttpResponseRedirect(reverse('supervisor_deposits'))
        
    deposits = Deposit.objects.filter(supervisor=True)
    zone = request.GET.get('zone')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if zone:
        deposits = deposits.filter(agent__profile__zone__name__icontains=zone)
    if from_date:
        deposits = deposits.filter(date__gte=from_date)
    if to_date:
        deposits = deposits.filter(date__lte=to_date)

    deposits = deposits.order_by('status', '-date')
    page = request.GET.get('page', 1)
    paginator = Paginator(deposits, 30)
    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/admin/supervisor_deposits.html", {
        'deposits': paginator, 'form': CreditSupervisorAccountForm, 'current_date': datetime.now(),
        'zones': Zone.objects.all(),
    })

@login_required
def refunds(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    if request.method == 'POST':
        form = RefundAgentForm(request.POST)
        if form.is_valid():
            if form.instance.refund_type == "Add to Opening Cash":
                form.instance.agent.profile.balance += form.instance.amount
                form.instance.agent.profile.opening_cash += form.instance.amount
            elif form.instance.refund_type == "Add to Additional Cash":
                form.instance.agent.profile.balance += form.instance.amount
                form.instance.agent.profile.additional_cash += form.instance.amount
            elif form.instance.refund_type == 'Deduct from Opening Cash':
                form.instance.agent.profile.balance -= form.instance.amount
                form.instance.agent.profile.opening_cash -= form.instance.amount
            else:
                form.instance.agent.profile.balance -= form.instance.amount
                form.instance.agent.profile.additional_cash -= form.instance.amount
            messages.success(request, "Agent's account refunded successfully")
            form.instance.agent.profile.save()
            form.save()
            return redirect('refunds')
    refunds = Refund.objects.all().order_by('-date')
    page = request.GET.get('page', 1)
    paginator = Paginator(refunds, 30)
    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)
    return render(request, "vault/refunds.html", {
        'refunds': paginator, 'current_date' : datetime.now(), 'form': RefundAgentForm
    })

@login_required
def ledger(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    if request.method == 'POST':
        print(request.POST['agent'])
        print(request.POST.get('date_from'))
        print(request.POST.get('date_to'))
    agents = User.objects.filter(
        Q(profile__is_supervisor=True) | Q(profile__is_cashier=True)
    )
    # logs = Ledger.objects.all().order_by('-date')
    logs =  []
    page = request.GET.get('page', 1)
    paginator = Paginator(logs, 25)
    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/ledger.html", {
        'logs': paginator, 'current_date' : datetime.now(), #'form': LedgerFilterForm,
        'agents': agents
    })

@login_required
def accounts(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    if request.method == 'POST':
        account = get_object_or_404(Account, name=request.POST.get('account'))
        if request.POST.get('type') == 'Credit':
            account.balance += float(request.POST.get('amount'))
        else:
            account.balance -= float(request.POST.get('amount'))
        account.save()
        messages.success(request, 'Account updated successfully')
        return redirect('accounts')
    return render(request, "vault/vault_accounts.html", {
        'accounts': Account.objects.all().order_by('-date'),
        'form': UpdateVaultAccountForm, 'current_date' : datetime.now()
    })

@login_required
def withdrawals(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    if request.method == 'POST':
        form = BankWithdrawalForm(request.POST)
        if form.is_valid():
            form.instance.withdrawer = request.user
        messages.success(request, "Cash withdrawal request is sent successfully")
        form.save()
        return HttpResponseRedirect(reverse("withdrawals"))
    withdrawals = Withdraw.objects.all().order_by('status', '-date')
    page = request.GET.get('page', 1)
    paginator = Paginator(withdrawals, 30)
    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/admin/withdrawals.html", {
        'withdrawals': paginator, 'form': BankWithdrawalForm, 'current_date': datetime.now(),
    })

@login_required
def bank_deposits(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    if request.method == "POST":
        form = BankDepositForm(request.POST)
        if form.is_valid():
            form.instance.depositor = request.user
            form.save()
            return HttpResponseRedirect(reverse("bank_deposits"))
    deposits = BankDeposit.objects.all().order_by('status', '-date')
    page = request.GET.get('page', 1)
    paginator = Paginator(deposits, 25)
    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/admin/bank_deposits.html", {
        'bank_deposits': paginator, 'form': BankDepositForm, 'current_date' : datetime.now(),
    })

@login_required
def borrows(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    if request.method == "POST":
        form = LoanForm(request.POST)
        if form.is_valid():
            form.instance.borrower = request.user
            messages.success(request, "Loan request is sent successfully")
            form.save()
            return HttpResponseRedirect(reverse("borrows"))
    borrows = Borrow.objects.all().order_by('status', '-date')
    page = request.GET.get('page', 1)
    paginator = Paginator(borrows, 30)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/borrows.html", {
        'borrows': paginator, 'form': LoanForm, 'current_date' : datetime.now()
    })

@login_required
def currency_transactions(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    
    if request.method == 'POST':
        form = CurrencyTransactionsForm(request.POST)
        if form.is_valid():
            form.instance.agent = request.user
            form.instance.total_amount = form.instance.rate * form.instance.currency_amount
            if form.instance.type == "buy":
                if form.instance.account.balance - (form.instance.currency_amount * form.instance.rate) < 0:
                    messages.error(request, "Insufficient Fund 😥")
                    return HttpResponseRedirect(reverse('currency_transactions'))
        if form.instance.type == "buy":
            messages.success(request, "Currency bought successfully 😊")
        else:
            messages.success(request, "Currency sold successfully 😊")
        form.save()
        return HttpResponseRedirect(reverse("currency_transactions"))
    transactions = CurrencyTransaction.objects.all().order_by('status', '-date')
    page = request.GET.get('page', 1)

    paginator = Paginator(transactions, 25)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)

    return render(request, "vault/currency_transactions.html", {
        'transactions': paginator, 'current_date': datetime.now(), 'form': CurrencyTransactionsForm
    })

@login_required
def my_withdrawals(request):
    if request.user.is_staff or request.user.profile.is_supervisor:
        if request.method == 'POST':
            form = BankWithdrawalForm(request.POST)
            if form.is_valid():
                form.instance.withdrawer = request.user
                messages.success(request, "Cash withdrawal request is sent successfully")
                form.save()
                return HttpResponseRedirect(reverse("my_withdrawals"))
        withdrawals = Withdraw.objects.filter(withdrawer=request.user).all().order_by('-date')

        page = request.GET.get('page', 1)
        paginator = Paginator(withdrawals, 30)
        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)
        return render(request, "vault/my_withdrawals.html", {
            'withdrawals': paginator, 'form': BankWithdrawalForm, 'current_date' : datetime.now()
        })
    raise PermissionDenied()

@login_required
def my_borrows(request):
    if request.user.is_staff or request.user.profile.is_supervisor:
        if request.method == 'POST':
            form = LoanForm(request.POST)
            if form.is_valid():
                form.instance.borrower = request.user
                messages.success(request, "Loan request is sent successfully")
                form.save()
                return HttpResponseRedirect(reverse("my_borrows"))
        borrows = Borrow.objects.filter(borrower=request.user).all().order_by('status', '-date')
        page = request.GET.get('page', 1)

        paginator = Paginator(borrows, 30)

        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)

        return render(request, "vault/my_borrows.html", {
            'borrows': paginator, 'form': LoanForm, 'current_date' : datetime.now()
        })
    raise PermissionDenied()


@login_required
def reports(request):
    if request.user.profile.is_supervisor:
        if request.method == 'POST':
            form = SupervisorReportingForm(request.POST)
            if form.is_valid():
                form.instance.reporter = request.user
                form.instance.zone = request.user.profile.zone
                form.instance.opening_cash = form.instance.reporter.profile.opening_cash
                form.instance.additional_cash = form.instance.reporter.profile.additional_cash
                form.save()
                messages.success(request, "Your daily report have been submitted successfully")
                return HttpResponseRedirect(reverse("reports"))
        reports = MainVault.objects.filter(reporter=request.user).all().order_by('-date')
        page = request.GET.get('page', 1)
        paginator = Paginator(reports, 30)

        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)
        return render(request, "vault/s_reports.html", {
            'reports': paginator, 'form': SupervisorReportingForm, 'current_date': datetime.now()
        })
    elif request.user.profile.is_cashier:
        if request.method == 'POST':
            form = CashierReportingForm(request.POST)
            if form.is_valid():
                form.instance.reporter = request.user
                form.instance.branch = request.user.profile.branch
                form.instance.zone = request.user.profile.zone
                form.instance.opening_cash = form.instance.reporter.profile.opening_cash
                form.instance.additional_cash = form.instance.reporter.profile.additional_cash
                form.save()
                messages.success(request, "Your daily report have been submitted successfully")
                return HttpResponseRedirect(reverse("reports"))
        reports = ZoneVault.objects.filter(reporter=request.user).all().order_by('-date')
        page = request.GET.get('page', 1)
        paginator = Paginator(reports, 30)

        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)
        return render(request, "vault/c_reports.html", {
            'reports': paginator, 'form': CashierReportingForm, 'current_date' : datetime.now()
        })
    elif request.user.is_staff:
        return HttpResponseRedirect(reverse('daily_cashier_reports'))
    raise PermissionDenied()


@login_required
def daily_supervisor_reports(request):
    if request.user.is_staff:
        reports = MainVault.objects.all().order_by('status', '-date')
        page = request.GET.get('page', 1)
        paginator = Paginator(reports, 25)

        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)
        return render(request, "vault/supervisor_reports.html", {
            'reports': paginator, 'current_date' : datetime.now()
        })
    raise PermissionDenied()


@login_required
def daily_cashier_reports(request):
    form = ReturnCashierAccountForm(request.user.profile.zone)
    if request.method == 'POST':
        form = ReturnCashierAccountForm(request.user.profile.zone, request.POST)
        if form.is_valid():
            form.instance.branch = form.instance.reporter.profile.branch
            form.instance.zone = form.instance.reporter.profile.zone
            form.instance.opening_cash = form.instance.reporter.profile.opening_cash
            form.instance.additional_cash = form.instance.reporter.profile.additional_cash
            form.save()
            messages.success(request, f"{form.instance.reporter}'s daily report have been submitted successfully")
            return HttpResponseRedirect(reverse("daily_cashier_reports"))
        
        
    reports = ZoneVault.objects.all().order_by('status', '-date')
    if request.user.profile.is_supervisor:
        reports = ZoneVault.objects.filter(
            reporter__profile__zone=request.user.profile.zone
        ).all().order_by('status', '-date')
    page = request.GET.get('page', 1)
    paginator = Paginator(reports, 30)

    try:
        paginator = paginator.page(page)
    except:
        paginator = paginator.page(1)
    return render(request, "vault/cashier_reports.html", {
        'reports': paginator, 'form': form, 'current_date' : datetime.now()
    })

class UpdateSupervisorAccount(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Deposit
    template_name = "vault/deposit_form.html"
    fields = ['agent', 'deposit_type', 'amount', 'account']

    def form_valid(self, form):
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
        context['current_date'] = datetime.now()
        return context

class UpdateCashierAccount(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Deposit
    template_name = "vault/deposit_form.html"
    fields = ['agent', 'deposit_type', 'amount', 'account']

    def form_valid(self, form):
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
        if not deposit.status:
            deposit.status = True
            deposit.approved_by = request.user
            if deposit.deposit_type == "Opening Cash":
                deposit.agent.profile.opening_cash = deposit.amount
                deposit.agent.profile.closing_balance = 0
            else:
                deposit.agent.profile.additional_cash += deposit.amount
            deposit.agent.profile.balance += deposit.amount
            deposit.agent.profile.save()
            deposit.save()
            messages.success(request, "Deposit Approved")
        else:
            messages.error(request, "This deposit is already approved")
    return HttpResponseRedirect(reverse('cashier_deposits'))
    
@login_required
def approve_cashier_report(request):
    if request.method == "POST":
        report = get_object_or_404(ZoneVault, id=request.POST["id"])
        if not report.status:
            report.status = True
            report.reporter.profile.opening_cash = 0
            report.reporter.profile.additional_cash = 0
            report.reporter.profile.balance = 0
            report.approved_by = request.user
            report.reporter.profile.closing_balance = report.closing_balance
            report.reporter.profile.save()
            report.save()
            messages.success(request, "Report Approved")
        else:
            messages.error(request, "This report is already approved")
    return HttpResponseRedirect(reverse('daily_cashier_reports'))
    
@login_required
def approve_supervisor_report(request):
    if request.method == "POST":
        report = get_object_or_404(MainVault, id=request.POST["id"])
        if not report.status:
            report.status = True
            report.reporter.profile.opening_cash = 0
            report.reporter.profile.additional_cash = 0
            report.reporter.profile.balance = 0
            report.approved_by = request.user

            account = Account.objects.filter(name="Main Vault").first()
            account.balance += report.closing_balance
            account.save()

            report.reporter.profile.closing_balance = report.closing_balance
            report.reporter.profile.save()
            report.save()
            messages.success(request, "Report Approved")
        else:
            messages.error(request, "This report is already approved")
    return HttpResponseRedirect(reverse('daily_supervisor_reports'))
    
@login_required
def disapprove_supervisor_report(request):
    if request.method == "POST":
        report = get_object_or_404(MainVault, id=request.POST["id"])
        report.status = True
        report.reporter.profile.opening_cash = 0
        report.reporter.profile.additional_cash = 0

        account = Account.objects.filter(name="Main Vault").first()
        if account:
            account.balance += report.closing_balance
            account.save()
        else:
            messages.error(request, "Couldn't find the Main Vault Account")
            return HttpResponseRedirect("accounts")
        
        report.reporter.profile.closing_balance = report.closing_balance
        report.reporter.profile.save()
        report.save()
        messages.success(request, "Report Approved")
    return HttpResponseRedirect(reverse('daily_supervisor_reports'))

@login_required
def approve_supervisor_deposit(request):
    if request.method == "POST":
        deposit = get_object_or_404(Deposit, id=request.POST["id"])
        if not deposit.status:
            deposit.status = True
            deposit.approved_by = request.user
            if deposit.deposit_type == "Opening Cash":
                deposit.agent.profile.opening_cash = deposit.amount
                deposit.agent.profile.balance += deposit.amount
                deposit.agent.profile.closing_balance = 0
                deposit.approved_by = request.user
            else:
                deposit.agent.profile.additional_cash += deposit.amount
                deposit.agent.profile.balance += deposit.amount
            deposit.agent.profile.save()
            deposit.save()
            messages.success(request, "Deposit Approved")
        else:
            messages.error(request, "This deposit is already approved")
    return HttpResponseRedirect(reverse('supervisor_deposits'))

@login_required
def disapprove_supervisor_deposit(request):
    if request.method == "POST":
        deposit = get_object_or_404(Deposit, id=request.POST["id"])
        deposit.account.balance += deposit.amount
        deposit.account.save()
        deposit.delete()
        messages.success(request, "Deposit Disapproved")
    return redirect('supervisor_deposits')

@login_required
def approve_withdrawal_request(request):
    if request.method == "POST":
        withdrawal = get_object_or_404(Withdraw, id=request.POST["id"])
        if not withdrawal.status:
            withdrawal.status = True
            if withdrawal.withdrawer.profile.is_supervisor:
                if not withdrawal.withdrawer.is_staff:
                    withdrawal.withdrawer.profile.balance += withdrawal.amount
                    withdrawal.withdrawer.profile.additional_cash += withdrawal.amount
                    withdrawal.withdrawer.profile.save()
                else:
                    withdrawal.account.balance += withdrawal.amount
            else:
                withdrawal.account.balance += withdrawal.amount
            withdrawal.save()
            withdrawal.account.save()
            messages.success(request, "Withdrawal Accepted")
        else:
            messages.error(request, "This request is already in approved")
    return HttpResponseRedirect(reverse('withdrawals'))

@login_required
def approve_deposit_request(request):
    if request.method == "POST":
        deposit = get_object_or_404(BankDeposit, id=request.POST["id"])
        if not deposit.status:
            deposit.status = True
            deposit.approved_by = request.user
            deposit.account.balance -= deposit.amount
            deposit.save()
            deposit.account.save()
            messages.success(request, "Deposit Accepted")
        else:
            messages.error(request, "This request is already in approved")
    return HttpResponseRedirect(reverse('bank_deposits'))

@login_required
def approve_borrow_request(request):
    if request.method == "POST":
        borrow = get_object_or_404(Borrow, id=request.POST["id"])
        if not borrow.status:
            borrow.status = True
            borrow.approved_by = request.user
            if borrow.borrower.profile.is_supervisor:
                if not borrow.borrower.is_staff:
                    borrow.borrower.profile.balance += borrow.amount
                    borrow.borrower.profile.additional_cash += borrow.amount
                    borrow.borrower.profile.save()
                else:
                    borrow.account.balance += borrow.amount
            else:
                borrow.account.balance += borrow.amount
            borrow.save()
            borrow.account.save()
            messages.success(request, "Borrow Accepted")
        else:
            messages.error(request, "This request is already in approved")
    return redirect('borrows')

@login_required
def disapprove_withdrawal_request(request):
    if request.method == "POST":
        withdrawal = get_object_or_404(Withdraw, id=request.POST["id"])
        withdrawal.delete()
        messages.success(request, "Withdrawal Rejected 😔")
        return HttpResponseRedirect(reverse('withdrawals'))

@login_required
def disapprove_cashier_deposit(request):
    if request.method == "POST":
        deposit = get_object_or_404(Deposit, id=request.POST["id"])
        deposit.agent.profile.zone.supervisor.profile.balance += deposit.amount
        deposit.agent.profile.zone.supervisor.profile.save()
        deposit.delete()
        messages.success(request, "Deposit Rejected 😔")
    return HttpResponseRedirect(reverse('cashier_deposits'))

@login_required
def disapprove_borrow_request(request):
    if request.method == "POST":
        borrow = get_object_or_404(Borrow, id=request.POST["id"])
        borrow.delete()
        messages.success(request, "Borrow Rejected 😔")
        return HttpResponseRedirect(reverse('borrows'))

class DepositCash(LoginRequiredMixin, CreateView):
    model = BankDeposit
    template_name = "vault/withdraw_form.html"
    fields = ['bank', 'amount', 'account', 'comment']

    def form_valid(self, form):
        form.instance.depositor = self.request.user
        messages.success(self.request, "Cash deposit request is sent successfully")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        if self.request.user.is_staff or self.request.user.profile.is_supervisor:
            context = super(DepositCash, self).get_context_data(*args, **kwargs)
            context['button'] = 'Withdraw'
            context['legend'] = 'Withdraw Cash'
            return context
        raise PermissionDenied()


class UpdateWithdrawCash(LoginRequiredMixin, UpdateView):
    model = Withdraw
    template_name = "vault/withdraw_form.html"
    fields = ['bank', 'cheque_number', 'amount', 'account', 'comment']

    def form_valid(self, form):
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

@login_required
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
@login_required
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

@login_required
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

@login_required
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

@login_required
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

class UpdateCurrencyTransact(LoginRequiredMixin, UpdateView):
    model = CurrencyTransaction
    template_name = "vault/currency_transact_form.html"
    fields = ['date', 'customer_name', 'phone_number', 'id_number', 'type', 'currency', 'currency_amount', 'rate', 'account']

    def form_valid(self, form):
        form.instance.total_amount = form.instance.rate * form.instance.currency_amount
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
        messages.success(request, "Transaction Approved")
        return HttpResponseRedirect(reverse('currency_transactions'))