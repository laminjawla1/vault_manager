from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (cashier_deposits, supervisor_deposits, dashboard, reports, CreditSupervisorAccount, 
                    UpdateSupervisorAccount, CreditCashierAccount, UpdateCashierAccount, approve_cashier_deposit,
                    approve_supervisor_deposit, refunds, RefundAgent, vault_log, accounts, withdrawals, WithdrawCash,
                    UpdateWithdrawCash, approve_withdrawal_request, my_withdrawals, disapprove_withdrawal_request,
                    SupervisorReporting, daily_supervisor_reports, UpdateSupervisorReporting, CashierReporting, UpdateCashierReporting,
                    daily_cashier_reports, approve_cashier_report, approve_supervisor_report, generate_cashier_deposit_report, 
                    generate_cashier_report, generate_supervisor_report, generate_withdrawal_report, generate_supervisor_deposit_report)

urlpatterns = [
    path("generate_supervisor_deposit_report/", generate_supervisor_deposit_report, name="generate_supervisor_deposit_report"),
    path("generate_cashier_deposit_report/", generate_cashier_deposit_report, name="generate_cashier_deposit_report"),
    path("generate_withdrawal_report/", generate_withdrawal_report, name="generate_withdrawal_report"),
    path("generate_cashier_report/", generate_cashier_report, name="generate_cashier_report"),
    path("generate_supervisor_report/", generate_supervisor_report, name="generate_supervisor_report"),
    path("agents/refunds/", refunds, name='refunds'),
    path("supervisors/reports/new", SupervisorReporting.as_view(), name='supervisor_reporting'),
    path("cashiers/reports/new", CashierReporting.as_view(), name='cashier_reporting'),
    path("agents/reports/<int:pk>/update", UpdateSupervisorReporting.as_view(), name='update_supervisor_reporting'),
    path("agents/reports/<int:pk>/update", UpdateCashierReporting.as_view(), name='update_cashier_reporting'),
    path("supervisors/reports/history", daily_supervisor_reports, name='daily_supervisor_reports'),
    path("cashiers/reports/history", daily_cashier_reports, name='daily_cashier_reports'),
    path("agents/logs", vault_log, name='vault_log'),
    path("accounts", accounts, name='accounts'),
    path("withdrawals", withdrawals, name='withdrawals'),
    path("my_withdrawals", my_withdrawals, name='my_withdrawals'),
    path("withdraw_cash", WithdrawCash.as_view(), name='withdraw_cash'),
    path("agents/refund", RefundAgent.as_view(), name='refund'),
    path("deposits/cashiers", cashier_deposits, name='cashier_deposits'),
    path("deposits/supervisors", supervisor_deposits, name='supervisor_deposits'),
    path("dashboard/", dashboard, name="dashboard"),
    path("me/reports/", reports, name='reports'),
    path("credit_supervisor", CreditSupervisorAccount.as_view(), name="credit_supervisor"),
    path("credit_cashier", CreditCashierAccount.as_view(), name="credit_cashier"),
    path("approve_supervisor_report", approve_supervisor_report, name="approve_supervisor_report"),
    path("approve_cashier_report", approve_cashier_report, name="approve_cashier_report"),
    path("approve_cashier_deposit", approve_cashier_deposit, name="approve_cashier_deposit"),
    path("approve_withdrawal_request", approve_withdrawal_request, name="approve_withdrawal_request"),
    path("disapprove_withdrawal_request", disapprove_withdrawal_request, name="disapprove_withdrawal_request"),
    path("approve_supervisor_deposit", approve_supervisor_deposit, name="approve_supervisor_deposit"),
    path("supervisor_deposit/<int:pk>/update", UpdateSupervisorAccount.as_view(), name="update_supervisor_deposit"),
    path("cashier_deposit/<int:pk>/update", UpdateCashierAccount.as_view(), name="update_cashier_deposit"),
    path("withdrawals/<int:pk>/update", UpdateWithdrawCash.as_view(), name="update_withdrawal_request"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)