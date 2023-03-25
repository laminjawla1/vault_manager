# Generated by Django 4.1.7 on 2023-03-21 12:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vault_manager", "0009_refund"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mainvault",
            name="cad_dollar",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="mainvault",
            name="cfa",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="mainvault",
            name="denish_krona",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="mainvault",
            name="euro",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="mainvault",
            name="gbp_pound",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="mainvault",
            name="swiss_franck",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="mainvault",
            name="swiss_krona",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="mainvault",
            name="us_dollar",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="zonevault",
            name="cad_dollar",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="zonevault",
            name="cfa",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="zonevault",
            name="denish_krona",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="zonevault",
            name="euro",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="zonevault",
            name="gbp_pound",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="zonevault",
            name="nor_krona",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="zonevault",
            name="swiss_franck",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="zonevault",
            name="swiss_krona",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="zonevault",
            name="us_dollar",
            field=models.IntegerField(
                blank=True,
                default=0,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10000),
                ],
            ),
        ),
    ]
