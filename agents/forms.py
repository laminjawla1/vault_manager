from django import forms
from django.contrib.auth.models import User
from agents.models import Profile
from vault_manager.models import Deposit, ZoneVault


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

class CreditMyCashierForm(forms.ModelForm):
    def __init__(self, supervisor_zone, *args, **kwargs):
        super(CreditMyCashierForm, self).__init__(*args, **kwargs)
        self.fields['agent'].queryset = User.objects.filter(
                                            profile__is_cashier=True, 
                                            profile__zone=supervisor_zone
                                        )
        self.fields['date'].widget=forms.DateInput(attrs={'type': 'date'})
    class Meta:
        model = Deposit
        fields = ['date', 'agent', 'deposit_type', 'amount']


class ReturnCashierAccountForm(forms.ModelForm):
    def __init__(self, zone, *args, **kwargs):
        super(ReturnCashierAccountForm, self).__init__(*args, **kwargs)
        self.fields['reporter'].queryset = User.objects.all.filter(
                                                profile__zone=zone
                                            ).order_by("name")
    class Meta:
        model = ZoneVault
        fields = ['cashier_name', 'reporter', 'closing_balance']