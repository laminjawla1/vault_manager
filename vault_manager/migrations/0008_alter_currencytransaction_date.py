# Generated by Django 4.1.7 on 2023-10-28 12:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vault_manager', '0007_alter_currencytransaction_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencytransaction',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 10, 28, 12, 11, 46, 798223, tzinfo=datetime.timezone.utc)),
        ),
    ]
