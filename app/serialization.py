from dataclasses import dataclass
from typing import Self

from app.types import LIGHTNING_MESSAGE_TYPES


@dataclass
class Element:
    id: str

    @classmethod
    def from_bytestream(cls, data: bytes) -> tuple[Self, bytes]:
        """Deserialize the element and then return remaining data as a slice"""
        raise NotImplementedError("Subclasses must implement this method")


@dataclass
class MessageType(Element):
    """The initial type of a message, stored in the first two bytes of the message"""

    type_int: int
    name: str

    @classmethod
    def from_bytestream(cls, data: bytes) -> tuple[Self, bytes]:
        type_int = int.from_bytes(data[:2], byteorder="big")
        name = LIGHTNING_MESSAGE_TYPES.get(type_int, "unknown")
        return (cls(id=f"{cls.__name__}", type_int=type_int, name=name), data[2:])
