from django.db import models
from data.models import Client

INTERVALS = [("month", "month"), ("year", "year")]


class Product(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    amount = models.FloatField(default=0)
    interval = models.CharField(
        max_length=10, choices=INTERVALS, default="month"
    )
    name = models.CharField(max_length=100)


class ServiceTitanInvoice(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    amount = models.FloatField(default=0)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    street = models.CharField(max_length=100, blank=True, null=True)
    created_on = models.DateField(blank=True, null=True)
