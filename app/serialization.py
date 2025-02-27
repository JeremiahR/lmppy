from dataclasses import dataclass
from typing import Self

from app.types import LIGHTNING_MESSAGE_TYPES


@dataclass
class Element:
    id = "ImplementMe!"

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        """Deserialize the element and then return remaining data as a slice"""
        raise NotImplementedError("Subclasses must implement this method")


@dataclass
class MessageType(Element):
    """The initial type of a message, stored in the first two bytes of the message"""

    id = "message_type"
    type_int: int
    name: str

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        type_int = int.from_bytes(data[:2], byteorder="big")
        name = LIGHTNING_MESSAGE_TYPES.get(type_int, "unknown")
        return (cls(type_int=type_int, name=name), data[2:])


@dataclass
class GlobalFeatures(Element):
    """The global features of a node."""

    id = "global_features"
    gflen: int
    features: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        gflen = int.from_bytes(data[:2], byteorder="big")
        features = data[2 : 2 + gflen]
        return (cls(gflen, features), data[2 + gflen :])


@dataclass
class LocalFeatures(Element):
    """The local features of a node."""

    id = "local_features"
    lflen: int
    features: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        lflen = int.from_bytes(data[:2], byteorder="big")
        features = data[2 : 2 + lflen]
        return (cls(lflen, features), data[2 + lflen :])


@dataclass
class PingOrPongBytes(Element):
    """The number of bytes in a ping or pong message."""

    id = "ping_or_pong_bytes"
    num_bytes: int
    ignored: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        num_bytes = int.from_bytes(data[:2], byteorder="big")
        ignored = data[2 : 2 + num_bytes]
        return (cls(num_bytes, ignored), data[2 + num_bytes :])


@dataclass
class NumPongBytes(Element):
    """The number of bytes in a pong message."""

    id = "num_pong_bytes"
    num_bytes: int

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        num_bytes = int.from_bytes(data[:2], byteorder="big")
        return (cls(num_bytes), data[2:])
