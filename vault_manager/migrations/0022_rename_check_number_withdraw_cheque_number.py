# Generated by Django 4.1.7 on 2023-04-01 13:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("vault_manager", "0021_alter_withdraw_bank"),
    ]

    operations = [
        migrations.RenameField(
            model_name="withdraw",
            old_name="check_number",
            new_name="cheque_number",
        ),
    ]
