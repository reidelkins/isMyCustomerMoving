# Generated by Django 3.2.8 on 2023-06-16 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_company_servicetitancustomersyncoption"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="zapier_recentlySold",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
