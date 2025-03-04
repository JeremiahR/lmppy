import argparse
import os
import sys
from datetime import datetime

from ecdsa import SECP256k1, SigningKey
from pyln.proto.primitives import PrivateKey
from pyln.proto.wire import connect

from app.message_decoder import MessageDecoder
from app.messages import PingMessage
from app.peer import Peer


def parse_args():
    parser = argparse.ArgumentParser(
        prog="lightning-mini-peer",
        description="A minimal lightning peer for testing and development",
    )
    parser.add_argument("host", help="the peer address in pubkey@host:port format")
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()


def generate_private_key():
    """Generate a new private key if one does not exist, otherwise return the existing one."""
    if os.path.exists("private_key.pem"):
        with open("private_key.pem", "rb") as f:
            return PrivateKey(f.read())
    else:
        pk = PrivateKey(SigningKey.generate(curve=SECP256k1).to_string())
        with open("private_key.pem", "wb") as f:
            f.write(pk.serializeCompressed())
            f.close()
        return pk


def main():
    args = parse_args()
    private_key = generate_private_key()
    peer = Peer.from_string(args.host)

    # Create an ephemeral keypair and connect to peer
    print(f"Connecting to {args.host}")
    lc = connect(private_key, peer.node_id, peer.host, port=peer.port)  # pyright: ignore

    # Send an init message, with no global features, and 0b10101010 as local
    # features.
    lc.send_message(b"\x00\x10\x00\x00\x00\x01\xaa")

    log_filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log"
    f = open(log_filename, "a")

    # connect to peer and log messages
    i = 0
    while True:
        try:
            data = lc.read_message()
        except ValueError as e:
            # do nothing on ValueError since it occurs so frequently, just print it.
            print(f"Error reading message: {e}")
            continue
        message = MessageDecoder.from_bytes(data)
        f.write(data.hex() + "\n")
        f.flush()
        print(message)
        if i % 3 == 0:
            ping = PingMessage.create(10, bytes.fromhex("aa"))
            lc.send_message(ping.to_bytes())
        i += 1


if __name__ == "__main__":
    main()
