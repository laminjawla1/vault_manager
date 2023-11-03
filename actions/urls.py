from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .currency_actions import currency_actions
from .loan_actions import loan_actions
from .withdrawal_actions import withdrawal_actions
from .bank_deposits_actions import bank_deposit_actions
from .cashier_deposit_actions import cashier_deposit_actions
from .supervisor_deposit_actions import supervisor_deposit_actions
from .cashier_reports_actions import cashier_reports_actions
from .supervisor_reports_actions import supervisor_reports_actions

urlpatterns = [
    path("currency_actions", currency_actions, name="currency_actions"),
    path("loan_actions", loan_actions, name="loan_actions"),
    path("withdrawal_actions", withdrawal_actions, name="withdrawal_actions"),
    path("bank_deposit_actions", bank_deposit_actions, name="bank_deposit_actions"),
    path("cashier_deposit_actions", cashier_deposit_actions, name="cashier_deposit_actions"),
    path("supervisor_deposit_actions", supervisor_deposit_actions, name="supervisor_deposit_actions"),
    path("cashier_reports_actions", cashier_reports_actions, name="cashier_reports_actions"),
    path("supervisor_reports_actions", supervisor_reports_actions, name="supervisor_reports_actions"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)