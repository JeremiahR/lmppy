from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Type, TypeAlias, cast

from app.message_elements import (
    MessageTypeElement,
    RemainderElement,
    SerializedElement,
    SizedBytesElement,
    U16Element,
)


class ElementKey(Enum):
    TYPE = "type"
    REMAINDER = "remainder"
    GLOBAL_FEATURES = "global_features"
    LOCAL_FEATURES = "local_features"
    NUM_PONG_BYTES = "num_pong_bytes"
    PING_OR_PONG_BYTES = "ping_or_pong_bytes"


KeyedElement: TypeAlias = Tuple[ElementKey, Type[SerializedElement]]
MessagePropertiesDict: TypeAlias = Dict[ElementKey, SerializedElement]


@dataclass
class Message:
    id: int
    name: str
    properties: MessagePropertiesDict

    @classmethod
    def features(cls) -> List[KeyedElement]:
        return [
            (ElementKey.TYPE, MessageTypeElement),
        ]

    @classmethod
    def from_bytes(cls, data: bytes):
        properties = {}
        chunked = bytes(data)
        for key, feature in cls.features():
            el, chunked = feature.from_bytes(bytes(chunked))
            properties[key] = el
            if feature is MessageTypeElement:
                el = cast(MessageTypeElement, el)
                id: int = el.id
                name: str = el.name
        if len(chunked) > 0:
            properties[ElementKey.REMAINDER], chunked = RemainderElement.from_bytes(
                chunked
            )
        assert len(chunked) == 0, f"Unexpected data left: {chunked}"
        return cls(id, name, properties)  # pyright: ignore

    def to_bytes(self) -> bytes:
        data = b""
        for key, feature in self.features():
            data += self.properties[key].to_bytes()
        if ElementKey.REMAINDER in self.properties:
            data += self.properties[ElementKey.REMAINDER].to_bytes()
        return data

    def __str__(self):
        out = []
        for key, property in self.properties.items():
            out.append(f"{key.value}: {property}")
        return f"{self.__class__.__name__}({', '.join(out)})"

    @property
    def length(self):
        return len(self.to_bytes())

    @property
    def type_name(self):
        return self.properties.get(ElementKey.TYPE).name  # pyright: ignore

    @property
    def type_code(self):
        return self.properties.get(ElementKey.TYPE).id  # pyright: ignore


class InitMessage(Message):
    id = 16

    @classmethod
    def features(cls) -> List[KeyedElement]:
        return super().features() + [
            (ElementKey.GLOBAL_FEATURES, SizedBytesElement),
            (ElementKey.LOCAL_FEATURES, SizedBytesElement),
        ]

    @property
    def global_features(self) -> SizedBytesElement:
        return self.properties[ElementKey.GLOBAL_FEATURES]  # pyright: ignore

    @property
    def local_features(self) -> SizedBytesElement:
        return self.properties[ElementKey.LOCAL_FEATURES]  # pyright: ignore


class PingMessage(Message):
    id: int = 18
    name: str = "ping"

    @classmethod
    def features(cls) -> List[KeyedElement]:
        return super().features() + [
            (ElementKey.NUM_PONG_BYTES, U16Element),
            (ElementKey.PING_OR_PONG_BYTES, SizedBytesElement),
        ]


class PongMessage(Message):
    id = 19

    @classmethod
    def features(cls) -> List[KeyedElement]:
        return super().features() + [
            (ElementKey.PING_OR_PONG_BYTES, SizedBytesElement),
        ]


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
