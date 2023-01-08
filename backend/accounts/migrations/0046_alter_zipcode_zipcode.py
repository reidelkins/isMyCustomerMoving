# Generated by Django 4.0.7 on 2022-12-31 22:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0045_alter_zipcode_lastupdated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zipcode',
            name='zipCode',
            field=models.IntegerField(primary_key=True, serialize=False, unique=True, validators=[django.core.validators.MinValueValidator(10000), django.core.validators.MaxValueValidator(99951)]),
        ),
    ]