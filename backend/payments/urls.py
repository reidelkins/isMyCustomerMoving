from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path("", include(router.urls)),
]
