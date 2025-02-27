from dataclasses import dataclass
from typing import List, Type

from app.serialization import (
    GlobalFeatures,
    LocalFeatures,
    MessageType,
    NumPongBytes,
    PingOrPongBytes,
    RemainderBytes,
    SerializedElement,
)


@dataclass
class Message:
    properties: dict

    @classmethod
    def features(cls) -> List[Type[SerializedElement]]:
        return [MessageType]

    @classmethod
    def from_bytes(cls, data: bytes):
        properties = {}
        chunked = bytes(data)
        for feature in cls.features():
            el, chunked = feature.from_bytes(chunked)
            properties[el.id] = el
        if len(chunked) > 0:
            properties[RemainderBytes.id], chunked = RemainderBytes.from_bytes(chunked)
            assert len(chunked) == 0, f"Unexpected data left: {chunked}"
        return cls(properties)

    def to_bytes(self) -> bytes:
        data = b""
        for feature in self.features():
            data += feature.to_bytes(self.properties[feature.id])
        if RemainderBytes.id in self.properties:
            data += self.properties[RemainderBytes.id].to_bytes()
        return data

    def __str__(self):
        out = []
        for property in self.properties.values():
            out.append(f"{property.id}: {property}")
        return f"{self.__class__.__name__}({', '.join(out)})"

    @property
    def length(self):
        return len(self.to_bytes())

    @property
    def type_name(self):
        return self.properties.get(MessageType.id, None).name

    @property
    def type_code(self):
        return self.properties.get(MessageType.id, None).type_int


class InitMessage(Message):
    id = 16

    @classmethod
    def features(cls) -> List[Type[SerializedElement]]:
        return super().features() + [GlobalFeatures, LocalFeatures]

    @property
    def global_features(self):
        return self.properties[GlobalFeatures.id]

    @property
    def local_features(self):
        return self.properties[LocalFeatures.id]


class PingMessage(Message):
    id = 18

    @classmethod
    def features(cls) -> List[Type[SerializedElement]]:
        return super().features() + [NumPongBytes, PingOrPongBytes]

    @classmethod
    def create(cls, ping_or_pong_bytes: PingOrPongBytes):
        return cls()


class PongMessage(Message):
    id = 19

    @classmethod
    def features(cls) -> List[Type[SerializedElement]]:
        return super().features() + [NumPongBytes, PingOrPongBytes]


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
