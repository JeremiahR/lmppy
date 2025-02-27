from dataclasses import dataclass

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
    type_code: int
    type_name: str
    length: int
    data: bytes
    properties: dict

    @classmethod
    def from_bytes(cls, data: bytes):
        message_type = int.from_bytes(data[:2], byteorder="big")
        message_type_str = LIGHTNING_MESSAGE_TYPES.get(message_type, "unknown")
        length = len(data)
        return cls(message_type, message_type_str, length, data, {})

    def __str__(self):
        return f"{self.__class__.__name__}(type={self.type_name}, type_code={self.type_code}, length={self.length}, data={self.data.hex()})"


@dataclass
class InitMessage(Message):
    @classmethod
    def from_bytes(cls, data: bytes):
        a = super().from_bytes(data)
        data = data[2:]
        gflen = int.from_bytes(data[:2], byteorder="big")
        data = data[2:]
        a.properties["global_features"] = data[:gflen]
        data = data[gflen:]
        lflen = int.from_bytes(data[:2], byteorder="big")
        data = data[2:]
        a.properties["local_features"] = data[:lflen]
        data = data[lflen:]
        a.properties["tlvs"] = data
        return a


class PingMessage(Message):
    @classmethod
    def from_bytes(cls, data: bytes):
        a = super().from_bytes(data)
        data = data[2:]  # trim type code
        a.properties["num_pong_bytes"] = int.from_bytes(data[:2], byteorder="big")
        data = data[2:]  # trim num_pong_bytes
        a.properties["byteslen"] = int.from_bytes(data[:2], byteorder="big")
        data = data[2:]  # trim byteslen
        a.properties["ignored"] = data
        return a


class PongMessage(Message):
    @classmethod
    def from_bytes(cls, data: bytes):
        a = super().from_bytes(data)
        data = data[2:]  # trim type code
        a.properties["byteslen"] = int.from_bytes(data[:2], byteorder="big")
        data = data[2:]  # trim byteslen
        a.properties["ignored"] = data
        return a


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
