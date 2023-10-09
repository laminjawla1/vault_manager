from django import forms
from vault_manager.models import Account, Deposit, Bank, Withdraw, ZoneVault, BankDeposit, MainVault
from django.contrib.auth.models import User

account_choices = [(account.name, account.name) for account in Account.objects.all()]
class UpdateVaultAccountForm(forms.Form):
    account = forms.ChoiceField(choices=account_choices,)
    amount = forms.FloatField()
    type = forms.ChoiceField(choices=[('Credit', 'Credit'),('Debit', 'Debit')])


class CreditSupervisorAccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreditSupervisorAccountForm, self).__init__(*args, **kwargs)
        self.fields['agent'].queryset = User.objects.filter(profile__is_supervisor=True).order_by("username")

    class Meta:
        model = Deposit
        fields = ['agent', 'deposit_type', 'amount', 'account']

class BankWithdrawalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BankWithdrawalForm, self).__init__(*args, **kwargs)
        self.fields['bank'].queryset = Bank.objects.all().order_by("name")
    class Meta:
        model = Withdraw
        fields = ['bank', 'cheque_number', 'amount', 'account', 'image', 'comment']

class ReturnCashierAccountForm(forms.ModelForm):
    def __init__(self, zone, *args, **kwargs):
        super(ReturnCashierAccountForm, self).__init__(*args, **kwargs)
        self.fields['reporter'].queryset = User.objects.all().filter(
                                                profile__is_cashier=True,
                                                profile__zone=zone
                                            ).order_by("username")
        self.fields['date'].widget=forms.DateInput(attrs={'type': 'date'})
    class Meta:
        model = ZoneVault
        fields = ['date', 'cashier_name', 'reporter', 'closing_balance']

class CashierReportingForm(forms.ModelForm):
    class Meta:
        model = ZoneVault
        fields = ['cashier_name', 'closing_balance']

class SupervisorReportingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SupervisorReportingForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget=forms.DateInput(attrs={'type': 'date'})
    class Meta:
        model = MainVault
        fields = ['date', 'closing_balance']

class BankDepositsForm(forms.ModelForm):
    class Meta:
        model = BankDeposit
        fields = ['bank', 'amount', 'account', 'comment']