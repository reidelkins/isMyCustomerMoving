# Generated by Django 3.2.8 on 2023-07-15 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0016_auto_20230713_0021'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='service_titan_lifetime_revenue',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
