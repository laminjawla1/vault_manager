from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from agents.models import Zone, Branch
from django.urls import reverse
from django.core.validators import MinValueValidator

class MainVault(models.Model):
    class Meta:
        verbose_name_plural = "Main Vault"

    date = models.DateTimeField(null=False, default=timezone.now)
    opening_cash = models.FloatField(blank=False, null=False,validators=[MinValueValidator(0)], default=0)
    additional_cash = models.FloatField(blank=False, null=False,validators=[MinValueValidator(0)], default=0)
    closing_balance = models.FloatField(blank=False, null=False,validators=[MinValueValidator(0)])
    status = models.BooleanField(default=False)

    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="approved_by", null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, default="")

    def __str__(self):
        return f"{self.reporter.username}"
    
    def get_absolute_url(self):
        return reverse('reports')


class Account(models.Model):

    date = models.DateTimeField(null=False, default=timezone.now)
    name = models.CharField(max_length=100, unique=True, null=False)
    owner = models.CharField(max_length=100, null=False)
    balance = models.FloatField(null=False, default=0)

    def __str__(self):
        return f"{self.name}"


# Zone Vault
class ZoneVault(models.Model):
    class Meta:
        verbose_name_plural = "Zone Vault"
    cashier_name = models.CharField(max_length=50)
    date = models.DateTimeField(null=False, default=timezone.now)
    opening_cash = models.FloatField(blank=False, null=False,validators=[MinValueValidator(0)], default=0)
    additional_cash = models.FloatField(blank=False, null=False,validators=[MinValueValidator(0)], default=0)
    closing_balance = models.FloatField(blank=False, null=False,validators=[MinValueValidator(0)], default=0)
    status = models.BooleanField(default=False)

    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="zone_vault_approval", null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, default="")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, default="")

    def __str__(self) -> str:
        return f"Opening cash: {self.opening_cash}"
    
    def get_absolute_url(self):
        return reverse("reports")
    

class Deposit(models.Model):
    deposit_type = models.CharField(max_length=50, choices=[('Opening Cash', 'Opening Cash'), ('Additional Cash', 'Additional Cash')])
    amount = models.FloatField(blank=False, null=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(null=False, default=timezone.now)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deposit_approval", null=True, blank=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    cashier = models.BooleanField(default=False)
    supervisor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.agent}"
    
    def get_absolute_url(self):
        if self.cashier:
            return reverse('cashier_deposits')
        return reverse('supervisor_deposits')

class Refund(models.Model):
    refund_type = models.CharField(max_length=50, choices=[('Add to Opening Cash', 'Add to Opening Cash'), 
                                                        ('Add to Additional Cash', 'Add to Additional Cash'),
                                                        ('Deduct from Opening Cash', 'Deduct from Opening Cash'),
                                                        ('Deduct from Additional Cash', 'Deduct from Additional Cash')])
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(blank=False, null=False)
    date = models.DateTimeField(null=False, default=timezone.now)
    refunded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refunded_by", null=True, blank=True)

    def __str__(self):
        return f"{self.agent}"
    
    def get_absolute_url(self):
        return reverse('refunds')

class Bank(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateTimeField(null=False, default=timezone.now)

    def __str__(self):
        return self.name
    
class Withdraw(models.Model):
    class Meta:
        verbose_name_plural = "Withdrawals"

    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    cheque_number = models.CharField(max_length=100)
    amount = models.FloatField(blank=False, null=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, default=timezone.now)
    status = models.BooleanField(default=False)
    withdrawer = models.ForeignKey(User, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdrawal_approval", null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='cheque_images', null=True, blank=True)

    def __str__(self):
        return f"{self.withdrawer}"
    
    def get_absolute_url(self):
        if self.withdrawer.profile.is_supervisor and not self.withdrawer.is_staff:
            return reverse('my_withdrawals')
        return reverse('withdrawals')
    
class BankDeposit(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    amount = models.FloatField(blank=False, null=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, default=timezone.now)
    status = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bank_deposit_approval", null=True, blank=True)
    depositor = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.depositor}"
    
    def get_absolute_url(self):
        if self.depositor.profile.is_supervisor:
            return reverse('my_bank_deposits')
        return reverse('bank_deposits')
    
class Borrow(models.Model):
    class Meta:
        verbose_name_plural = "Withdrawals"

    customer_name = models.CharField(max_length=61, default="")
    address = models.CharField(max_length=100, default="")
    phone = models.CharField(max_length=20, default="")
    amount = models.FloatField(blank=False, null=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, default=timezone.now)
    status = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrow_approval", null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.borrower}"
    
    def get_absolute_url(self):
        if self.borrower.profile.is_supervisor and not self.borrower.is_staff:
            return reverse('my_borrows')
        return reverse('borrows')

class Currency(models.Model):
    class Meta:
        verbose_name_plural = "Currencies"
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class CurrencyTransaction(models.Model):
    customer_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)
    id_number = models.CharField(max_length=50)
    type = models.CharField(max_length=20, choices=(('buy', 'buy'), ('sell', 'sell')))
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    currency_amount = models.FloatField()
    rate = models.FloatField()
    total_amount = models.FloatField()
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, default=timezone.now)
    status = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="current_approval", null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return self.customer_name
    
    def get_absolute_url(self):
        return reverse('currency_transactions')