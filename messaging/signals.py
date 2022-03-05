from django.core.exceptions import ObjectDoesNotExist
from .models import ChatingRoomMessage
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


@receiver(signal=post_save, sender=ChatingRoomMessage)
def websocket_send_message(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        
        chat_room1 = f"room_{instance.get_to_user}"
        chat_room2 = f"room_{instance.sent_by_user}"

        instance_data = json.dumps({
            "from_user": f"{instance.sent_by_user}",
            "to_user": f"{instance.get_to_user}",
            "message": instance.message,
            "slug": instance.slug,
            "date_created": f"{instance.date_created}",
        })
        print("\n")
        print("From Signal", chat_room1)

        async_to_sync(channel_layer.group_send)(
            chat_room1,
            {
                "type": "send.message",
                "data": instance_data
            }
        )
        
        print("\n")
        print("\n")
        print("\n")
        
        async_to_sync(channel_layer.group_send)(
            chat_room2,
            {
                "type": "send.message",
                "data": instance_data
            }
        )

        print("\n")

