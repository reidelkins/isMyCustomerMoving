# Generated by Django 4.0 on 2023-03-02 04:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_client_company_alter_client_zipcode_and_more'),
    ]

    operations = [                
        migrations.AddField(
            model_name='company',
            name='franchise',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.franchise'),
        )
    ]
