import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from .utils import get_user, send_message

User = get_user_model()


class MessagingConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("[ CONNECTED ] ", event)
        await self.send({
            "type": "websocket.accept"
        })
        user = await self.get_user()
        if user is None:
            await self.send({
                "type": "websocket.close"
            })
            return False

        room = f"room_{user.username}"
        self.scope["user"] = user
        self.chat_room = room
        # print(room)
        await self.channel_layer.group_add(
            room,
            self.channel_name,
        )



    @database_sync_to_async
    def get_user(self):
        url_queries = str(self.scope["query_string"].decode("utf-8"))
        and_split = url_queries.split("&")
        url_queries = {}
        for i in and_split:
            key_pair = i.split("=")
            url_queries[key_pair[0]] = key_pair[1]

        username = url_queries.get("user")
        # print(username)
        if username is None:
            return None
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return None

        return user

    async def websocket_receive(self, event):
        """
        Data should be something like this comming from Frontend
        {
            "command": "new_message",
            "message": "Hello World",
            "user": "new_user"
        }
        """
        data = json.loads(event["text"])
        print(data, "\n")

        commands = {
            "new_message": self.send_new_message,
        }

        command = data.get("command")
        try:
            message = data.get("message")
            user = data.get("user")
            await commands[command](message, user)

        except KeyError as e:
            print("KEY ERROR: ", e)
            await self.send({"type": "websocket.close"})

        return False

    async def send_new_message(self, message, user):
        print("Inside Send Message", message, user)
        user = await get_user(user)
        print("GOt USER ", str(user))
        if user is None:
            await self.send({"type": "websocket.close"})
            return

        print(user)
        curr_user = self.scope["user"]
        message = await send_message(from_user=curr_user, to_user=user, text=message)
        if message is None:
            await self.send({"type": "websocket.close"})
            return

        print(message)

    async def send_message(self, event):
        data = event["data"]
        await self.send({"type": "websocket.send", "text": data})

    async def websocket_disconnect(self, event):
        print("[ DISCONNECTED ] ", event)

