# Generated by Django 3.2.8 on 2023-07-15 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('payments', '0002_servicetitaninvoice'), ('payments', '0003_remove_servicetitaninvoice_street')]

    dependencies = [
        ('data', '0017_client_service_titan_lifetime_revenue'),
        ('payments', '0001_squashed_0006_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceTitanInvoice',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('amount', models.FloatField(default=0)),
                ('created_on', models.DateField(blank=True, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.client')),
            ],
        ),
    ]