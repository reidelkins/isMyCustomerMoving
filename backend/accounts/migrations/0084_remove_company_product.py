# Generated by Django 4.0 on 2023-02-21 03:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0083_company_sfrefreshtoken'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='product',
        ),
    ]