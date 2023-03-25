# Generated by Django 4.1.7 on 2023-03-11 08:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("agents", "0001_initial"),
        ("vault_manager", "0002_rename_approved_deposit_status_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="mainvault",
            options={"verbose_name_plural": "Main Vault"},
        ),
        migrations.AlterModelOptions(
            name="zonevault",
            options={"verbose_name_plural": "Zone Vault"},
        ),
        migrations.AddField(
            model_name="zonevault",
            name="branch",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                to="agents.branch",
            ),
        ),
        migrations.AddField(
            model_name="zonevault",
            name="zone",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                to="agents.zone",
            ),
        ),
    ]
