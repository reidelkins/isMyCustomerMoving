# Generated by Django 4.2.2 on 2023-06-29 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20230622_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='for_sale_purchased',
            field=models.BooleanField(default=False),
        ),
    ]