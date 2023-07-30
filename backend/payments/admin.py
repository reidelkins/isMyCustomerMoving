from django.contrib import admin
from .models import Product, ServiceTitanInvoice


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'amount', 'interval']


class ServiceTitanInvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'client', 'created_on', 'attributed']
    list_filter = ['attributed']


# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(ServiceTitanInvoice, ServiceTitanInvoiceAdmin)
