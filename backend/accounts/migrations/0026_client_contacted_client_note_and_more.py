# Generated by Django 4.0.7 on 2022-10-11 04:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_company_email_frequency_company_next_email_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='contacted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='client',
            name='note',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='company',
            name='next_email_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='homelisting',
            name='listed',
            field=models.CharField(default='2022-10-11 04:26:26.848847', max_length=30),
        ),
    ]