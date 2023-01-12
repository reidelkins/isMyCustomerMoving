# Generated by Django 4.0.7 on 2023-01-11 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0057_alter_client_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='status',
            field=models.CharField(choices=[('For Sale', 'For Sale'), ('For Rent', 'For Rent'), ('Recently Sold (6)', 'Recently Sold (6)'), ('Recently Sold (12)', 'Recently Sold (12)'), ('Taken Off Market', 'Taken Off Market'), ('No Change', 'No Change')], default='No Change', max_length=20),
        ),
        migrations.AlterField(
            model_name='homelisting',
            name='status',
            field=models.CharField(choices=[('For Sale', 'For Sale'), ('For Rent', 'For Rent'), ('Recently Sold (6)', 'Recently Sold (6)'), ('Recently Sold (12)', 'Recently Sold (12)'), ('Taken Off Market', 'Taken Off Market'), ('No Change', 'No Change')], default='Off Market', max_length=20),
        ),
    ]