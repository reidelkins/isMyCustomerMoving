# Generated by Django 3.2.8 on 2023-04-14 18:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("djstripe", "0011_2_7"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="serviceTitanForSaleContactedTagID",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="company",
            name="serviceTitanRecentlySoldContactedTagID",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
