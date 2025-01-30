from django.urls import path, re_path
from . import consumers
from .consumers import *
# routing.py
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room>\w+)/$', ChatConsumer.as_asgi()),
]