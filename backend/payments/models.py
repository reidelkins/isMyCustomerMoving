from django.db import models

INTERVALS = [("month", "month"), ("year", "year")]


class Product(models.Model):
    id = models.CharField(max_length=100)
    amount = models.FloatField(default=0)
    interval = models.CharField(
        max_length=10, choices=INTERVALS, default="month"
    )
    name = models.CharField(max_length=100)
