# Generated by Django 4.0.7 on 2023-01-09 03:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0053_task'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='completed',
            new_name='complete',
        ),
        migrations.RemoveField(
            model_name='task',
            name='ProgressUpdate',
        ),
        migrations.AddField(
            model_name='task',
            name='updater',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.progressupdate'),
        ),
    ]