from django.db import models
from data.models import Client

import uuid

INTERVALS = [("month", "month"), ("year", "year")]


class Product(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    amount = models.FloatField(default=0)
    interval = models.CharField(
        max_length=10, choices=INTERVALS, default="month"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        if self.interval == "month":
            return f"${self.amount}/month"
        else:
            return f"${self.amount}/year"


class CRMInvoice(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    invoice_id = models.CharField(max_length=100)
    amount = models.FloatField(default=0)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_on = models.DateField(blank=True, null=True)
    attributed = models.BooleanField(default=False)
    existing_client = models.BooleanField(default=False)
