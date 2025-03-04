from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Type, TypeAlias, cast

from app.message_elements import (
    Fixed8BytesElement,
    Fixed32BytesElement,
    Fixed64BytesElement,
    MessageTypeElement,
    PointElement,
    RemainderElement,
    SerializedElement,
    U16Element,
    VarBytesElement,
)


class MessageProperty(Enum):
    """
    An ElementKey represents the unique names for datatypes which are encoded in documentation, for example see [channel_announcement](https://github.com/lightning/bolts/blob/master/07-routing-gossip.md#the-channel_announcement-message) in Bolt 7.
    """

    TYPE = "type"
    REMAINDER = "remainder"
    GLOBAL_FEATURES = "global_features"
    LOCAL_FEATURES = "local_features"
    NUM_PONG_BYTES = "num_pong_bytes"
    PING_OR_PONG_BYTES = "ping_or_pong_bytes"
    NODE_SIGNATURE_1 = "node_signature_1"
    NODE_SIGNATURE_2 = "node_signature_2"
    BITCOIN_SIGNATURE_1 = "bitcoin_signature_1"
    BITCOIN_SIGNATURE_2 = "bitcoin_signature_2"
    CHANNEL_FEATURES = "features"
    CHAIN_HASH = "chain_hash"
    SHORT_CHANNEL_ID = "short_channel_id"
    NODE_ID_1 = "node_id_1"
    NODE_ID_2 = "node_id_2"
    BITCOIN_KEY_1 = "bitcoin_key_1"
    BITCOIN_KEY_2 = "bitcoin_key_2"


KeyedElement: TypeAlias = Tuple[MessageProperty, Type[SerializedElement]]
MessagePropertiesDict: TypeAlias = Dict[MessageProperty, SerializedElement]


@dataclass
class Message:
    id: int
    name: str
    properties: MessagePropertiesDict

    @classmethod
    def features(cls) -> List[KeyedElement]:
        return [
            (MessageProperty.TYPE, MessageTypeElement),
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
            properties[MessageProperty.REMAINDER], chunked = (
                RemainderElement.from_bytes(chunked)
            )
        assert len(chunked) == 0, f"Unexpected data left: {chunked}"
        return cls(id, name, properties)  # pyright: ignore

    def to_bytes(self) -> bytes:
        data = b""
        for key, feature in self.features():
            data += self.properties[key].to_bytes()
        if MessageProperty.REMAINDER in self.properties:
            data += self.properties[MessageProperty.REMAINDER].to_bytes()
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
        return self.properties.get(MessageProperty.TYPE).name  # pyright: ignore

    @property
    def type_code(self):
        return self.properties.get(MessageProperty.TYPE).id  # pyright: ignore


class InitMessage(Message):
    id = 16

    @classmethod
    def features(cls) -> List[KeyedElement]:
        return super().features() + [
            (MessageProperty.GLOBAL_FEATURES, VarBytesElement),
            (MessageProperty.LOCAL_FEATURES, VarBytesElement),
        ]

    @property
    def global_features(self) -> VarBytesElement:
        return self.properties[MessageProperty.GLOBAL_FEATURES]  # pyright: ignore

    @property
    def local_features(self) -> VarBytesElement:
        return self.properties[MessageProperty.LOCAL_FEATURES]  # pyright: ignore


class PingMessage(Message):
    id: int = 18
    name: str = "ping"

    @classmethod
    def features(cls) -> List[KeyedElement]:
        return super().features() + [
            (MessageProperty.NUM_PONG_BYTES, U16Element),
            (MessageProperty.PING_OR_PONG_BYTES, VarBytesElement),
        ]

    @property
    def num_pong_bytes(self):
        num_pong_bytes = cast(
            U16Element, self.properties[MessageProperty.NUM_PONG_BYTES]
        )  # pyright: ignore
        return num_pong_bytes.num_bytes

    @classmethod
    def create(cls, num_pong_bytes: int, message: bytes):
        return PingMessage(
            id=18,
            name="ping",
            properties={
                MessageProperty.TYPE: MessageTypeElement(id=18, name="ping"),
                MessageProperty.NUM_PONG_BYTES: U16Element(num_bytes=num_pong_bytes),
                MessageProperty.PING_OR_PONG_BYTES: VarBytesElement(
                    len(message), data=message
                ),
            },
        )


class PongMessage(Message):
    id = 19
    name = "pong"

    @classmethod
    def features(cls) -> List[KeyedElement]:
        return super().features() + [
            (MessageProperty.PING_OR_PONG_BYTES, VarBytesElement),
        ]

    @property
    def num_bytes(self):
        return self.properties[MessageProperty.PING_OR_PONG_BYTES].num_bytes  # pyright: ignore

    @classmethod
    def create_from_ping(cls, msg: PingMessage):
        return PongMessage(
            id=19,
            name="pong",
            properties={
                MessageProperty.TYPE: MessageTypeElement(id=19, name="pong"),
                MessageProperty.PING_OR_PONG_BYTES: VarBytesElement(
                    msg.num_pong_bytes, data=b"0" * msg.num_pong_bytes
                ),
            },
        )


class ChannelAnnouncement(Message):
    id = 256
    name = "channel_announcement"

    @classmethod
    def features(cls) -> List[KeyedElement]:
        return super().features() + [
            (MessageProperty.NODE_SIGNATURE_1, Fixed64BytesElement),
            (MessageProperty.NODE_SIGNATURE_2, Fixed64BytesElement),
            (MessageProperty.BITCOIN_SIGNATURE_1, Fixed64BytesElement),
            (MessageProperty.BITCOIN_SIGNATURE_2, Fixed64BytesElement),
            (MessageProperty.CHANNEL_FEATURES, VarBytesElement),
            (MessageProperty.CHAIN_HASH, Fixed32BytesElement),
            (MessageProperty.SHORT_CHANNEL_ID, Fixed8BytesElement),
            (MessageProperty.NODE_ID_1, PointElement),
            (MessageProperty.NODE_ID_2, PointElement),
            (MessageProperty.BITCOIN_KEY_1, PointElement),
            (MessageProperty.BITCOIN_KEY_2, PointElement),
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
