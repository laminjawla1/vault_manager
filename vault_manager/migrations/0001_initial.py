# Generated by Django 4.1.7 on 2023-10-12 09:37

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('owner', models.CharField(max_length=100)),
                ('balance', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Currencies',
            },
        ),
        migrations.CreateModel(
            name='ZoneVault',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cashier_name', models.CharField(max_length=50)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('opening_cash', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('additional_cash', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('closing_balance', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('status', models.BooleanField(default=False)),
                ('branch', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='agents.branch')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('zone', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='agents.zone')),
            ],
            options={
                'verbose_name_plural': 'Zone Vault',
            },
        ),
        migrations.CreateModel(
            name='Withdraw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cheque_number', models.CharField(max_length=100)),
                ('amount', models.FloatField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='cheque_images')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vault_manager.account')),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vault_manager.bank')),
                ('withdrawer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Withdrawals',
            },
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refund_type', models.CharField(choices=[('Add to Opening Cash', 'Add to Opening Cash'), ('Add to Additional Cash', 'Add to Additional Cash'), ('Deduct from Opening Cash', 'Deduct from Opening Cash'), ('Deduct from Additional Cash', 'Deduct from Additional Cash')], max_length=50)),
                ('amount', models.FloatField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MainVault',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('opening_cash', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('additional_cash', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('closing_balance', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('status', models.BooleanField(default=False)),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('zone', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='agents.zone')),
            ],
            options={
                'verbose_name_plural': 'Main Vault',
            },
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deposit_type', models.CharField(choices=[('Opening Cash', 'Opening Cash'), ('Additional Cash', 'Additional Cash')], max_length=50)),
                ('amount', models.FloatField()),
                ('status', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('cashier', models.BooleanField(default=False)),
                ('supervisor', models.BooleanField(default=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vault_manager.account')),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CurrencyTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=50)),
                ('phone_number', models.CharField(max_length=50)),
                ('id_number', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('buy', 'buy'), ('sell', 'sell')], max_length=20)),
                ('currency_amount', models.FloatField()),
                ('rate', models.FloatField()),
                ('total_amount', models.FloatField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.BooleanField(default=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vault_manager.account')),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vault_manager.currency')),
            ],
        ),
        migrations.CreateModel(
            name='Borrow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(default='', max_length=61)),
                ('address', models.CharField(default='', max_length=100)),
                ('phone', models.CharField(default='', max_length=20)),
                ('amount', models.FloatField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.BooleanField(default=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vault_manager.account')),
                ('borrower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Withdrawals',
            },
        ),
        migrations.CreateModel(
            name='BankDeposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vault_manager.account')),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vault_manager.bank')),
                ('depositor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
