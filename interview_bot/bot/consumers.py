from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import *
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['room']
        self.room_group_name = f"chat_{self.chatroom_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = self.scope["user"]
        chatroom = self.chatroom_name

        # Correct way to use sync_to_async with querysets
        @sync_to_async
        def get_user():
            return User.objects.filter(username=username.username).first()

        @sync_to_async
        def get_chat():
            return chatGroup.objects.filter(roomName=chatroom).first()

        @sync_to_async
        def create_message(user, chat):
            return Messages.objects.create(
                user=user,
                message=message,
                group=chat
            )

        # Get user and chat objects
        user = await get_user()
        chat = await get_chat()

        # Create message
        await create_message(user, chat)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": username.username,
                "room": self.chatroom_name
            }
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "user": event["user"],
            "room": event["room"]
        }))