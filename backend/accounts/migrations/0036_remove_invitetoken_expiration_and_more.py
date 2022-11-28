# Generated by Django 4.0.7 on 2022-11-28 23:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0035_alter_company_accesstoken_alter_zipcode_lastupdated_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invitetoken',
            name='expiration',
        ),
        migrations.AlterField(
            model_name='company',
            name='accessToken',
            field=models.CharField(default='nkBWJntAb5rT8VNUXvKKQbvSDJFTXlva', max_length=100),
        ),
        migrations.AlterField(
            model_name='company',
            name='next_email_date',
            field=models.DateField(default=datetime.datetime(2022, 11, 28, 23, 4, 15, 309628)),
        ),
        migrations.AlterField(
            model_name='zipcode',
            name='lastUpdated',
            field=models.DateField(default='2022-11-27'),
        ),
    ]
