# Generated by Django 4.1.7 on 2023-04-04 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vault_manager", "0029_currencytransaction_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="currencytransaction",
            name="status",
            field=models.BooleanField(default=False),
        ),
    ]
