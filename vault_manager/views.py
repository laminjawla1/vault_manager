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
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import UpdateView

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
            date__year=timezone.now().year, date__month=timezone.now(
            ).month, date__day=timezone.now().day,
            supervisor=True, deposit_type="Opening Cash"
        ).aggregate(Sum('amount')).get('amount__sum') or 0
        additional_cash = Deposit.objects.filter(
            date__year=datetime.now().year, date__month=datetime.now(
            ).month, date__day=datetime.now().day,
            supervisor=True, deposit_type="Additional Cash"
        ).aggregate(Sum('amount')).get('amount__sum') or 0
        users = User.objects.count()
        zone_cnt = Zone.objects.count()

        zones = Zone.objects.all().order_by('name')
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
            'deposit_amount': deposit_amount, 'zones': zones, 'loan_amount': borrow_amount, 't_loans': t_borrows
        })
    elif request.user.profile.is_supervisor:
        opening_cash = Deposit.objects.filter(
            date__year=timezone.now().year, date__month=timezone.now(
            ).month, date__day=timezone.now().day,
            supervisor=True, deposit_type="Opening Cash"
        ).aggregate(Sum('amount')).get('amount__sum') or 0
        additional_cash = Deposit.objects.filter(
            date__year=datetime.now().year, date__month=datetime.now(
            ).month, date__day=datetime.now().day,
            supervisor=True, deposit_type="Additional Cash"
        ).aggregate(Sum('amount')).get('amount__sum') or 0
        branches = Branch.objects.filter(
            teller__profile__zone__supervisor=request.user).order_by('name')
        total_branches = branches.count()
        return render(request, "vault/admin/supervisor_dashboard.html", {
            'opening_cash': opening_cash, 'additional_cash': additional_cash, 'branches': branches, 'total_branches': total_branches,
        })


@login_required
def cashier_deposits(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    today = datetime.now()
    return render(request, "vault/cashier_deposits.html", {
        'deposits': Deposit.objects.filter(cashier=True, date__year=today.year, date__month=today.month, date__day=today.day)
    })


@login_required
def supervisor_deposits(request):
    # Authorization
    if not request.user.is_staff:
        raise PermissionDenied()
    # Checking for filtering or new deposit requests
    if request.method == 'POST':
        form = CreditSupervisorAccountForm(request.POST)
        if form.is_valid():
            if form.instance.account.balance - form.instance.amount < 0:
                messages.error(request, "Insufficient Fund 😥")
                return HttpResponseRedirect(reverse('supervisor_deposits'))
            form.instance.supervisor = True
            form.instance.account.balance -= form.instance.amount
            form.instance.account.save()
            form.save()
            messages.success(
                request, "Agent's account credited successfully 😊")
            return HttpResponseRedirect(reverse('supervisor_deposits'))
    year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
    deposits = Deposit.objects.filter(
        supervisor=True, date__year=year, date__month=month, date__day=day)
    return render(request, "vault/admin/supervisor_deposits.html", {
        'deposits': deposits, 'form': CreditSupervisorAccountForm
    })


@login_required
def refunds(request):
    if not request.user.is_staff:
        raise PermissionDenied()

    if request.method == 'POST':
        form = RefundAgentForm(request.POST)
        if form.is_valid():
            if form.instance.refund_type == "Opening":
                form.instance.agent.profile.balance += form.instance.amount
                form.instance.agent.profile.opening_cash += form.instance.amount
            else:
                form.instance.agent.profile.balance += form.instance.amount
                form.instance.agent.profile.additional_cash += form.instance.amount
            messages.success(request, "Agent's account refunded successfully")
            form.instance.agent.profile.save()
            form.save()
            return redirect('refunds')
    return render(request, "vault/refunds.html", {
        'refunds': Refund.objects.all(), 'form': RefundAgentForm
    })


@login_required
def ledger(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    if request.method == 'POST':
        ...
    agents = User.objects.filter(
        Q(profile__is_supervisor=True) | Q(profile__is_cashier=True)
    )
    # logs = Ledger.objects.all().order_by('-date')
    return render(request, "vault/ledger.html", {
        'logs': [], 'agents': agents
    })


@login_required
def accounts(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    if request.method == 'POST':
        account = get_object_or_404(Account, name=request.POST.get('account'))
        account.balance += float(request.POST.get('amount'))
        account.save()
        messages.success(request, 'Account updated successfully')
        return redirect('accounts')
    return render(request, "vault/vault_accounts.html", {
        'accounts': Account.objects.all(), 'form': UpdateVaultAccountForm
    })


@login_required
def withdrawals(request):
    if not request.user.is_staff:
        raise PermissionDenied()

    if request.method == 'POST':
        form = BankWithdrawalForm(request.POST)
        if form.is_valid():
            form.instance.withdrawer = request.user
        messages.success(
            request, "Cash withdrawal request is sent successfully")
        form.save()
        return HttpResponseRedirect(reverse("withdrawals"))
    withdrawals = Withdraw.objects.all().order_by('-date')
    return render(request, "vault/admin/withdrawals.html", {
        'withdrawals': withdrawals, 'form': BankWithdrawalForm, 'current_date': datetime.now(),
    })


@login_required
def bank_deposits(request):
    if not request.user.is_staff:
        raise PermissionDenied()

    if request.method == "POST":
        form = BankDepositForm(request.POST)
        if form.is_valid():
            form.instance.depositor = request.user
            if form.instance.account.balance - form.instance.amount < 0:
                messages.error(request, "Insufficient Fund 😥")
                return HttpResponseRedirect(reverse('bank_deposits'))
            form.instance.account.balance -= form.instance.amount
            form.instance.account.save()
            form.save()
            return HttpResponseRedirect(reverse("bank_deposits"))
    return render(request, "vault/admin/bank_deposits.html", {
        'bank_deposits': BankDeposit.objects.all(), 'form': BankDepositForm
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
    borrows = Borrow.objects.all().order_by('-date')
    return render(request, "vault/borrows.html", {
        'borrows': borrows, 'form': LoanForm
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
    transactions = CurrencyTransaction.objects.all().order_by('-date')
    return render(request, "vault/currency_transactions.html", {
        'transactions': transactions, 'current_date': datetime.now(), 'form': CurrencyTransactionsForm
    })


@login_required
def my_withdrawals(request):
    if request.user.is_staff or request.user.profile.is_supervisor:
        if request.method == 'POST':
            form = BankWithdrawalForm(request.POST)
            if form.is_valid():
                form.instance.withdrawer = request.user
                messages.success(
                    request, "Cash withdrawal request is sent successfully")
                form.save()
                return HttpResponseRedirect(reverse("my_withdrawals"))
        withdrawals = Withdraw.objects.filter(
            withdrawer=request.user).all().order_by('-date')

        page = request.GET.get('page', 1)
        paginator = Paginator(withdrawals, 30)
        try:
            paginator = paginator.page(page)
        except:
            paginator = paginator.page(1)
        return render(request, "vault/my_withdrawals.html", {
            'withdrawals': paginator, 'form': BankWithdrawalForm, 'current_date': datetime.now()
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
        return render(request, "vault/my_borrows.html", {
            'borrows': Borrow.objects.filter(borrower=request.user), 'form': LoanForm
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
                messages.success(
                    request, "Your daily report have been submitted successfully")
                return HttpResponseRedirect(reverse("reports"))
        return render(request, "vault/s_reports.html", {
            'reports': MainVault.objects.filter(reporter=request.user), 'form': SupervisorReportingForm
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
                messages.success(
                    request, "Your daily report have been submitted successfully")
                return HttpResponseRedirect(reverse("reports"))
        return render(request, "vault/c_reports.html", {
            'reports': ZoneVault.objects.filter(reporter=request.user), 'form': CashierReportingForm
        })


@login_required
def daily_supervisor_reports(request):
    if request.user.is_staff:
        return render(request, "vault/supervisor_reports.html", {
            'reports': MainVault.objects.all()
        })
    raise PermissionDenied()


@login_required
def daily_cashier_reports(request):
    form = ReturnCashierAccountForm(request.user.profile.zone)
    if request.method == 'POST':
        form = ReturnCashierAccountForm(
            request.user.profile.zone, request.POST)
        if form.is_valid():
            form.instance.branch = form.instance.reporter.profile.branch
            form.instance.zone = form.instance.reporter.profile.zone
            form.instance.opening_cash = form.instance.reporter.profile.opening_cash
            form.instance.additional_cash = form.instance.reporter.profile.additional_cash
            form.save()
            messages.success(
                request, f"{form.instance.reporter}'s daily report have been submitted successfully")
            return HttpResponseRedirect(reverse("daily_cashier_reports"))

    year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
    reports = ZoneVault.objects.all(
        date__year=year, date__month=month, date__day=day)
    if request.user.profile.is_supervisor:
        reports = ZoneVault.objects.filter(
            reporter__profile__zone=request.user.profile.zone, date__year=year, date__month=month, date__day=day)
    return render(request, "vault/cashier_reports.html", {
        'reports': reports, 'form': form
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
        return not deposit.approved

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        context = super(UpdateSupervisorAccount,
                        self).get_context_data(*args, **kwargs)
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
        return not deposit.approved

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        context = super(UpdateCashierAccount,
                        self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        return context


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


class UpdateWithdrawCash(LoginRequiredMixin, UpdateView):
    model = Withdraw
    template_name = "vault/withdraw_form.html"
    fields = ['bank', 'cheque_number', 'amount', 'account', 'comment']

    def form_valid(self, form):
        messages.success(
            self.request, "Withdrawal request updated successfully.")
        return super().form_valid(form)

    def test_func(self):
        withdrawal = self.get_object()
        return not withdrawal.approved

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        context = super(UpdateWithdrawCash, self).get_context_data(
            *args, **kwargs)
        context['button'] = 'Update'
        context['legend'] = 'Update Withdraw Cash'
        return context


class UpdateBankDeposit(LoginRequiredMixin, UpdateView):
    model = BankDeposit
    template_name = "vault/bank_deposit_form.html"
    fields = ['bank', 'amount', 'account', 'comment']

    def form_valid(self, form):
        messages.success(
            self.request, "Bank deposit request updated successfully.")
        return super().form_valid(form)

    def test_func(self):
        bank_deposit = self.get_object()
        return not bank_deposit.approved

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        context = super(UpdateBankDeposit, self).get_context_data(
            *args, **kwargs)
        context['button'] = 'Update'
        context['legend'] = 'Update Bank Deposit'
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
        return not borrow.approved

    def get_context_data(self, *args, **kwargs):
        if self.request.user.is_staff or self.request.user.profile.is_supervisor:
            context = super(UpdateBorrowCash, self).get_context_data(
                *args, **kwargs)
            context['button'] = 'Update'
            context['legend'] = 'Update Cash Borrowed'
            return context
        raise PermissionDenied()


class UpdateSupervisorReporting(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
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
        return not report.approved

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.profile.is_supervisor:
            raise PermissionDenied()
        context = super(UpdateSupervisorReporting,
                        self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        return context


class UpdateCashierReporting(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ZoneVault
    template_name = "vault/daily_report_form.html"
    fields = ['cashier_name', 'opening_cash',
              'additional_cash', 'closing_balance']

    def form_valid(self, form):
        messages.success(self.request, "Daily Report Updated Successfully")
        return super().form_valid(form)

    def test_func(self):
        report = self.get_object()
        return not report.approved

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateCashierReporting,
                        self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        return context


class UpdateReturnCashierAccount(LoginRequiredMixin, UpdateView):
    model = ZoneVault
    template_name = "vault/daily_report_form.html"
    fields = ['cashier_name', 'reporter', 'opening_cash',
              'additional_cash', 'closing_balance']

    def form_valid(self, form):
        messages.success(self.request, "Daily Report Updated Successfully")
        return super().form_valid(form)

    def test_func(self):
        report = self.get_object()
        return not report.approved

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateReturnCashierAccount,
                        self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        return context


class UpdateCurrencyTransact(LoginRequiredMixin, UpdateView):
    model = CurrencyTransaction
    template_name = "vault/currency_transact_form.html"
    fields = ['date', 'customer_name', 'phone_number', 'id_number',
              'type', 'currency', 'currency_amount', 'rate', 'account']

    def form_valid(self, form):
        form.instance.total_amount = form.instance.rate * form.instance.currency_amount
        messages.success(self.request, "Deposit updated successfully.")
        return super().form_valid(form)

    def test_func(self):
        deposit = self.get_object()
        return not deposit.approved

    def get_context_data(self, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied()
        context = super(UpdateCurrencyTransact,
                        self).get_context_data(*args, **kwargs)
        context['button'] = 'Update'
        return context
