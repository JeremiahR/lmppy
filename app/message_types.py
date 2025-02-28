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
class SizedBytesElement(SerializedElement):
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
class U16Element(SerializedElement):
    num_bytes: int

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        num_bytes = int.from_bytes(data[:2], byteorder="big")
        return (cls(num_bytes), data[2:])

    def to_bytes(self) -> bytes:
        return self.num_bytes.to_bytes(2, byteorder="big")


@dataclass
class RemainderElement(SerializedElement):
    """Special case element when we have bytes at the end that we don't handle yet."""

    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        """Takes all remaining bytes."""
        return (cls(bytes(data)), b"")

    def to_bytes(self) -> bytes:
        return bytes(self.data)
