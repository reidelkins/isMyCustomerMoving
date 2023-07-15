from rest_framework import serializers
from .models import Product


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=100, read_only=True)
    amount = serializers.FloatField(read_only=True)
    interval = serializers.CharField(max_length=100, read_only=True)
    name = serializers.CharField(max_length=100, read_only=True)

    class Meta:
        model = Product
        fields = ("id", "amount", "interval", "name")
