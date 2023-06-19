# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from .models import CustomUser, Company, InviteToken, Enterprise


class CustomUserAdmin(UserAdmin):
    """Define admin model for custom User model with no username field."""

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "status",
                    "email",
                    "phone",
                    "company",
                    "isVerified",
                    "otp_enabled",
                    "otp_base32",
                    "otp_auth_url",
                    "enterprise",
                    "is_enterprise_owner",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "is_staff",
                    "password1",
                    "password2",
                    "company",
                    "email",
                    "phone",
                ),
            },
        ),
    )

    list_display = (
        "first_name",
        "last_name",
        "email",
        "isVerified",
        "company",
        "enterprise",
    )
    search_fields = ("id", "first_name", "last_name", "email")
    ordering = ("id",)
    list_filter = (
        "is_staff",
        "isVerified",
    )


class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "crm",
        "recentlySoldPurchased",
        "product",
        "enterprise",
    )


class InviteTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "company")
    search_fields = ["id", "email", "company"]


class EnterpriseAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ["id", "name"]


admin.site.register(Company, CompanyAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(InviteToken, InviteTokenAdmin)
admin.site.register(Enterprise, EnterpriseAdmin)
