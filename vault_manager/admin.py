from django.contrib import admin
from .models import MainVault, ZoneVault, Withdraw, Deposit, Account, Bank, Currency, CurrencyTransaction, BankDeposit
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
import csv


def generate_cashier_report(modeladmin, request, queryset):
    if not request.user.is_staff:
        raise PermissionDenied()

    headers  =["ZONE", "BRANCH", "LOCATION", "TELLER", "OPENING CASH", "ADDITIONAL CASH", "CLOSING BALANCE", "STATUS", "DATE"]
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="cashier_reports.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(["DAILY CASHIER REPORTS"])
    writer.writerow(headers)
    cr = queryset.values_list('zone__name', 'branch__name', 'location__name', 'reporter__username', 'opening_cash', 'additional_cash',
                                'closing_balance', 'status', 'date')
    for r in cr:
        writer.writerow(r)
    return response


def generate_supervisor_report(modeladmin, request, queryset):
    headers  =["ZONE", "SUPERVISOR", "OPENING CASH", "ADDITIONAL CASH", "CLOSING BALANCE", "STATUS", "DATE"]
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="supervisor_reports.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(["DAILY SUPERVISOR REPORTS"])
    writer.writerow(headers)
    cr = queryset.values_list('zone__name', 'reporter__username', 'opening_cash', 'additional_cash', 'closing_balance', 'status', 'date')
    for r in cr:
        writer.writerow(r)
    return response


def generate_withdrawal_report(modeladmin, request, queryset):
    headers  =["AGENT", "ZONE", "AMOUNT","STATUS", "DATE"]
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="withdrawal_reports.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(["DAILY WITHDRAWAL REPORTS"])
    writer.writerow(headers)
    dw = queryset.values_list("withdrawer__username", "withdrawer__profile__zone__name", "amount", "status", "date")
    for w in dw:
        writer.writerow(w)
    return response


def generate_cashier_deposit_report(modeladmin, request, queryset):
    headers  =["ZONE", "BRANCH", "TELLER", "AMOUNT", "DEPOSIT TYPE", "DATE"]
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="withdrawal_reports.csv"'},
    )
    writer = csv.writer(response)
    writer = csv.writer(response)
    writer.writerow(["DAILY CASHIER DEPOSIT REPORTS"])
    writer.writerow(headers)
    cd = queryset.values_list("agent__profile__zone__name", "agent__profile__branch__name", "agent__username", "amount", "deposit_type", "date")
    for d in cd:
        writer.writerow(d)
    return response


def generate_supervisor_deposit_report(modeladmin, request, queryset):
    headers  =["ZONE", "SUPERVISOR", "AMOUNT", "DEPOSIT TYPE", "DATE"]
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="withdrawal_reports.csv"'},
    )
    writer = csv.writer(response)
    writer = csv.writer(response)
    writer.writerow(["DAILY SUPERVISOR DEPOSIT REPORTS"])
    writer.writerow(headers)
    sd = queryset.values_list("agent__profile__zone__name", "agent__username", "amount", "deposit_type", "date")
    for d in sd:
        writer.writerow(d)
    return response


generate_cashier_report.short_description = 'Export Cashier Reports as csv'
generate_supervisor_report.short_description = 'Export Supervisor Report as csv'
generate_cashier_deposit_report.short_description = 'Export Cashier Deposit Report as csv'
generate_supervisor_deposit_report.short_description = 'Export Supervisor Deposit Report as csv'
generate_withdrawal_report.short_description = 'Export Withdrawal Report as csv'

class MainVaultAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'zone', 'closing_balance', 'date']
    search_fields = ['reporter__username', 'zone__name', 'closing_balance', 'date']
    sortable_by = ['reporter__username','zone__name', 'closing_balance', 'date']
    filter_by = ['reporter__username','zone__name', 'closing_balance', 'date']
    list_filter = ['zone__name', 'date']
    readonly_fields = ['closing_balance', 'date']
    fieldsets = (
        ('Meta Information', {
            'classes': ('collapse',),
            'fields': ('reporter', 'zone', 'date')
        }),
        ('Vault Admin', {
            'classes': ('collapse',),
            'fields': ('closing_balance', 'status')
        }),
    )
    actions = [generate_supervisor_report]

class ZoneVaultAdmin(admin.ModelAdmin):
    list_display = ['cashier_name','zone', 'branch', 'closing_balance', 'date']
    search_fields = ['cashier_name','zone__name', 'branch__name', 'closing_balance', 'date']
    sortable_by = ['cashier_name','zone__name', 'branch__name', 'opening_cash', 'additional_cash',
                    'closing_balance', 'date']
    filter_by = ['cashier_name','zone__name', 'branch__name', 'location__name', 'date']
    list_filter = ['zone__name', 'branch__name', 'date']
    readonly_fields = ['closing_balance', 'date']
    fieldsets = (
        ('Meta Information', {
            'classes': ('collapse',),
            'fields': ('reporter', 'zone', 'branch', 'location', 'date')
        }),
        ('Vault Admin', {
            'classes': ('collapse',),
            'fields': ('closing_balance', 'status')
        }),
    )
    actions = [generate_cashier_report]

class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'balance', 'date']
    search_fields = ['name', 'owner', 'balance', 'date']
    sortable = ['name', 'owner', 'balance', 'date']
    list_filter = ['name', 'owner', 'balance', 'date']
    readonly_fields = ['balance', 'date']

class DepositAdmin(admin.ModelAdmin):
    list_display = ['agent', 'amount', 'account', 'deposit_type', 'cashier', 'supervisor', 'date']
    filter_by = ['agent__username', 'account__name', 'deposit_type', 'cashier', 'supervisor', 'date']
    list_filter = ['deposit_type', 'cashier', 'supervisor', 'date']
    sortable_by = ['agent__name', 'amount', 'account__name', 'deposit_type', 'date']
    search_fields = ['agent__username', 'amount', 'account__name', 'deposit_type', 'date']
    readonly_fields = ['agent', 'amount', 'account', 'deposit_type', 'date', 'cashier', 'supervisor']
    actions = [generate_cashier_deposit_report, generate_supervisor_deposit_report]

class WithdrawAdmin(admin.ModelAdmin):
    list_display = ['withdrawer', 'amount', 'account', 'date']
    sortable_by = ['withdrawer__username', 'amount', 'account__name', 'date']
    filter_by = ['withdrawer__username', 'approved', 'disapproved', 'date']
    list_filter = ['withdrawer__username', 'date']
    search_fields = ['withdrawer__username', 'amount', 'account__name', 'date']
    readonly_fields = ['withdrawer', 'amount', 'account', 'date']
    actions = [generate_withdrawal_report]

class BankDepositAdmin(admin.ModelAdmin):
    list_display = ['depositor', 'amount', 'account', 'date']
    sortable_by = ['depositor__username', 'amount', 'account__name', 'date']
    filter_by = ['depositor__username', 'approved', 'disapproved', 'date']
    list_filter = ['depositor__username', 'date']
    search_fields = ['depositor__username', 'amount', 'account__name', 'date']
    readonly_fields = ['depositor', 'amount', 'account', 'date']

class BankAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']
    sortable_by = ['name', 'date']
    filter_by = ['name', 'date']
    list_filter = ['name', 'date']
    search_fields = ['name', 'date']
    readonly_fields = ['date']

admin.site.register(MainVault, MainVaultAdmin)
admin.site.register(ZoneVault, ZoneVaultAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(Withdraw, WithdrawAdmin)
admin.site.register(BankDeposit, BankDepositAdmin)
admin.site.register(Bank, BankAdmin)
admin.site.register(Currency)
admin.site.register(CurrencyTransaction)