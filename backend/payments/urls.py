from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path(
        "stripe/webhook/97eb874d-ad5d-4b4b-8889-5eb7c31f83d5/",
        include("djstripe.urls", namespace="djstripe"),
    ),
    path("", include(router.urls)),
]
