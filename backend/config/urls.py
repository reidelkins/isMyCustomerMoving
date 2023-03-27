from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static


from .views import not_found, app_error
router = routers.DefaultRouter()
handler404 = not_found
handler500 = app_error

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/payments/', include('payments.urls')),
    path('api/v1/data/', include('data.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)