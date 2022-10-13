# Generated by Django 4.0.7 on 2022-09-20 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_alter_client_zipcode_alter_homelisting_listed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='city',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='state',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='homelisting',
            name='listed',
            field=models.CharField(default='2022-09-20 15:20:06.946749', max_length=30),
        ),
    ]
