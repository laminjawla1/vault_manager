# Generated by Django 4.1.7 on 2023-10-28 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vault_manager', '0010_currencytransaction_date_set_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='currencytransaction',
            name='date_set',
        ),
    ]
