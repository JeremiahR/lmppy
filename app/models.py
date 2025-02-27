from dataclasses import dataclass
from typing import Optional

from pyln.proto.primitives import PublicKey

from app.types import LIGHTNING_MESSAGE_TYPES


@dataclass
class Peer:
    node_id: PublicKey
    host: str
    port: int

    @classmethod
    def from_string(cls, s: str):
        node_id, host = s.split("@")
        host, port = host.split(":")
        port = int(port)
        node_id = PublicKey(bytes.fromhex(node_id))
        return cls(node_id, host, port)


@dataclass
class Message:
    message_type: int
    message_type_str: Optional[str]
    length: int
    content: bytes

    @classmethod
    def from_bytes(cls, data: bytes):
        message_type = int.from_bytes(data[:2], byteorder="big")
        message_type_str = LIGHTNING_MESSAGE_TYPES.get(message_type)
        length = len(data)
        return cls(message_type, message_type_str, length, data)

    def __repr__(self):
        return f"Message(message_type={self.message_type_str}({self.message_type}), length={self.length}, content={self.content.hex()})"
