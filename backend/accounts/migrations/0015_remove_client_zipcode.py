# Generated by Django 4.0.7 on 2022-09-14 03:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_alter_client_zipcode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='zipCode',
        ),
    ]
