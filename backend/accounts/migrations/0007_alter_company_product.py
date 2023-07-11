# Generated by Django 3.2.8 on 2023-07-08 22:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_product'),
        ('accounts', '0006_auto_20230526_0753_squashed_0012_alter_company_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='product',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payments.product'),
        ),
    ]
