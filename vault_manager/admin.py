from django.contrib import admin
from .models import MainVault, ZoneVault, Withdraw, Deposit, Account
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
import csv


def generate_cashier_report(modeladmin, request, queryset):
    if not request.user.is_staff:
        raise PermissionDenied()
    cr = ZoneVault.objects.all().order_by("date")

    headers  =["ZONE", "BRANCH", "TELLER", "OPENING CASH", "ADDITIONAL CASH", "TOTAL", "CLOSING BALANCE", "EURO", 
               "USD", "GBP", "CFA", "Swiss Krona", "Nor Krona", "Swiss Franck", "Denish Krona", "Cad Dollar", "DATE"]
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="cashier_reports.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(["DAILY CASHIER REPORTS"])
    writer.writerow(headers)
    for r in cr:
        writer.writerow((r.reporter.profile.zone.name, r.reporter.profile.branch.name, f'{r.reporter.first_name} {r.reporter.last_name}',
                                r.opening_cash, r.additional_cash, r.opening_cash + r.additional_cash, r.closing_balance,
                                r.euro, r.us_dollar, r.gbp_pound, r.cfa, r.swiss_krona, r.nor_krona, r.swiss_franck, r.denish_krona, 
                                r.cad_dollar, r.date.strftime("%Y-%m-%d")))
    return response

def generate_supervisor_report(modeladmin, request, queryset):
    
    cr = MainVault.objects.all().order_by("date")
    
    headers  =["ZONE", "SUPERVISOR", "OPENING CASH", "ADDITIONAL CASH", "TOTAL", "CLOSING BALANCE", "EURO", 
               "USD", "GBP", "CFA", "Swiss Krona", "Nor Krona", "Swiss Franck", "Denish Krona", "Cad Dollar", "DATE"]
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="supervisor_reports.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(["DAILY SUPERVISOR REPORTS"])
    writer.writerow(headers)
    for r in cr:
        writer.writerow((r.reporter.profile.zone.name, f'{r.reporter.first_name} {r.reporter.last_name}',
                                r.opening_cash, r.additional_cash, r.opening_cash + r.additional_cash, r.closing_balance,
                                r.euro, r.us_dollar, r.gbp_pound, r.cfa, r.swiss_krona, r.nor_krona, r.swiss_franck, r.denish_krona, 
                                r.cad_dollar, r.date.strftime("%Y-%m-%d")))
    return response

def generate_withdrawal_report(modeladmin, request, queryset):
    dw = Withdraw.objects.all().order_by("date")
    headers  =["AGENT FULLNAME", "ZONE", "AMOUNT","STATUS", "DATE"]
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="withdrawal_reports.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(["DAILY WITHDRAWAL REPORTS"])
    writer.writerow(headers)
    for w in dw:
        writer.writerow((f'{w.withdrawer.first_name} {w.withdrawer.last_name}', w.withdrawer.profile.zone.name,
                          w.amount, w.status, w.date.strftime("%Y-%m-%d")))

    return response

def generate_cashier_deposit_report(modeladmin, request, queryset):
    cd = Deposit.objects.filter(cashier=True).all().order_by("date")
    headers  =["ZONE", "BRANCH", "TELLER", "AMOUNT", "DEPOSIT TYPE", "DATE"]
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="withdrawal_reports.csv"'},
    )
    writer = csv.writer(response)
    writer = csv.writer(response)
    writer.writerow(["DAILY CASHIER DEPOSIT REPORTS"])
    writer.writerow(headers)
    for d in cd:
        writer.writerow((d.agent.profile.zone.name, d.agent.profile.branch.name, f'{d.agent.first_name} {d.agent.last_name}',
                         d.amount, d.deposit_type, d.date.strftime("%Y-%m-%d")))
    return response

def generate_supervisor_deposit_report(modeladmin, request, queryset):
    sd = Deposit.objects.filter(supervisor=True).all().order_by("date")
    headers  =["ZONE", "SUPERVISOR", "AMOUNT", "DEPOSIT TYPE", "DATE"]
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="withdrawal_reports.csv"'},
    )
    writer = csv.writer(response)
    writer = csv.writer(response)
    writer.writerow(["DAILY SUPERVISOR DEPOSIT REPORTS"])
    writer.writerow(headers)
    for d in sd:
        writer.writerow((d.agent.profile.zone.name, f'{d.agent.first_name} {d.agent.last_name}', d.amount, d.deposit_type, 
                         d.date.strftime("%Y-%m-%d")))

    return response

generate_cashier_report.short_description = 'Export Cashier Reports as csv'
generate_supervisor_report.short_description = 'Export Supervisor Report as csv'
generate_cashier_deposit_report.short_description = 'Export Cashier Deposit Report as csv'
generate_supervisor_deposit_report.short_description = 'Export Supervisor Deposit Report as csv'
generate_withdrawal_report.short_description = 'Export Withdrawal Report as csv'

class MainVaultAdmin(admin.ModelAdmin):
    list_display = ['reporter','zone', 'opening_cash', 'additional_cash', 'closing_balance', 'date']
    search_fields = ['reporter__username','zone__name', 'opening_cash', 'additional_cash', 'closing_balance', 'date']
    sortable_by = ['reporter__username','zone__name', 'opening_cash', 'additional_cash', 'closing_balance', 'date']
    filter_by = ['reporter__username','zone__name', 'opening_cash', 'additional_cash', 'closing_balance', 'date']
    list_filter = ['reporter__username','zone__name', 'date']
    readonly_fields = ['opening_cash', 'additional_cash', 'closing_balance', 'date', 'euro', 'us_dollar', 
                       'gbp_pound', 'swiss_krona', 'nor_krona', 'swiss_franck', 'cfa', 'denish_krona', 'cad_dollar']
    fieldsets = (
        ('Meta Information', {
            'classes': ('collapse',),
            'fields': ('reporter', 'zone', 'date')
        }),
        ('Currencies', {
            'classes': ('collapse',),
            'fields': ('euro', 'us_dollar', 'gbp_pound', 'swiss_krona', 'nor_krona', 'swiss_franck', 'cfa', 'denish_krona', 'cad_dollar')
        }),
        ('Vault Admin', {
            'classes': ('collapse',),
            'fields': ('opening_cash', 'additional_cash', 'closing_balance', 'status')
        }),
    )
    actions = [generate_supervisor_report]

class ZoneVaultAdmin(admin.ModelAdmin):
    list_display = ['reporter','zone', 'branch', 'opening_cash', 'additional_cash', 'closing_balance', 'date']
    search_fields = ['reporter__username','zone__name', 'branch__name', 'opening_cash', 'additional_cash', 'closing_balance', 'date']
    sortable_by = ['reporter__username','zone__name', 'branch__name','opening_cash', 'additional_cash', 'closing_balance', 'date']
    filter_by = ['reporter__username','zone__name', 'branch__name', 'date']
    list_filter = ['reporter__username','zone__name', 'branch__name', 'date']
    readonly_fields = ['opening_cash', 'additional_cash', 'closing_balance', 'date', 'euro', 'us_dollar', 
                       'gbp_pound', 'swiss_krona', 'nor_krona', 'swiss_franck', 'cfa', 'denish_krona', 'cad_dollar']
    fieldsets = (
        ('Meta Information', {
            'classes': ('collapse',),
            'fields': ('reporter', 'zone', 'branch', 'date')
        }),
        ('Currencies', {
            'classes': ('collapse',),
            'fields': ('euro', 'us_dollar', 'gbp_pound', 'swiss_krona', 'nor_krona', 'swiss_franck', 'cfa', 'denish_krona', 'cad_dollar')
        }),
        ('Vault Admin', {
            'classes': ('collapse',),
            'fields': ('opening_cash', 'additional_cash', 'closing_balance', 'status')
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
    list_display = ['agent', 'amount', 'account', 'deposit_type', 'status', 'date']
    filter_by = ['agent__username', 'account__name', 'deposit_type', 'status', 'date']
    list_filter = ['agent__username', 'account__name', 'deposit_type', 'status', 'date']
    sortable_by = ['agent__name', 'amount', 'account__name', 'deposit_type', 'status', 'date']
    search_fields = ['agent__username', 'amount', 'account__name', 'deposit_type', 'status', 'date']
    readonly_fields = ['agent', 'amount', 'account', 'deposit_type', 'status', 'date', 'cashier', 'supervisor']
    actions = [generate_cashier_deposit_report, generate_supervisor_deposit_report]

class WithdrawAdmin(admin.ModelAdmin):
    list_display = ['withdrawer', 'amount', 'account', 'status', 'date']
    sortable_by = ['withdrawer__username', 'amount', 'account__name', 'status', 'date']
    filter_by = ['withdrawer__username', 'status', 'date']
    list_filter = ['withdrawer__username', 'status', 'date']
    search_fields = ['withdrawer__username', 'amount', 'account__name', 'status', 'date']
    readonly_fields = ['withdrawer', 'amount', 'account', 'status', 'date']
    actions = [generate_withdrawal_report]

admin.site.register(MainVault, MainVaultAdmin)
admin.site.register(ZoneVault, ZoneVaultAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(Withdraw, WithdrawAdmin)