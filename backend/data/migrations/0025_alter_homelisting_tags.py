# Generated by Django 4.2.5 on 2023-10-20 02:54

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0024_alter_client_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homelisting',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, null=True, size=None),
        ),
    ]
