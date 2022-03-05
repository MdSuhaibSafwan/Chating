from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from messaging.consumers import MessagingConsumer
from django.urls import path


application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                path("message/", MessagingConsumer.as_asgi(), ),
            ]
        )
    )
})
