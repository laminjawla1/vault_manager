# Generated by Django 4.1.7 on 2023-03-20 08:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("vault_manager", "0008_delete_deposittype"),
    ]

    operations = [
        migrations.CreateModel(
            name="Refund",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "refund_type",
                    models.CharField(
                        choices=[
                            ("Add to Opening Cash", "Add to Opening Cash"),
                            ("Add to Additional Cash", "Add to Additional Cash"),
                            ("Deduct from Opening Cash", "Deduct from Opening Cash"),
                            (
                                "Deduct from Additional Cash",
                                "Deduct from Additional Cash",
                            ),
                        ],
                        max_length=50,
                    ),
                ),
                ("amount", models.FloatField()),
                ("date", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "agent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
