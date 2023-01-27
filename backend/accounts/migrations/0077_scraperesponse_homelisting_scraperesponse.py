# Generated by Django 4.1 on 2023-01-27 14:42

import accounts.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0076_alter_clientupdate_listed"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScrapeResponse",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("date", models.DateField(default=accounts.models.formatToday)),
                ("response", models.TextField(default="")),
                ("zip", models.IntegerField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("House For Sale", "House For Sale"),
                            ("House For Rent", "House For Rent"),
                            ("House Recently Sold (6)", "House Recently Sold (6)"),
                            ("Recently Sold (12)", "Recently Sold (12)"),
                            ("Taken Off Market", "Taken Off Market"),
                            ("No Change", "No Change"),
                        ],
                        default="No Change",
                        max_length=25,
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="homelisting",
            name="ScrapeResponse",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="accounts.scraperesponse",
            ),
        ),
    ]
