# Generated by Django 3.2.8 on 2023-05-01 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0009_alter_homelisting_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homelistingtags",
            name="tag",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]