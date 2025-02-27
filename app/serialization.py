from dataclasses import dataclass
from typing import Self

from app.types import LIGHTNING_MESSAGE_TYPES


@dataclass
class SerializedElement:
    key = "serialized_element"

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        """Deserialize the element and then return remaining data as a slice"""
        raise NotImplementedError("Subclasses must implement this method")

    def to_bytes(self) -> bytes:
        """Serialize the element and then return the bytes"""
        raise NotImplementedError("Subclasses must implement this method")


@dataclass
class MessageTypeElement(SerializedElement):
    """The initial type of a message, stored in the first two bytes of the message"""

    key = "message_type"
    id: int
    name: str

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        id = int.from_bytes(data[:2], byteorder="big")
        name = LIGHTNING_MESSAGE_TYPES.get(id, "unknown")
        return (cls(id=id, name=name), data[2:])

    def to_bytes(self) -> bytes:
        return self.id.to_bytes(2, byteorder="big")


@dataclass
class SizedBytes(SerializedElement):
    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        byteslen = int.from_bytes(data[:2], byteorder="big")
        bytesdata = data[2 : 2 + byteslen]
        return (cls(bytesdata), data[2 + byteslen :])

    def to_bytes(self) -> bytes:
        return self.byteslen.to_bytes(2, byteorder="big") + bytes(self.data)

    @property
    def byteslen(self) -> int:
        return len(self.data)


@dataclass
class GlobalFeatures(SizedBytes):
    """The global features of a node."""

    key = "global_features"


@dataclass
class LocalFeatures(SizedBytes):
    """The local features of a node."""

    key = "local_features"


@dataclass
class PingOrPongBytes(SizedBytes):
    """The number of bytes in a ping or pong message."""

    key = "ping_or_pong_bytes"


@dataclass
class NumPongBytes(SerializedElement):
    """The number of bytes in a pong message."""

    key = "num_pong_bytes"
    num_bytes: int

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        num_bytes = int.from_bytes(data[:2], byteorder="big")
        return (cls(num_bytes), data[2:])

    def to_bytes(self) -> bytes:
        return self.num_bytes.to_bytes(2, byteorder="big")


@dataclass
class RemainderBytes(SerializedElement):
    """Special case element when we have bytes at the end that we don't handle yet."""

    key = "remainder"
    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        return (cls(bytes(data)), b"")

    def to_bytes(self) -> bytes:
        return bytes(self.data)
