# Generated by Django 4.0.7 on 2022-12-31 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_rename_name_product_tier'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='customerLimit',
            field=models.IntegerField(default=0),
        ),
    ]