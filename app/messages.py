from dataclasses import dataclass
from typing import List, Type

from app.serialization import (
    Element,
    GlobalFeatures,
    LocalFeatures,
    MessageType,
    NumPongBytes,
    PingOrPongBytes,
)


@dataclass
class Message:
    data: bytes
    properties: dict

    @classmethod
    def features(cls) -> List[Type[Element]]:
        return [MessageType]

    @classmethod
    def from_bytes(cls, data: bytes):
        properties = {}
        chunked = bytes(data)
        for feature in cls.features():
            el, chunked = feature.from_bytes(chunked)
            properties[el.id] = el
        return cls(data, properties)

    def __str__(self):
        return f"{self.__class__.__name__}(...)"

    @property
    def length(self):
        return len(self.data)

    @property
    def type_name(self):
        return self.properties.get(MessageType.id, None).name

    @property
    def type_code(self):
        return self.properties.get(MessageType.id, None).type_int


@dataclass
class InitMessage(Message):
    @classmethod
    def features(cls) -> List[Type[Element]]:
        return super().features() + [GlobalFeatures, LocalFeatures]

    @property
    def global_features(self):
        return self.properties[GlobalFeatures.id]

    @property
    def local_features(self):
        return self.properties[LocalFeatures.id]


class PingMessage(Message):
    @classmethod
    def from_bytes(cls, data: bytes):
        a = super().from_bytes(data)
        data = data[2:]  # trim type code
        a.properties["num_pong_bytes"], data = NumPongBytes.from_bytestream(data)
        a.properties["pingpongdata"], data = PingOrPongBytes.from_bytestream(data)
        return a


class PongMessage(Message):
    @classmethod
    def from_bytes(cls, data: bytes):
        a = super().from_bytes(data)
        data = data[2:]  # trim type code
        a.properties["pingpongdata"], data = PingOrPongBytes.from_bytestream(data)
        return a


class MessageDecoder:
    @classmethod
    def from_bytes(cls, data: bytes):
        message_type = int.from_bytes(data[:2], byteorder="big")
        # TODO: a cleaner way to decode, such as a global registry
        if message_type == 16:
            return InitMessage.from_bytes(data)
        elif message_type == 18:
            return PingMessage.from_bytes(data)
        elif message_type == 19:
            return PongMessage.from_bytes(data)
        else:
            return Message.from_bytes(data)
