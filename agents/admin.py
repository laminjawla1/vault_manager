from django.contrib import admin
from agents.models import Profile, Zone, Branch, Ledger
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

class UserProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    readonly_fields = ['opening_cash', 'additional_cash', 'balance', 'closing_balance']

class AccountsUserAdmin(AuthUserAdmin):
    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(AccountsUserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [UserProfileInline]
        return super(AccountsUserAdmin, self).change_view(*args, **kwargs)

class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'teller')
    filter_by = ['name', 'teller']
    search_fields = ('name', 'teller__username')
    sortable_by = ['name', 'teller__username']

class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'supervisor')
    search_fields = ('name', 'supervisor__username')
    sortable_by = ['name', 'supervisor__username']

class LedgerAdmin(admin.ModelAdmin):
    list_display = ('agent', 'added_by', 'narration', 'debit', 'credit', 'balance', 'date')
    search_fields = ('agent__username', 'added_by__username', 'date')
    sortable_by = ['agent__username', 'action', 'date']

admin.site.unregister(User)
admin.site.register(User, AccountsUserAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(Ledger, LedgerAdmin)