# Generated by Django 4.0.7 on 2022-09-14 00:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_client_company_alter_customuser_company'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='company',
        ),
    ]