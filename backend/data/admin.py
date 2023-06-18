from django.contrib import admin

from .models import (
    Client,
    ClientUpdate,
    ZipCode,
    HomeListing,
    Task,
    ScrapeResponse,
    HomeListingTags,
    Realtor,
    SavedFilter,
)


# Register your models here.
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "address",
        "status",
        "revenue",
        "company__name",
        "servTitanID",
        "phoneNumber",
        "price",
        "year_built",
        "city",
        "state",
        "contacted",
        "note",
        "zipCode__zip",
        "equipmentInstalledDate",
        "serviceTitanCustomerSince",
    )
    search_fields = (
        "name",
        "address",
        "status",
        "city",
        "state",
        "servTitanID",
        "zipCode__zipCode",
        "company__name",
    )

    def zipCode__zip(self, obj):
        return obj.zipCode.zipCode

    def company__name(self, obj):
        return obj.company.name


class ClientUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "client__name", "company__name", "status", "listed")
    search_fields = (
        "id",
        "client__name",
        "status",
        "listed",
        "client__company__name",
    )

    def client__name(self, obj):
        return obj.client.name

    def company__name(self, obj):
        return obj.client.company.name


class ZipcodeAdmin(admin.ModelAdmin):
    list_display = ("zipCode", "lastUpdated", "count")
    search_fields = ["zipCode", "lastUpdated"]

    def count(self, obj):
        return Client.objects.filter(zipCode=obj.zipCode).count()


class HomeListingAdmin(admin.ModelAdmin):
    list_display = (
        "address",
        "city",
        "zipCode__zip",
        "status",
        "listed",
        "price",
        "year_built",
    )
    search_fields = [
        "address",
        "status",
        "zipCode__zipCode",
    ]

    def zipCode__zip(self, obj):
        return obj.zipCode.zipCode


class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "completed", "deletedClients")


class ScrapeResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "zip", "status", "url")
    search_fields = ["id", "date", "zip", "status", "url"]


class HomeListingTagsAdmin(admin.ModelAdmin):
    list_display = ("id", "tag")
    search_fields = ["id", "tag"]


class RealtorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "email", "company")
    search_fields = ["id", "name", "phone", "email", "company"]

    def company__name(self, obj):
        return obj.name


class SavedFilterAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "company")
    search_fields = ["id", "name", "company"]


admin.site.register(HomeListing, HomeListingAdmin)
admin.site.register(ZipCode, ZipcodeAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(ScrapeResponse, ScrapeResponseAdmin)
admin.site.register(ClientUpdate, ClientUpdateAdmin)
admin.site.register(HomeListingTags, HomeListingTagsAdmin)
admin.site.register(Realtor, RealtorAdmin)
admin.site.register(SavedFilter, SavedFilterAdmin)
