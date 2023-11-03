from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from vault_manager.models import (Account, CurrencyTransaction, Withdraw)

@login_required
def withdrawal_actions(request):
    action = request.POST.get('action')

    if not action:
        messages.error(request, "Please select an action")
        return redirect("withdrawals")
    
    transactions = request.POST.getlist('selected_transactions')
    if not transactions:
        messages.error(request, "Please select at least one transaction")
        return redirect("withdrawals")
    match action:
        case "approve":
            for transaction in transactions:
                approve_withdrawal_request(int(transaction))
            messages.success(request, "Transactions Approved")
        case "disapprove":
            for transaction in transactions:
                disapprove_withdrawal_request(int(transaction))
            messages.success(request, "Transactions disapproved")
    return redirect("withdrawals")

def approve_withdrawal_request(id):
    withdrawal = get_object_or_404(Withdraw, id=id)
    if not withdrawal.approved:
        withdrawal.approved = True
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

def disapprove_withdrawal_request(id):
    withdrawal = get_object_or_404(Withdraw, id=id)
    if not withdrawal.disapproved:
        withdrawal.disapproved = True
        withdrawal.save()