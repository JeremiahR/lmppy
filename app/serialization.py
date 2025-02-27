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

    def to_bytes(self) -> bytes:
        """Serialize the element and then return the bytes"""
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

    def to_bytes(self) -> bytes:
        return self.type_int.to_bytes(2, byteorder="big")


@dataclass
class SizedBytes(Element):
    id = "sized_bytes"
    byteslen: int
    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        byteslen = int.from_bytes(data[:2], byteorder="big")
        features = data[2 : 2 + byteslen]
        return (cls(byteslen, features), data[2 + byteslen :])

    def to_bytes(self) -> bytes:
        return self.byteslen.to_bytes(2, byteorder="big") + bytes(self.data)


@dataclass
class GlobalFeatures(SizedBytes):
    """The global features of a node."""

    id = "global_features"


@dataclass
class LocalFeatures(SizedBytes):
    """The local features of a node."""

    id = "local_features"


@dataclass
class PingOrPongBytes(SizedBytes):
    """The number of bytes in a ping or pong message."""

    id = "ping_or_pong_bytes"


@dataclass
class NumPongBytes(Element):
    """The number of bytes in a pong message."""

    id = "num_pong_bytes"
    num_bytes: int

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        num_bytes = int.from_bytes(data[:2], byteorder="big")
        return (cls(num_bytes), data[2:])

    def to_bytes(self) -> bytes:
        return self.num_bytes.to_bytes(2, byteorder="big")


@dataclass
class RemainderBytes(Element):
    """Special case element when we have bytes at the end that we don't handle yet."""

    id = "remainder"
    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        return (cls(bytes(data)), b"")

    def to_bytes(self) -> bytes:
        return bytes(self.data)
