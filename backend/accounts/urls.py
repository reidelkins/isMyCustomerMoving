from django.urls import path, include
from rest_framework import routers
from . import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)

urlpatterns = [
    # path('reset/', views.ResetView, name='reset'),
    # path('reset_request/', views.ResetRequestView.as_view(), name='reset_request'),
    path('verify_registration/', views.VerifyRegistrationView.as_view(), name='verify'),
    path('refresh_token/', TokenRefreshView.as_view(), name='refresh_token'),
    path('confirmation/<str:pk>/<str:uid>/', views.confirmation, name='email_confirmation'),
    
    path('update/<str:company>/', views.UpdateStatusView.as_view(), name='update-status'),
    path('servicetitan/<str:company>/', views.ServiceTitanView.as_view(), name='servicetitian'),
    path('company/', views.company, name='createCompany'),
    path('manageuser/<str:id>/', views.ManageUserView.as_view(), name='manageuser'),    
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('updateclient/<str:pk>/', views.update_client, name='updateclient'),
    path('upload/', views.UploadFileView.as_view(), name='upload-file'),
    path('clients/<str:company>/', views.ClientListView.as_view(), name='client-list'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.MyTokenObtainPairView.as_view(), name='login'),
    path("", include(router.urls)),
    
]
