from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()


client_patterns = [
    path(
        "<str:user>/",
        views.ClientListView.as_view(),
        name="client-list",
    ),
    path(
        "",
        views.ClientListView.as_view(),
        name="save-client-filter",
    ),
]

recently_sold_patterns = [
    path("", views.RecentlySoldView.as_view(), name="recently-sold"),
    path(
        "recentlysold/<str:filter>/",
        views.RecentlySoldView.as_view(),
        name="delete-recently-sold-filter",
    ),
]

for_sale_patterns = [
    path("", views.ForSaleView.as_view(), name="for-sale"),
    path(
        "forsale/<str:filter>/",
        views.ForSaleView.as_view(),
        name="delete-for-sale-filter",
    ),
]

service_titan_patterns = [
    path(
        "servicetitan/",
        views.ServiceTitanView.as_view(),
        name="servicetitan",
    ),
    path(
        "servicetitan/<str:task>/",
        views.ServiceTitanView.as_view(),
        name="servicetitan-with-task",
    ),
]

upload_file_patterns = [
    path(
        "upload/",
        views.UploadFileView.as_view(),
        name="upload-file",
    ),
    path(
        "upload/<str:task>/",
        views.UploadFileView.as_view(),
        name="upload-file-check",
    ),
]

urlpatterns = [
    path("recentlysold", include(recently_sold_patterns)),
    path(
        "downloadrecentlysold/",
        views.AllRecentlySoldView.as_view(),
        name="all-recently-sold",
    ),
    path("forsale", include(for_sale_patterns)),
    path(
        "downloadforsale/",
        views.AllForSaleView.as_view(),
        name="all-for-sale",
    ),
    path(
        "update/",
        views.UpdateStatusView.as_view(),
        name="update-status",
    ),
    path(
        "updateclient/",
        views.UpdateClientView.as_view(),
        name="update-client",
    ),
    path("upload/", include(upload_file_patterns)),
    path(
        "downloadclients/",
        views.DownloadClientView.as_view(),
        name="all-client-list",
    ),
    path("clients/", include(client_patterns)),
    path(
        "salesforce/",
        views.SalesforceView.as_view(),
        name="salesforce",
    ),
    path("servicetitan/", include(service_titan_patterns)),
]
