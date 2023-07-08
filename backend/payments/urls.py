from django.urls import path, include
from rest_framework import routers
from payments import views

router = routers.DefaultRouter()

urlpatterns = [
    # path('save-stripe-info/', views.save_stripe_info, name='save-stripe-info'),
    # path('setup-intent/', views.setup_intent, name='setup_intent'),
    # path('publishable-key/', views.publishable_key, name='publishable-key'),
    path(
        "stripe/webhook/<uuid:uuid>/",
        views.StripeWebhook.as_view(),
        name="djstripe_webhook_by_uuid",
    ),
    path("stripe/webhook/$", views.StripeWebhook.as_view(), name="webhook"),
    path("", include(router.urls)),
]
