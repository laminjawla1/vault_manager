from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (cashier_deposits, supervisor_deposits, dashboard, reports, my_borrows, bank_deposits,
                    UpdateSupervisorAccount, UpdateCashierAccount, refunds, ledger, accounts, withdrawals,
                    UpdateWithdrawCash, my_withdrawals, UpdateBankDeposit,daily_supervisor_reports, UpdateSupervisorReporting,
                    UpdateCashierReporting, daily_cashier_reports, UpdateBorrowCash, borrows, currency_transactions,
                    UpdateCurrencyTransact, UpdateReturnCashierAccount, bank_deposits)

urlpatterns = [
    path("currency_transactions", currency_transactions, name="currency_transactions"),
    path("currency_transactions/<int:pk>/update/", UpdateCurrencyTransact.as_view(), name="update_currency_transaction"),
    path("agents/refunds/", refunds, name='refunds'),
    path("supervisor/reports/<int:pk>/update", UpdateSupervisorReporting.as_view(), name='update_supervisor_reporting'),
    path("cashier/reports/<int:pk>/update", UpdateCashierReporting.as_view(), name='update_cashier_reporting'),
    path("supervisor/cashier/reports/<int:pk>/update", UpdateReturnCashierAccount.as_view(), name='update_return_cashier_account'),
    path("supervisors/reports/history", daily_supervisor_reports, name='daily_supervisor_reports'),
    path("cashiers/reports/history", daily_cashier_reports, name='daily_cashier_reports'),
    path("agents/logs", ledger, name='ledger'),
    path("accounts", accounts, name='accounts'),
    path("withdrawals", withdrawals, name='withdrawals'),
    path("bank_deposits", bank_deposits, name='bank_deposits'),
    path("bank_deposits", bank_deposits, name='bank_deposits'),
    path("borrows", borrows, name='borrows'),
    path("my_withdrawals", my_withdrawals, name='my_withdrawals'),
    path("my_borrows", my_borrows, name='my_borrows'),
    path("deposits/cashiers", cashier_deposits, name='cashier_deposits'),
    path("deposits/supervisors", supervisor_deposits, name='supervisor_deposits'),
    path("dashboard/", dashboard, name="dashboard"),
    path("me/reports/", reports, name='reports'),
    path("supervisor_deposit/<int:pk>/update", UpdateSupervisorAccount.as_view(), name="update_supervisor_deposit"),
    path("cashier_deposit/<int:pk>/update", UpdateCashierAccount.as_view(), name="update_cashier_deposit"),
    path("withdrawals/<int:pk>/update", UpdateWithdrawCash.as_view(), name="update_withdrawal_request"),
    path("bank_deposits/<int:pk>/update", UpdateBankDeposit.as_view(), name="update_bank_deposit_request"),
    path("borrows/<int:pk>/update", UpdateBorrowCash.as_view(), name="update_borrow_request"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)