import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from apps.b2b.consumers import OrderConsumer,LedgerConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter([
        path("ws/orders/", OrderConsumer.as_asgi()),
         path("ws/ledger/", LedgerConsumer.as_asgi()),
    ]),
})