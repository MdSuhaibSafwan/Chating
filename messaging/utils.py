from django.core.exceptions import ObjectDoesNotExist
from .models import ChatingRoom, ChatingRoomMessage
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from django.http import Http404

User = get_user_model()


@sync_to_async
def get_user(username):
    try:
        obj = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return False

    return obj


@sync_to_async
def send_message(from_user, to_user, text):
    print(to_user, from_user)
    try:
        room = ChatingRoom.objects.get_or_create_room(str(from_user), str(to_user))
    except ObjectDoesNotExist as e:
        print(e)
        return None
    except Http404 as e:
        print(e)
        return None
    message_obj = ChatingRoomMessage.objects.create(user1=from_user, user2=to_user, sent_by_user=from_user, 
                                        message=text, chat_room=room)
    return message_obj
