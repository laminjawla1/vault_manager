from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from vault_manager.models import BankDeposit

@login_required
def bank_deposit_actions(request):
    action = request.POST.get('action')

    if not action:
        messages.error(request, "Please select an action")
        return redirect("bank_deposits")
    
    transactions = request.POST.getlist('selected_transactions')
    if not transactions:
        messages.error(request, "Please select at least one transaction")
        return redirect("bank_deposits")
    match action:
        case "approve":
            for transaction in transactions:
                approve_bank_deposit_request(int(transaction))
            messages.success(request, "Transactions Approved")
        case "disapprove":
            for transaction in transactions:
                disapprove_bank_deposit_request(int(transaction))
            messages.success(request, "Transactions disapproved")
    return redirect("bank_deposits")

def approve_bank_deposit_request(id):
    bank_deposit = get_object_or_404(BankDeposit, id=id)
    if not bank_deposit.approved:
        bank_deposit.approved = True
        bank_deposit.save()

def disapprove_bank_deposit_request(id):
    bank_deposit = get_object_or_404(BankDeposit, id=id)
    if not bank_deposit.disapproved:
        bank_deposit.disapproved = True
        bank_deposit.account.balance += bank_deposit.amount
        bank_deposit.account.save()
        bank_deposit.save()