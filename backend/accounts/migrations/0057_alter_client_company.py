# Generated by Django 4.0.7 on 2023-01-10 04:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0056_task_deleted_alter_task_updater'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.company'),
        ),
    ]
