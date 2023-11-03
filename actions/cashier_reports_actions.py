from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from vault_manager.models import ZoneVault

@login_required
def cashier_reports_actions(request):
    action = request.POST.get('action')

    if not action:
        messages.error(request, "Please select an action")
        return redirect("daily_cashier_reports")
    
    transactions = request.POST.getlist('selected_transactions')
    if not transactions:
        messages.error(request, "Please select at least one transaction")
        return redirect("daily_cashier_reports")
    match action:
        case "approve":
            for transaction in transactions:
                approve_cashier_report(request, int(transaction))
            messages.success(request, "Transactions Approved")
        case "disapprove":
            for transaction in transactions:
                disapprove_cashier_report(int(transaction))
            messages.success(request, "Transactions disapproved")
    return redirect("daily_cashier_reports")

def approve_cashier_report(request, id):
    report = get_object_or_404(ZoneVault, id=id)
    if not report.approved:
        report.approved = True
        report.reporter.profile.opening_cash = 0
        report.reporter.profile.additional_cash = 0
        report.reporter.profile.balance = 0
        report.approved_by = request.user
        report.reporter.profile.closing_balance = report.closing_balance
        report.reporter.profile.save()
        report.save()

def disapprove_cashier_report(id):
    report = get_object_or_404(ZoneVault, id=id)
    if not report.disapproved:
        report.disapproved = True
        report.save()