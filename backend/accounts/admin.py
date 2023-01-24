from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from .models import CustomUser, Company, Client, ZipCode, HomeListing, InviteToken, ClientUpdate


class CustomUserAdmin(UserAdmin):
    """Define admin model for custom User model with no username field."""
    fieldsets = (
        (None, {'fields': ('first_name',
                           'last_name',
                           'status',
                           'email',
                           'company',
                           'isVerified',
                           'otp_enabled',
                            'otp_base32',
                            'otp_auth_url',                            
                           )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'is_staff', 'password1', 'password2'),
        }),
    )

    list_display = ('first_name', 'last_name', 'email',
                    'isVerified')
    search_fields = ('id', 'first_name', 'last_name', 'email')
    ordering = ('id',)
    list_filter = ('is_staff', 'isVerified',)

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'accessToken', 'product')

class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'status', 'city', 'state', 'contacted', 'note', 'zipCode', 'company', 'servTitanID', 'phoneNumber')
    search_fields = ('name', 'address', 'status', 'city', 'state', 'servTitanID')

class ClientUpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'status', 'listed')

class ZipcodeAdmin(admin.ModelAdmin):
    list_display = ('zipCode', 'lastUpdated')
    search_fields = ['zipCode', 'lastUpdated']

class HomeListingAdmin(admin.ModelAdmin):
    list_display = ('address', 'zipCode', 'status', 'listed')
    search_fields = ['address', 'status']

class InviteTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'company')
    search_fields = ['id', 'email', 'company']

class ProgressUpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'percentDone')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'complete', 'updater', 'deleted')


# Register your models here.
admin.site.register(HomeListing, HomeListingAdmin)
admin.site.register(ZipCode, ZipcodeAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(InviteToken, InviteTokenAdmin)
admin.site.register(ClientUpdate, ClientUpdateAdmin)
