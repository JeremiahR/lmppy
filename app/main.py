import argparse
import sys
from datetime import datetime

from ecdsa import SECP256k1, SigningKey
from pyln.proto.primitives import PrivateKey
from pyln.proto.wire import connect

from app.messages import MessageDecoder, PingMessage
from app.peer import Peer


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
    lc = connect(private_key, peer.node_id, peer.host, port=peer.port)  # pyright: ignore

    # Send an init message, with no global features, and 0b10101010 as local
    # features.
    lc.send_message(b"\x00\x10\x00\x00\x00\x01\xaa")

    log_filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log"
    f = open(log_filename, "a")

    ping = PingMessage.create(10, bytes.fromhex("aa"))

    # connect to peer and log messages
    i = 0
    error_count = 0
    while True:
        try:
            data = lc.read_message()
        except ValueError as e:
            print(f"Error reading message: {e}")
            error_count += 1
            if error_count > 10:
                print("Too many errors, exiting")
                sys.exit(1)
            continue
        message = MessageDecoder.from_bytes(data)
        f.write(data.hex() + "\n")
        f.flush()
        print(message)
        if i % 3 == 0:
            lc.send_message(ping.to_bytes())
        i += 1


if __name__ == "__main__":
    main()
