# Generated by Django 4.2.5 on 2023-09-30 06:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0019_homelisting_url'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ScrapeResponse',
        ),
    ]