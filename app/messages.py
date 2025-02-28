from dataclasses import dataclass
from typing import List, Type

from app.message_types import (
    GlobalFeatures,
    LocalFeatures,
    MessageTypeElement,
    NumPongBytes,
    PingOrPongBytes,
    RemainderBytes,
    SerializedElement,
)


@dataclass
class Message:
    id: int
    name: str
    properties: dict

    @classmethod
    def features(cls) -> List[Type[SerializedElement]]:
        return [MessageTypeElement]

    @classmethod
    def from_bytes(cls, data: bytes):
        properties = {}
        chunked = bytes(data)
        id, name = None, None
        for feature in cls.features():
            el, chunked = feature.from_bytes(bytes(chunked))
            properties[el.key] = el
            if feature is MessageTypeElement:
                id = el.id
                name = el.name
        if len(chunked) > 0:
            properties[RemainderBytes.key], chunked = RemainderBytes.from_bytes(chunked)
        assert len(chunked) == 0, f"Unexpected data left: {chunked}"
        return cls(id, name, properties)

    def to_bytes(self) -> bytes:
        data = b""
        for feature in self.features():
            data += self.properties[feature.key].to_bytes()
        if RemainderBytes.key in self.properties:
            data += self.properties[RemainderBytes.key].to_bytes()
        return data

    def __str__(self):
        out = []
        for property in self.properties.values():
            out.append(f"{property.key}: {property}")
        return f"{self.__class__.__name__}({', '.join(out)})"

    @property
    def length(self):
        return len(self.to_bytes())

    @property
    def type_name(self):
        return self.properties.get(MessageTypeElement.key, None).name

    @property
    def type_code(self):
        return self.properties.get(MessageTypeElement.key, None).id


class InitMessage(Message):
    id = 16

    @classmethod
    def features(cls) -> List[Type[SerializedElement]]:
        return super().features() + [GlobalFeatures, LocalFeatures]

    @property
    def global_features(self):
        return self.properties[GlobalFeatures.key]

    @property
    def local_features(self):
        return self.properties[LocalFeatures.key]


class PingMessage(Message):
    id: int = 18
    name: str = "ping"

    @classmethod
    def features(cls) -> List[Type[SerializedElement]]:
        return super().features() + [NumPongBytes, PingOrPongBytes]


class PongMessage(Message):
    id = 19

    @classmethod
    def features(cls) -> List[Type[SerializedElement]]:
        return super().features() + [PingOrPongBytes]


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
