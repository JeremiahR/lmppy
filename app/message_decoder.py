import inspect
import sys

from app.messages import *  # noqa: F403, F401
from app.messages import Message


# Automatically build the message type dictionary
def build_message_map():
    message_map = {}
    for _, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if issubclass(obj, Message) and hasattr(obj, "id"):
            message_map[obj.id] = obj
    return message_map


MESSAGE_MAP = build_message_map()


class MessageDecoder:
    @classmethod
    def from_bytes(cls, data: bytes):
        message_type = int.from_bytes(data[:2], byteorder="big")
        message_class = MESSAGE_MAP.get(message_type)
        if message_class:
            return message_class.from_bytes(data)
        else:
            return Message.from_bytes(data)
