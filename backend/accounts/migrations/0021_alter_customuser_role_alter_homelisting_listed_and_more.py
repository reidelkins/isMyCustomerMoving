# Generated by Django 4.0.7 on 2022-09-16 04:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_homelisting_listed_alter_customuser_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('Backend Developer', 'Backend Developer'), ('Full Stack Designer', 'Full Stack Designer'), ('Front End Developer', 'Front End Developer'), ('Full Stack Developer', 'Full Stack Developer'), ('admin', 'admin')], default='Full Stack Developer', max_length=100),
        ),
        migrations.AlterField(
            model_name='homelisting',
            name='listed',
            field=models.CharField(default='2022-09-16 04:04:45.109548', max_length=30),
        ),
        migrations.AlterField(
            model_name='zipcode',
            name='lastUpdated',
            field=models.DateField(default='2022-09-15'),
        ),
        migrations.AlterField(
            model_name='zipcode',
            name='zipCode',
            field=models.IntegerField(primary_key=True, serialize=False, unique=True, validators=[django.core.validators.MinValueValidator(500), django.core.validators.MaxValueValidator(99951)]),
        ),
    ]