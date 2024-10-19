"""
ASGI config for Pizza project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Pizza.settings')
application = get_asgi_application()

from channels.routing import ProtocolTypeRouter,URLRouter
from django.urls import path
from Home.consumers import MyConsumer

ws_pattern=[
    path('ws/main/<order_id>',MyConsumer)
]

application = ProtocolTypeRouter({
    # WebSocket chat handler
    "websocket":(
            URLRouter(ws_pattern)
    ),
})
        