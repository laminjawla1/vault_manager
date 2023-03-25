# Generated by Django 4.1.7 on 2023-03-25 13:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "vault_manager",
            "0010_alter_mainvault_cad_dollar_alter_mainvault_cfa_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="mainvault",
            name="additional_cash",
            field=models.FloatField(
                validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
        migrations.AlterField(
            model_name="mainvault",
            name="closing_balance",
            field=models.FloatField(
                validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
        migrations.AlterField(
            model_name="mainvault",
            name="opening_cash",
            field=models.FloatField(
                validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
        migrations.AlterField(
            model_name="zonevault",
            name="additional_cash",
            field=models.FloatField(
                validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
        migrations.AlterField(
            model_name="zonevault",
            name="closing_balance",
            field=models.FloatField(
                validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
        migrations.AlterField(
            model_name="zonevault",
            name="opening_cash",
            field=models.FloatField(
                validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
    ]
