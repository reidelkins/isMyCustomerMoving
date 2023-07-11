from django.urls import path, include
from rest_framework import routers

from . import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"glogin", views.GoogleLoginViewSet, basename="glogin")

login_patterns = [
    path("", views.MyTokenObtainPairView.as_view(), name="login"),
    path("google/", views.TokenValidateView.as_view(), name="google-login"),
]

zapier_patterns = [
    path("", views.ZapierTokenView.as_view(), name="zapier-login"),
    path(
        "sold/",
        views.ZapierSoldSubscribeView.as_view(),
        name="zapier-sold-subscribe",
    ),
    path(
        "forSale/",
        views.ZapierForSaleSubscribeView.as_view(),
        name="zapier-forSale-subscribe",
    ),
    path(
        "recentlySold/",
        views.ZapierRecentlySoldSubscribeView.as_view(),
        name="zapier-recentlySold-subscribe",
    ),
]

urlpatterns = [
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("otp/disable/", views.OTPDisableView.as_view(), name="otp-disable"),
    path(
        "otp/validate/", views.OTPValidateView.as_view(), name="otp-validate"
    ),
    path("otp/verify/", views.OTPVerifyView.as_view(), name="otp-verify"),
    path(
        "otp/generate/", views.OTPGenerateView.as_view(), name="otp-generate"
    ),
    path("company/", views.CompanyView.as_view(), name="createCompany"),
    path(
        "manageuser/<str:id>/",
        views.ManageUserView.as_view(),
        name="manage-user",
    ),
    path(
        "acceptinvite/<str:invitetoken>/",
        views.AcceptInvite.as_view(),
        name="accept-invite",
    ),
    # TODO: figure out how to write a reverse url for this
    path(
        "password_reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    path("users/", views.UserListView.as_view(), name="user-list"),
    path("register/", views.RegisterView.as_view(), name="register"),
    # TODO: write test for google login url
    path("login/", include(login_patterns)),
    path(
        "enterprise/", views.UserEnterpriseView.as_view(), name="enterprise"
    ),
    # TODO: write tests for zapier and authenticated_user urls
    path("zapier/", include(zapier_patterns)),
    path(
        "authenticated_user/",
        views.AuthenticatedUserView.as_view(),
        name="authenticated_user",
    ),
    path("", include(router.urls)),
]
