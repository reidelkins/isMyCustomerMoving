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


class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "address",
        "status",
        "revenue",
        "display_company_name",
        "serv_titan_id",
        "phone_number",
        "price",
        "year_built",
        "city",
        "state",
        "contacted",
        "note",
        "display_zip_code",
        "equipment_installed_date",
        "service_titan_customer_since",
    )
    search_fields = (
        "name",
        "address",
        "status",
        "city",
        "state",
        "serv_titan_id",
        "zip_code__zip_code",
        "company__name",
    )

    def display_zip_code(self, obj):
        return obj.zip_code.zip_code

    display_zip_code.short_description = "Zip Code"

    def display_company_name(self, obj):
        return obj.company.name

    display_company_name.short_description = "Company Name"


class ClientUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "display_client_name",
        "display_company_name",
        "status",
        "listed",
    )
    search_fields = (
        "id",
        "client__name",
        "status",
        "listed",
        "client__company__name",
    )

    def display_client_name(self, obj):
        return obj.client.name

    display_client_name.short_description = "Client Name"

    def display_company_name(self, obj):
        return obj.client.company.name

    display_company_name.short_description = "Company Name"


class ZipcodeAdmin(admin.ModelAdmin):
    list_display = ("zip_code", "last_updated", "count")
    search_fields = ["zip_code", "last_updated"]

    def count(self, obj):
        return Client.objects.filter(zip_code=obj.zip_code).count()


class HomeListingAdmin(admin.ModelAdmin):
    list_display = (
        "address",
        "city",
        "display_zip_code",
        "status",
        "listed",
        "price",
        "year_built",
    )
    search_fields = [
        "address",
        "status",
        "zip_code__zip_code",
    ]

    def display_zip_code(self, obj):
        return obj.zip_code.zip_code

    display_zip_code.short_description = "Zip Code"


class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "completed", "deleted_clients")


class ScrapeResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "zip", "status", "url")
    search_fields = ["id", "date", "zip", "status", "url"]


class HomeListingTagsAdmin(admin.ModelAdmin):
    list_display = ("id", "tag")
    search_fields = ["id", "tag"]


class RealtorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "company")
    search_fields = ["id", "name", "company"]


class SavedFilterAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "filter_type", "company")
    search_fields = ["id", "name", "filter_type", "company"]


admin.site.register(HomeListing, HomeListingAdmin)
admin.site.register(ZipCode, ZipcodeAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(ScrapeResponse, ScrapeResponseAdmin)
admin.site.register(ClientUpdate, ClientUpdateAdmin)
admin.site.register(HomeListingTags, HomeListingTagsAdmin)
admin.site.register(Realtor, RealtorAdmin)
admin.site.register(SavedFilter, SavedFilterAdmin)
