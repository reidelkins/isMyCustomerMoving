"""
ASGI config

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/

"""
import os
import sys
from pathlib import Path

from accounts.consumers import ChatConsumer

from django.urls import path
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack

# If DJANGO_SETTINGS_MODULE is unset, default to the local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# This application object is used by any ASGI server configured to use this file.
# django_application = get_asgi_application()

# Import websocket application here, so apps from django_application are loaded first
from config import routing  # noqa isort:skip

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa isort:skip


# application = ProtocolTypeRouter(
#     {
#         "http": get_asgi_application(),
#         "websocket": URLRouter(routing.websocket_urlpatterns),
#     }
# )

application = get_asgi_application()

ws_pattern = [
    path("chats/" , ChatConsumer.as_asgi())
]

application = ProtocolTypeRouter({
    "websocket" : AuthMiddlewareStack(URLRouter(
        ws_pattern
    )),
    "http": get_asgi_application(),
})