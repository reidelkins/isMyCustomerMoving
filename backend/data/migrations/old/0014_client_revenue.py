# Generated by Django 3.2.8 on 2023-05-29 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0013_auto_20230526_0753"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="revenue",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]