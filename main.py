import argparse
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ecdsa import SECP256k1, SigningKey
from pyln.proto.primitives import PrivateKey, PublicKey
from pyln.proto.wire import connect

# https://github.com/lightning/bolts/blob/master/02-peer-protocol.md
LIGHTNING_MESSAGE_TYPES = {
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
    parser = argparse.ArgumentParser(
        prog="lightning-mini-peer",
        description="A minimal lightning peer for testing and development",
    )
    parser.add_argument("host", help="the peer address in pubkey@host:port format")
    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    peer = Peer.from_string(args.host)

    # Create an ephemeral keypair and connect to peer
    print(f"Connecting to {args.host}")
    private_key = PrivateKey(SigningKey.generate(curve=SECP256k1).to_string())
    lc = connect(private_key, peer.node_id, peer.host, port=peer.port, socks_addr=None)

    # Send an init message, with no global features, and 0b10101010 as local
    # features.
    lc.send_message(b"\x00\x10\x00\x00\x00\x01\xaa")

    log_filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log"
    f = open(log_filename, "a")

    # connect to peer and log messages
    while True:
        message = lc.read_message()
        message = Message.from_bytes(message)
        f.write(message.content.hex() + "\n")
        f.flush()
        print(message)


if __name__ == "__main__":
    main()
