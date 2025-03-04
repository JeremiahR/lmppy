import argparse
import os
import sys

from ecdsa import SECP256k1, SigningKey
from pyln.proto.primitives import PrivateKey


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
