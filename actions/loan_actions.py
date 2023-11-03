from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from vault_manager.models import Borrow

@login_required
def loan_actions(request):
    action = request.POST.get('action')
    if not action:
        messages.error(request, "Please select an option")
        return redirect("borrows")
    transactions = request.POST.getlist('selected_transactions')
    if not transactions:
        messages.error(request, "Please select at least one transaction")
        return redirect("borrows")
    match action:
        case "approve":
            for transaction in transactions:
                approve_loan_request(int(transaction), request)
            messages.success(request, "Loan requests Approved")
        case "disapprove":
            for transaction in transactions:
                disapprove_loan_request(int(transaction))
            messages.success(request, "Loan requests Approved")
    return redirect("borrows")

def approve_loan_request(id, request):
    loan = get_object_or_404(Borrow, id=id)
    if not loan.approved:
        loan.approved = True
        loan.approved_by = request.user
        if loan.borrower.profile.is_supervisor:
            if not loan.borrower.is_staff:
                loan.borrower.profile.balance += loan.amount
                loan.borrower.profile.additional_cash += loan.amount
                loan.borrower.profile.save()
            else:
                loan.account.balance += loan.amount
        else:
            loan.account.balance += loan.amount
        loan.save()
        loan.account.save()

def disapprove_loan_request(id):
    loan = get_object_or_404(Borrow, id=id)
    if not loan.disapproved:
        loan.disapproved = True
        loan.save()