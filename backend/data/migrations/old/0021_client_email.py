# Generated by Django 3.2.8 on 2023-08-21 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0020_auto_20230722_0048'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='email',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]