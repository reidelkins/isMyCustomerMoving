from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from .models import CustomUser, Company, Client, ZipCode, HomeListing


class CustomUserAdmin(UserAdmin):
    """Define admin model for custom User model with no username field."""
    fieldsets = (
        (None, {'fields': ('first_name',
                           'last_name',
                           'avatarUrl',
                           'status',
                           'email',
                           'role',
                           'company',
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
                    'isVerified', 'role')
    search_fields = ('id', 'first_name', 'last_name', 'email')
    ordering = ('id',)
    list_filter = ('is_staff', 'role', 'isVerified',)

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'accessToken', 'avatarUrl')

class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'status', 'city', 'state', 'contacted', 'note')
    search_fields = ('name', 'address', 'status')

class ZipcodeAdmin(admin.ModelAdmin):
    list_display = ('zipCode', 'lastUpdated')
    search_fields = ['zipCode', 'lastUpdated']

class HomeListingAdmin(admin.ModelAdmin):
    list_display = ('address', 'zipCode', 'status', 'listed')
    search_fields = ['address', 'status']


# Register your models here.
admin.site.register(HomeListing, HomeListingAdmin)
admin.site.register(ZipCode, ZipcodeAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
