# Generated by Django 4.0.7 on 2022-09-15 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_homelisting_listed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='status',
            field=models.CharField(choices=[('active', 'ACTIVE'), ('banned', 'BANNED'), ('admin', 'ADMIN')], default='active', max_length=100),
        ),
        migrations.AlterField(
            model_name='homelisting',
            name='listed',
            field=models.CharField(default='2022-09-15 00:05:51.011394', max_length=30),
        ),
        migrations.AlterField(
            model_name='zipcode',
            name='lastUpdated',
            field=models.DateField(default='2022-09-14'),
        ),
    ]