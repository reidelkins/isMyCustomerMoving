# Generated by Django 3.2.8 on 2023-05-16 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0011_auto_20230505_0014"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="latitude",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="client",
            name="longitude",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
