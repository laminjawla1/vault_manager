# Generated by Django 4.1.7 on 2023-04-01 13:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vault_manager", "0018_alter_withdraw_bank"),
    ]

    operations = [
        migrations.AlterField(
            model_name="withdraw",
            name="bank",
            field=models.ForeignKey(
                blank=True,
                default="Yonna",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="vault_manager.bank",
            ),
        ),
    ]