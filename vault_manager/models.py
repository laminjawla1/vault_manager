from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from agents.models import Zone, Branch
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator

class MainVault(models.Model):
    class Meta:
        verbose_name_plural = "Main Vault"

    date = models.DateTimeField(null=False, default=timezone.now)
    opening_cash = models.FloatField(blank=False, null=False,validators=[MinValueValidator(0)])
    additional_cash = models.FloatField(blank=False, null=False,validators=[MinValueValidator(0)])

    euro = models.IntegerField(blank=True, null=True, default=0,  validators=[MinValueValidator(0), MaxValueValidator(10000)])
    us_dollar = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    gbp_pound = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    swiss_krona = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    nor_krona = models.IntegerField(blank=True, null=True, default=0)
    swiss_franck = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    cfa = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    denish_krona = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    cad_dollar = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])

    closing_balance = models.FloatField(blank=False, null=False,validators=[MinValueValidator(0)])
    status = models.BooleanField(default=False)

    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
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


# Zone Valut
class ZoneVault(models.Model):
    class Meta:
        verbose_name_plural = "Zone Vault"
    @property
    def gmd(value):
        """Format value as GMD"""
        if not "GMD" in str(value):
            return f"GMD {value:,.2f}"
        return value
    date = models.DateTimeField(null=False, default=timezone.now)
    opening_cash = models.FloatField(blank=False, null=False,validators=[MinValueValidator(0)])
    additional_cash = models.FloatField(blank=False, null=False,validators=[MinValueValidator(0)])

    # Currencies
    euro = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    us_dollar = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    gbp_pound = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    swiss_krona = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    nor_krona = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    swiss_franck = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    cfa = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    denish_krona = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])
    cad_dollar = models.IntegerField(blank=True, null=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(10000)])

    # closing
    closing_balance = models.FloatField(blank=False, null=False,validators=[MinValueValidator(0)])
    status = models.BooleanField(default=False)

    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
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
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    cashier = models.BooleanField(default=False)
    supervisor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.agent}"
    
    def get_absolute_url(self):
        if self.cashier:
            return reverse('my_deposits')
        return reverse('supervisor_deposits')

class Refund(models.Model):
    @property
    def gmd(value):
        """Format value as GMD"""
        if not "GMD" in str(value):
            return f"GMD {value:,.2f}"
        return value

    refund_type = models.CharField(max_length=50, choices=[('Add to Opening Cash', 'Add to Opening Cash'), 
                                                           ('Add to Additional Cash', 'Add to Additional Cash'),
                                                           ('Deduct from Opening Cash', 'Deduct from Opening Cash'),
                                                           ('Deduct from Additional Cash', 'Deduct from Additional Cash')])
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(blank=False, null=False)
    date = models.DateTimeField(null=False, default=timezone.now)

    def __str__(self):
        return f"{self.agent}"
    
    def get_absolute_url(self):
        return reverse('refunds')

class Withdraw(models.Model):
    class Meta:
        verbose_name_plural = "Withdrawals"
    @property
    def gmd(value):
        """Format value as GMD"""
        if not "GMD" in str(value):
            return f"GMD {value:,.2f}"
        return value

    amount = models.FloatField(blank=False, null=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, default=timezone.now)
    status = models.BooleanField(default=False)
    withdrawer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.withdrawer}"
    
    def get_absolute_url(self):
        if self.withdrawer.profile.is_supervisor:
            return reverse('my_withdrawals')
        return reverse('withdrawals')
