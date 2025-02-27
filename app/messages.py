from dataclasses import dataclass

from app.serialization import (
    GlobalFeatures,
    LocalFeatures,
    MessageType,
    NumPongBytes,
    PingOrPongBytes,
)


@dataclass
class Message:
    type_code: int
    type_name: str
    length: int
    data: bytes
    properties: dict

    @classmethod
    def from_bytes(cls, data: bytes):
        mt, _ = MessageType.from_bytestream(data[:2])
        length = len(data)
        return cls(mt.type_int, mt.name, length, data, {})

    def __str__(self):
        return f"{self.__class__.__name__}(type={self.type_name}, type_code={self.type_code}, length={self.length}, data={self.data.hex()})"


@dataclass
class InitMessage(Message):
    @classmethod
    def from_bytes(cls, data: bytes):
        a = super().from_bytes(data)
        data = data[2:]  # trim type code
        a.properties["global_features"], data = GlobalFeatures.from_bytestream(data)
        a.properties["local_features"], data = LocalFeatures.from_bytestream(data)
        # a.properties["tlvs"] = data
        return a

    @property
    def global_features(self):
        return self.properties["global_features"]

    @property
    def local_features(self):
        return self.properties["local_features"]


class PingMessage(Message):
    @classmethod
    def from_bytes(cls, data: bytes):
        a = super().from_bytes(data)
        data = data[2:]  # trim type code
        a.properties["num_pong_bytes"], data = NumPongBytes.from_bytestream(data)
        a.properties["pingpongdata"], data = PingOrPongBytes.from_bytestream(data)
        return a


class PongMessage(Message):
    @classmethod
    def from_bytes(cls, data: bytes):
        a = super().from_bytes(data)
        data = data[2:]  # trim type code
        a.properties["pingpongdata"], data = PingOrPongBytes.from_bytestream(data)
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
