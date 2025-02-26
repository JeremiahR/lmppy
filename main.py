import os
import sys
from dataclasses import dataclass
from typing import Optional

from ecdsa import SECP256k1, SigningKey
from pyln.proto.primitives import PrivateKey, PublicKey
from pyln.proto.wire import connect

LOGGING_DIRECTORY = "log"

LIGHTNING_MESSAGE_TYPES = {
    # Connection & Keepalive
    16: "init",
    17: "error",
    18: "ping",
    19: "pong",
    # Channel Establishment (BOLT #2)
    32: "open_channel",
    33: "accept_channel",
    34: "funding_created",
    35: "funding_signed",
    36: "funding_locked",
    38: "shutdown",
    39: "closing_signed",
    # Channel Updates & HTLC Management (BOLT #3)
    128: "update_add_htlc",
    130: "update_fulfill_htlc",
    131: "update_fail_htlc",
    132: "commitment_signed",
    133: "revoke_and_ack",
    134: "update_fee",
    135: "update_fail_malformed_htlc",
    136: "channel_reestablish",
    # Gossip & Network Announcements (BOLT #7)
    256: "channel_announcement",
    257: "node_announcement",
    258: "channel_update",
    259: "announcement_signatures",
    265: "gossip_timestamp_filter",
}


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


def main():
    if len(sys.argv) < 2:
        print("Usage: python lmppy.py pubkey@url:port")
        sys.exit(1)
    peer = Peer.from_string(sys.argv[1])

    print(f"Host: {peer.host}, Port: {peer.port}, Public Key: {peer.node_id}")

    private_key = SigningKey.generate(curve=SECP256k1)
    private_key = PrivateKey(private_key.to_string())

    # sock = socket.socket()
    # sock.connect((peer.host, peer.port))

    lc = connect(private_key, peer.node_id, peer.host, port=peer.port, socks_addr=None)
    # Send an init message, with no global features, and 0b10101010 as local
    # features.
    lc.send_message(b"\x00\x10\x00\x00\x00\x01\xaa")

    # Now just read whatever our peer decides to send us
    os.mkdir(LOGGING_DIRECTORY)
    f = open(f"{LOGGING_DIRECTORY}/log.txt", "a")
    while True:
        message = lc.read_message()
        message = Message.from_bytes(message)
        f.write(message.content.hex() + "\n")
        f.flush()
        print(message)


if __name__ == "__main__":
    main()
