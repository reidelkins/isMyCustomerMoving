from django.contrib import admin
from .models import Product, CRMInvoice


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'amount', 'interval']


class CRMInvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'client', 'created_on', 'attributed']
    list_filter = ['attributed']


# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(CRMInvoice, CRMInvoiceAdmin)
