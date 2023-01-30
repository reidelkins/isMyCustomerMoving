from django.contrib import admin
from .models import Product

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'tier', 'timeFrame', 'pid', 'customerLimit')

admin.site.register(Product, ProductAdmin)