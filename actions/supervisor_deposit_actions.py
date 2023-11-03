from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from vault_manager.models import Deposit

@login_required
def supervisor_deposit_actions(request):
    action = request.POST.get('action')

    if not action:
        messages.error(request, "Please select an action")
        return redirect("supervisor_deposits")
    
    transactions = request.POST.getlist('selected_transactions')
    if not transactions:
        messages.error(request, "Please select at least one transaction")
        return redirect("supervisor_deposits")
    match action:
        case "approve":
            for transaction in transactions:
                approve_supervisor_deposit(request, int(transaction))
            messages.success(request, "Deposits Approved")
        case "disapprove":
            for transaction in transactions:
                disapprove_supervisor_deposit(int(transaction))
            messages.success(request, "Deposits disapproved")
    return redirect("supervisor_deposits")

def approve_supervisor_deposit(request, id):
    deposit = get_object_or_404(Deposit, id=id)
    if not deposit.approved:
        deposit.approved = True
        deposit.approved_by = request.user
        if deposit.deposit_type == "Opening Cash":
            deposit.agent.profile.opening_cash = deposit.amount
            deposit.agent.profile.closing_balance = 0
        else:
            deposit.agent.profile.additional_cash += deposit.amount
        deposit.agent.profile.balance += deposit.amount
        deposit.agent.profile.save()
        deposit.save()

def disapprove_supervisor_deposit(id):
    deposit = get_object_or_404(Deposit, id=id)
    if not deposit.disapproved:
        deposit.disapproved = True
        deposit.account.balance += deposit.amount
        deposit.account.save()
        deposit.save()