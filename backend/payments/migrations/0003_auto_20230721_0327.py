# Generated by Django 3.2.8 on 2023-07-21 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_servicetitaninvoice_squashed_0003_remove_servicetitaninvoice_street'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicetitaninvoice',
            name='attributed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='servicetitaninvoice',
            name='existing_client',
            field=models.BooleanField(default=False),
        ),
    ]