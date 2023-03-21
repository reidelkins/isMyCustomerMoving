from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()


urlpatterns = [
    # path('save-stripe-info/', views.save_stripe_info, name='save-stripe-info'),
    # path('setup-intent/', views.setup_intent, name='setup_intent'),
    # path('publishable-key/', views.publishable_key, name='publishable-key'),
    path("upgrade_plan/<str:user>/", views.Upgrade_Plan.as_view(), name="upgradePlan"),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path("", include(router.urls)),
]