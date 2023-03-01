# Generated by Django 4.0 on 2023-03-01 20:01

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_client_unique_together_remove_client_company_and_more'),
        ('data', '0001_initial'),
    ]

    operations = [
        # migrations.AlterUniqueTogether(
        #     name='client',
        #     unique_together={('address')},
        # ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('contacted', models.BooleanField(default=False)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referralClient', to='data.client')),
                ('franchise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.franchise')),
                ('referredFrom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referredFrom', to='accounts.company')),
                ('referredTo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referredTo', to='accounts.company')),
            ],
        ),
    ]
