# Generated by Django 4.0.7 on 2022-10-11 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0031_alter_homelisting_listed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homelisting',
            name='listed',
            field=models.CharField(default=' ', max_length=30),
        ),
    ]
