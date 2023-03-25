# Generated by Django 4.1.7 on 2023-03-20 08:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("agents", "0002_alter_branch_teller_alter_zone_supervisor"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="branch",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="agents.branch",
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="zone",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="agents.zone",
            ),
        ),
    ]
