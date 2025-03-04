from dataclasses import dataclass
from typing import Self

TLV_MESSAGE_TYPES = {
    1: "networks",
    3: "remote_addr",
}

# https://github.com/lightning/bolts/blob/master/02-peer-protocol.md
LIGHTNING_MESSAGE_TYPES = {
    1: "warning",
    2: "stfu",
    # Connection & Keepalive
    16: "init",
    17: "error",
    18: "ping",
    19: "pong",
    # Channel Establishment
    32: "open_channel",
    33: "accept_channel",
    34: "funding_created",
    35: "funding_signed",
    36: "channel_ready",
    38: "shutdown",
    39: "closing_signed",
    40: "closing_complete",
    41: "closing_sig",
    64: "open_channel2",
    65: "accept_channel2",
    # TX updates
    66: "tx_add_input",
    67: "tx_add_output",
    68: "tx_remove_input",
    69: "tx_remove_output",
    70: "tx_complete",
    71: "tx_signatures",
    72: "tx_init_rbf",
    73: "tx_ack_rbf",
    74: "tx_abort",
    # Channel Updates & HTLC Management
    128: "update_add_htlc",
    130: "update_fulfill_htlc",
    131: "update_fail_htlc",
    132: "commitment_signed",
    133: "revoke_and_ack",
    134: "update_fee",
    135: "update_fail_malformed_htlc",
    136: "channel_reestablish",
    # Network Announcements
    256: "channel_announcement",
    257: "node_announcement",
    258: "channel_update",
    259: "announcement_signatures",
    # Gossip
    261: "query_short_channel_ids",
    262: "reply_short_channel_ids_end",
    263: "query_channel_range",
    264: "reply_channel_range",
    265: "gossip_timestamp_filter",
}


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
class SingleByteElement(SerializedElement):
    """A single byte element."""

    key = "single_byte_element"
    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        signature = data[:1]
        return (cls(data=signature), data[1:])

    def to_bytes(self) -> bytes:
        return bytes(self.data)


@dataclass
class Fixed8BytesElement(SerializedElement):
    """A fixed 8 byte element."""

    key = "bytes_8_element"
    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        signature = data[:8]
        return (cls(data=signature), data[8:])

    def to_bytes(self) -> bytes:
        return bytes(self.data)


class ShortChannelIDElement(Fixed8BytesElement):
    pass


@dataclass
class Fixed32BytesElement(SerializedElement):
    """A fixed 32 byte element."""

    key = "bytes_32_element"
    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        signature = data[:32]
        return (cls(data=signature), data[32:])

    def to_bytes(self) -> bytes:
        return bytes(self.data)


class ChainHashElement(Fixed32BytesElement):
    pass


@dataclass
class Fixed33BytesElement(SerializedElement):
    """A fixed 33 byte element."""

    key = "bytes_33_element"
    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        signature = data[:33]
        return (cls(data=signature), data[33:])

    def to_bytes(self) -> bytes:
        return bytes(self.data)


class PointElement(Fixed33BytesElement):
    pass


@dataclass
class Fixed64BytesElement(SerializedElement):
    """A fixed 64 byte element."""

    key = "bytes_64_element"
    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        signature = data[:64]
        return (cls(data=signature), data[64:])

    def to_bytes(self) -> bytes:
        return bytes(self.data)


class SignatureElement(Fixed64BytesElement):
    pass


@dataclass
class U16VarBytesElement(SerializedElement):
    num_bytes: int
    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        num_bytes = int.from_bytes(data[:2], byteorder="big")
        bytes_data = data[2 : 2 + num_bytes]
        return (cls(num_bytes, bytes_data), data[2 + num_bytes :])

    def to_bytes(self) -> bytes:
        return self.num_bytes.to_bytes(2, byteorder="big") + bytes(self.data)


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
class U32Element(SerializedElement):
    value: int

    @classmethod
    def from_bytes(cls, data: bytes) -> tuple[Self, bytes]:
        value = int.from_bytes(data[:4], byteorder="big")
        return (cls(value), data[4:])

    def to_bytes(self) -> bytes:
        return self.value.to_bytes(4, byteorder="big")


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
