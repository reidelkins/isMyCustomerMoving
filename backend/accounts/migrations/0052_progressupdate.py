# Generated by Django 4.0.7 on 2023-01-08 17:20

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0051_company_servicetitanforrenttagid_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgressUpdate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('percentDone', models.IntegerField(default=0)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.company')),
            ],
        ),
    ]