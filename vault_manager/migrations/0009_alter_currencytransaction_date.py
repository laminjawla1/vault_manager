# Generated by Django 4.1.7 on 2023-10-28 12:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('vault_manager', '0008_alter_currencytransaction_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencytransaction',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]