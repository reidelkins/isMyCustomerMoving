# Generated by Django 4.0 on 2023-03-01 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_client_company_alter_client_zipcode_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referral',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referralClient', to='data.client'),
        ),
    ]