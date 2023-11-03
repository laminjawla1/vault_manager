from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from vault_manager.models import (Account, CurrencyTransaction)

@login_required
def currency_actions(request):
    action = request.POST.get('action')
    if not action:
        messages.error(request, "Please select an action")
        return redirect("currency_transactions")
    transactions = request.POST.getlist('selected_transactions')
    if not transactions:
        messages.error(request, "Please select at least one transaction")
        return redirect("currency_transactions")
    match action:
        case "approve":
            for transaction in transactions:
                approve_currency_transaction(int(transaction))
            messages.success(request, "Transactions Approved")
        case "disapprove":
            for transaction in transactions:
                disapprove_currency_transaction(int(transaction))
            messages.success(request, "Transactions disapproved")
    return redirect("currency_transactions")

def approve_currency_transaction(id):
    transaction = get_object_or_404( CurrencyTransaction, id=id)
    if not transaction.approved:
        transaction.approved = True
        account = get_object_or_404(Account, id=transaction.account.id)
        if transaction.type == "buy":
            account.balance -= transaction.total_amount
        else:
            account.balance += transaction.total_amount
        transaction.save()
        account.save()

def disapprove_currency_transaction(id):
    transaction = get_object_or_404( CurrencyTransaction, id=id)
    if not transaction.disapproved:
        transaction.disapproved = True
        transaction.save()