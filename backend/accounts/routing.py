from django.urls import path
from . import consumers


urlpatterns = [
    path('createCompany/', consumers.ProgressConsumer.as_asgi()),
]



