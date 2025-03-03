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
    # Gossip & Network Announcements
    256: "channel_announcement",
    257: "node_announcement",
    258: "channel_update",
    259: "announcement_signatures",
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
